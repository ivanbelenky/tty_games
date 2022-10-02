from game import Game
import numpy as np

class Snake(Game):
    DIRECTION_MAP = {
        'a': 'left',
        's': 'down',
        'd': 'right',
        'w': 'up',
        '\x1b[D': 'left',
        '\x1b[B': 'down',
        '\x1b[C': 'right',
        '\x1b[A': 'up',
    }

    UPDATE_MAP = {
        'right': (1, 0),
        'left': (-1, 0),
        'up': (0, -1),
        'down': (0, 1)
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
    
    def __init__(self, grid_wh, x0, y0, initial_length=3, ups=10):
        super().__init__(grid_wh, ups)
        if initial_length > self.grid.width:
            raise ValueError("Initial length is greater than grid width")
        
        self.direction = 'right'
        self.initialize_body(x0, y0, initial_length)
        self.eating = []
        self.to_eat = []
        self.to_eat_special = []
        self.initial_length = initial_length
        self.score = 0
        self.PLAY_CONDITION = True

    def initialize_body(self, x0, y0, initial_length):
        self.body = [(x, y0) for x in [x0-i % self.grid.width for i in range(initial_length)]][::-1]
 
    def check_if_dead(self):
        if self.body[-1] in self.body[:-1]:
            self.PLAY_CONDITION = False
    
    def update_food(self):
        if not self.to_eat:
            while True:
                x = np.random.randint(self.grid.width)
                y = np.random.randint(self.grid.height)
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
                x = np.random.randint(self.grid.width)
                y = np.random.randint(self.grid.height)
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

        self.body.append((
            (self.body[-1][0] + xx) % self.grid.width,
            (self.body[-1][1] + yy) % self.grid.height
        ))

        if self.body[-1] in self.to_eat:
            self.score += 1
            self.eating.append(self.body[-1])
            self.to_eat.pop(0)
        
        if self.body[-1] in self.to_eat_special:
            self.score += 5
            self.eating.append(self.body[-1])
            self.to_eat_special.pop(0)

    def update_header(self):
        self.HEADER = f"Score: {self.score}"

    def update_game(self):
        self.update_food()
        self.update_special()
        self.update_body()
        self.update_header()
        self.check_if_dead()
        

    def update_grid(self):
        for x,y in self.body[:-1]:

            self.grid.grid[x,y] = '⬤'

        for x,y in self.eating:
            self.grid.grid[x,y] = 'x'
            
        head_char = self.HEAD_MAP[self.direction]
        headx, heady = self.body[-1]
        self.grid.grid[headx, heady] = head_char

        for x,y in self.to_eat:
            self.grid.grid[x,y] = '@'

        if self.to_eat_special and self.special_countdown > 0:
            x,y = self.to_eat_special[0]
            self.grid.grid[x,y] = '🐭'

    def on_key_press(self, key):
        if key in self.DIRECTION_MAP.keys():
            self.change_direction(key)

    def change_direction(self, new_direction):
        if (self.direction, new_direction) not in self.PROHIBITED_NEW_DIRECTIONS:
            self.direction = self.DIRECTION_MAP[new_direction]



if __name__ == "__main__":
    pysnake = Snake((33, 33), 11, 11, ups=20)
    pysnake()