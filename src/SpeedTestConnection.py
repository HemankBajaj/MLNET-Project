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
        df = pd.read_csv(csv_file)
        self.df_empty = True
        # verify if this is the client or the host. Current assumption is that this is a client
        if len(df) > 0:
            self.df_empty = False
            self.client = df.iloc[0]['Source IP'] 
            self.setver = df.iloc[0]['Destination IP'] 
        
    def get_dataframe(self):
        return pd.read_csv(self.conn_csv)
    
    def is_empty(self):
        return self.df_empty

    # def get_connection_metadata(self):
    
if __name__ == "__main__":
    print("SpeedTestConnection.py") 