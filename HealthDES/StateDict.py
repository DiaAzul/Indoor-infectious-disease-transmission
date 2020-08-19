""" HealthDES - A python library to support discrete event simulation in health and social care """

from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import dataclass

from typing import Union, Iterable, Optional, FrozenSet, Dict


AttrDict_KT = str
AttrDict_VT = Union[Optional[bool],
                    Optional[bytes],
                    Optional[str],
                    Optional[int],
                    Optional[float],
                    Optional[complex],
                    Optional[FrozenSet]]


@dataclass
class StateObject:
    """The StateObject is a classification object with multiple allowable states.
    + *current_state* is the current state of the object.
    + *allowable_states* are the states the object is allowed to have.
    + *default_state* the initial state of the object. Object can be reset to this state.
    """
    __slots__ = ['current_state', 'allowable_states', 'default_state']
    current_state: AttrDict_VT
    allowable_states: FrozenSet[AttrDict_VT]
    default_state: AttrDict_VT


class StateDict(MutableMapping):
    """The StateDict is a dictionary of StateObjects holding state attributes for either
    a person or a resource within the model. Example state objects could include health
    condition (healthy, unhealthy), injury severity (minor, major, critical), or infection
    state (susceptible, exposed, infected, recovered).
    """
    def __init__(self) -> None:
        self._status_register: Dict[AttrDict_KT, StateObject] = {}

    def __getitem__(self, key: AttrDict_KT) -> Optional[AttrDict_VT]:
        try:
            return self._status_register[key].current_state
        except KeyError:
            raise KeyError('{key} does not exist in status register.')

    def __delitem__(self, key: AttrDict_KT) -> None:
        try:
            del self._status_register[key]
        except KeyError:
            raise KeyError('{key} does not exist in status register.')

    def __setitem__(self, key: AttrDict_KT, value: AttrDict_VT) -> None:
        try:
            if value not in self._status_register[key].allowable_states:
                raise ValueError(f'{value} is not an allowable state in {key} status register.')
            self._status_register[key].current_state = value
        except KeyError:
            raise KeyError('{key} does not exist in status register.')

    def __iter__(self) -> Iterable[AttrDict_KT]:
        return iter(self._status_register)

    def __len__(self) -> int:
        return len(self._status_register)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._status_register})"

    def add_status_attribute(self, key: AttrDict_KT, allowable_states: FrozenSet[AttrDict_VT], default_state: AttrDict_VT):
        """Add a status attribute to the dictionary.

        Args:
            key (AttrDict_KT): Name of the state attribute. Used to reference the attribute.
            allowable_states (FrozenSet[AttrDict_VT]): A frozenset of allowable states for the attribute. Note, states must be unique within the set.
            default_state (AttrDict_VT): The default state for the StateObject when it is initialise or reset.

        Raises:
            KeyError: Raises a KeyError if the attribute is already defined within the dictionary
            ValueError: Raises a value error if the value of default_state is not in the allowable_states.
        """
        if key in self._status_register.keys():
            raise KeyError('{key} already already exists in status register.')
        if default_state not in allowable_states:
            raise ValueError('{default_state} is not an allowable state in {key} status register.')
        self._status_register[key] = StateObject(current_state=default_state,
                                                 allowable_states=allowable_states,
                                                 default_state=default_state)

    def reset(self, key: AttrDict_KT):
        """Resets the state attribute to the default value.

        Args:
            key (AttrDict_KT): The name of the state attribute to reset.

        Raises:
            KeyError: Raises a key error if the state attribute is not in the dictionary.
        """
        try:
            self._status_register[key].current_state = self._status_register[key].default_state
        except KeyError:
            raise KeyError('{key} does not exist in status register.')
