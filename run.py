""" Runner to start simulation from the command line for debugging purposes """

from Simulation import Simulation


if __name__ == "__main__":
    periods = 100
    simulation_name = 'Lounge-Two People-Winter-1 hour'
    simulation_run = '1'
    arrivals_per_hour = None
    max_arrivals = None
    quanta_emission_rate = 147
    inhalation_rate = 0.54

    simulation = Simulation(simulation_name, simulation_run, microenvironment=simulation_name, periods=periods)

    simulation.run(arrivals_per_hour=arrivals_per_hour,
                   quanta_emission_rate=quanta_emission_rate,
                   inhalation_rate=inhalation_rate,
                   max_arrivals=max_arrivals,
                   report_time=True)
