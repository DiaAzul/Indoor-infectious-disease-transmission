""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math
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

    def __init__(self, simulation_params, starting_node_id, infection_status_label=None, quanta_emission_rate=None, person_type=None):
        """ Establish the persons characteristics, this will be specific to each model

            Keyword arguments:
            env                     A simpy environment
            quanta_emission_rate    The rate at which the person emits quanta (convention per hour)                     
        """
        Person_base.__init__(self, simulation_params, starting_node_id, person_type)
        
        # Characteristics
        self.infection_status = DiseaseProgression(infection_status_label)
        self.quanta_emission_rate = quanta_emission_rate
        self.cumulative_exposure = 0


    def get_quanta_emission_rate(self):
        """Get the parsons quanta emmission rate

        Returns:
            Number -- Quanta emission rate
        """        
        return self.quanta_emission_rate



    def expose_person_to_quanta(self, quanta_concentration):
        """Expose person to a quanta

        Arguments:
            quanta_concentration {Number} -- Concentration of quanta the person is exposed to
        """        
        pass
