""" Python library to model the spread of infectious diseases within a microenvironment """

import pandas as pd


class Config:

    def __init__(self):

        self.microenvironments = {}

    def import_microenvironments(self):
        file_db = pd.read_excel('./Configuration/Environment database.xlsx', header=4, engine='openpyxl')

        for _, row in file_db.iterrows():
            config_name = row['environment']
            params = row.to_dict()
            self.microenvironments[config_name] = params



# Run as script to test the import procedure

if __name__ == "__main__":
    # execute only if run as a script
    config = Config()
    config.import_microenvironments()

    print('Done.')    
