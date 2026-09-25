"""
This module provides the RandomAgent class, a simple baseline agent for ARC-AGI-3 environments
that selects actions uniformly at random from the available action space.
"""

import random
from typing import Any, Dict
from .base_agent import BaseAgent

DEFAULT_NUM_ACTIONS: int = 10
DEFAULT_AGENT_NAME: str = "RandomAgent"
MIN_ACTION_INDEX: int = 0


class RandomAgent(BaseAgent):
    """
    A simple agent that selects random actions.

    Useful as a baseline for comparing more sophisticated agents.
    """

    def __init__(self, num_actions: int = DEFAULT_NUM_ACTIONS, name: str = DEFAULT_AGENT_NAME) -> None:
        """
        Initialize the random agent.

        Args:
            num_actions: Number of possible actions.
            name: Name of the agent.
        """
        super().__init__(name)
        self.num_actions = num_actions

    def select_action(self, observation: Any, info: Dict[str, Any]) -> int:
        """
        Select a random action.

        Args:
            observation: Current game state (unused for random agent).
            info: Additional information (unused for random agent).

        Returns:
            Random action index between 0 and num_actions - 1.
        """
        return random.randint(MIN_ACTION_INDEX, self.num_actions - 1)
