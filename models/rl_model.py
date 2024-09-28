import random
import numpy as np

class RLModel:
    
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.2):
        self.q_table = {}  
        self.actions = actions  
        self.learning_rate = learning_rate 
        self.discount_factor = discount_factor  
        self.exploration_rate = exploration_rate  
    
    def get_state(self, user_profile, report_details):
        state = (user_profile['confidence_score'], report_details['severity'])
        return state
    
    def choose_action(self, state):
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(self.actions)  
        else:
            return self.get_best_action(state)  
    
    def get_best_action(self, state):
        if state not in self.q_table:
            return random.choice(self.actions)  
        return max(self.q_table[state], key=self.q_table[state].get)
    
    def update_q_table(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {action: 0 for action in self.actions}
        
        current_q_value = self.q_table[state][action]
        
        future_q_value = max(self.q_table[next_state].values()) if next_state in self.q_table else 0
        
        new_q_value = current_q_value + self.learning_rate * (reward + self.discount_factor * future_q_value - current_q_value)
        
        self.q_table[state][action] = new_q_value
    
    def get_reward(self, user_profile, report_details, is_real_report):
        if is_real_report:
            reward = 1  
        else:
            reward = -1  
        
        if report_details['severity'] == 'high':
            reward *= 2  
        elif report_details['severity'] == 'low':
            reward *= 0.5
        
        return reward
