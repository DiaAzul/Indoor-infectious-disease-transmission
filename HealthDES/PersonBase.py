""" HealthDES - A python library to support discrete event simulation in health and social care """

import simpy
import simpy.events
import itertools
import yaml
import sys
from dataclasses import dataclass
from .AttrActions import AttrActions
from typing import Generator, Optional, NewType, Any

# We are not importing SimEnv and ACtivity, we are only using them for type checking.
# Note: import annotations from future for Python < 3.8
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .SimulationEnvironment import SimEnv
    from .ActivityBase import Activity


@dataclass
class Status:
    __slots__ = ['activity_a', 'activity_b', 'received_message']
    activity_a: Optional[Activity]
    activity_b: Optional[Activity]
    received_message: str


class PersonBase(AttrActions):
    """ Class to implement a person as a simpy discreate event simulation

        The person will have various characteristics which influences the simulation

        The person will have a flow around the simulation implemented as a list of activities
        which are callled as each one completes.
    """

    # create a unique ID counter
    get_new_id = itertools.count()

    # Load the state diagram for the finite state machine
    state_diagram = yaml.load(sys.intern("""
    init:
      initialise_a:
        action: run_a
        message_to_a: initialise
        next_state: initialised_a
    initialised_a:
      initialised_a:
        message_to_a: seize_resources
        next_state: resources_seized_a
    resources_seized_a:
      resources_seized_a:
        message_to_a: start
        next_state: started_a
    started_a:
      completed_a:
        action: get_next_node
        next_state: branch_if_end
    branch_if_end:
      initialise_b:
        action: run_b
        message_to_b: initialise
        next_state: initialised_b
      branch_to_end:
        message_to_a: end
        next_state: end
    initialised_b:
      initialised_b:
        message_to_b: seize_resources
        next_state: resources_seized_b
    resources_seized_b:
      resources_seized_b:
        message_to_a: release_resources
        next_state: resources_released_a
    resources_released_a:
      resources_released_a:
        message_to_a: end
        next_state: stop_a_transfer_to_b
    stop_a_transfer_to_b:
      ended_a:
        action: b_to_a
        next_state: resources_seized_a
    """), Loader=yaml.SafeLoader)

    def __init__(self, sim_env: SimEnv, starting_node_id: str) -> None:

        # import simulation parameters
        self.sim_env = sim_env

        # Routing is the list of environments that the person traverses
        self.starting_node_id = starting_node_id

        # Initialise AttrActions
        super().__init__()

    def run(self) -> Generator[simpy.events.Event, Any, Any]:
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

        machine_state = 'init'
        received_message = 'initialise_a'
        activity_a = self.get_next_activity(self.starting_node_id)
        activity_b = None
        status: Status = Status(activity_a, activity_b, received_message)

        # TODO: Add a periodic timeout (optional)
        #       periodic loop - inner state machine - end sm loop - yield - end periodic loop

        # For each microenvironment that the person visits
        finished = False
        while not finished:

            actions = PersonBase.state_diagram.get(machine_state, 'NoState') \
                                              .get(status.received_message, 'NoMessage')
            if actions == 'NoState':
                raise ValueError(f'Person state error:s->{machine_state}:m->{received_message}')
            if actions == 'NoMessage':
                raise ValueError(f'Person received message error:s->{machine_state}:m->{received_message}')

            action = actions.get('action', 'NOP')
            message_to_a = actions.get('message_to_a', 'NOP')
            message_to_b = actions.get('message_to_b', 'NOP')
            machine_state = actions.get('next_state', None)
            if not machine_state:
                raise ValueError('Person next state invalid')

            # execute action
            status = function_dict.get(action)(status)

            # execute activities
            if message_to_a != 'NOP':
                status.activity_a.kwargs['message_to_activity'].put(message_to_a)
                rm = yield status.activity_a.kwargs['message_to_person'].get()
                if rm is not None:
                    status.received_message = ''.join((rm, '_a'))
                else:
                    raise NotImplementedError('Unknown message from activity')

            elif message_to_b != 'NOP':
                status.activity_b.kwargs['message_to_activity'].put(message_to_b)
                rm = yield status.activity_b.kwargs['message_to_person'].get()
                if rm is not None:
                    status.received_message = ''.join((rm, '_a'))
                else:
                    raise NotImplementedError('Unknown message from activity')

            finished = True if machine_state == 'end' else finished

    def nop(self, status: Status) -> Status:
        """Function which does nothing
        """
        return status

    def run_a(self, status: Status) -> Status:
        if status.activity_a is not None:
            self.run_activity(status.activity_a)
        return status

    def run_b(self, status: Status) -> Status:
        if status.activity_b is not None:
            self.run_activity(status.activity_b)
        return status

    def transfer_b_to_a(self, status: Status) -> Status:
        status.activity_a, status.activity_b = status.activity_b, None
        status.received_message = 'resources_seized_a'
        return status

    def run_activity(self, activity):
        activity_class = activity.activity_class(self.sim_env, **activity.kwargs)
        self.sim_env.env.process(activity_class.run())

    # TODO: Still need to implement decision making logic
    def get_next_node(self, status: Status) -> Status:
        if status.activity_a.graph_ref[1] == 'end':
            status.activity_b = None
            status.received_message = 'branch_to_end'
        else:
            # TODO: Need to manage situation where there is no decision.
            decision = self.sim_env.routing.get_decision_from_activity_ref(status.activity_a.kwargs['graph_activity_ref'])
            status.activity_b = self.get_next_activity(decision.id)
            status.received_message = 'initialise_b'

        return status

    def get_next_activity(self, decision_id: str) -> Activity:
        activity_list = self.sim_env.routing.get_activities_from_decision_id(decision_id)

        # TODO: If more than one activity need to implement decision node
        if activity_list is None or len(activity_list) != 1:
            raise ValueError('Starting node must have only one next activity')

        activity: Activity = activity_list[0]

        # Add this instance to the arguments list
        activity.kwargs['person'] = self

        # Create two communication pipes for bi-directional communication with activity
        activity.kwargs['message_to_activity'] = simpy.Store(self.sim_env.env)
        activity.kwargs['message_to_person'] = simpy.Store(self.sim_env.env)

        return activity


PersonType = NewType('PersonType', PersonBase)
