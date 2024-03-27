from SpeedTestConnection import SpeedTestConnection
from SpeedTestEnv import SpeedTestEnv
from QLearningAgent import QLearningAgent
import os


directory = "cached_csv"
files = os.listdir(directory)
csv_files = [os.path.join(directory, file) for file in files if file.endswith(".csv")]
connections_list = [SpeedTestConnection(csv) for csv in csv_files]


connection = connections_list[0]
env = SpeedTestEnv(connection)

agent = QLearningAgent(env)

# Training parameters
num_episodes = 1000

# Training loop
for episode in range(num_episodes):
    state = env.reset()
    total_reward = 0
    done = False

    while not done:
        action = agent.choose_action(state)
        next_state, reward, done, _ = env.step(action)
        agent.update_q_table(state, action, reward, next_state, done)
        state = next_state
        total_reward += reward

    agent.decay_epsilon()
    print(f"Episode {episode + 1}/{num_episodes}, Total Reward: {total_reward}")

# state = env.reset()
# done = False
# while not done:
#     action = agent.choose_action(state)
#     state, reward, done, _ = env.step(action)


"""
TODO: 
1) Modify the code to train on multiple connection instances
2) Fetch files from cached csvs  (OK)
3) Connection MetaData and updating in env
4) Develop Testing Framework? 
5) Fix the hardcoding state space issue (Hardcoded for now)
"""