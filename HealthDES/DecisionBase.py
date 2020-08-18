""" HealthDES - A python library to support discrete event simulation in health and social care """

# import simpy
from .ActivityBase import Activity
from typing import Dict, NewType
from dataclasses import dataclass


class DecisionBase:

    # TODO: Need to return a function which includes list of next activities
    def set_next_activity(self, activity):
        return self.get_next_activity

    def get_next_activity(self, person, activity_a):
        """ Dummy method to anchor class """
        return Activity('Dummy', None, None, None)


@dataclass
class Decision:
    __slots__ = ['id', 'decision_class', 'kwargs']
    id: str
    decision_class: DecisionBase
    kwargs: Dict


DecisionType = NewType('DecisionType', DecisionBase)
