""" Python library to model the spread of infectious diseases within a microenvironment """

import math
import random

from HealthDES import PersonBase
from typing import Optional
# from DiseaseProgression import DiseaseProgression


class Person(PersonBase):
    """ Class to implement a person as a simpy discreate event simulation

        The person will have various characteristics which influences the simulation

        The person will have a flow around the simulation implemented as a list of activities
        which are callled as each one completes.
    """

    def __init__(self,
                 simulation_params,
                 starting_node_id: str,
                 infection_status_label: Optional[str] = None,
                 quanta_emission_rate: Optional[float] = None,
                 inhalation_rate: Optional[float] = None,
                 person_type: Optional[str] = None):
        """Establish the persons characteristics, this will be specific to each model

        Args:
            simulation_params (dict): Dictionary of simulation parameters.
            starting_node_id (string): id for the starting node within the network graph.
            infection_status_label (disease_status, optional): Disease status of the person. Defaults to None.
            quanta_emission_rate (number, optional): Quanta emitted by the person per hour. Defaults to None.
            inhalation_rate (number, optional): Respiratory rate of the person per hour. Defaults to None.
            person_type (string, optional): Type of the person (visitor, staff, etc.). Defaults to None.
        """
        # Initialise the base class
        super().__init__(simulation_params, starting_node_id)

        # Characteristics
        self.status.add_status_attribute(key='infection_status',
                                         allowable_status=frozenset(['susceptible', 'exposed', 'infected', 'recovered']),
                                         default_status='susceptible')

        self.att['quanta_emission_rate'] = quanta_emission_rate if quanta_emission_rate else 147
        self.att['inhalation_rate'] = inhalation_rate if inhalation_rate else 0.54
        self.att['cumulative_exposure'] = 0.0

        self.att['infected'] = False
        self.att['person_type'] = person_type
        self.att['age'] = 50
        self.att['sex'] = 'female'

        self.add_do_action('expose_person_to_quanta', self.expose_person_to_quanta)
        self.add_do_action('infection_risk', self.infection_risk)
        self.add_do_action('infection_risk_instant', self.infection_risk_instant)

    def expose_person_to_quanta(self, quanta_concentration: float) -> None:
        """Calculate the amount of quanta the person is exposed to

        Args:
            quanta_concentration (number): The concentration of infectious material in the environment in quanta
        """
        self.att['cumulative_exposure'] += quanta_concentration

        if random.random() < self.infection_risk_instant(quanta_concentration):
            if self.status['infection_status'] == 'susceptible':
                self.log_infection()
                self.dc.counter_increment('Infections')

            self.status['infection_status'] = 'exposed'

    def infection_risk(self):
        """Determine risk that a patient is infected"""
        return 1 - math.exp(-1 * self.att['inhalation_rate'] * self.time_interval * self.att['cumulative_exposure'])

    def infection_risk_instant(self, quanta_concentration):
        """Return the probability the person will become infections

        Args:
            quanta_concentration (number): Concentration of infectious material in the environment

        Returns:
            number: Probability that the person will become infected.
        """
        return 1 - math.exp(-1 * self.att['inhalation_rate'] * self.time_interval * quanta_concentration)

    def log_infection_risk(self):
        """Log visitors infection risk"""
        self.dc.log_reporting('Infection risk',
                              {'Person': self.id,
                               'Infection risk': self.infection_risk()})

    def log_infection(self):
        """Log visitor activity within the process visitor process"""
        self.dc.log_reporting('Infections',
                              {'Person': self.id})
