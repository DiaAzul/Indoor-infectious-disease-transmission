""" HealthDES - A python library to support discrete event simulation in health and social care """

import pandas as pd
import simpy

from typing import List, Any, Optional, Union

from .DataCollection import DataCollection
from .Routing import Routing
from .SimulationEnvironment import SimEnv


class SimulationBase:
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

    def __init__(self,
                 simulation_name: str,
                 simulation_run: str,
                 time_interval: float,
                 **kwargs: Optional[Any]
                 ) -> None:
        """Initialise the simulation.

        Keyword Arguments:
            simulation_name {string} -- The name for this simulation (default: {None})
            simulation_run {string} -- The sequence number for this run of the
                                       simulation (default: {None})
        """

        # Create a simpy environment
        env = simpy.Environment()
        dc = DataCollection(env, simulation_name, simulation_run)

        self.sim_env = SimEnv(simulation_name=simulation_name,
                              simulation_run=simulation_run,
                              env=env,
                              dc=dc,
                              routing=Routing(),
                              time_interval=time_interval)

        # call specific initialisations
        self.initialise(**kwargs)

    def initialise(self) -> None:
        pass

    def get_list_of_reports(self) -> List[str]:
        """Get the list of reports.

        Returns:
            list of strings -- List of reports.
        """

        return self.sim_env.dc.get_list_of_reports()

    def get_results(self, data_set_name: str) -> Optional[pd.DataFrame]:
        """Return stored report as a pandas dataFrame.

        Arguments:
            data_set_name {string} -- Name of the dataset to get

        Returns:
            pandas dataFrame -- dataFrame containing the results
        """
        return self.sim_env.dc.get_results(data_set_name)

    def get_counter(self, data_set_name: str) -> Optional[Union[int, float]]:
        """Return stored value of a counter

        Arguments:
            data_set_name {string} -- Name of the counter to get

        Returns:
            number -- value of the counter
        """
        return self.sim_env.dc.get_counter(data_set_name)
