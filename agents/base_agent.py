from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        self.episode_count = 0
        self.total_reward = 0.0
    
    @abstractmethod
    def select_action(self, observation: Any, info: Dict) -> int:
        """Interface: Must return an integer action."""
        pass
    
    def reset(self):
        self.episode_count += 1
    
    def update(self, observation: Any, action: int, reward: float, 
               next_observation: Any, done: bool, info: Dict):
        self.total_reward += reward