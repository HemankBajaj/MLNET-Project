from ConnectionCSV import pcap_to_df, formatting_df, readPCAP
import datetime 
from FileIO import MatrixFileIO
from constants import NUM_BINS_LIST
import math 
import numpy as np


def tuple_to_integer(x):
    y = 0
    p = 1
    for i in range(len(x)):
        y += x[-i-1]*p
        p*= 10
    return y

class ConnectionDF:
    def __init__(self, pcap_file):
        self.pcap_file = pcap_file
    def get_dataframe(self):
        df = pcap_to_df(self.pcap_file)
        df = formatting_df(df)
        return df 


# df['Source IP'] 
# df['Destination IP'] = df['dst_ip']
# df['Source Port'] = df['tcp_sport']
# df['Destination Port'] = df['tcp_dport']
# df['Payload Length'] = df['len']


class TestFramework:
    def __init__(self, connection_df, q_table):
        self.num_bins_list = NUM_BINS_LIST
        self.df = connection_df.get_dataframe()

        self.client_ip = self.df["Source IP"].iloc[0]
        self.server_ip = self.df["Destination IP"].iloc[0]

        # print(self.df["Source IP"] == self.client_ip)
        df_upload = self.df[(self.df["Source IP"] == self.client_ip) & (self.df["Destination IP"] == self.server_ip)]
        df_download = self.df[(self.df["Source IP"] == self.server_ip) & (self.df["Destination IP"] == self.client_ip)]

        if len(self.df) == 0:
            return 
        self.total_upload_bytes = df_upload["Payload Length"].sum()
        self.total_download_bytes = df_download["Payload Length"].sum()
        self.total_time = float(self.df["Timestamp"].iloc[-1] - self.df["Timestamp"].iloc[0] )+ 1e-6


        self.actual_upload_speed = self.total_upload_bytes/self.total_time
        self.actual_download_speed = self.total_download_bytes/self.total_time

        self.q_table = q_table

        # Initialize state variables
        self.upload_bytes = 0
        self.download_bytes = 0
        self.current_index = -1
        self.current_time = 0
        

        # features 
        self.current_download_speed = 0
        self.current_upload_speed = 0
        self.throughPutQueue = [1e9, 2e9, 3e9] # stores the relative differences in throughputs, adding dummy values for now (keeping std deviation super high for dummy)
        self.prevThroughPut = None  # previous throughput to update the differences
        self.prev_time = 0

        self.upload_error = None 
        self.download_error = None 
        self.time_saved = None 

        self.sent_packets = 0
        self.received_packets = 0

        self.speed_test_type = None 


    def _discretize_state(self, observation):
        state_bins = []
        for i in range(len(observation)):
            value = observation[i]
            bin_width = 1.0 / self.num_bins_list[i]
            bin_index = int(value / bin_width)
            state_bins.append(bin_index)
        return tuple(state_bins)

    def _get_observation(self):
        # Calculate observation components
        tr1 = self.throughPutQueue[0]
        tr2 = self.throughPutQueue[1]
        tr3 = self.throughPutQueue[2]
        # error_download = abs(self.current_download_speed - self.actual_download_speed)/self.actual_download_speed
        # error_upload = abs(self.current_upload_speed - self.actual_upload_speed)/self.actual_upload_speed

        # mean_squared_error = math.sqrt((math.pow(error_download, 2) + math.pow(error_upload, 2))/2)

        # Discretize observation
        observation = [min(tr1, 0.99), min(tr2, 0.99), min(tr3, 0,99)]
        discretized_observation = self._discretize_state(observation)

        return discretized_observation


    def simulate_test(self):
        done = False 
        cnt = 0
        while not done:
            self.current_index += 1
            if self.current_index >= len(self.df):
                done = True 
                break 
            
            packet = self.df.iloc[self.current_index]

            self.current_time = float(packet["Timestamp"] - self.df["Timestamp"].iloc[0])
            if packet["Source IP"] == self.client_ip and packet["Destination IP"] == self.server_ip:
                self.upload_bytes += packet["Payload Length"]
                self.sent_packets += 1
            if packet["Source IP"] == self.server_ip and packet["Destination IP"] == self.client_ip:
                self.download_bytes += packet["Payload Length"]
                self.received_packets += 1
            self.current_bytes_transferred = self.upload_bytes + self.download_bytes
            self.current_download_speed = self.download_bytes / (self.current_time + 1e-6)
            self.current_upload_speed = self.upload_bytes / (self.current_time + 1e-6)

            
            # Decide the speed test type while the agent polls for decision
            if self.current_time - self.prev_time > 0.5:
                cnt += 1
                total_time = self.current_time - self.prev_time
                self.current_throughPut = self.current_bytes_transferred/(self.current_time + 1e-6)
                self.sent_packets = 0
                self.received_packets = 0
                self.prev_time = self.current_time 

                if self.total_download_bytes > self.total_upload_bytes:
                    self.speed_test_type = "DOWNLOAD"
                else:
                    self.speed_test_type = "UPLOAD"

                # Update ThroughPutQueue
                if self.prevThroughPut != None:
                    throughputChange = abs(self.current_throughPut - self.prevThroughPut)
                    throughput_proxy = math.tanh(throughputChange/self.current_throughPut)
                    self.throughPutQueue.append(throughput_proxy)
                    self.throughPutQueue.pop(0)
                self.prevThroughPut = self.current_throughPut

                if cnt > 2:
                    state = self._get_observation()
                    state_index = tuple_to_integer(state)
                    if q_table[state_index][1]  == 0 and  q_table[state_index][0] == 0: # unexplored 
                        choices = [0, 1]; prob = [0.15, 0.85]
                        random_choice = np.random.choice(choices, p=prob)
                        if random_choice == 0:
                            done = True
                    if q_table[state_index][1] < q_table[state_index][0]:
                        done = True 
            if done:
                break
                


        if (len(self.df) ==0):
            self.time_saved = 0
            self.upload_error = 0
            self.download_error = 0
        
        self.time_saved = (self.total_time - self.current_time)/self.total_time
        self.upload_error = abs(self.actual_upload_speed - self.current_upload_speed)/self.actual_upload_speed
        self.download_error = abs(self.actual_download_speed - self.current_download_speed)/self.actual_download_speed

        

    def get_results(self):
        return self.upload_error, self.download_error, self.time_saved, self.speed_test_type
        
     

if __name__ == "__main__":
    q_table = MatrixFileIO.read_matrix("q_table.txt")
    data_directory = "/home/hemankbajaj/Desktop/Semester-8/MLNET/MLNET-Project/PCAP_DATA"
    pcap_list = readPCAP(data_directory)
    upload_error = []; download_error = []; time_saved = []; error_list = []
    tcs = 0
    for pcap in pcap_list:
        connection_df = ConnectionDF(pcap)
        L = len(connection_df.get_dataframe())
        print(L)
        if L < 10000 or L> 400000:
            print("Skipped")
            continue 
        try:
        # if True:
            test_case = TestFramework(connection_df, q_table)
            test_case.simulate_test()
            upload_error, download_error , ts , err_type = test_case.get_results()
            time_saved.append(ts)
            tcs += 1
            if err_type == "UPLOAD":
                error_list.append(upload_error)
                error = upload_error
            else:
                error_list.append(download_error)
                error = download_error
            
            print(f"STATS FOR CURRENT TEST {tcs} -> {len(connection_df.get_dataframe())} packets: \n\t{err_type} Error : {error} \n\tFraction of Time Saved :{ts}")
            print(f"AVERAGE RUNNING STATS {tcs} -> {len(connection_df.get_dataframe())} packets: \n\t Error: {np.array(error_list).mean()} \n\tFraction Of Time Saved: {np.array(time_saved).mean()}")
        except Exception as e:
            print(f"Error occurred: {e}")

