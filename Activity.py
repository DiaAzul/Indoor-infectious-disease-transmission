""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math
import itertools

from HealthDES.Check import Check, CheckList
from HealthDES.DataCollection import DataCollection

from DiseaseProgression import DiseaseProgression
from Microenvironment import Microenvironment
from Person import Person

class Visitor_activity:
    """Person's activity within the system, models interaction between poeple and environment """
    
    def __init__(self, simulation_params, person, **kwargs):
        """Create a new activity

        Arguments:
            simulation_params {Obj} -- Parameters for the simulation
        """
        self.env = simulation_params.get('simpy_env', None)
        self.dc = simulation_params.get('data_collector', None)
        self.time_interval = simulation_params.get('time_interval', None)

        # Activity participants
        self.person = person        
        self.microenvironment = kwargs['microenvironment']
        self.duration = kwargs['duration']


    # Entry point to the activity
    def start(self, finished_activity):
        """Introduce a person to the microenvironment

            Arguments:
            finished_activity    Event notification that activity has completed
            duration             Length of time that infected person remains in the microenvironment
        """
        # Request entry into the microenvironment
        with self.microenvironment.request_entry() as request_entry:
            self.log_visitor_activity("Visitor {PID} requests entry.".format(PID=self.person.PID))         
            yield request_entry

            # Wait in the shop
            self.log_visitor_activity("Visitor {PID} entered.".format(PID=self.person.PID))

            person_request_to_leave = self.env.event()

            if self.person.infection_status.is_state('infected'):
                self.env.process(self.infected_visitor(self.microenvironment.add_quanta_to_microenvironment,
                                                         person_request_to_leave,
                                                         self.duration))
                yield person_request_to_leave

            elif self.person.infection_status.is_state('susceptible'):
                self.env.process(self.susceptible_visitor(self.microenvironment.get_quanta_concentration,
                                                            person_request_to_leave,
                                                            self.duration))
                yield person_request_to_leave

            self.log_visitor_activity("Visitor {PID} left.".format(PID=self.person.PID))

            finished_activity.succeed()


    def infected_visitor(self, callback_add_quanta, request_to_leave, periods):
        """Callback from microenvironment for an infected person to generate quanta

            Arguments:
            callback_add_quanta             Callback to microenvironment to add quanta
            request_to_leave                Event notification to let microenvironment know we wish to leave
                                            to allow clean up before existing the microenvironment.
            periods                         Number of periods person in the microenvironment
         """

        end_trigger =  self.env.timeout(periods, value='end')

        while True:
            period_trigger = self.env.timeout(1, value='periodic')

            # Add quanta to the environment
            quanta_emission_rate = self.person.get_quanta_emission_rate()
            self.microenvironment.add_quanta_to_microenvironment(quanta_emission_rate * self.time_interval)

            fired_trigger = yield period_trigger | end_trigger
            if fired_trigger == {end_trigger: 'end'}:
                break

        request_to_leave.succeed()


    def susceptible_visitor(self, callback_quanta_concentration, request_to_leave, periods):
        """Callback from microenvironment for a susceptible person to calculate exposure

            Arguments:
            callback_quanta_concentration   callback to microenvironment to get quanta_concentration
            request_to_leave                Event notification to let microenvironment know we wish to leave
                                            to allow clean up before existing the microenvironment.
            periods                         Number of period that person in the microenvironment
        """
        end_trigger =  self.env.timeout(periods, value='end')

        while True:
            period_trigger = self.env.timeout(1, value='periodic')

            # Assess exposure
            quanta_concentration = self.microenvironment.get_quanta_concentration()
            self.person.expose_person_to_quanta(quanta_concentration)

            fired_trigger = yield period_trigger | end_trigger
            if fired_trigger == {end_trigger: 'end'}:
                break

        request_to_leave.succeed()


    def log_visitor_activity(self, activity):
        """Log visitor activity within the process visitor process 
        
            Arguments:
            activity                  String descibing the activity that has occured.
        """
        # self.dc.log_reporting('Visitor activity', {'queue':self.queueing, 'visitors':self.visitors, 'activity': activity})
        self.dc.log_reporting('Visitor activity',
                             {'queue':self.microenvironment.get_queue_length(),
                              'visitors':self.microenvironment.get_active_users,
                               'activity': activity})