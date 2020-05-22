""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math
from Tools.Check import Check
from DataCollection import DataCollection

class Microenvironment:
    """ Class to implement a microenvironment as a simpy discreate event simulation """

    def __init__(self, env, dc, time_interval, volume, air_exchange_rate, capacity=None):
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
        Check.is_greater_than_zero(time_interval)
        Check.is_greater_than_zero(volume)
        Check.is_greater_than_zero(air_exchange_rate)

        self.env = env
        self.dc = dc
        self.time_interval = time_interval
        self.volume = volume
        self.air_exchange_rate = air_exchange_rate

        if capacity is None:
            self.capacity = simpy.core.Infinity
        else:
            self.capacity = capacity

        self.microenvironment = simpy.Resource(self.env, self.capacity)

        # Initialise the building environment
        self.quanta_concentration = 0.0
        # Assume there are no infected people in the building at start
        self.infected = 0.0
        self.total_quanta_emission_rate = 0.0

        # Store results in a list
        self.quanta_concentration_results = []
        self.quanta_concentration_results.append(self.quanta_concentration)

        # Limit number of people in the microenvironment
        # Visitors that can't get in immediately join a queue
        self.visitor_limit = None
        self.visitors = 0

    def run(self):
        """ Calculate the new quanta concentration in the building """
        while True:
            yield self.env.timeout(1)

            if self.total_quanta_emission_rate and self.infected:
                quanta_emission_rate = self.total_quanta_emission_rate / self.infected
            else:
                quanta_emission_rate = 1
            
            self.quanta_concentration = self.calc_quanta_concentration(1, self.infected, 
                                                quanta_emission_rate,
                                                self.quanta_concentration,
                                                self.time_interval)
            self.quanta_concentration_results.append(self.quanta_concentration)

    def get_results(self):
        """ Returns the results from the simulation run """
        return self.quanta_concentration_results

    # Calculate the quanta concentration at time t
    def calc_quanta_concentration(self, t, infected, quanta_emission_rate, initial_concentration=0.0, time_interval=1.0):
        """ Calculate the quanta concentration at time t

        Keyword arguments:
        t                       Number of time intervals in the future when concentration is calculated
        infected                The number of infectious subjects 
        quanta_emission_rate    Rate at which an infected person emits infectious droplets
        initial_concentration   Quanta concentration at the start of the period (default=0.0)
                                Note: Original paper n0 is absolute quanta, not concentration
        time_interval           Scaling factor for time interval to enable sub-unit calculations (default=1.0, minutes would be 1/60th of an hour)

        Return value:
        quanta_concentration    Concentration of quanta at time period t.

        Note conventions:
            Time period is measured in hours
            Volumes are metres^3
            Concentration is quanta per m^3 (for initial concentration and returned results)
            Emmission rate is quanta per hour
        """

        Check.is_greater_than_zero(t)
        Check.is_greater_than_or_equal_to_zero(infected)
        Check.is_greater_than_zero(quanta_emission_rate)
        Check.is_greater_than_or_equal_to_zero(initial_concentration)
        Check.is_greater_than_zero(time_interval)  

        a = quanta_emission_rate * infected / (self.air_exchange_rate * self.volume) * time_interval
        quanta_concentration = a + (initial_concentration + a) * math.exp(-self.air_exchange_rate * t * time_interval)
        
        return quanta_concentration   

    def request_entry(self, patient, duration, infected=0, quanta_emission_rate=0):
        """ Introduce an infected person to the microenvironment

        Keyword arguments:
        quanta_emission_rate    Rate at which an infected person emits infectious droplets
        duration                Length of time that infected person remains in the microenvironment
        """

        # Request entry into the microenvironment
        request_entry = self.microenvironment.request()
        yield request_entry

        # Granted an entry
        self.visitors += 1
        self.infected += infected
        self.total_quanta_emission_rate += quanta_emission_rate
        # Wait in the shop
        print("patient:", patient.PID)
        yield self.env.timeout(duration+1)
        self.total_quanta_emission_rate -= quanta_emission_rate
        self.infected -= infected
        self.visitors -= 1


    def entry_callback(self):
        """ Method to call when a person needs entry to the microenvironment
        
        Return value:
        Method to call
        """
        return self.request_entry

    def initialise_periodic_reporting(self):
        """ Initialise periodic reporting """
        column_names=['Quanta concentration']
        self.dc.periodic_reporting("Quanta concentration", column_names, self.periodic_reporting_callback, 1)

    def periodic_reporting_callback(self):
        """ Callback to collect data for periodic reporting """
        return self.quanta_concentration
