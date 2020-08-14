""" HealthDES - A python library to support discrete event simulation in health and social care """

import itertools
from typing import NewType, Dict, Any, Callable
from .AttrDict import AttrDict, StatusDict


# DoActions and Attributes are not stored within the class but a separate dictionary.
# This is to minimise the risk that dangerous code is injected into classes if at a
# future point in time end users are allowed to configure additional attributes.
class ActionQuery:

    # create a unique ID counter
    get_new_id = itertools.count()

    def __init__(self):

        # keep a record of units ID
        self.id = next(ActionQuery.get_new_id)
        # Dictionary of 'do' actions
        self._do_action: Dict[str, Any] = {}
        # Dictionary of attributes (immutable types only)
        self.att: AttrDict = AttrDict()
        # Dictionary of statuses
        self.status: StatusDict = StatusDict()

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


ActionQueryType = NewType('ActionQueryType', ActionQuery)
