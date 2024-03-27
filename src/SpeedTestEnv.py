import gym
import numpy as np
from constants import NUM_BINS

# TODO: Resolve upload and download packets 
class SpeedTestEnv(gym.Env):
    def __init__(self, connection, num_bins=NUM_BINS):
        super(SpeedTestEnv, self).__init__()
        self.connection = connection
        self.df = self.connection.get_dataframe()
        self.total_bytes = self.df['Payload Length'].sum()
        self.total_time = self.df.iloc[-1]['Timestamp']
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
        if action == 0:  # Terminate connection
            done = True
        else:  # Continue connection
            done = False
            # Process next packet
            self.current_index += 1
            if self.current_index < len(self.df):
                packet = self.df.iloc[self.current_index]
                self.current_time = packet['Timestamp']
                self.current_bytes_transferred += packet['Payload Length']
                time_elapsed = (self.current_time - self.df.iloc[0]['Timestamp']) / (self.total_time - self.df.iloc[0]['Timestamp'])
                self.current_download_speed = self.current_bytes_transferred / (self.total_bytes * time_elapsed)
                self.current_upload_speed = self.current_download_speed  # Example, modify as per requirements
            else:
                done = True

        # Calculate reward (example)
        reward = -0.1  # Penalty for each step
        if done:
            reward += 1  # Reward for completing connection

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
        time_elapsed = (self.current_time - self.df.iloc[0]['Timestamp']) / (self.total_time - self.df.iloc[0]['Timestamp'])

        # Discretize observation
        observation = [bytes_transferred, self.current_download_speed, self.current_upload_speed, time_elapsed]
        discretized_observation = self._discretize_state(observation)

        return discretized_observation
