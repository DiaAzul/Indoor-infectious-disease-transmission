
# Import local libraries
from Simulation import Simulation

def run_parallel_simulation(simulation_name):
    periods = 180
    print(".", end='')
    
    simulation_run = 1

    quanta_emission_rate=147
    inhalation_rate=0.54

    simulation = Simulation(simulation_name, simulation_run, microenvironment=simulation_name, periods=periods)

    simulation.run(quanta_emission_rate=quanta_emission_rate, 
                    inhalation_rate=inhalation_rate, 
                    report_time=False)

    infections = simulation.get_counter('Infections')
    infections = infections if infections else 0

    total_visitors = simulation.get_counter('Total visitors')

    attack_rate = infections / total_visitors

    return infections, total_visitors, attack_rate

