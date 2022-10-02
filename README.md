```
Score: 5


              ⬤ ⬤ ⬤ ⬤ ⬤ ⬤                                              
      < ⬤ ⬤ ⬤             ⬤                                 
                             ⬤                                                                                                        
                                                                  
@                               
                                

    🐭
                                 
```
# `python tty game`   *`engine?`*

## `Game` interface:

### ```__init__(self, grid_wh: tuple, ups: int)```

- ### `grid_wh`: grid width height tuple 
- ### `ups`: UPDATES_PER_SECOND 

#### ```update_game(self)```: 

- #### executed at every time step. Time steps are determined by the `ups`. Should contain all game time dependent behaviour. 

#### ```update_grid(self)```:
- #### executed at every time stemp. Time steps are determined by `ups`. Modifies `GameGrid` 


#### ```on_key_press(self)```: 
- #### key pressed event kind of *callback*



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
