

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
    def fail_if_empty(li):
        """ Check whether a list is empty """

        if not li:
            raise ValueError('list must have at least one entry')

