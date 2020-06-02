

class Check:
    """ Class containing functions to check whether values meet certain conditions

    In Data Science analysis it is more important to ensure that data is correct than code is fast. Therefore,
    a greater degree of parameter checking may be appropriate to ensure that parameters meet defined criteria.
    This Class contains common checks that are applied to base types (int, float, string) to confirm data integrity.
    """
    @staticmethod
    def is_equal_to_zero(x):
        """ Check that variable is equal to zero."""
        if not(type(x) is int or type(x) is float):
            raise ValueError('value must be a number')
        if not (x == 0):
            raise ValueError('value must be equal to zero')

    @staticmethod
    def is_not_equal_to_zero(x):
        """ Check that variable is not equal to zero."""
        if not(type(x) is int or type(x) is float):
            raise ValueError('value must be a number')
        if not (x != 0):
            raise ValueError('value must not equal to zero')
    
    @staticmethod
    def is_greater_than_zero(x):
        """ Check that variable is greater than zero."""
        if not(type(x) is int or type(x) is float):
            raise ValueError('value must be a number')
        if not (x > 0):
            raise ValueError('value must be greater than zero')

    @staticmethod
    def is_greater_than_or_equal_to_zero(x):
        """ Check that variable is greater than, or equal to, zero."""
        if not(type(x) is int or type(x) is float):
            raise ValueError('value must be a number')
        if not (x >= 0):
            raise ValueError('value must be greater than, or equal to, zero')

    @staticmethod
    def is_less_than_zero(x):
        """ Check that variable is less than zero."""
        if not(type(x) is int or type(x) is float):
            raise ValueError('value must be a number')
        if not (x < 0):
            raise ValueError('value must be less than zero')

    @staticmethod
    def is_less_than_or_equal_to_zero(x):
        """ Check that variable is less than, or equal to, zero."""
        if not(type(x) is int or type(x) is float):
            raise ValueError('value must be a number')
        if not (x <= 0):
            raise ValueError('value must be less than, or equal to, zero')

class CheckList:
    """ Class containing functions to check whether lists have certain characteristics """

    @staticmethod
    def is_a_list(li):
        """ Check whether variable is a list """
        if not isinstance(li, list):
            raise ValueError('This must be a list')
    
    @staticmethod
    def fail_if_list_empty(li):
        """ Check whether a list is empty """
        if not li:
            raise ValueError('list must have at least one entry')

    @staticmethod
    def fail_if_not_in_list(test_item, li):
        """ fail if item is not in the list """
        in_list = False
        for item in li:
            if item == test_item:
                in_list = True
                break

        if not in_list:
            raise ValueError('Item not in list')

    @staticmethod
    def is_a_dictionary(di):
        """ Check whether variable is a list """
        if not isinstance(di, dict):
            raise ValueError('This must be a dictionary')

    @staticmethod
    def fail_if_dict_empty(li):
        """ Check whether a list is empty """
        if not li:
            raise ValueError('list must have at least one entry')

    @staticmethod
    def fail_if_this_key_in_the_dictionary(test_key, di):
        if test_key in di:
            raise ValueError('Cannot have duplicate keys in dictionary')

    