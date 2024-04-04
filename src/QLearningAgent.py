import numpy as np
import random
from constants import (
    LEARNING_RATE, 
    DISCOUNT_FACTOR,
    EPS, 
    EPS_DECAY, 
    EPS_MIN
)

import numpy as np
import random
from constants import (
    LEARNING_RATE, 
    DISCOUNT_FACTOR,
    EPS, 
    EPS_DECAY, 
    EPS_MIN
)

class QLearningAgent:
    def __init__(self, env, learning_rate=LEARNING_RATE, discount_factor= DISCOUNT_FACTOR, epsilon=EPS, epsilon_decay=EPS_DECAY, epsilon_min=EPS_MIN):
        self.env = env
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table = np.zeros((10000, env.action_space.n)) # HARDCODING for now
        self.state_index_map = {}  # Dictionary to map state tuples to indices

        # Populate state index map
        index = 0
        for state in self._enumerate_states():
            if index >= self.q_table.shape[0]:
                print("Index exceeds Q-table size:", index,"STATE ", state)
            self.state_index_map[state] = index
            index += 1

        print("Q-table size:", self.q_table.shape)

    def _enumerate_states(self):
        """Generate all possible states"""
        for state in self._enumerate_states_recursive([], self.env.observation_space.nvec):
            yield tuple(state)

    def _enumerate_states_recursive(self, state_prefix, shape):
        """Recursively enumerate states"""
        if len(shape) == 0:
            yield state_prefix
        else:
            for i in range(shape[0]):
                yield from self._enumerate_states_recursive(state_prefix + [i], shape[1:])


    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return self.env.action_space.sample()  # Explore action space
        else:
            return np.argmax(self.q_table[self.state_index_map[state]])  # Exploit learned values

    def update_q_table(self, state, action, reward, next_state, done):
        state_index = self.state_index_map[state]
        next_state_index = self.state_index_map.get(next_state, None)

        
        if next_state_index is None:
            print("Next state not found in state_index_map")
            return

        state_index = self.state_index_map[state]
        if not done:
            max_next_q_value = np.max(self.q_table[self.state_index_map[next_state]])
            target = reward + self.discount_factor * max_next_q_value
        else:
            target = reward

        # Update Q-value for current state-action pair
        self.q_table[state_index, action] += self.learning_rate * (target - self.q_table[state_index, action])

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
