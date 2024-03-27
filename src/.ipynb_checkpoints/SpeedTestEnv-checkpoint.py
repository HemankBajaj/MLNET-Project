import gym
import numpy as np

class SpeedTestEnv(gym.Env):
    def __init__(self, connection):
        super(SpeedTestEnv, self).__init__()
        self.connection = connection
        self.df = self.connection.get_dataframe()
        self.total_bytes = self.df['Payload Length'].sum()
        self.current_index = 0
        self.current_time = self.df.iloc[self.current_index]['Timestamp']
        self.total_time = self.df.iloc[-1]['Timestamp']
        self.current_upload_speed = 0  
        self.current_download_speed = 0  
        self.current_bytes_transferred = 0

        # Define action and observation space
        self.action_space = gym.spaces.Discrete(2)  # 0: Terminate connection, 1: Continue
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)  

    def step(self, action):
        # Step function implementation

    def reset(self):
        # Reset function implementation

if __name__ == "__main__":
    print("env")