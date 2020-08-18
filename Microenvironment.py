""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import simpy.core
import math

from HealthDES import ResourceBase
from HealthDES.SimulationBase import SimEnv


class Microenvironment(ResourceBase):
    """ Class to implement a microenvironment as a simpy discreate event simulation """

    def __init__(self,
                 sim_env: SimEnv,
                 environment_name,
                 volume,
                 air_exchange_rate,
                 capacity=None):

        super().__init__(sim_env)

        self.attr['time_interval'] = self.sim_env.time_interval

        # Microenvironment characteristics
        if not volume > 0:
            raise ValueError('Air volume must be greater than zero.')
        if not air_exchange_rate > 0:
            raise ValueError('Air Exchange Rate must be greater than zero.')

        self.attr['environment_name'] = environment_name
        self.attr['volume'] = volume
        self.attr['air_exchange_rate'] = air_exchange_rate

        # Initialise the building environment
        self.attr['quanta_in_microenvironment'] = 0.0

        # Set limits to the visitor capacity in the microenvironment managed
        # through a simpy resource
        if capacity is None:
            self.attr['capacity'] = simpy.core.Infinity
        else:
            if not capacity > 0:
                raise ValueError('Capacity must be greater than zero.')
            self.attr['capacity'] = capacity

        self.microenvironment = simpy.Resource(self.sim_env.env, self.attr['capacity'])

        # Set up periodic reporting
        self.initialise_periodic_reporting()

    # Start the microenvironment, usually when simulation established
    def run(self):
        """ Calculate the new quanta concentration in the building """
        while True:

            # Reduce quanta concentration over time
            self.attr['quanta_in_microenvironment'] *= math.exp(-1 * self.attr['air_exchange_rate'] * self.attr['time_interval'])

            yield self.sim_env.env.timeout(1)

    # Allow visitors to request entry

    def request_entry(self):
        """Request entery into the microenvironment

        Returns:
            simpy resource  -- Simpy resource (with potential capacity constraint)
        """
        return self.microenvironment.request()

    def get_queue_length(self):
        """Get the number of people waiting in the queue

        Returns:
            {integer} -- Number of people waiting in the queue

        """
        return len(self.microenvironment.queue)

    def get_active_users(self):
        """Get the number of people in the microenvironment

        Returns:
            {integer} -- Number of active people in the microenvironment
        """
        return len(self.microenvironment.users)

    # Calculate quanta load and report quanta per unit volume

    def add_quanta_to_microenvironment(self, quanta):
        """ Callback from person class to add quanta to the microenvironment

            Arguments:
            quanta              The number of quanta to add to the microenvironment
        """
        if not quanta >= 0:
            raise ValueError('Quanta must be greater than or equal to zero.')
        self.attr['quanta_in_microenvironment'] += quanta

    def get_quanta_concentration(self):
        """ Callback from person class to get the quanta concentration """
        return self.attr['quanta_in_microenvironment'] / self.attr['volume']

    # Periodic reporting
    def initialise_periodic_reporting(self):
        """ Initialise periodic reporting """
        data_set_name = f"Quanta concentration {self.attr['environment_name']}"
        callback = self.periodic_reporting_callback
        periods = 1

        self.sim_env.dc.create_period_reporting(data_set_name, callback, periods)

    def periodic_reporting_callback(self):
        """ Callback to collect data for periodic reporting """
        return {f"Quanta concentration {self.attr['environment_name']}": self.get_quanta_concentration()}
