""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import itertools
import yaml


class PersonBase:
    """ Class to implement a person as a simpy discreate event simulation

        The person will have various characteristics which influences the simulation

        The person will have a flow around the simulation implemented as a list of activities
        which are callled as each one completes.
    """

    # create a unique ID counter
    get_new_id = itertools.count()

    # Load the state diagram for the finite state machine
    state_diagram = yaml.load("""
    init:
      initialise_a:
        action: run_a
        message_to_a: initialise
        message_to_b: NOP
        next_state: initialised_a
    initialised_a:
      initialised_a:
        action: NOP
        message_to_a: seize_resources
        message_to_b: NOP
        next_state: resources_seized_a
    resources_seized_a:
      resources_seized_a:
        action: NOP
        message_to_a: start
        message_to_b: NOP
        next_state: started_a
    started_a:
      completed_a:
        action: get_next_node
        message_to_a: NOP
        message_to_b: NOP
        next_state: branch_if_end
    branch_if_end:
      initialise_b:
        action: run_b
        message_to_a: NOP
        message_to_b: initialise
        next_state: initialised_b
      branch_to_end:
        action: NOP
        message_to_a: NOP
        message_to_b: NOP
        next_state: end_graph_release_a
    initialised_b:
      initialised_b:
        action: NOP
        message_to_a: NOP
        message_to_b: seize_resources
        next_state: resources_seized_b
    resources_seized_b:
      resources_seized_b:
        action: NOP
        message_to_a: release_resources
        message_to_b: NOP
        next_state: resources_released_a
    resources_released_a:
      resources_released:
        action: NOP
        message_to_a: end
        message_to_b: NOP
        next_state: stop_a_transfer_to_b
    stop_a_transfer_to_b:
      ended_a:
        action: b_to_a
        message_to_a: NOP
        message_to_b: start
        next_state: started_a
    end_graph_release_a:
      branch_to_end:
        action: NOP
        message_to_a: end
        message_to_b: NOP
        next_state: end
    """, Loader=yaml.SafeLoader)

    def __init__(self, simulation_params, starting_node_id, person_type=None):
        """Establish the persons characteristics, this will be specific to each model

        Arguments:
            simulation_params {Obj} -- Dictionary of parameters for the simulation
                                       (see simulation.py)

        Keyword Arguments:
            person_type {string} -- Type of person within the model e.g visitor, staff
                                    (default: {None})
        """
        # import simulation parameters
        self.simulation_params = simulation_params
        self.env = simulation_params.get('simpy_env', None)
        self.dc = simulation_params.get('data_collector', None)
        self.routing = simulation_params.get('routing', None)
        self.time_interval = simulation_params.get('time_interval', None)

        # keep a record of person IDs
        self.PID = next(PersonBase.get_new_id)

        # Routing is the list of environments that the person traverses
        self.starting_node_id = starting_node_id

        # Person type is a characteristic which affects behaviour in the microenvironment
        self.person_type = person_type

    def get_PID(self):
        """Return the Person ID (PID)

        Returns:
            string -- Person ID for the instance
        """
        return self.PID

    def run(self):
        """ Simulation process for the person

            Tests that the routing list still has destinations to visit

            pops the microenvironment to visit and uses entry_callback function to return the entry
            point passes a reference to person instance (self); pops the arguments passed as keyword
            list; and, passes as new argument list to entry point parameters; initiates a new simpy
            process for the persons activity within the microenvironment
        """

        # How can we set prioritisation of patients so that they can queue jump?
        # How do we handle reneging and re-routing (return message could achieve this at
        # resource_seized)
        function_dict = {
            'NOP': self.nop,
            'get_next_node': self.get_next_node,
            'run_a': self.run_a,
            'run_b': self.run_b,
            'b_to_a': self.transfer_b_to_a
        }

        state = 'init'
        received_message = 'initialise_a'
        activity_a = self.get_activity(self.starting_node_id)
        activity_b = None

        # For each microenvironment that the person visits
        finished = False
        while not finished:

            state_dict = PersonBase.state_diagram.get(state, 'No State')
            if state_dict == 'No state':
                raise ValueError(f'Person state error:s->{state}:m->{received_message}')

            actions = state_dict.get(received_message, 'No message')
            if actions == 'No message':
                raise ValueError(f'Person received message error:s->{state}:m->{received_message}')

            action = actions.get('action', 'NOP')
            message_to_a = actions.get('message_to_a', 'NOP')
            message_to_b = actions.get('message_to_b', 'NOP')
            state = actions.get('next_state', None)
            if not state:
                raise ValueError('Person next state invalid')

            # execute action
            activity_a, activity_b, received_message = function_dict.get(action)(activity_a,
                                                                                 activity_b,
                                                                                 received_message)

            # execute activities
            if message_to_a != 'NOP':
                activity_a.kwargs['message_to_activity'].put(message_to_a)
                received_message = yield activity_a.kwargs['message_to_person'].get()
                # print(f'RM_A:->{received_message}')
                received_message += '_a'

            elif message_to_b != 'NOP':
                activity_b.kwargs['message_to_activity'].put(message_to_b)
                received_message = yield activity_b.kwargs['message_to_person'].get()
                received_message += '_b'

            # print(f'RMP:->{received_message}')

            finished = True if state == 'end' else finished

    def nop(self, a, b, received_message):
        """Function which does nothing
        """
        return (a, b, received_message)

    def get_next_node(self, a, b, received_message):
        if a.next_activity_id != 'end':
            b = self.get_activity(a.next_activity_id)
            received_message = 'initialise_b'
        else:
            b = None
            received_message = 'branch_to_end'
        return (a, b, received_message)

    def run_a(self, a, b, received_message):
        if a is not None:
            self.run_activity(a)
        return (a, b, received_message)

    def run_b(self, a, b, received_message):
        if b is not None:
            self.run_activity(b)
        return (a, b, received_message)

    def transfer_b_to_a(self, a, b, received_message):
        a, b = b, None
        return (a, b, received_message)

    def run_activity(self, activity):
        activity_class = activity.activity_class(self.simulation_params, **activity.kwargs)
        self.env.process(activity_class.run())

    def get_activity(self, routing_id):
        activity = self.routing.get_activity(routing_id)

        # Add this instance to the arguments list
        activity.kwargs['person'] = self

        # Create two communication pipes for bi-directional communication with activity
        activity.kwargs['message_to_activity'] = simpy.Store(self.env)
        activity.kwargs['message_to_person'] = simpy.Store(self.env)

        return activity
