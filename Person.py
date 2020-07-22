""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math
import random
import itertools

from HealthDES.DataCollection import DataCollection
from HealthDES.PersonBase import Person_base

from DiseaseProgression import DiseaseProgression

class Person(Person_base):
    """ Class to implement a person as a simpy discreate event simulation
    
        The person will have various characteristics which influences the simulation

        The person will have a flow around the simulation implemented as a list of activities
        which are callled as each one completes.
    """

    def __init__(self, simulation_params, starting_node_id, infection_status_label=None, quanta_emission_rate=None, inhalation_rate=None, person_type=None):
        """Establish the persons characteristics, this will be specific to each model

        Args:
            simulation_params (dict): Dictionary of simulation parameters.
            starting_node_id (string): id for the starting node within the network graph.
            infection_status_label (disease_status, optional): Disease status of the person. Defaults to None.
            quanta_emission_rate (number, optional): Quanta emitted by the person per hour. Defaults to None.
            inhalation_rate (number, optional): Respiratory rate of the person per hour. Defaults to None.
            person_type (string, optional): Type of the person (visitor, staff, etc.). Defaults to None.
        """

        Person_base.__init__(self, simulation_params, starting_node_id, person_type)
        
        # Characteristics
        self.infection_status = DiseaseProgression(infection_status_label)
        self.quanta_emission_rate = quanta_emission_rate if quanta_emission_rate else 147
        self.inhalation_rate = inhalation_rate if inhalation_rate else 0.54  # m^3 h^-1

        self.cumulative_exposure = 0
        self.infected = False


    def get_quanta_emission_rate(self):
        """Get the parsons quanta emmission rate

        Returns:
            Number -- Quanta emission rate
        """        
        return self.quanta_emission_rate


    def expose_person_to_quanta(self, quanta_concentration):
        """Calculate the amount of quanta the person is exposed to

        Args:
            quanta_concentration (number): The concentration of infectious material in the environment in quanta
        """

        # TODO: We don't use cumulative exposure, so can we remove?
        self.cumulative_exposure += quanta_concentration

        # if random.random() < self.infection_risk():
        if random.random() < self.infection_risk_instant(quanta_concentration):
            if self.infection_status.is_state('susceptible'):
                self.log_infection()
                self.dc.counter_increment('Infections')
     
            self.infection_status.set_state('exposed')


    # TODO: Check whether this can be removed
    def infection_risk(self):
        """Determine risk that a patient is infected"""
        return  1 - math.exp(-self.inhalation_rate* self.time_interval * self.cumulative_exposure)


    # TODO: Move this inside expose person to quanta (simplify)
    def infection_risk_instant(self, quanta_concentration):
        """Return the probability the person will become infections

        Args:
            quanta_concentration (number): Concentration of infectious material in the environment

        Returns:
            number: Probability that the person will become infected.
        """
        return  1 - math.exp(-self.inhalation_rate* self.time_interval * quanta_concentration)


    def log_infection_risk(self):
        """Log visitors infection risk"""
        self.dc.log_reporting('Infection risk',
                             {'Person':self.PID,
                               'Infection risk': self.infection_risk()})    

    
    def log_infection(self):
        """Log visitor activity within the process visitor process"""
        self.dc.log_reporting('Infections',
                             {'Person':self.PID})
        
