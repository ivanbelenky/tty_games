from game import TrainableGame
import numpy as np


class Snake(TrainableGame):
    DIRECTION_MAP = {
        'a': 'left',
        's': 'down',
        'd': 'right',
        'w': 'up',
    }

    UPDATE_MAP = {
        'right': (1, 0),
        'left': (-1, 0),
        'up': (0, -1),
        'down': (0, 1)
    }

    ACTION_MAP = {
        'left': [1, 0, 0],
        'right': [0, 1, 0],
        'none': [0, 0, 1]
    }
    
    PROHIBITED_NEW_DIRECTIONS = [
        ('right', 'a'), 
        ('left', 'd'), 
        ('up', 's'), 
        ('down', 'w')
    ]

    HEAD_MAP = {
        'left': '<',
        'right': '>',
        'up' : '^',
        'down': 'v'
    }

    MAPPING = {
            ('up', (1, 0, 0)): 'a',
            ('down', (1, 0, 0)): 'd',
            ('left', (1, 0, 0)): 's',
            ('right', (1, 0, 0)): 'w',
            ('up', (0, 1, 0)): 'd',
            ('down', (0, 1, 0)): 'a',
            ('left', (0, 1, 0)): 'w',
            ('right', (0, 1, 0)): 's',
            ('', (0, 0, 1)): 'none'
        }
        
    
    def __init__(self, grid_wh, x0, y0, initial_length=3, ups=10, special=False, walls=True):
        super().__init__(grid_wh, ups)
        if initial_length > self.grid.width:
            raise ValueError("Initial length is greater than grid width")

        self.special = special
        self.walls = walls

        self.direction = 'right'
        self.x0, self.y0 = x0, y0 
        self.initial_length = initial_length
        self.initialize_body(self.x0, self.y0, self.initial_length)

        self.eating = []
        self.to_eat = []
        if special:
            self.to_eat_special = []
        self.score = 0
        self.PLAY_CONDITION = True
        
        self.state_size = self.get_state().shape[0]
        
    def initialize_body(self, x0, y0, initial_length):
        self.body = [(x, y0) for x in [x0-i % self.grid.width for i in range(initial_length)]][::-1]
 
    def is_dead(self):
        if self.body[-1] in self.body[:-1]:
            return True
        if self.walls:
            if self.body[-1][0] < 0 or self.body[-1][0] >= self.grid.width:
                return True
            if self.body[-1][1] < 0 or self.body[-1][1] >= self.grid.height:
                return True
        return False
    
    def update_food(self):
        if not self.to_eat:
            while True:
                x = np.random.randint(0, self.grid.width)
                y = np.random.randint(0, self.grid.height)
                if (x,y) not in self.body:
                    self.to_eat = [(x,y)]
                    break
    
    def update_special(self):
        if self.to_eat_special:
            self.special_countdown -= 1 
            if self.special_countdown == 0:
                self.to_eat_special.pop(0)

        if not self.to_eat_special and (self.score % 5 == 0) and self.score:
            while True:
                x = np.random.randint(0, self.grid.width)
                y = np.random.randint(0, self.grid.height)
                if (x,y) not in self.body:
                    self.to_eat_special = [(x,y)]
                    self.special_countdown = self.UPDATE_PER_SECOND*5
                    break
            
    def update_body(self):
        if self.body[0] in self.eating:
            self.eating.pop(0)
            self.body.pop(0)
            self.body.insert(0, self.body[0])
        else:
            self.body.pop(0)

        xx, yy = self.UPDATE_MAP[self.direction]

        if self.walls:
            self.body.append((
            (self.body[-1][0] + xx),
            (self.body[-1][1] + yy) 
        ))
        else:            
            self.body.append((
                (self.body[-1][0] + xx) % self.grid.width,
                (self.body[-1][1] + yy) % self.grid.height
            ))

        if self.body[-1] in self.to_eat:
            self.score += 1
            self.eating.append(self.body[-1])
            self.to_eat.pop(0)
        
        if self.special:
            if self.body[-1] in self.to_eat_special:
                self.score += 5
                self.eating.append(self.body[-1])
                self.to_eat_special.pop(0)

    def update_header(self):
        self.HEADER = f"Score: {self.score}"

    def update_game(self):
        self.update_food()
        if self.special:
            self.update_special()
        self.update_body()
        self.update_header()
        if self.is_dead():
            self.PLAY_CONDITION = False
        
    def update_grid(self):
        for x,y in self.body[:-1]:

            self.grid.grid[y,x] = '⬤'

        for x,y in self.eating:
            self.grid.grid[y,x] = 'x'
            
        head_char = self.HEAD_MAP[self.direction]
        headx, heady = self.body[-1]
        self.grid.grid[heady, headx] = head_char

        for x,y in self.to_eat:
            self.grid.grid[y,x] = '@'

        if self.special:
            if self.to_eat_special and self.special_countdown > 0:
                x,y = self.to_eat_special[0]
                self.grid.grid[y,x] = '🐭'

    def on_key_press(self, key):
        if key in self.DIRECTION_MAP.keys():
            self.change_direction(key)

    def change_direction(self, new_direction):
        if (self.direction, new_direction) not in self.PROHIBITED_NEW_DIRECTIONS:
            self.direction = self.DIRECTION_MAP[new_direction]

    def get_state(self):
        dir_u = self.direction == 'up'
        dir_d = self.direction == 'down'
        dir_l = self.direction == 'left'
        dir_r = self.direction == 'right'

        if self.to_eat:
            food_up = self.body[-1][1] > self.to_eat[0][1]
            food_down = self.body[-1][1] < self.to_eat[0][1]
            food_left = self.body[-1][0] > self.to_eat[0][0]
            food_right = self.body[-1][0] < self.to_eat[0][0]
        else:
            food_up = food_down = food_left = food_right = False
        
        head_x, head_y = self.body[-1]

        danger_up = (head_x, (head_y - 1) % self.grid.height) in self.body
        danger_down = (head_x, (head_y + 1) % self.grid.height) in self.body
        danger_left = ((head_x - 1) % self.grid.width, head_y) in self.body
        danger_right = ((head_x + 1) % self.grid.width, head_y) in self.body
        
        state = [
            dir_u,
            dir_d,
            dir_l,
            dir_r,
            food_up,
            food_down,
            food_left,
            food_right,
            danger_up,
            danger_down,
            danger_left,
            danger_right
        ]

        return np.array(state, dtype=int)

    def reset(self, train=False):
        if train:
            self.initial_length = np.random.randint(3, self.grid.width)
            if self.walls and self.initial_length > 4:
                self.initial_length //= 2
        self.initialize_body(self.x0, self.y0, self.initial_length)
        self.direction = 'right'
        self.eating = []
        self.to_eat = []
        self.score = 0
        self.PLAY_CONDITION = True
        
    def play_step(self, action):
        self.on_key_press(self.map_action(action))
        score_before = self.score
        self.update_game()
        score_after = self.score

        if self.PLAY_CONDITION == False:
            reward = -10
            game_over = True
            return reward, game_over, self.score
        elif score_after > score_before:
            reward = 30
            game_over = False
            return reward, game_over, self.score
        
        return -0.01, False, self.score
        
    def map_action(self, action):
        return self.MAPPING.get((self.direction, tuple(action)), None)


if __name__ == "__main__":
    pysnake = Snake((25, 25), 3, 3, 2, walls=True, ups=15)
    pysnake.train(model_filename='neg_reward.pth', watch_training=False, plot=True)
    