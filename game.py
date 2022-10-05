import asyncio
import numpy as np
import termios
import tty
import sys
import select
import time
from typing import Dict, List, Tuple
from abc import ABC, abstractmethod

from agent import GameAgent

from utils import getch, plot_progress


class Game(ABC):
    
    PLAY_CONDITION = False
    HEADER = ""

    @abstractmethod
    def __init__(self, grid_wh: Tuple[int, int], ups: int):
        width, height = grid_wh
        self.grid = GameGrid(width=width, height=height)
        self.UPDATE_PER_SECOND = ups

    @abstractmethod
    def update_game(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_grid(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_key_press(self, key: str) -> None:
        raise NotImplementedError

    async def play(self):
        while self.PLAY_CONDITION:
            self.grid.print(self)
            self.update_game()
            await asyncio.sleep(1/self.UPDATE_PER_SECOND)

    async def key_task(self) -> None:
        while self.PLAY_CONDITION:
            loop = asyncio.get_event_loop()
            key = await loop.run_in_executor(None, getch)
            self.on_key_press(key)
            if key == 'q':
                self.PLAY_CONDITION = False
    
    async def single_thread_key_event(self) -> None:
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
            
    async def main_loop(self) -> None:
        tasks = [self.play(), self.single_thread_key_event()]
        await asyncio.gather(*tasks)

    def __call__(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main_loop())
        loop.close()


class TrainableGame(Game):

    @abstractmethod
    def __init__(self, grid_wh: Tuple[int,int], ups: int = 15):
        super().__init__(grid_wh, ups)

    @abstractmethod
    def play_step(self, action: List[int]) -> Tuple[float, bool, float]:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> np.ndarray:
        raise NotImplementedError
    
    @abstractmethod
    def reset(self, train: bool = False) -> None:
        raise NotImplementedError

    def set_map_actions(self) -> None:
        action_size = len(self.ACTION_MAP) 
        action_matrix = np.identity(action_size, dtype=int)

        map_actions = [[list(k),v] for k,v in zip(action_matrix, self.ACTION_MAP.keys())]    
        
        self.action_space = [ma[0] for ma in map_actions]
        self.map_actions = map_actions
        self.action_size = action_size

    def map_action(self, action: List[int]) -> str:
        for k,v in self.map_actions:
            if np.array_equal(action, k):
                return v
        return 'none'

    def train(
        self, 
        watch_training: bool = True, 
        watching_speed: float = None,
        plot: bool = False, 
        max_games: int = 10_000,
        max_steps: int = None, 
        model_filename: str = 'model.pth',
        train_params: Dict[str,str] = {} 
        ) -> None:

        game = self
        game.set_map_actions()
        agent = GameAgent(game, **train_params)

        if max_steps == None:
            max_steps = np.inf

        if max_games == None:
            max_games = np.inf

        time_sleep = 1/watching_speed if watching_speed else 1/game.UPDATE_PER_SECOND

        scores = []
        mean_scores = []
        total_score = 0
        record = 0
        
        step_counter = 0
        game_counter = 0
        while True and game_counter < max_games:
            old_state = agent.get_state()
            action = agent.get_action(old_state)
            
            if watch_training:
                game.grid.print(game)
                time.sleep(time_sleep)
            
            reward, game_over, score = game.play_step(action)
            
            new_state = agent.get_state()
            agent.train_short_memory(old_state, action, reward, new_state, game_over)
            agent.remember(old_state, action, reward, new_state, game_over)

            step_counter += 1

            if game_over or step_counter >= max_steps:
                game.reset(train=True)
                agent.n_games += 1
                agent.train_long_memory()

                if score > record:
                    record = score
                    agent.model.save(model_filename)

                scores.append(score)
                total_score += score
                mean_score = total_score / agent.n_games
                mean_scores.append(mean_score)
                
                if plot:
                    plot_progress(scores, mean_scores)
                else:
                    print('Game', agent.n_games, 'Score', score, 'Record:', record, 'Mean Score:', mean_score)
                
                game_counter += 1
                step_counter = 0
    
    def watch_agent_play(
        self, 
        max_games: int = 30, 
        forever: bool = True, 
        model_path: str = 'model/model.pth', 
        watching_speed: int = None
        ) -> None:
        
        game = self
        game.set_map_actions()
        agent = GameAgent(game)
        agent.load(model_path)

        sleep_time = 1/watching_speed if watching_speed else 1/game.UPDATE_PER_SECOND

        game_counter = 0
        while True:
            old_state = agent.get_state()
            action = agent.get_action(old_state)
            game.grid.print(game)
            time.sleep(sleep_time)
            reward, game_over, score = game.play_step(action)
            if game_over: 
                if not forever and game_counter < max_games:
                    break
                game.reset()
    

class GameGrid:
    def __init__(self, width: int = 25, height: int = 25):
        self.width = width
        self.height = height
        self.grid = np.full((height, width), ' ')        
    
    def reset_grid(self) -> None:
        self.grid = np.full((self.height, self.width), ' ')

    def print(self, game: Game) -> None:
        self.reset_grid()
        game.update_grid()
        
        print("\033c", end="")
        
        print(game.HEADER, end="")
        print('\n\r')
        
        game_grid = ""
        game_grid += '  ' + "# "*self.width + '\n\r'
        for j in range(self.height):
            game_grid += '# '
            for i in range(self.width):
                game_grid+=self.grid[j, i]+' '
            game_grid+='#\n\r'
        game_grid += '  ' + "# "*self.width + '\n\r'

        print(game_grid)