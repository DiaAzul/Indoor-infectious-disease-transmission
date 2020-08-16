""" HealthDES - A python library to support discrete event simulation in health and social care """

from dataclasses import dataclass
import simpy
import pandas as pd

# Import local libraries
from HealthDES import DataCollection
from HealthDES import Routing
from typing import List, Any, Optional


# TODO: Work out how to distribute global environment parameters.
@dataclass
class SimEnv:
    __slots__ = ['env', 'dc', 'routing']
    env: simpy.Environment
    dc: DataCollection
    routing: Routing


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

    # TODO: Move simulation_run to run() method call, and implement a reset simulation.
    def __init__(self,
                 simulation_name: Optional[str] = None,
                 simulation_run: Optional[str] = None,
                 **kwargs: Optional[Any]
                 ) -> None:
        """Initialise the simulation.

        Keyword Arguments:
            simulation_name {string} -- The name for this simulation (default: {None})
            simulation_run {string} -- The sequence number for this run of the
                                       simulation (default: {None})
        """
        # Create a simpy environment
        self.env = simpy.Environment()
        self.dc = DataCollection(self.env, simulation_name, simulation_run)

        # Routing of people through the model, nodes are decisions, edges are activities
        self.routing = Routing()

        self.simulation_params = {'simpy_env': self.env,
                                  'data_collector': self.dc,
                                  'routing': self.routing
                                  }
        # REPLACES THE ABOVE...maybe
        self.simenv = SimEnv(self.env, self.dc, self.routing)

        # call specific initialisations
        self.initialise(**kwargs)

    def initialise(self) -> None:
        pass

    def add_simulation_param(self, param_name: str, param: Any) -> None:
        self.simulation_params[param_name] = param

    def get_list_of_reports(self) -> List[str]:
        """Get the list of reports.

        Returns:
            list of strings -- List of reports.
        """

        return self.dc.get_list_of_reports()

    def get_results(self, data_set_name: str) -> pd.DataFrame:
        """Return stored report as a pandas dataFrame.

        Arguments:
            data_set_name {string} -- Name of the dataset to get

        Returns:
            pandas dataFrame -- dataFrame containing the results
        """
        return self.dc.get_results(data_set_name)

    def get_counter(self, data_set_name: str) -> int:
        """Return stored value of a counter

        Arguments:
            data_set_name {string} -- Name of the counter to get

        Returns:
            number -- value of the counter
        """
        return self.dc.get_counter(data_set_name)
