"""
Baseline Agent - Uses random valid actions with fallback handling
"""
from typing import Any, Dict
import numpy as np
import random
from agents.base_agent import BaseAgent

from arcengine import GameAction


class BaselineAgent(BaseAgent):
    """Agent that uses random valid GameAction enums"""
    
    def __init__(self):
        super().__init__()
        # Available GameAction enums (ACTION1-7, RESET)
        self.valid_actions = [
            GameAction.ACTION1,
            GameAction.ACTION2,
            GameAction.ACTION3,
            GameAction.ACTION4,
            GameAction.ACTION5,
            GameAction.ACTION6,
            GameAction.ACTION7,
        ]
        
    def reset(self):
        """Reset agent state"""
        pass
        
    def select_action(self, observation: Any, info: Dict[str, Any]):
        """
        Select a random valid action.
        Returns GameAction enum to avoid the 'int' object has no attribute 'name' error.
        """
        # Get available actions from info if provided
        available_actions = info.get('available_actions', None)
        
        # If available_actions is provided and is a list of GameAction enums, use them
        if available_actions and len(available_actions) > 0:
            # Return a GameAction enum directly
            return random.choice(available_actions)
        
        # Otherwise, return a random GameAction enum from our valid list
        return random.choice(self.valid_actions)

# Made with Bob
