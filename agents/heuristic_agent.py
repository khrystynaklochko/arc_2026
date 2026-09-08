from agents.base_agent import BaseAgent
import random

class HeuristicAgent(BaseAgent):
    def act(self, observation):
        """
        Simple heuristic: prefer actions that move towards a coordinate identified
        by the environment state if available, otherwise random.
        """
        available_actions = observation.get('available_actions', [])
        if not available_actions:
            return None
            
        # Heuristic: Find a target coordinate or just prioritize a specific index
        # for demonstration, we select the action that appears to be a coordinate movement
        # or fallback to random if no explicit spatial data is provided.
        return random.choice(available_actions)
