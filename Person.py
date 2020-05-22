""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math
import itertools
from Tools.Check import Check, CheckList
from Microenvironment import Microenvironment
from DataCollection import DataCollection

class Person:
    """ Class to implement a person as a simpy discreate event simulation
    
    The person will have various characteristics which influences the simulation

    The person will have a flow around the simulation implemented as a list of activities
    which are callled as each one completes.
    """

    # create a unique ID counter
    get_new_id = itertools.count()

    def __init__(self, env, dc, quanta_emission_rate):
        """ Establish the persons characteristics, this will be specific to each model

        Keyword arguments:
        env                     A simpy environment
        quanta_emission_rate    The rate at which the person emits quanta (convention per hour)                     
        """
        self.env = env
        self.dc = dc

        self.left_microenvironment = self.env.event()

        # keep a record of person IDs
        self.PID = next(Person.get_new_id)

        # Routing is the list of environments that the person traverses
        self.routing = []



    def get_PID(self):
        """ Return the Person ID (PID) """
        return self.PID


    def enqueue(self, microenvironment, **kwargs):
        """ Enqueue a microenvironment to the routing list 

        Keyword arguments:
        microenvironment        The microenvironment to which the person is routed
        parameters              Parameters passed to the microenvironment when called (optional)   
        """
        self.routing.insert(0, (microenvironment, kwargs) )  


    def dequeue(self):
        """ Dequeue the next microenvironment from the routing list 
        
        Return value (returns a tuple):
        microenvironment        The reference to the microenvironment to be execute
        parameters              any parameters that need to be passed to the environment
        """
        CheckList.fail_if_empty(self.routing)

        return self.routing.pop()

    def clear_routing(self):
        """ Clear the routing list """
        self.routing = []


    def run(self):
        """" Simulation process for the person
        
        Tests that the routing list still has destinations to visit

        pops the microenvironment to visit and uses entry_callback function to return the entry point
        passes a reference to person instance (self)
        pops the arguments passed as keyword list and passes as new argument list to entry point parameters
        initates a new simpy process for the persons activity within the microenvironment
        """
        # For each microenvironment that the person visits
        while self.routing:
            microenvironment, kwargs = self.routing.pop()
            callback = microenvironment.entry_callback()
            self.env.process(callback(self, **kwargs))
            yield self.left_microenvironment

        """********************************************************************************
        We need to have a yield somewhere in this function.

        once we have set the process running we need to yield until it completes.
        *********************************************************************************"""