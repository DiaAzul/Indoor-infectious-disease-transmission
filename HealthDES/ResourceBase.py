""" HealthDES - A python library to support discrete event simulation in health and social care """

import itertools
from .ActionQuery import ActionQuery


class ResourceBase(ActionQuery):

    # create a unique ID counter
    get_new_id = itertools.count()

    def __init__(self, simulation_params, resource_name):

        self.env = simulation_params.get('simpy_env', None)
        self.dc = simulation_params.get('data_collector', None)

        # keep a record of person IDs
        self.RID = next(ResourceBase.get_new_id)

        super().__init__()

    def get_RID(self):
        """Return the Resource ID (RID)

        Returns:
            string -- Resource ID for the instance
        """
        return self.RID
