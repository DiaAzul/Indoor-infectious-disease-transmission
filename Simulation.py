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

        self.microenvironments = {}
        self.population = {}

    def create_microenvironments(self):
        """ Create the microenvironments used within the simulation """
        volume = 75 # m^3
        air_exchange_rate = 0.2  # h^-1: natural ventilation (0.2) mechanical ventilation (2.2)  
        environment_name = 'Pharmacy'
        capacity = 5

        self.microenvironments[environment_name] = Microenvironment(self.env, self.dc, self.time_interval, volume, air_exchange_rate, capacity=capacity)


    def create_routing(self, person, **kwargs):
        """ Create the routing for a person """


        person.enqueue(self.microenvironments['Pharmacy'], 
                            duration=kwargs['duration'], 
                            infected=kwargs['infected'], 
                            quanta_emission_rate=kwargs['quanta_emission_rate'])


    def create_people(self, arrivals_per_hour):
        """ Create a method of generating people """

        quanta_emission_rate = 147
        is_someone_infected = False

        while True:        
            infected = 0 if is_someone_infected else 1
            is_someone_infected = True

            person = Person(self.env, self.dc, quanta_emission_rate)
            self.create_routing(person, duration=10, infected=infected, quanta_emission_rate=147)
            self.env.process(person.run())

            time_to_next_person = 60 / arrivals_per_hour
            yield self.env.timeout(time_to_next_person) 

        """ **************************************************************************
        Need to work out how to create people, add them to the list, start them running, return for next person
        ****************************************************************************** """


    def run(self, periods):
        """ Run the simulation 

        Keyword arguments:
        periods             Number of periods to run the simulation
        """

        arrivals_per_hour = 100

        self.create_microenvironments()

        # Start the microenvironments
        for key in self.microenvironments:
            self.env.process(self.microenvironments[key].run())

        self.env.process(self.create_people(arrivals_per_hour))

        # Start the data collection process
        # self.env.process(self.dc.run())

        print("Periods:", periods)
        self.env.run(until=periods)
