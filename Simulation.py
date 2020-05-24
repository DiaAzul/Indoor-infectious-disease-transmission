""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import math
import time

# Import local libraries
from Tools.Check import Check
from Microenvironment import Microenvironment
from Person import Person
from DataCollection import DataCollection
from DiseaseProgression import DiseaseProgression

class Simulation:
    """ Class to implement a simulation using simpy discreate event simulation
    
    The simulation class is the main controlling class for the simulation and 
    is responsible for:
        * Creating the simpy environment
        * Creating the data collection environment
        * Creating individual microenvironments
        * Generating people
        * Defining the routing for each person
        * Starting and stopping the model
     """

    def __init__(self, simulation_name=None, simulation_run=None):
        """ Initialise the simulation

        Keyworkd parameters:
        simulation_name     The name for this simulation
        simulation_run      The sequence number for this run of the simulation 
        """
        # Create a simpy environment
        self.env = simpy.Environment()
        self.dc = DataCollection(self.env, simulation_name, simulation_run)

        # Set the time interval relative to one hour (minutes = 1/60)
        self.time_interval = 1/60
        # Numper of periods the simulation will run
        self.periods = 180 

        self.microenvironments = {}
        self.population = {}


    def get_list_of_reports(self):
        """ Get the list of result tables """

        return self.dc.get_list_of_reports()


    def get_results(self, data_set_name):
        """ Return stored data as a pandas data frame """
        return self.dc.get_results(data_set_name)


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
                            duration=kwargs['duration'])


    def create_people(self, arrivals_per_hour):
        """ Create a method of generating people """
        quanta_emission_rate = 147
        duration=10
        is_someone_infected = False

        while True:        
            infection_status_label = DiseaseProgression.valid_state('susceptible') if is_someone_infected else DiseaseProgression.valid_state('infected')
            is_someone_infected = True

            person = Person(self.env, self.dc, person_type='visitor', infection_status_label=infection_status_label, quanta_emission_rate=quanta_emission_rate)
            self.create_routing(person, duration=duration)
            self.env.process(person.run())

            time_to_next_person = 60 / arrivals_per_hour
            yield self.env.timeout(time_to_next_person) 


    def run(self, periods, report_time=None):
        """ Run the simulation 

        Keyword arguments:
        periods             Number of periods to run the simulation
        report_time         When True the simulation prints the time taken to execute the simulation to console.
        """
        arrivals_per_hour = 100
      
        # Start the microenvironments
        self.create_microenvironments()
        for key in self.microenvironments:
            self.env.process(self.microenvironments[key].run())

        # Start people generation process
        self.env.process(self.create_people(arrivals_per_hour))

        # Run the model
        t_start = time.time()        
        if report_time:         
            print("Running the model for {periods} periods".format(periods=periods))
        
        self.env.run(until=periods)

        if report_time:
            t_end = time.time()
            t_duration = t_end - t_start
            print("Simulation finished. Execution time:{duration:.3f} seconds".format(duration=t_duration))
    
