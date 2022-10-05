```
Score: 5


              ⬤ ⬤ ⬤ ⬤ ⬤ ⬤                                              
      < ⬤ ⬤ ⬤             ⬤                                 
                             ⬤                                                                                                        
                                                                  
@                               
                                

    🐭
                                 
```
# Qtty trainable game *engine?*

## Introduction

This is a basic tty game *engine?* that allows you to implement any 2d game that will react on single key events. The interfaces is quite simple, you must define

- update rules for the **game** parameters
- update rules for the **grid** 
- update rules on **key** pressed events

If you want to go further there is a `TrainableGame` interface that takes care of training a `GameAgent` to play your game by defining
- update rules for each play **step** 
- **reset** rules when the game is over
- a **state** getter

## `Game` interface:


```update_game(self)```: 

- executed at every time step. Time steps are determined by the `ups`. Should contain all game time dependent behaviour. 

```update_grid(self)```:
-  executed at every time stemp. Time steps are determined by `ups`. Modifies `GameGrid` 

```on_key_press(self)```: 
- key pressed event kind of *callback*

## `TrainableGame` interface:


```play_step(self)```: 

- executed once every  `not  game_over` training step. Pretty similar to update game but it must return a tuple consisting of `(reward, game_over, current_score)`  

```reset(self)```:
- executed at every `game_over` Time steps are determined by `ups`. Modifies `GameGrid` 

```get_state(self)```: 
- represents the state you want to give the trainer to reflect environment awareness. 


## Snake

```python
def update_game(self):
    self.update_food()
    self.update_special()
    self.update_body()
    self.check_if_dead()
```


``` python 
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
```

```python
def on_key_press(self, key):
    if key in self.DIRECTION_MAP.keys():
        self.change_direction(key)
```

## Snake Agent
```python
pysnake = Snake((25, 25), 3, 3, 2, walls=False, ups=25)
pysnake.train()
pysnake.watch_agent_play()
```

 ![snakerini](https://github.com/ivanbelenky/tty_games/blob/main/static/snake_agent.gif)

```python
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
        reward = 10
        game_over = False
        return reward, game_over, self.score
    
    return 0, False, self.score
```


``` python 
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
```

```python
def get_state(self):
    ...
    
    state = [
        dir_up,
        dir_down,
        dir_left,
        dir_right,
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

```

