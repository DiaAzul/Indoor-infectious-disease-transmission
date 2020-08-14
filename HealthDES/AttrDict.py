""" HealthDES - A python library to support discrete event simulation in health and social care """

from __future__ import annotations
from typing import Union, Iterable, Optional, List, Type, FrozenSet, Dict
from collections.abc import MutableMapping
from dataclasses import dataclass

AttrDict_KT = str
AttrDict_VT = Union[Optional[bool],
                    Optional[bytes],
                    Optional[str],
                    Optional[int],
                    Optional[float],
                    Optional[complex],
                    Optional[FrozenSet]]


class AttrDict(MutableMapping):

    valid_types: List[Type] = [bool, bytes, str, int, float, complex, frozenset]

    def __init__(self) -> None:
        self._att_register: Dict[AttrDict_KT, AttrDict_VT] = {}

    def __getitem__(self, key: AttrDict_KT) -> Optional[AttrDict_VT]:
        try:
            return self._att_register[key]
        except KeyError:
            print("Attribute {key} does not exist.")

    def __delitem__(self, key: AttrDict_KT) -> None:
        del self._att_register[key]

    def __setitem__(self, key: AttrDict_KT, value: AttrDict_VT) -> None:
        if type(value) in AttrDict.valid_types:
            self._att_register[key] = value
        else:
            raise ValueError(f'Update {key} must be immutable value.')

    def __iter__(self) -> Iterable[AttrDict_KT]:
        return iter(self._att_register)

    def __len__(self) -> int:
        return len(self._att_register)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._att_register})"


@dataclass
class StatusObject:
    __slots__ = ['current_status', 'allowable_status', 'default_status']
    current_status: AttrDict_VT
    allowable_status: FrozenSet[AttrDict_VT]
    default_status: AttrDict_VT


class StatusDict(MutableMapping):

    valid_types: List[Type] = [bool, bytes, str, int, float, complex, frozenset]

    def __init__(self) -> None:
        self._status_register: Dict[AttrDict_KT, StatusObject] = {}

    def __getitem__(self, key: AttrDict_KT) -> Optional[AttrDict_VT]:
        try:
            return self._status_register[key].current_status
        except KeyError:
            raise KeyError('{key} does not exist in status register.')

    def __delitem__(self, key: AttrDict_KT) -> None:
        try:
            del self._status_register[key]
        except KeyError:
            raise KeyError('{key} does not exist in status register.')

    def __setitem__(self, key: AttrDict_KT, value: AttrDict_VT) -> None:
        try:
            if value not in self._status_register[key].allowable_status:
                raise ValueError(f'{value} is not an allowable state in {key} status register.')
            self._status_register[key].current_status = value
        except KeyError:
            raise KeyError('{key} does not exist in status register.')

    def __iter__(self) -> Iterable[AttrDict_KT]:
        return iter(self._status_register)

    def __len__(self) -> int:
        return len(self._status_register)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._status_register})"

    def add_status_attribute(self, key: AttrDict_KT, allowable_status: FrozenSet[AttrDict_VT], default_status: AttrDict_VT):
        if key in self._status_register.keys():
            raise ValueError('{key} already already exists in status register.')
        if default_status not in allowable_status:
            raise ValueError('{default_status} is not an allowable state in {key} status register.')
        self._status_register[key] = StatusObject(current_status=default_status,
                                                  allowable_status=allowable_status,
                                                  default_status=default_status)

    def reset(self, key: AttrDict_KT):
        try:
            self._status_register[key].current_status = self._status_register[key].default_status
        except KeyError:
            raise KeyError('{key} does not exist in status register.')
