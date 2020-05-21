""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math
from Tools.Check import Check 

class Microenvironment:
    """ Class to implement a microenvironment as a simpy discreate event simulation """

    def __init__(self, env, time_interval, volume, air_exchange_rate):
        """ Initialise the microenvironment 

        Keyword arguments:
        env                     A simpy environment
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
        self.time_interval = time_interval
        self.volume = volume
        self.air_exchange_rate = air_exchange_rate

        # Initialise the building environment
        self.quanta_concentration = 0.0
        # Assume there are no infected people in the building at start
        self.infected = 0.0
        self.quanta_emission_rate = 0.0

        # Store results in a list
        self.quanta_concentration_results = []
        self.quanta_concentration_results.append(self.quanta_concentration)

    def simulate(self):
        """ Calculate the new quanta concentration in the building """
        while True:
            yield self.env.timeout(1)
            self.quanta_concentration = self.calc_quanta_concentration(1, self.infected, self.quanta_emission_rate, self.quanta_concentration, self.time_interval)
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

    def infected_person(self, quanta_emission_rate, duration):
        """ Introduce an infected person to the microenvironment

        Keyword arguments:
        quanta_emission_rate    Rate at which an infected person emits infectious droplets
        duration                Length of time that infected person remains in the microenvironment
        """

        self.infected = 1.0
        self.quanta_emission_rate = quanta_emission_rate
        yield self.env.timeout(duration+1)
        self.infected = 0.0