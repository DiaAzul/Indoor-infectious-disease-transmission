""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import simpy.core
import time

# Import local libraries
from HealthDES import Check
from HealthDES import CheckList
from HealthDES import SimulationBase

from Microenvironment import Microenvironment
from Activity import Visitor_activity
from Person import Person
# from DiseaseProgression import DiseaseProgression

from Configuration import Config

# TODO: from collections import namedtuple as data_structure [consider how we can use named tuples
#       within the simulation where there are multiple return values.]


class Simulation(SimulationBase):
    """ Class to implement a simulation using simpy discreate event simulation

    The simulation class is the main controlling class for the simulation and
    is responsible for:
    * Creating the simpy environment
    * Creating the data collection environment
    * Creating individual microenvironments
    * Generating people
    * Defining the routing for each person
    * Starting and stopping the model
     """

    # TODO: Move simulation_run to run() method call, and implement a reset simulation.
    def initialise(self, **kwargs) -> None:
        """Initialise the simulation.
        """

        self.microenvironment_name = kwargs['microenvironment']

        # Set the time interval relative to one hour (minutes = 1/60)
        self.time_interval = 1 / 60
        self.add_simulation_param('time_interval', self.time_interval)
        # Number of periods the simulation will run
        self.periods = kwargs['periods'] if kwargs['periods'] else 180
        self.add_simulation_param('simulation_length', self.periods)

        # Import configuration information
        self.config = Config()
        self.config.import_microenvironments()
        self.add_simulation_param('configuration', self.config)

        # Variables in this scope only
        self.microenvironments = {}
        self.population = {}

    def create_microenvironments(self):
        """Create the microenvironments used within the simulation."""

        CheckList.fail_if_dict_empty(self.config.microenvironments)

        for name, microenv in self.config.microenvironments.items():
            # name = microenv.get('environment')
            volume = microenv.get('volume')  # m^3
            air_exchange_rate = microenv.get('air-exchange-rate')
            capacity = microenv.get('visitor-capacity')
            capacity = None if capacity == 0 else capacity

            self.microenvironments[name] = Microenvironment(self.simulation_params,
                                                            name,
                                                            volume,
                                                            air_exchange_rate,
                                                            capacity=capacity)

    def create_activities(self, microenvironment_name):
        """Create a dictionary of activities."""

        duration = self.config.microenvironments.get(microenvironment_name) \
                                                .get('average-length-of-stay')
        duration = duration / self.time_interval  # Convert hours to time measures

        activity_name = 'visit environment'
        activity_class, arguments = Visitor_activity.pack_parameters(
            self.microenvironments[microenvironment_name],
            duration)

        self.routing.register_activity(activity_name, activity_class, **arguments)

    def create_network_routing(self):
        """Create a simple network routing.

        From 'start' to 'end' via 'visit environment
        """
        routing_entry_point = self.routing.add_decision('start')
        self.routing.add_decision('end')

        self.routing.add_activity('visit environment', 'start', 'end')

        return routing_entry_point

    def create_people(self,
                      arrivals_per_hour,
                      max_arrivals=None,
                      quanta_emission_rate=None,
                      inhalation_rate=None):
        """ Create a method of generating people """

        is_someone_infected = False
        generated_people = 0

        while True:
            infection_status_label = 'susceptible' if is_someone_infected else 'infected'

            is_someone_infected = True

            generated_people += 1
            person = Person(self.simulation_params,
                            starting_node_id='start',
                            person_type='visitor',
                            infection_status_label=infection_status_label,
                            quanta_emission_rate=quanta_emission_rate,
                            inhalation_rate=inhalation_rate)

            # self.create_routing(person, duration=duration)
            self.env.process(person.run())

            time_to_next_person = 60 / arrivals_per_hour
            yield self.env.timeout(time_to_next_person)

            # If we have generated enough people then stop
            if max_arrivals and (generated_people >= max_arrivals): break  # noqa:E701

    def run(self,
            arrivals_per_hour=None,
            quanta_emission_rate=None,
            inhalation_rate=None,
            max_arrivals=None,
            report_time=None):
        """ Run the simulation

        Keyword arguments:
        periods             Number of periods to run the simulation
        report_time         When True the simulation prints the time taken to execute the simulation to console.
        """

        if arrivals_per_hour:
            Check.is_greater_than_or_equal_to_zero(arrivals_per_hour)
        if quanta_emission_rate:
            Check.is_greater_than_or_equal_to_zero(quanta_emission_rate)
        if inhalation_rate:
            Check.is_greater_than_or_equal_to_zero(inhalation_rate)
        if max_arrivals:
            Check.is_greater_than_or_equal_to_zero(max_arrivals)

        # Start the microenvironments
        self.create_microenvironments()

        # Comment out running all
        # for key in self.microenvironments:
        #    self.env.process(self.microenvironments[key].run())
        self.env.process(self.microenvironments.get(self.microenvironment_name).run())

        if arrivals_per_hour is None:
            arrivals_per_hour = self.config.microenvironments.get(self.microenvironment_name).get('visitor-arrival-rate')

        if not max_arrivals:
            temp = self.config.microenvironments.get(self.microenvironment_name).get('max-arrivals', 0)
            if temp > 0:
                max_arrivals = temp
            else:
                max_arrivals = simpy.core.Infinity

        # Create activities
        self.create_activities(self.microenvironment_name)

        # Create the network routing graph
        self.create_network_routing()

        # Start people generation process
        self.env.process(self.create_people(arrivals_per_hour,
                                            max_arrivals=max_arrivals,
                                            quanta_emission_rate=quanta_emission_rate,
                                            inhalation_rate=inhalation_rate))

        # Run the model
        t_start = time.time()
        if report_time:
            print(f"Running the model for {self.periods} periods")

        self.env.run(until=self.periods)

        if report_time:
            t_end = time.time()
            t_duration = t_end - t_start
            print(f"Simulation finished. Execution time:{t_duration:.3f} seconds")
