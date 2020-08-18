""" HealthDES - A python library to support discrete event simulation in health and social care """

import itertools
from typing import Dict, Any, Callable
from .AttrDict import AttrDict
from .StateDict import StateDict


class AttrActions:
    """Inherited by person and resource base classes to provide a standardised interface for recording
    attributes and methods. Attributes are held in a separately from the class dictionary so that access
    can be controlled through a standardised interfaces.

    Three types of attributes are available:
    + *att[name]* - These are regular value attributes, however, they can only store immutable objects.
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
            raise KeyError(f'Action {action} already defined')
        self._do[action] = do_action

    def do(self, action: str, **kwargs: Any) -> None:
        """Calls a method on the person or resource with a list of named arguments.

        Args:
            action: Name of the action.
            kwargs: Dictionary of keyword arguments.

        Raises:
            KeyError: If the method doesn't exist in the dictionary.
        """

        try:
            action_function = self._do[action]
            action_function(**kwargs)
        except KeyError:
            raise KeyError(f'Received an invalid action: {action}')

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
            raise KeyError(f'{action} isn''t a defined action.')
