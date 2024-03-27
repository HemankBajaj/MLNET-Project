import pandas as pd           
import numpy as np             
from datetime import datetime


# TODO: Read the cached csv in the constructor and extract metadata there itself. Reading CSVs should'nt take long as pcaps
class SpeedTestConnection:
    """
    Takes in a csv file of the connection. The csv file is prepared using the Connection CSV object
    """
    def __init__(self, csv_file):
        self.conn_csv = csv_file 
        
    def get_dataframe(self):
        return pd.read_csv(self.conn_csv)

    # def get_connection_metadata(self):
    
if __name__ == "__main__":
    print("SpeedTestConnection.py") 