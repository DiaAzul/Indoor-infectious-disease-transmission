
from HealthDES.AttrActions import AttrActions
import pytest


def test_AttrActions():

    # TODO: Pass in the class to be tested as a parameter (replace -> AttrActions)

    testClass = AttrActions()

    ########################
    # Test Attributes exist
    ########################

    assert hasattr(testClass, 'id')
    assert hasattr(testClass, 'attr')
    assert hasattr(testClass, 'state')

    id = testClass.id

    testClass2 = AttrActions()

    # Check we are generatring sequential IDs
    assert testClass2.id == id + 1

    ############################
    # Test Attributes dictionary
    ############################

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

    test_string = 'mutate_me'
    testClass.attr['test_mutable_string'] = test_string
    test_string = 'I changed'
    assert testClass.attr['test_mutable_string'] == 'mutate_me'

    #######################
    # Test State dictionary
    #######################

    allowable_states = frozenset(('one', 'two', 'three'))
    default_state = 'one'

    testClass.state.add_state_attribute('state_test', allowable_states, default_state)

    # Test we can't add the same key twice
    with pytest.raises(KeyError) as exception_info:
        testClass.state.add_state_attribute('state_test', allowable_states, default_state)
    assert('already exists' in str(exception_info.value))

    # Test we still only have one state attribute
    assert len(testClass.state) == 1

    # Test we can't set an incorrect state value
    state_error = 'four'
    with pytest.raises(ValueError) as exception_info:
        testClass.state['state_test'] = state_error
    assert('not an allowable state' in str(exception_info.value))

    # Set state to new value and test
    testClass.state['state_test'] = 'two'
    assert testClass.state['state_test'] == 'two'

    # reset state to default and test
    testClass.state.reset('state_test')
    assert testClass.state['state_test'] == 'one'

    # Delete the state attribute and test it no longer exists
    del testClass.state['state_test']
    with pytest.raises(KeyError) as exception_info:
        _ = testClass.state['state_test']
    assert('does not exist' in str(exception_info.value))

    #################
    # Test Do Actions
    #################

    # create a callable for the test
    def test_callable(value: int) -> int:
        return value

    # Test we can add an action.
    testClass.add_do_action('test_action', test_callable)

    # Test we can call an action with arguments and get a return value
    assert testClass.do('test_action', value=42) == 42

    # Test we can't add the same key twice
    with pytest.raises(KeyError) as exception_info:
        testClass.add_do_action('test_action', test_callable)
    assert('already exists' in str(exception_info.value))

    # Delete the test action and test it no longer exists
    testClass.delete_action('test_action')
    with pytest.raises(KeyError) as exception_info:
        _ = testClass.do('test_action', value=42)
    assert('does not exist' in str(exception_info.value))
