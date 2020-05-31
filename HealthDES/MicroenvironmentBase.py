""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math

# pylint: disable=relative-beyond-top-level
from .Check import Check
from .DataCollection import DataCollection
from .DiseaseProgression import DiseaseProgression

class Microenvironment:
    """ Class to implement a microenvironment as a simpy discreate event simulation """

    def __init__(self, simulation_params, volume, air_exchange_rate, capacity=None):
        """ Initialise the microenvironment 

        Keyword arguments:
        env                     A simpy environment
        dc                      Data collection object
        time_interval           Scaling factor for time interval to enable sub-unit calculations (default=1.0, minutes would be 1/60th of an hour)
        volume                  Volume of the indoor environment
        air_exchange_rate       Rate at which air is exchanged

        Note conventions:
            Time period is measured in hours
            Volumes are metres^3
            Concentration is quanta per m^3 (for initial concentration and returned results)
            Emmission rate is quanta per hour
        """
        self.env = simulation_params.get('simpy_env', None)
        self.dc = simulation_params.get('data_collector', None)
        self.time_interval = simulation_params.get('time_interval', None)

        # Microenvironment characteristics
        Check.is_greater_than_zero(volume)
        Check.is_greater_than_zero(air_exchange_rate)

        self.volume = volume
        self.air_exchange_rate = air_exchange_rate

        # Initialise the building environment
        self.quanta_in_microenvironment = 0.0

        # Set limits to the visitor capacity in the microenvironment managed
        # through a simpy resource
        if capacity is None:
            self.capacity = simpy.core.Infinity
        else:
            self.capacity = capacity

        self.microenvironment = simpy.Resource(self.env, self.capacity)

        # Set up periodic reporting
        self.initialise_periodic_reporting()


    # Start the microenvironment, usually when simulation established

    def run(self):
        """ Calculate the new quanta concentration in the building """
        while True:

            # Reduce quanta concentration over time
            self.quanta_in_microenvironment *= math.exp(-self.air_exchange_rate * self.time_interval)

            yield self.env.timeout(1)  

    # Allow visitors to request entry  
  
    def request_entry(self):
        """Request entery into the microenvironment

        Returns:
            simpy resource  -- Simpy resource (with potential capacity constraint)
        """        
        return self.microenvironment.request()


    # Calculate quanta load and report quanta per unit volume

    def add_quanta_to_microenvironment(self, quanta):
        """ Callback from person class to add quanta to the microenvironment
        
            Arguments:
            quanta              The number of quanta to add to the microenvironment
        """
        Check.is_greater_than_or_equal_to_zero(quanta)
        self.quanta_in_microenvironment += quanta


    def get_quanta_concentration(self):
        """ Callback from person class to get the quanta concentration """
        return self.quanta_in_microenvironment / self.volume


    # Periodic reporting

    def initialise_periodic_reporting(self):
        """ Initialise periodic reporting """
        data_set_name = 'Quanta concentration'
        callback = self.periodic_reporting_callback
        periods = 1

        self.dc.create_period_reporting(data_set_name, callback, periods)

    def periodic_reporting_callback(self):
        """ Callback to collect data for periodic reporting """
        return {'quanta_concentration':self.get_quanta_concentration()}
