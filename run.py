""" Runner to start simulation from the command line for debugging purposes """

from Simulation import Simulation


if __name__ == "__main__":
    periods = 100
    simulation_name = 'Pharmacy'
    simulation_run = 1

    simulation = Simulation(simulation_name, simulation_run)
    simulation.run(periods, report_time=True)



