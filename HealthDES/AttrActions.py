"""Class to manage model attributes on model elements.

Elements within the model can have attributes. To reduce the risk of side-effects, these attributes
should unique and immutable. Attributes can be single value immutable types (such as str, int),
or attributes taking on pre-defined states (e.g. mild, moderate, severe), or do action attributes
(methods) which can be called with arguments and return value.
"""

from __future__ import annotations
from collections.abc import MutableMapping
from dataclasses import dataclass
import itertools

from typing import Any, Callable, Dict, FrozenSet, Iterable, NewType, Optional, Set, Type, Union


# Define valid key and value types for dictionaries (immutable values only)
AttrDict_KT = str
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
    """Dictionary to hold attributes for model objects. Attributes are constrained to
    immutable types"""

    valid_types: Set[Type] = {bool, bytes, str, int, float, complex, frozenset}

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
        if type(value) in AttrDict.valid_types or value is None:
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

    def add_state_attribute(self, key: AttrDict_KT,
                            allowable_states: FrozenSet[AttrDict_VT],
                            default_state: AttrDict_VT):
        """Add a state attribute to the dictionary.

        Args:
            key (AttrDict_KT): Name of the state attribute. Used to reference the attribute.
                               allowable_states (FrozenSet[AttrDict_VT]): A frozenset of allowable
                               states for the attribute. Note, states must be unique within the set.
            default_state (AttrDict_VT): The default state for the StateObject when it is
                                         initialise or reset.

        Raises:
            KeyError: Raises a KeyError if the attribute is already defined within the
        dictionary
            ValueError: Raises a value error if the value of default_state is not in the
                        allowable_states.
        """
        if key in self._status_register.keys():
            raise KeyError('{key} already exists in state register.')
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


class AttrActions:
    """Inherited by person and resource base classes to provide a standardised interface for recording
    attributes and methods. Attributes are held in a separately from the class dictionary so that \
    access can be controlled through a standardised interfaces.

    Three types of attributes are available:
    + *att[name]* - These are regular value attributes, however, they can only store immutable \
    objects.
    + *state[name]* - Attributes that can only hold a defined list of states.
    + *do[name]* - Method attributes, which allow external access to class functions.

    This class also generates a unique id within reach of the person and resource classes.

    Raises:
        KeyError: If a new action is added with the same name as a previous action.
        KeyError: If an action is not defined at the point it is called.
    """
    # create a unique ID counter
    _get_new_id = itertools.count()

    def __init__(self):
        # keep a record of units ID
        self.id = next(AttrActions._get_new_id)
        # Dictionary of 'do' actions
        self._do: Dict[str, Any] = {}
        # Dictionary of attributes (immutable types only)
        self.attr: AttrDict = AttrDict()
        # Dictionary of States
        self.state: StateDict = StateDict()

    def add_do_action(self, action: str, do_action: Callable) -> None:
        """Adds a callable method to the 'do' dictionary of actions which can be called.

        Args:
            action: Name of the action.
            do_function: Callable method.

        Raises:
            KeyError: If the method is already in the dictionary.
        """
        if self._do.get(action) is not None:
            raise KeyError(f'Action {action} already exists in action register.')
        self._do[action] = do_action

    def do(self, action: str, **kwargs: Any) -> Any:
        """Calls a method on the person or resource with a list of named arguments.

        Args:
            action: Name of the action.
            kwargs: Keyword arguments to pass to the action

        Raises:
            KeyError: If the action doesn't exist in the dictionary.

        Returns:
            The return value from the action.
        """
        try:
            action_function = self._do[action]
            return_value = action_function(**kwargs)
        except KeyError:
            raise KeyError(f'{action} does not exist in action register.')

        return return_value

    def delete_action(self, action: str):
        """Delete an action from the dictionary

        Args:
            action: Name of the action.

        Raises:
            KeyError: If the action doesn't exist in the dictionary.
        """
        try:
            del self._do[action]
        except KeyError:
            raise KeyError(f'{action} does not exist in action register.')
