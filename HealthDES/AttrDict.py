""" HealthDES - A python library to support discrete event simulation in health and social care """

from __future__ import annotations
from typing import Union, Iterable, Optional, List, Type, FrozenSet, Dict, NewType
from collections.abc import MutableMapping

AttrDict_KT = str
# Need to consider how to do dynamic typing in a dictionary where keys are not know upfront
# This is very permissive, which undermines typing philosophy. Though does ensure that we
# do not assign mutable types to attributes.
AttrDict_VT = NewType('AttrDict_VT', Union[bool,
                                           bytes,
                                           str,
                                           int,
                                           float,
                                           complex,
                                           FrozenSet,
                                           Optional[bool],
                                           Optional[bytes],
                                           Optional[str],
                                           Optional[int],
                                           Optional[float],
                                           Optional[complex],
                                           Optional[FrozenSet]])


class AttrDict(MutableMapping):
    """Dictionary of immutable attributes."""

    valid_types: List[Type] = [bool, bytes, str, int, float, complex, frozenset]

    def __init__(self) -> None:
        self._att_register: Dict[AttrDict_KT, AttrDict_VT] = {}

    def __getitem__(self, key: AttrDict_KT) -> AttrDict_VT:
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
