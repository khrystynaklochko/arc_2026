"""
Base Agent class for ARC-AGI-3 environments
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import numpy as np


class BaseAgent(ABC):
    """
    Abstract base class for ARC-AGI-3 agents.
    
    All agents should inherit from this class and implement the required methods.
    """
    
    def __init__(self, name: str = "BaseAgent"):
        """
        Initialize the agent.
        
        Args:
            name: Name of the agent
        """
        self.name = name
        self.episode_count = 0
        self.total_reward = 0.0
        self.memory: list = []
    
    @abstractmethod
    def select_action(self, observation: Any, info: Dict) -> int:
        """
        Select an action based on the current observation.
        
        Args:
            observation: Current game state/observation
            info: Additional information about the environment
            
        Returns:
            Action to take (integer)
        """
        pass
    
    def reset(self):
        """Reset agent state for a new episode."""
        self.episode_count += 1
        self.memory = []
    
    def update(self, observation: Any, action: int, reward: float, 
               next_observation: Any, done: bool, info: Dict):
        """
        Update agent after taking an action.
        
        Args:
            observation: Previous observation
            action: Action taken
            reward: Reward received
            next_observation: New observation after action
            done: Whether episode is complete
            info: Additional information
        """
        self.total_reward += reward
        self.memory.append({
            'observation': observation,
            'action': action,
            'reward': reward,
            'next_observation': next_observation,
            'done': done,
            'info': info
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics.
        
        Returns:
            Dictionary of agent statistics
        """
        return {
            'name': self.name,
            'episodes': self.episode_count,
            'total_reward': self.total_reward,
            'avg_reward': self.total_reward / max(1, self.episode_count),
            'memory_size': len(self.memory)
        }
    
    def save(self, filepath: str):
        """Save agent state to file."""
        raise NotImplementedError("Save method not implemented")
    
    def load(self, filepath: str):
        """Load agent state from file."""
        raise NotImplementedError("Load method not implemented")

# Made with Bob
