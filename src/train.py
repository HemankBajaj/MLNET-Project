from SpeedTestConnection import SpeedTestConnection
from SpeedTestEnv import SpeedTestEnv
from QLearningAgent import QLearningAgent
import os

import time 
from FileIO import MatrixFileIO


directory = "cached_csv"
files = os.listdir(directory)
csv_files = [os.path.join(directory, file) for file in files if file.endswith(".csv")]
connections_list = [SpeedTestConnection(csv) for csv in csv_files]


connection = connections_list[0]
env = SpeedTestEnv(connection)

agent = QLearningAgent(env)

# Training parameters
num_episodes = 100

start_time = time.time()
cnt = 0
for connection in connections_list:
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
    cnt += 1

    if cnt % 1000 == 0:
        print(f"Trained {cnt} CSVs for {num_episodes} episodes in Time {time.time() - start_time} seconds.")
        MatrixFileIO.write_matrix(matrix=agent.q_table, filename="q_table.txt")
        print("Q-Table Written!")

MatrixFileIO.write_matrix(matrix=agent.q_table, filename="q_table.txt")
print(agent.q_table)

cnt = 0
sum = 0
lis = []
print(agent.q_table.shape)
for i in range(len(agent.q_table)):
    for j in range(len(agent.q_table[i])):
        if agent.q_table[i][j] != 0:
            print(f" OK FOUND {i}, {j}, -> {agent.q_table[i][j]}")
            sum += agent.q_table[i][j]
            cnt += 1
    if agent.q_table[i][0] > agent.q_table[i][1]:
        lis.append(i)

print(lis)
print(len(lis))


# print(f"AVG -> , {sum/cnt}")
print(cnt)

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