""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math
import itertools
from Tools.Check import Check, CheckList

class Person:
    """ Class to implement a person as a simpy discreate event simulation
    
    The person will have various characteristics which influences the simulation

    The person will have a flow around the simulation implemented as a list of activities
    which are callled as each one completes.
    """

    # create a unique ID counter
    get_new_id = itertools.count()

    def __init__(self, env, quanta_emission_rate):
        """ Establish the persons characteristics, this will be specific to each model

        Keyword arguments:
        env                     A simpy environment
        quanta_emission_rate    The rate at which the person emits quanta (convention per hour)                     
        """

        # keep a record of person IDs
        self.PID = next(Person.get_new_id)

        # Set person characteristics
        self.quanta_emission_rate = quanta_emission_rate
        self.infected = 0

        # Routing is the list of environments that the person traverses
        self.routing = []


    def get_PID(self):
        """ Return the Person ID (PID) """
        return self.PID


    def enqueue(self, microenvironment, parameters=None):
        """ Enqueue a microenvironment to the routing list 

        Keyword arguments:
        microenvironment        The microenvironment to which the person is routed
        parameters              Parameters passed to the microenvironment when called (optional)   
        """
        self.routing.insert(0, (microenvironment, parameters) )  


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



 
