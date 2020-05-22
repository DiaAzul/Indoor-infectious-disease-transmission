""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math

# Import local libraries
from Tools.Check import Check
from Microenvironment import Microenvironment
from Person import Person
from DataCollection import DataCollection

class Simulation:
    """ Class to implement a simulation using simpy discreate event simulation
    
    The simulation class is the main controlling class for the simulation and 
    is responsible for:
        + Creating the simpy environment
        + Creating individual microenvironments
        + Generating people
        + Defining the routing for each person
        + Starting and stopping the model

     """

    def __init__(self):
        """ Initialise the simulation """

        # Create a simpy environment
        self.env = simpy.Environment()
        self.dc = DataCollection(self.env)

        # Set the time interval relative to one hour (minutes = 1/60)
        self.time_interval = 1/60
        # Numper of periods the simulation will run
        self.periods = 180 

        microenvironments = []
        population = []


    def create_microenvironments(self):
        """ Create the microenvironments used within the simulation """
        pass

    def create_routing(self, person):
        """ Create the routing for a person """
        pass

    def run(self, periods):
        """ Run the simulation 

        Keyword arguments:
        periods             Number of periods to run the simulation
        """
        pass


    def dummy(self):
             

        # Set base statistics
        self.me_volume = 75 # m^3
        self.me_air_exchange_rate = 2.2  # h^-1: natural ventilation (0.2) mechanical ventilation (2.2)
        self.me_quanta_emission_rate = 142 # quanta h^-1: Resting(98.1), Standing (147), Light Exercise (317)
        self.me_n0 = 0.0

        self.me_infected = 1


