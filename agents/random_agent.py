"""
Random Agent for ARC-AGI-3 environments
"""

import random
from typing import Any, Dict
from .base_agent import BaseAgent


class RandomAgent(BaseAgent):
    """
    A simple agent that selects random actions.
    
    Useful as a baseline for comparing more sophisticated agents.
    """
    
    def __init__(self, num_actions: int = 10, name: str = "RandomAgent"):
        """
        Initialize the random agent.
        
        Args:
            num_actions: Number of possible actions
            name: Name of the agent
        """
        super().__init__(name)
        self.num_actions = num_actions
    
    def select_action(self, observation: Any, info: Dict) -> int:
        """
        Select a random action.
        
        Args:
            observation: Current game state (unused for random agent)
            info: Additional information (unused for random agent)
            
        Returns:
            Random action index
        """
        return random.randint(0, self.num_actions - 1)

# Made with Bob
