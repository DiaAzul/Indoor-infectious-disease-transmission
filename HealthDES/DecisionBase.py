""" HealthDES - A python library to support discrete event simulation in health and social care """


class DecisionBase:

    # TODO: Need to return a function which includes list of next activities
    def set_next_activity(self):
        raise NotImplementedError

    def get_next_activity(self):
        """ Dummy method to anchor class """
        raise NotImplementedError
