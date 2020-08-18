""" HealthDES - A python library to support discrete event simulation in health and social care """

from __future__ import annotations
from .AttrActions import AttrActions

# We are not importing SimEnv, we are only using them for type checking.
# Note: import annotations from future for Python < 3.8
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .SimulationEnvironment import SimEnv


class ResourceBase(AttrActions):

    def __init__(self, sim_env: SimEnv):

        self.sim_env = sim_env

        super().__init__()
