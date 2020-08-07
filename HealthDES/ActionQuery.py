""" HealthDES - A python library to support discrete event simulation in health and social care """

from typing import (
    Union
)

# Only permit immutable types as attributes
AttributeTypes = Union[bool, bytes, str, int, float, complex, frozenset]


# TODO: Remove __setattr__ and __getattribute__ and use separate dictionary to prevent name clash
class ActionQuery:

    def __init__(self):
        self.do_action = {}
        self.attributes = {}

    def add_do_action(self, action: str, do_function: str) -> None:
        if self.do_action.get(action, None) is None:
            self.do_action[action] = do_function
        else:
            raise(f'Action: {action} already defined')

    def do(self, action: str, **kwargs: str) -> None:
        """ Perform an action on the person """
        action_function = self.do_action.get(action, None)
        if action_function:
            action_function(**kwargs)
        else:
            raise ValueError(f'Received an invalid action: {action}')

    def add_attribute(self, attribute: str, attribute_value: AttributeTypes) -> None:
        try:
            self.__getattribute__(attribute)
        except(AttributeError):
            self.__setattr__(attribute, attribute_value)
            self.attributes[attribute] = attribute_value
        else:
            raise(f'Attribute: {attribute} already defined in {self.__class__}')

    def add_attributes(self, **attributes: str) -> None:
        for attribute, attribute_value in attributes:
            self.add_attribute(attribute, attribute_value)

    def get_attribute(self, attribute: str) -> AttributeTypes:
        """ Get a the value of an attribute."""
        try:
            return_value = self.__getattribute__(attribute)
        except(AttributeError):
            raise ValueError(
                f'Received an invalid parameter to query: {attribute}in {self.__class__}')

        return return_value

    def update_attribute(self, attribute: str, attribute_value: AttributeTypes) -> None:
        """ Update value of an attribute """
        try:
            self.__setattr__(attribute, attribute_value)
        except(AttributeError):
            raise(f'Attribute: {attribute} doesn''t exists in {self.__class__}')
