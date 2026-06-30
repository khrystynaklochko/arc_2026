"""
LLM-based Agent for ARC-AGI-3 environments
"""

import os
from typing import Any, Dict, Optional
from .base_agent import BaseAgent


class LLMAgent(BaseAgent):
    """
    An agent that uses a Large Language Model to make decisions.
    
    This agent analyzes the game state and uses an LLM to reason about
    the best action to take.
    """
    
    def __init__(self, 
                 model: str = "gpt-4",
                 api_key: Optional[str] = None,
                 name: str = "LLMAgent"):
        """
        Initialize the LLM agent.
        
        Args:
            model: LLM model to use (e.g., "gpt-4", "claude-3-opus")
            api_key: API key for the LLM service
            name: Name of the agent
        """
        super().__init__(name)
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.conversation_history = []
        
        if not self.api_key:
            print("Warning: No API key provided. Set OPENAI_API_KEY environment variable.")
    
    def select_action(self, observation: Any, info: Dict) -> int:
        """
        Use LLM to select an action based on observation.
        
        Args:
            observation: Current game state
            info: Additional information about the environment
            
        Returns:
            Action selected by the LLM
        """
        # Build prompt for LLM
        prompt = self._build_prompt(observation, info)
        
        # Get LLM response (placeholder - implement with actual LLM API)
        action = self._query_llm(prompt)
        
        return action
    
    def _build_prompt(self, observation: Any, info: Dict) -> str:
        """
        Build a prompt for the LLM based on current state.
        
        Args:
            observation: Current game state
            info: Additional information
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are playing an ARC-AGI-3 game. Analyze the current state and choose the best action.

Current Observation:
{observation}

Additional Info:
{info}

Available Actions:
- ACTION1: Move/Transform in direction 1
- ACTION2: Move/Transform in direction 2
- ACTION3: Move/Transform in direction 3
- ACTION4: Move/Transform in direction 4
- ACTION5: Special action 1
- ACTION6: Special action 2
- ACTION7: Special action 3
- ACTION8: Special action 4
- ACTION9: Submit/Confirm
- ACTION10: Reset/Undo

Based on the game state, which action should be taken? Respond with just the action number (0-9).
"""
        return prompt
    
    def _query_llm(self, prompt: str) -> int:
        """
        Query the LLM with a prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Action index (0-9)
        """
        # TODO: Implement actual LLM API call
        # For now, return a placeholder action
        print(f"[{self.name}] Would query LLM with prompt (not implemented yet)")
        print(f"Model: {self.model}")
        
        # Placeholder: return action 0
        return 0
    
    def reset(self):
        """Reset agent state for a new episode."""
        super().reset()
        self.conversation_history = []


class OpenAIAgent(LLMAgent):
    """
    Agent using OpenAI's API (GPT models).
    """
    
    def __init__(self, model: str = "gpt-4", name: str = "OpenAIAgent"):
        super().__init__(model=model, name=name)
    
    def _query_llm(self, prompt: str) -> int:
        """
        Query OpenAI API.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Action index
        """
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI agent playing ARC-AGI-3 games. Respond with only a single digit (0-9) representing the action to take."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=10
            )
            
            action_text = response.choices[0].message.content.strip()
            # Extract first digit from response
            for char in action_text:
                if char.isdigit():
                    return int(char)
            
            print(f"[{self.name}] No valid action in response: {action_text}")
            return 0
            
        except ImportError:
            print(f"[{self.name}] OpenAI package not installed. Run: pip install openai")
            return 0
        except Exception as e:
            print(f"[{self.name}] Error querying OpenAI: {e}")
            return 0


class AnthropicAgent(LLMAgent):
    """
    Agent using Anthropic's Claude API.
    """
    
    def __init__(self, model: str = "claude-3-opus-20240229", name: str = "AnthropicAgent"):
        super().__init__(model=model, name=name)
        self.api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
    
    def _query_llm(self, prompt: str) -> int:
        """
        Query Anthropic API.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Action index
        """
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": f"You are an AI agent playing ARC-AGI-3 games. Respond with only a single digit (0-9) representing the action to take.\n\n{prompt}"}
                ]
            )
            
            action_text = message.content[0].text.strip()
            # Extract first digit from response
            for char in action_text:
                if char.isdigit():
                    return int(char)
            
            print(f"[{self.name}] No valid action in response: {action_text}")
            return 0
            
        except ImportError:
            print(f"[{self.name}] Anthropic package not installed. Run: pip install anthropic")
            return 0
        except Exception as e:
            print(f"[{self.name}] Error querying Anthropic: {e}")
            return 0

# Made with Bob
