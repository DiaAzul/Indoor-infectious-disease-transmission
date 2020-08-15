""" HealthDES - A python library to support discrete event simulation in health and social care """

import itertools
from typing import NewType, Dict, Any, Callable
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

    Raises:
        ValueError: [description]
        ValueError: [description]
    """
    # create a unique ID counter
    get_new_id = itertools.count()

    def __init__(self):

        # keep a record of units ID
        self.id = next(AttrActions.get_new_id)
        # Dictionary of 'do' actions
        self._do_action: Dict[str, Any] = {}
        # Dictionary of attributes (immutable types only)
        self.att: AttrDict = AttrDict()
        # Dictionary of statuses
        self.state: StateDict = StateDict()

    # TODO: Check the error raise type - should it be key error?
    def add_do_action(self, action: str, do_function: Callable) -> None:
        if self._do_action.get(action, None) is None:
            self._do_action[action] = do_function
        else:
            raise ValueError(f'Action: {action} already defined')

    def do(self, action: str, **kwargs: str) -> None:
        """ Perform an action on the person """
        action_function = self._do_action.get(action, None)
        if action_function:
            action_function(**kwargs)
        else:
            raise ValueError(f'Received an invalid action: {action}')


AttrActionsType = NewType('AttrActionsType', AttrActions)
