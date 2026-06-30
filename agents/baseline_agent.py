"""
Baseline Agent - Uses provided baseline actions to win games
"""
from typing import Any, Dict
import numpy as np
from agents.base_agent import BaseAgent


class BaselineAgent(BaseAgent):
    """Agent that uses baseline actions from game metadata"""
    
    def __init__(self):
        super().__init__()
        self.baseline_actions = []
        self.action_index = 0
        
    def reset(self):
        """Reset agent state"""
        self.action_index = 0
        
    def select_action(self, observation: Any, info: Dict[str, Any]) -> int:
        """Select next baseline action"""
        # Get baseline actions from observation if available
        if hasattr(observation, 'baseline_actions') and self.action_index == 0:
            self.baseline_actions = observation.baseline_actions
            
        # Return next baseline action
        if self.action_index < len(self.baseline_actions):
            action = self.baseline_actions[self.action_index]
            self.action_index += 1
            return action
        
        # If we run out of baseline actions, return 0
        return 0

# Made with Bob
