""" HealthDES - A python library to support discrete event simulation in health and social care """

from typing import Union, List, Dict, Any, Type

# Only permit immutable types as attributes
AttributeTypes = Union[bool, bytes, str, int, float, complex, frozenset, None]


# DoActions and Attributes are not stored within the class but a separate dictionary.
# This is to minimise the risk that dangerous code is injected into classes if at a
# future point in time end users are allowed to configure additional attributes.
class ActionQuery:

    valid_types: List[Type] = [bool, bytes, str, int, float, complex, frozenset]

    def __init__(self):
        self.do_action: Dict[str, Any] = {}
        self.attributes: Dict[str, AttributeTypes] = {}

    def add_do_action(self, action: str, do_function: str) -> None:
        if self.do_action.get(action, None) is None:
            self.do_action[action] = do_function
        else:
            raise ValueError(f'Action: {action} already defined')

    def do(self, action: str, **kwargs: str) -> None:
        """ Perform an action on the person """
        action_function = self.do_action.get(action, None)
        if action_function:
            action_function(**kwargs)
        else:
            raise ValueError(f'Received an invalid action: {action}')

    def set_attribute(self, attribute: str, attribute_value: AttributeTypes) -> None:

        tp: Type = type(attribute_value)
        if not(tp in self.valid_types):
            raise ValueError(f'Attribute: {attribute} of type {tp} must be \
                    immutable in {self.__class__}')

        self.attributes[attribute] = attribute_value

    def set_attribute_mutable(self, attribute: str, attribute_value: Any) -> None:
        self.attributes[attribute] = attribute_value

    def set_attributes(self, **attributes: str) -> None:
        for attribute, attribute_value in attributes:
            self.set_attribute(attribute, attribute_value)

    def get_attribute(self, attribute: str) -> AttributeTypes:
        """ Get a the value of an attribute."""
        return_value = self.attributes.get(attribute, None)
        if return_value is None:
            raise ValueError(f'Received an invalid parameter to query: \
                               {attribute} in {self.__class__}')

        return return_value
