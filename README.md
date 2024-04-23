# Early Termination Strategy for Speed Test

```
Hemank Bajaj, 2020CS10349
Dhruv Tyagi, 2020CS10341
```

Github Link : [https://github.com/HemankBajaj/MLNET-Project](https://github.com/HemankBajaj/MLNET-Project)

## Problem Statement


## Problem Formulation
The problem at hand is to determine the optimal termination policy for conducting speed tests based on the observed states and rewards in a reinforcement learning (RL) framework. In this scenario, the RL agent aims to learn when to terminate a speed test connection to balance the need for collecting network quality information with minimizing data overhead.

## Data Preparation
Before training the RL model, the PCAP data obtained from M-Lab Speed tests needs to be preprocessed to extract relevant features for training. Currently, we are assuming that each pcap file represents an independent speed test which was executed. We assume this because the total time of the capture is typically of a single speed test and their is only 1 client and 1 server involved which further justifies are assumption. 

We have developed a script to fetch all the pcap files and extract the packet level data from the pcap file and cache it as a csv file. The idea behind saving it as a csv is that we just store the csv path in the `SpeedTestConnection` object. This allows us to load the csv only when it is required. 

The code for this can be found in `ConnectionCSV.py` and `SpeedTestConnection.py`

## RL Model Architecture
The RL model architecture consists of the following architecture:
### State Representation 
The state space represents the observed features of the speed test connection. We include a four-tuple of the following in the state:
- Fraction of time elapsed
- Fraction of data transferred
- Current Upload Speed
- Current Download Speed
Let us consdier some design considertations for our state representation:
#### Discretization of States
The initial state space of the environment is a continous space. To make the system effecient to learn we have discretized the state space and divided each part of the state tuple into 10 bins. So effectively, each value is mapped to an integer between 0 to 9. The result of this discretization is that the state space reduces to tuples like (a, b, c, d). Where a, b, c, d are integers between 0 to 9. The idea behind chosing 10 bins was that it is easier to map a tuple to an integer. For example (1, 4, 5, 0) can be directly mapped to 1450 in the Q Table.
### **Action Space**: 
The action space consists of two actions: continue the test or terminate the test. The RL agent decides which action to take based on the current state and learned policies.
### **Reward Function**: 
The reward function provides feedback to the RL agent based on its actions. 
We penalize the following: 
- Fraction of Data Transferred
- Fraction of Time Elapsed 
- Absolute Difference between actual and current upload speed
- Absolute Difference between actual and current download speed

Code for this part can be found in `QLearningAgent.py` and `SpeedTestEnvironment.py`

## Training Architecture
Once the data preparation is complete, the RL model is trained using the prepared dataset. During training, the RL agent explores different termination decisions and observes their consequences in terms of rewards. Through this exploration and exploitation process, the RL agent learns optimal termination policies that balance the trade-off between collecting network quality information and minimizing data overhead.

Code for this part can be found in `QLearningAgent.py` and `main.py`


## Inference Architecture 


## Future Scope
- Training On a Larger Dataset. Multiple workers deployed for updating different sections of the Q-Table. 
- Right now, we have an offline learning of the Q-Table. This can be extended to update the Q-Table online. This has several advantages for example, we need not train the Q-Table with extensive network conditions. Each deployment learns according to the traffic it encounters. 
