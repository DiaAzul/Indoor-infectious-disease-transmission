
from HealthDES.AttrActions import AttrActions
import pytest


def test_AttrActions():

    # TODO: Pass in the class to be tested as a parameter (replace -> AttrActions)
    testClass = AttrActions()

    ###########################
    # Test Attribute dictionary
    ###########################

    assert hasattr(testClass, 'id')
    assert hasattr(testClass, 'attr')
    assert hasattr(testClass, 'state')

    id = testClass.id

    testClass2 = AttrActions()

    # Check we are generatring sequential IDs
    assert testClass2.id == id + 1

    # Test attributes on status dictionary.
    # Test for acceptance of immutable types
    testClass.attr['test_bool'] = True
    testClass.attr['test_bytes'] = b"0"
    testClass.attr['test_str'] = 'Test string'
    testClass.attr['test_int'] = 1
    testClass.attr['test_float'] = 1.1
    testClass.attr['test_complex'] = complex(1, 1)
    testClass.attr['test_frozenSet'] = frozenset((1, 2, 3))
    testClass.attr['test_None'] = None

    # Check we now have eight entries
    assert len(testClass.attr) == 8

    # Test that we can delete item
    del testClass.attr['test_None']
    assert len(testClass.attr) == 7

    # Test we can manipulate items
    testClass.attr['test_str'] = 'New test string'
    assert testClass.attr['test_str'] == 'New test string'

    testClass.attr['test_int'] += 1
    assert testClass.attr['test_int'] == 2

    # Test for rejection of mutable types
    with pytest.raises(ValueError) as exception_info:
        testClass.attr['test_list'] = [1, 2, 3]
    assert('immutable value' in str(exception_info.value))

    with pytest.raises(ValueError) as exception_info:
        testClass.attr['test_dict'] = {'one': 1, 'two': 2}
    assert('immutable value' in str(exception_info.value))

    #######################
    # Test State dictionary
    #######################

    #

    #################
    # Test Do Actions
    #################
