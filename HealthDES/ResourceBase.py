""" HealthDES - A python library to support discrete event simulation in health and social care """

from .AttrActions import AttrActions
from .SimulationEnvironment import SimEnv


class ResourceBase(AttrActions):

    def __init__(self, sim_env: SimEnv):

        self.sim_env = sim_env

        super().__init__()
