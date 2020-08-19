""" HealthDES - A python library to support discrete event simulation in health and social care """

import pandas as pd
import simpy

from typing import List, Any, Optional, Union

from .DataCollection import DataCollection
from .Routing import Routing
from .SimulationEnvironment import SimEnv


class SimulationBase:
    """The simulation class is the main controlling class for the simulation and is responsible for:
    * Creating the simpy environment
    * Creating the data collection environment
    * Creating resources and activities
    * Generating people
    * Defining the routing for each person
    * Starting and stopping the model
     """

    def __init__(
        self,
        simulation_name: str,
        simulation_run: str,
        time_interval: float,
        **kwargs: Optional[Any]
    ) -> None:
        """Initialise the simulation.

        Args:
            simulation_name ([type]): The name for this simulation
            simulation_run ([type]): The sequence number for this run of the simulation
            time_interval ([type]): Each ratio of simulation periods to time periods.
        """
        env = simpy.Environment()
        dc = DataCollection(env, simulation_name, simulation_run)

        self._sim_env = SimEnv(
            simulation_name=simulation_name,
            simulation_run=simulation_run,
            env=env,
            dc=dc,
            routing=Routing(),
            time_interval=time_interval,
        )

        # call specific initialisations
        self.initialise(**kwargs)

    def initialise(self, **kwargs: Any) -> None:
        """Method to be overridden to initialise additional arguments for the simulation.
        """
        pass

    def get_list_of_reports(self) -> List[str]:
        """Returns a list of reports available from the data collection module.

        Returns:
            Returns a list of available reports
        """
        return self._sim_env.dc.get_list_of_reports()

    def get_results(self, data_set_name: str) -> Optional[pd.DataFrame]:
        """Returns the named report from the data collection module.

        Args:
            data_set_name: Name of the report to be returned

        Returns:
            Returns the report as a Pandas dataFrame.
        """
        return self._sim_env.dc.get_results(data_set_name)

    def get_counter(self, data_set_name: str) -> Optional[Union[int, float]]:
        """Returns the value of the named counter.

        Args:
            data_set_name: Name of the counter to return.

        Returns:
            Value of the counter.
        """
        return self._sim_env.dc.get_counter(data_set_name)
