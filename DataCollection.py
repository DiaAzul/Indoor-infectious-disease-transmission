""" Python library to model the spread of infectious diseases within a microenvironment """

import pandas as pd # modin
import simpy

# Import local libraries
from Tools.Check import Check
from Microenvironment import Microenvironment
from Person import Person

class DataCollection:
    """ Class to collect data from across the simulation
    
    Data collection can be period (driven by periodic simpy event process)
    or logged by other parts of the simulation.

     """

    def __init__(self, env):
        """ Create a class to collect data within a simulation run
        
        Keyworkd parameters:
        env                 simpy environment

        """

        self.env = env

        # All the data goes into a dictionary
        # Table name is the key, value is a pandas dataframe
        self.data = {}


    def periodic_reporting(self, data_set_name, column_names, callback, periods):
        """ Add a new period_reporting collector

        NOTE: This has not yet been tested and may suffer from mutable object problems if called multiple times.
        NOTE: This needs to be called within an env.process
        """

        self.data[data_set_name] = pd.DataFrame(columns=column_names)

        while True:
            self.data[data_set_name].append(callback())
            yield self.env.timeout(periods+1)



    def run(self):
        """ Run the data collection process """
        pass




