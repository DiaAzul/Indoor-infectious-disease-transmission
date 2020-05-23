""" Python library to model the spread of infectious diseases within a microenvironment """

import pandas as pd # modin
import simpy
from io import BytesIO, StringIO
from csv import DictWriter, reader

# Import local libraries
from Tools.Check import Check, CheckList

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
        simulation_name     The name for this simulation
        simulation_run      The sequence number for this run of the simulation

        """
        self.env = env
        self.simulation_name = simulation_name
        self.simulation_run = simulation_run

        # All the memory tables referenced from dictionary
        self.memory_file = {}
        self.memory_writer = {}


    def create_period_reporting(self, data_set_name, callback, periods, column_dictionary):
        """ Register a periodic report

        Keyword parameters:
        data_set_name           The name for the data set to be recorded
        column_dictionary            Dictionary of column_names
        callback                Function to call periodically to collect data
        periods                 The number of periods between data collections 

        Note data collection is triggered when the model first starts
        """
        CheckList.is_a_dictionary(column_dictionary)
        CheckList.fail_if_this_key_in_the_dictionary(data_set_name, self.memory_file)

        header_list = []
        for key, _ in column_dictionary.items():
            header_list.append(key)

        header_list.insert(0, 'time')
        header_list.insert(0, 'simulation_run')
        header_list.insert(0, 'simulation_name')

        # Create a new memory file into which data will be stored as CSV file
        self.memory_file[data_set_name] = StringIO()
        self.memory_writer[data_set_name] = DictWriter(self.memory_file[data_set_name], header_list, restval='Null', extrasaction='raise')

        self.memory_writer[data_set_name].writeheader()

        self.env.process(self.periodic_reporting(data_set_name, callback, periods))
        # stream_writer.writerow()


    def periodic_reporting(self, data_set_name, callback, periods):
        """ Add a new period_reporting collector 

        Keyword parameters:
        data_set_name           The name of the dataset into which data stored
        callback                The method to call to fetch the data
        periods                 The number of periods between fetches of data

        """
        while True:
            data = callback()
            data['time'] = self.env.now
            data['simulation_run'] = self.simulation_run
            data['simulation_name'] = self.simulation_name
            self.memory_writer[data_set_name].writerow(data)

            yield self.env.timeout(periods)

    def get_results(self, data_set_name):
        """ Return stored data as a pandas data frame """
        self.memory_file[data_set_name].seek(0)
        df = pd.read_csv(self.memory_file[data_set_name])

        return df


    def log_reporting(self, data_set_name, data):
        pass


    def run(self):
        """ Run the data collection process """
        yield self.env.timeout(1)




