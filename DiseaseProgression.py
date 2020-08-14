""" Python library to model the spread of infectious diseases within a microenvironment """

from __future__ import annotations
from HealthDES.Check import CheckList
from typing import List, Optional

import copy


class DiseaseProgression:
    """ Disease status of person within the model """

    _disease_states: List[str] = ['susceptible', 'exposed', 'infected', 'recovered']
    _status: Optional[str] = None

    def __init__(self, infection_status_label: str = None) -> None:
        """ All people have an initial status of susceptible """

        self._status = DiseaseProgression.valid_state('susceptible') if infection_status_label is None else DiseaseProgression.valid_state(infection_status_label)

    @staticmethod
    def valid_state(infection_status_label: str) -> str:
        """ Checks text and returns text if it is a valid disease state """

        CheckList.fail_if_not_in_list(infection_status_label, DiseaseProgression._disease_states)
        return infection_status_label

    def set_state(self, infection_status_label: str) -> None:
        """ Sets the disease state """

        CheckList.fail_if_not_in_list(infection_status_label, DiseaseProgression._disease_states)
        self._status = infection_status_label

    def is_state(self, infection_status_label: str) -> bool:
        """ Tests disease state and return True if matches """

        CheckList.fail_if_not_in_list(infection_status_label, DiseaseProgression._disease_states)
        return self._status == infection_status_label

    def copy(self) -> DiseaseProgression:
        return copy.deepcopy(self)
