""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math
import itertools

# pylint: disable=relative-beyond-top-level
from .Check import Check, CheckList
from .Routing import Routing


class Person_base: 
    """ Class to implement a person as a simpy discreate event simulation
    
        The person will have various characteristics which influences the simulation

        The person will have a flow around the simulation implemented as a list of activities
        which are callled as each one completes.
    """

    # create a unique ID counter
    get_new_id = itertools.count()

    def __init__(self, simulation_params, starting_node_id, person_type=None):
        """Establish the persons characteristics, this will be specific to each model

        Arguments:
            simulation_params {Obj} -- Dictionary of parameters for the simulation (see simulation.py)

        Keyword Arguments:
            person_type {string} -- Type of person within the model e.g visitor, staff (default: {None})
        """
        # import simulation parameters
        self.simulation_params = simulation_params
        self.env = simulation_params.get('simpy_env', None)
        self.dc = simulation_params.get('data_collector', None)
        self.routing = simulation_params.get('routing', None)       
        self.time_interval = simulation_params.get('time_interval', None)

        # keep a record of person IDs
        self.PID = next(Person_base.get_new_id)

        # Routing is the list of environments that the person traverses
        self.routing_node_id = starting_node_id

        # Person type is a characteristic which affects behabviour in the microenvironment
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

            pops the microenvironment to visit and uses entry_callback function to return the entry point
            passes a reference to person instance (self)
            pops the arguments passed as keyword list and passes as new argument list to entry point parameters
            initates a new simpy process for the persons activity within the microenvironment
        """
        # For each microenvironment that the person visits
        while self.routing_node_id != 'end':
            # microenvironment, kwargs = self.routing.pop()
            self.routing_node_id, activity_class, kwargs = self.routing.get_next_activity(self.routing_node_id)
            finished_activity = self.env.event()
            # callback = microenvironment.entry_callback(visit_type=self.person_type)

            this_activity_class = activity_class(self.simulation_params, self, **kwargs)
            
            # Need to find a way to pass variable args
            # self.env.process(activity_class.start(self, finished_activity, **kwargs))
            self.env.process(this_activity_class.start(finished_activity))
            yield finished_activity


    # TODO: Remove once network routing implemented
    def enqueue(self, microenvironment, **kwargs):
        """Enqueue a microenvironment to the routing list 

        Arguments:
            microenvironment {obj.method}   -- The microenvironment to which the person is routed
            parameters                      -- Parameters passed to the microenvironment when called (optional)   
        """        
        self.routing.insert(0, (microenvironment, kwargs) )  

    # TODO: Remove once network routing implemented
    def dequeue(self):
        """[summary]

        Returns:
            microenvironment {obj.method}   -- The microenvironment to which the person is routed
            parameters                      -- Parameters passed to the microenvironment when called (optional)   
        """        
        CheckList.fail_if_empty(self.routing)

        return self.routing.pop()

    # TODO: Remove once network routing implemented
    def clear_routing(self):
        """Clear the routing list """
        self.routing = []
