import asyncio
import numpy as np
import termios
import tty
import sys
import select
from abc import ABC, abstractmethod


from utils import getch


class Game(ABC):
    
    PLAY_CONDITION = False
    HEADER = ""

    @abstractmethod
    def __init__(self, grid_wh: tuple, ups: int):
        self.grid = GameGrid(*grid_wh)
        self.UPDATE_PER_SECOND = ups

    @abstractmethod
    def update_game(self):
        raise NotImplementedError

    @abstractmethod
    def update_grid(self):
        raise NotImplementedError

    @abstractmethod
    def on_key_press(self, key):
        raise NotImplementedError

    async def play(self):
        while self.PLAY_CONDITION:
            self.grid.print(self)
            self.update_game()
            await asyncio.sleep(1/self.UPDATE_PER_SECOND)

    async def key_task(self):
        while self.PLAY_CONDITION:
            loop = asyncio.get_event_loop()
            key = await loop.run_in_executor(None, getch)
            self.on_key_press(key)
            if key == 'q':
                self.PLAY_CONDITION = False
    
    async def single_thread_key_event(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())

        while self.PLAY_CONDITION:
            await asyncio.sleep(1/self.UPDATE_PER_SECOND)            
            inputready, _, _ = select.select([fd], [],[], 0.0001)
            if fd in inputready:
                key = sys.stdin.read(1)
                self.on_key_press(key)
                if key == 'q':
                    self.PLAY_CONDITION = False
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            

    async def main_loop(self):
        tasks = [self.play(), self.single_thread_key_event()]
        await asyncio.gather(*tasks)

    def __call__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main_loop())
        loop.close()


class GameGrid:
    def __init__(self, width: int = 25, height: int = 25):
        self.width = width
        self.height = height
        self.grid = np.full((height, width), ' ')        
    
    def reset_grid(self):
        self.grid = np.full((self.height, self.width), ' ')

    def print(self, game: Game) -> None:
        self.reset_grid()
        game.update_grid()
        print("\033c", end="")
        print(game.HEADER, end="")
        print('\n\r')
        game_grid = ""
        for i in range(self.width):
            for j in range(self.height):
                game_grid+=self.grid[j, i]+' '
            game_grid+='\n\r'
        print(game_grid)