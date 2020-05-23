""" Python library to model the spread of infectious diseases within a microenvironment """

import pandas as pd # modin
import simpy

# Import local libraries
from Tools.Check import Check

class DataCollection:
    """ Class to collect data from across the simulation
    
    Data collection can be period (driven by periodic simpy event process)
    or logged by other parts of the simulation.

    Data collection writes to an in-memory csv file, which may be exported or converted to pandas DataFrame

    """
    # TODO: Implement in-memory csv file writer
    """
    I used this answer's df.loc[i] = [new_data] suggestion, but I have > 500,000 rows and that was very slow.

    While the answers given are good for the OP's question, I found it more efficient, when dealing with large
    numbers of rows up front (instead of the tricking in described by the OP) to use csvwriter to add data to an
    in memory CSV object, then finally use pandas.read_csv(csv) to generate the desired DataFrame output.

    from io import BytesIO
    from csv import writer 
    import pandas as pd

    output = BytesIO()
    csv_writer = writer(output)

    for row in iterable_object:
        csv_writer.writerow(row)

    output.seek(0) # we need to get back to the start of the BytesIO
    df = pd.read_csv(output)
    return df

    This, for ~500,000 rows was 1000x faster and as the row count grows the speed improvement will only get larger
    (the df.loc[1] = [data] will get a lot slower comparatively)
    """
    # TODO: Implement some form of memory management to flush in-memory csv to disk/database if memory tight

    def __init__(self, env, simulation_name=None, simulation_run=None):
        """ Create a class to collect data within a simulation run
        
        Keyworkd parameters:
        env                 simpy environment

        """

        self.env = env
        self.simulation_name = simulation_name
        self.simulation_run = simulation_run

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
            yield self.env.timeout(periods)



    def run(self):
        """ Run the data collection process """
        pass




