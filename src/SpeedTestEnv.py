import gym
import numpy as np
from constants import NUM_BINS

import math

# TODO: Resolve upload and download packets 
class SpeedTestEnv(gym.Env):
    def __init__(self, connection, num_bins=NUM_BINS):
        super(SpeedTestEnv, self).__init__()
        self.connection = connection
        self.df = self.connection.get_dataframe()

        self.upload_bytes = 0
        self.download_bytes = 0

        self.total_bytes = self.df['Payload Length'].sum()
        self.total_time = self.df.iloc[-1]['Timestamp']  #end time
        self.num_bins = num_bins

        # Define action space
        self.action_space = gym.spaces.Discrete(2)  # 0: Terminate connection, 1: Continue

        # Discretize continuous state space
        self.observation_space = gym.spaces.MultiDiscrete([num_bins] * 4)  # Four components, each with num_bins

        # Initialize state variables
        self.current_index = 0
        self.current_time = self.df.iloc[self.current_index]['Timestamp']
        self.current_bytes_transferred = 0
        self.current_download_speed = 0
        self.current_upload_speed = 0

        df_upload = self.df[self.df["Source IP"] == self.connection.client]

        df_download = self.df[self.df["Destination IP"] == self.connection.client]

        self.actual_upload_speed = df_upload['Payload Length'].sum() / (self.total_time - df_upload.iloc[0]['Timestamp'] + 1e-6)
        self.actual_download_speed = df_download['Payload Length'].sum() / (self.total_time - df_download.iloc[0]['Timestamp'] + 1e-6)
        

    def _discretize_state(self, observation):
        state_bins = []
        for i in range(len(observation)):
            value = observation[i]
            bin_width = 1.0 / self.num_bins
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
                packet = self.df.iloc[self.current_index]
                self.current_time = packet['Timestamp']
                self.current_bytes_transferred += packet['Payload Length']
                time_elapsed = (self.current_time - self.df.iloc[0]['Timestamp'])
                self.current_download_speed = self.current_bytes_transferred / (self.total_bytes * time_elapsed)

                if packet["Source IP"] == self.connection.client:
                    self.upload_bytes += packet['Payload Length']
                else:
                    self.download_bytes += packet['Payload Length']
                
                self.current_download_speed = (self.download_bytes/time_elapsed)
                self.current_upload_speed_speed = (self.upload_bytes/time_elapsed)

                download_speed_reward = abs(self.current_download_speed - self.actual_download_speed) 
                upload_speed_reward = abs(self.current_upload_speed - self.actual_upload_speed) 

                normalized_upload_reward = upload_speed_reward/(self.actual_upload_speed + 1e-6)
                normalized_download_reward = download_speed_reward/(self.actual_download_speed + 1e-6)
                normalized_time_reward = time_elapsed / (self.total_time - self.df.iloc[0]['Timestamp'] + 1e-6)
                normalized_data_reward = self.current_bytes_transferred/self.total_bytes

            else:
                done = True

        # Calculate reward 
        x = self.current_index/len(self.df)
        reward =  100*math.log(-x + math.e)  # Penalty for each step, higher reward for exploration initially then the reward dies down exponentially
        if done:
            reward += 1  # Reward for completing connection
        else:
            reward = -(normalized_download_reward + normalized_upload_reward + normalized_time_reward + normalized_data_reward)
        

        # Get next state
        next_state = self._get_observation()

        return next_state, reward, done, {}

    def reset(self):
        # Reset environment
        self.current_index = 0
        self.current_time = self.df.iloc[self.current_index]['Timestamp']
        self.current_bytes_transferred = 0
        self.current_download_speed = 0
        self.current_upload_speed = 0

        return self._get_observation()

    def _get_observation(self):
        # Calculate observation components
        bytes_transferred = self.current_bytes_transferred / self.total_bytes
        time_elapsed_normalized = (self.current_time - self.df.iloc[0]['Timestamp']) / (self.total_time - self.df.iloc[0]['Timestamp'] + 1e-6)

        # Discretize observation
        download_state = min(self.current_download_speed/self.actual_download_speed, 0.99)
        upload_state = min(self.current_upload_speed/self.actual_upload_speed, 0.99)
        observation = [bytes_transferred, download_state ,upload_state , time_elapsed_normalized]

        discretized_observation = self._discretize_state(observation)

        return discretized_observation
