import random
import time
from collections import deque

import torch 
import matplotlib.pyplot as plt

from model import DQN, DQNTrainer

plt.style.use("dark_background")

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
GAMMA = 0.9
EPS = 0.05
MAX_EPS_GAMES = 1000

class GameAgent:
    def __init__(
        self, 
        game,
        hidden_size=256,
        eps=EPS, 
        gamma=GAMMA, 
        lr=LR, 
        max_memory=MAX_MEMORY, 
        batch_size=BATCH_SIZE,
        max_eps_games=MAX_EPS_GAMES):

        self.game = game
        self.n_games = 0
        self.memory = deque(maxlen=MAX_MEMORY)

        self.model = DQN(self.game.state_size, hidden_size, self.game.action_size)
        self.trainer = DQNTrainer(self.model, lr, gamma)
        
        self.eps = eps
        self.max_memory = max_memory
        self.batch_size = batch_size
        self.max_eps_games = max_eps_games


    def get_state(self):
        return torch.tensor(self.game.get_state(), dtype=torch.float)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        if len(self.memory) > self.batch_size:
            mini_sample = random.sample(self.memory, self.batch_size)
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        final_move = [0]*self.game.action_size
        if random.random() < self.eps*(self.max_eps_games-self.n_games)/self.max_eps_games:
            final_move = random.choice(self.game.action_space)
        else:
            idx = self.model(state).argmax().item()
            final_move[idx] = 1

        return final_move

    def save(self, path):
        torch.save(self.model.state_dict(), path)

    def load(self, path):
        self.model.load_state_dict(torch.load(path))
