""" HealthDES - A python library to support discrete event simulation in health and social care """

from .AttrActions import AttrActions


class ResourceBase(AttrActions):

    def __init__(self, simulation_params):

        self.env = simulation_params.get('simpy_env', None)
        self.dc = simulation_params.get('data_collector', None)

        super().__init__()
