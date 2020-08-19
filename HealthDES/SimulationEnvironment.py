""" HealthDES - A python library to support discrete event simulation in health and social care """

from __future__ import annotations

from dataclasses import dataclass

# We are not importing Simpy, DataCollection, and Routing, we are only using them for type checking.
# Note: import annotations from future for Python < 3.8
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import simpy
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
