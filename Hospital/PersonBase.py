""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math
import itertools
from Check import Check, CheckList
from ..Microenvironment import Microenvironment
from ..DataCollection import DataCollection


class PersonBase:
    """ Class to implement a person as a simpy discreate event simulation
    
        The person will have various characteristics which influences the simulation

        The person will have a flow around the simulation implemented as a list of activities
        which are callled as each one completes.
    """

    # create a unique ID counter
    get_new_id = itertools.count()

    def __init__(self, env, dc, infection_status_label=None, quanta_emission_rate=None, person_type=None):
        """ Establish the persons characteristics, this will be specific to each model

            Keyword arguments:
            env                     A simpy environment
            quanta_emission_rate    The rate at which the person emits quanta (convention per hour)                     
        """
        self.env = env
        self.dc = dc

        # keep a record of person IDs
        self.PID = next(Person.get_new_id)

        # Characteristics
        self.infection_status = DiseaseProgression(infection_status_label)
        self.quanta_emission_rate = quanta_emission_rate
        self.cumulative_exposure = 0


        # Routing is the list of environments that the person traverses
        self.routing = []

        # Person type is a characteristic which affects behabviour in the microenvironment
        self.person_type = person_type

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

    # TODO: Complete infected visitor
    def infected_visitor(self, callback_add_quanta, request_to_leave, periods):
        """ Callback from microenvironment for an infected person to generate quanta

            Arguments:
            callback_add_quanta             Callback to microenvironment to add quanta
            request_to_leave                Event notification to let microenvironment know we wish to leave
                                            to allow clean up before existing the microenvironment.
            periods                         Number of periods person in the microenvironment
         """
        not_finished = True
        while not_finished:

            not_finished =  yield self.env.timeout(1, True) | self.env.timeout(periods, False)

        request_to_leave.succeed()


    # TODO: Complete susceptible visitor
    def susceptible_visitor(self, callback_quanta_concentration, request_to_leave, period):
        """ Callback from microenvironment for a susceptible person to calculate exposure

            Arguments:
            callback_quanta_concentration   callback to microenvironment to get quanta_concentration
            request_to_leave                Event notification to let microenvironment know we wish to leave
                                            to allow clean up before existing the microenvironment.
            periods                         Number of period that person in the microenvironment
        """
        yield self.env.timeout(1)
        request_to_leave.succeed()


    def run(self):
        """ Simulation process for the person
        
            Tests that the routing list still has destinations to visit

            pops the microenvironment to visit and uses entry_callback function to return the entry point
            passes a reference to person instance (self)
            pops the arguments passed as keyword list and passes as new argument list to entry point parameters
            initates a new simpy process for the persons activity within the microenvironment
        """
        # For each microenvironment that the person visits
        while self.routing:
            microenvironment, kwargs = self.routing.pop()
            left_microenvironment = self.env.event()              
            callback = microenvironment.entry_callback(visit_type=self.person_type)
            self.env.process(callback(self, left_microenvironment, **kwargs))
            yield left_microenvironment
