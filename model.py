import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class DQN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc3(x)
        return x
    
    def save(self, file_name='model.pth'):
        model_folder = './model'
        if not os.path.exists(model_folder):
            os.makedirs(model_folder)
        file_name = os.path.join(model_folder, file_name)
        torch.save(self.state_dict(), file_name)


class DQNTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.loss_fn = nn.MSELoss()

    def train_step(self, states, actions, rewards, next_states, game_overs):
        
        if not isinstance(states, tuple):
            states = torch.tensor(states, dtype=torch.float)
            next_states = torch.tensor(next_states, dtype=torch.float)
            actions = torch.tensor(actions, dtype=torch.long)
            rewards = torch.tensor(rewards, dtype=torch.float)

            states = torch.unsqueeze(states, 0)
            next_states = torch.unsqueeze(next_states, 0)
            actions = torch.unsqueeze(actions, 0)
            rewards = torch.unsqueeze(rewards, 0)
            game_overs = (game_overs,)
        
        else:
            states = torch.stack([torch.tensor(state, dtype=torch.float) for state in states])
            next_states = torch.stack([torch.tensor(n_state, dtype=torch.float) for n_state in next_states])
            actions = torch.stack([torch.tensor(action, dtype=torch.long) for action in actions])
            rewards = torch.stack([torch.tensor(reward, dtype=torch.float) for reward in rewards])
            
        pred = self.model(states)
        target = pred.clone()
        for idx in range(len(game_overs)):
            Q_new = rewards[idx]
            if not game_overs[idx]:
                Q_new = rewards[idx] + self.gamma * torch.max(self.model(next_states[idx]))
            target[idx][torch.argmax(actions[idx]).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.loss_fn(target, pred)
        loss.backward()
        self.optimizer.step()