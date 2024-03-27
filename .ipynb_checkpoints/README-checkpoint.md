# Early Termination Strategy for Speed Test
# Project Proposal

```
Hemank Bajaj, 2020CS10349
Dhruv Tyagi, 2020CS10341
```

## Goals and Objectives

1. Develop an early termination strategy for speed tests to optimize the trade-off between data overhead and information about network quality.
2. Formulate the problem of test termination as a reinforcement learning (RL) problem to enable intelligent decision-making.
3. Train the RL model using PCAP data from M-Lab Speed tests to learn effective termination policies.
4. Evaluate the proposed solution to quantify data savings achieved versus information loss incurred.


## Solution Sketch

The proposed solution involves developing an intelligent early termination strategy for speed tests using reinforcement learning. Here's a sketch of the solution:

1. **Problem Formulation**: Define the problem of test termination as a reinforcement learning problem, with the agent (RL model) learning when to terminate the speed test based on observed states and rewards.

2. **RL Model Architecture**: Design the architecture of the RL model, including the state representation, action space (terminate or continue the test), and the reward function. Considerations will be made to balance the need for network quality information with minimizing data overhead.

3. **Data Preparation**: Preprocess the PCAP data obtained from M-Lab Speed tests to extract relevant features for training the RL model. Features may include network throughput, latency, packet loss rates, and test duration.

4. **Training**: Train the RL model using the prepared dataset. The model will learn optimal termination policies by exploring different termination decisions and observing their consequences in terms of rewards.

5. **Evaluation**: Evaluate the trained RL model on separate validation datasets to assess its performance in terms of data savings achieved and information loss incurred. Metrics such as cumulative rewards, data usage, and network quality metrics will be used for evaluation.

6. **Refinement**: Refine the termination strategy based on the evaluation results and feedback. Adjustments may include tweaking the reward function, exploring different state representations, or fine-tuning hyperparameters of the RL model.

## Major Milestones and Timeline
Here is our 8 week action plan for this project:
1. **Problem Formulation and Model Design** (Week 1, 2):
   - Define the problem statement and key metrics.
   - Design the architecture of the RL model, including the state space, action space, and reward function.

2. **Data Preparation** (Week 3):
   - Preprocess the PCAP data to extract relevant features.
   - Split the dataset into training and validation sets.

3. **Model Implementation and Training** (Week 4, 5):
   - Implement the RL algorithm for early termination.
   - Train the RL model using the prepared dataset.
   - Fine-tune the model based on initial training results.

4. **Evaluation and Analysis** (Week 5, 6):
   - Evaluate the trained model on validation datasets.
   - Analyze the trade-off between data savings and information loss.
   - Identify areas for improvement and refinement.

5. **Refinement and Finalization** (Week 7, 8):
   - Refine the termination strategy based on evaluation results.
   - Finalize the solution and document the findings.
   - Prepare the project report and presentation.


