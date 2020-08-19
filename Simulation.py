""" Python library to model the spread of infectious diseases within a microenvironment """


import simpy
import simpy.core
import time
import sys
import traceback

# Import local libraries
from HealthDES import SimulationBase

from Microenvironment import Microenvironment
from Activity import VisitorActivity
from HealthDES.Routing import Activity
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

    def initialise(self, **kwargs) -> None:
        """Initialise the simulation.
        """

        self.microenvironment_name = kwargs["microenvironment"]

        self.periods = kwargs["periods"] if kwargs["periods"] else 180
        # self.add_simulation_param('simulation_length', self.periods)

        # Import configuration information
        self.config = Config()
        self.config.import_microenvironments()

        # Variables in this scope only
        self.microenvironments = {}
        self.population = {}

    def create_microenvironments(self):
        """Create the microenvironments used within the simulation."""

        if not bool(self.config.microenvironments):
            raise ValueError("No microenvironments defined")

        for name, microenv in self.config.microenvironments.items():
            # name = microenv.get('environment')
            volume = microenv.get("volume")  # m^3
            air_exchange_rate = microenv.get("air-exchange-rate")
            capacity = microenv.get("visitor-capacity")
            capacity = None if capacity == 0 else capacity

            self.microenvironments[name] = Microenvironment(
                self._sim_env, name, volume, air_exchange_rate, capacity=capacity
            )

    def create_activities(self, microenvironment_name):
        """Create a dictionary of activities."""

        duration = self.config.microenvironments.get(microenvironment_name).get(
            "average-length-of-stay"
        )
        duration = (
            duration / self._sim_env.time_interval
        )  # Convert hours to time measures

        # TODO: NEED TO GET AN ACTIVITY OBJECT BACK NOT COMPONENTS!!!!!
        activity_name = "visit environment"
        activity_class, arguments = VisitorActivity.pack_parameters(
            self.microenvironments[microenvironment_name], duration
        )
        activity = Activity(
            id=activity_name,
            graph_ref=None,
            activity_class=activity_class,
            kwargs=arguments,
        )

        self._sim_env.routing.register_activity(activity)

    def create_network_routing(self):
        """Create a simple network routing.

        From 'start' to 'end' via 'visit environment
        """
        routing_entry_point = self._sim_env.routing.add_decision("start")
        self._sim_env.routing.add_decision("end")

        self._sim_env.routing.add_activity("visit environment", "start", "end")

        return routing_entry_point

    def create_people(
        self,
        arrivals_per_hour,
        max_arrivals=None,
        quanta_emission_rate=None,
        inhalation_rate=None,
    ):
        """ Create a method of generating people """

        is_someone_infected = False
        generated_people = 0

        while True:
            infection_status_label = (
                "susceptible" if is_someone_infected else "infected"
            )

            is_someone_infected = True

            generated_people += 1
            person = Person(
                self._sim_env,
                starting_node_id="start",
                person_type="visitor",
                infection_status_label=infection_status_label,
                quanta_emission_rate=quanta_emission_rate,
                inhalation_rate=inhalation_rate,
            )

            # self.create_routing(person, duration=duration)
            self._sim_env.env.process(person.run())

            time_to_next_person = arrivals_per_hour * self._sim_env.time_interval
            yield self._sim_env.env.timeout(time_to_next_person)

            # If we have generated enough people then stop
            if max_arrivals and (generated_people >= max_arrivals):
                break  # noqa:E701

    def run(
        self,
        arrivals_per_hour=None,
        quanta_emission_rate=None,
        inhalation_rate=None,
        max_arrivals=None,
        report_time=None,
    ):
        """ Run the simulation

        Keyword arguments:
        periods             Number of periods to run the simulation
        report_time         When True the simulation prints the time taken to execute the simulation to console.
        """

        # Start the microenvironments
        self.create_microenvironments()

        # Comment out running all
        # for key in self.microenvironments:
        #    self.env.process(self.microenvironments[key].run())
        self._sim_env.env.process(
            self.microenvironments.get(self.microenvironment_name).run()
        )

        if arrivals_per_hour is None:
            arrivals_per_hour = self.config.microenvironments.get(
                self.microenvironment_name
            ).get("visitor-arrival-rate")

        if not max_arrivals:
            temp = self.config.microenvironments.get(self.microenvironment_name).get(
                "max-arrivals", 0
            )
            if temp > 0:
                max_arrivals = temp
            else:
                max_arrivals = simpy.core.Infinity

        # Create activities
        self.create_activities(self.microenvironment_name)

        # Create the network routing graph
        self.create_network_routing()

        # Start people generation process
        self._sim_env.env.process(
            self.create_people(
                arrivals_per_hour,
                max_arrivals=max_arrivals,
                quanta_emission_rate=quanta_emission_rate,
                inhalation_rate=inhalation_rate,
            )
        )

        # Run the model
        t_start = time.time()
        if report_time:
            print(f"Running the model for {self.periods} periods")

        try:
            self._sim_env.env.run(until=self.periods)
        except Exception as ex:
            _, _, ex_traceback = sys.exc_info()
            tb_lines = traceback.format_exception(ex.__class__, ex, ex_traceback)
            tb_text = "".join(tb_lines)
            print(tb_text)
            raise Exception(ex)

        if report_time:
            t_end = time.time()
            t_duration = t_end - t_start
            print(f"Simulation finished. Execution time:{t_duration:.3f} seconds")
