""" HealthDES - A python library to support discrete event simulation in health and social care """

from __future__ import annotations
import simpy
from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:  # Type checking creates a circular import (needs annotations as well)
    from .DataCollection import DataCollection
    from .Routing import Routing


@dataclass(frozen=True)
class SimEnv:
    __slots__ = ['simulation_name', 'simulation_run', 'time_interval', 'env', 'dc', 'routing']
    simulation_name: str
    simulation_run: str
    time_interval: float
    env: simpy.Environment
    dc: DataCollection
    routing: Routing
