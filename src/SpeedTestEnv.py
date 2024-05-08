import gym
import numpy as np
from constants import NUM_BINS_LIST

import math



"""
FeatureList : 
    - Relative Change in Absolute Throughput 1 (using tanh for normalization)  (Range 0-1)
    - Relative Change in Absolute Throughput 2 (using tanh for normalization)  (Range 0-1)
    - Relative Change in Absolute Throughput 3 (using tanh for normalization)  (Range 0-1)

    6 tuple represent a state -> Deci Descretization of each state element -> 10^6 total states 

Reward Function: 
    Reward =  -1*(Std Deviation in Relative changes + Std Dev in RTT + Error) , the idea is that throughput does not changes much and the error in upload and download speeds is minimal
"""


"""
Schema of Processed Data : 
    - Total Time
    - Upload Bytes
    - Download Bytes
    - Cumulative Time
"""

def weighted_average(values):
    n = len(values)
    # weights = list(range(1, n + 1))  # Generate weights from 1 to n
    weights = [i for i in range(1, n+1)]
    total_weighted_sum = sum(value * weight for value, weight in zip(values, weights))
    total_weight = sum(weights)
    return total_weighted_sum / total_weight if total_weight != 0 else 0

def capValue(x):
    if x < 0:
        return 0
    elif x > 1:
        return 1
    return x 

# TODO: Resolve upload and download packets 
class SpeedTestEnv(gym.Env):
    def __init__(self, connection, num_bins_list=NUM_BINS_LIST):
        super(SpeedTestEnv, self).__init__()
        self.connection = connection        
        self.df = self.connection.get_dataframe()

        self.total_upload_bytes = self.df["Upload Bytes"].sum()
        self.total_download_bytes = self.df["Download Bytes"].sum()
        self.total_time = self.df["Cumulative Time"].iloc[-1]

        self.actual_upload_speed = self.total_upload_bytes/self.total_time
        self.actual_download_speed = self.total_download_bytes/self.total_time

        # Environment Specifications, defining action space and distrectization of continous state space 
        self.num_bins_list = num_bins_list
        self.action_space = gym.spaces.Discrete(2)  # 0: Terminate connection, 1: Continue
        self.observation_space = gym.spaces.MultiDiscrete(NUM_BINS_LIST)  # 6 components, each with num_bins

        # Initialize state variables
        self.upload_bytes = 0
        self.download_bytes = 0
        self.current_index = -1
        self.current_time = 0
        

        # Flag to indicate if download or upload test
        self.speed_test_type = None 
        if self.total_download_bytes > self.total_upload_bytes:
            self.speed_test_type = "DOWNLOAD"
        else: 
            self.speed_test_type = "UPLOAD"

        # features 
        self.current_download_speed = 0
        self.current_upload_speed = 0
        self.throughPutQueue = [1e9, 2e9, 3e9] # stores the relative differences in throughputs, adding dummy values for now (keeping std deviation super high for dummy)
        # self.rttQueue = [1e9, 2e9, 3e9] # stores the relative differences in throughputs
        self.prevThroughPut = None  # previous throughput to update the differences
        # self.prevRTT = None

    def _discretize_state(self, observation):
        state_bins = []
        for i in range(len(observation)):
            value = observation[i]
            bin_width = 1.0 / self.num_bins_list[i]
            bin_index = int(value / bin_width)
            state_bins.append(bin_index)
        return tuple(state_bins)

    def step(self, action):
        # Execute action
        if action == 0 or self.connection.is_empty():  # Terminate connection
            done = True
        else:  # Continue connection
            done = False
            # Process next packet
            self.current_index += 1
            if self.current_index < len(self.df):
                packet_group = self.df.iloc[self.current_index]
                self.current_time = packet_group["Cumulative Time"]
                self.upload_bytes += packet_group["Upload Bytes"]
                self.download_bytes += packet_group["Download Bytes"]
                self.current_bytes_transferred = self.upload_bytes + self.download_bytes
                self.current_download_speed = self.download_bytes / (self.current_time + 1e-6)
                self.current_upload_speed = self.upload_bytes / (self.current_time + 1e-6)

                self.current_throughPut = self.current_bytes_transferred/(self.current_time + 1e-6)

                if self.prevThroughPut != None:
                    throughputChange = abs(self.current_throughPut - self.prevThroughPut)
                    throughput_proxy = math.tanh(throughputChange/self.current_throughPut)
                    self.throughPutQueue.append(throughput_proxy)
                    self.throughPutQueue.pop(0)
                self.prevThroughPut = self.current_throughPut


                throughput_reward = weighted_average(self.throughPutQueue)
                error_download = abs(self.current_download_speed - self.actual_download_speed)/self.actual_download_speed
                error_upload = abs(self.current_upload_speed - self.actual_upload_speed)/self.actual_upload_speed

                error_download_reward = math.tanh(error_download)
                error_upload_reward = math.tanh(error_upload)
                
            else:
                done = True

        # Calculate reward 
        x = self.current_index/len(self.df)
        reward = 0
        # reward =  100*math.log(-x + math.e)  # Penalty for each step, higher reward for exploration initially then the reward dies down exponentially
        if max(self.throughPutQueue) == 9: # no reward if just started state
            reward += -10
        elif done:
            reward += 2  # Reward for completing connection
        else:
            # reward for lesser error and higher accuracy
            if self.speed_test_type == "DOWNLOAD":
                reward = 1 -(5*capValue(throughput_reward) + 5*error_download_reward)/(5 + 5)
                if error_download_reward <= 0.1:
                    reward += 100
            else:
                reward = 1 -(5*capValue(throughput_reward) + 5*error_upload_reward)/(5 + 5)
                if error_upload_reward <= 0.1:
                    reward += 100

        # Get next state
        next_state = self._get_observation()
        # print("NEXT STATE -> ", next_state)
        return next_state, reward, done, {}

    def reset(self):
        # Reset environment
        self.current_index = 0
        self.current_time = 0
        self.current_bytes_transferred = 0
        self.current_download_speed = 0
        self.current_upload_speed = 0

        return self._get_observation()

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
