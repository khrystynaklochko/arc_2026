"""
ARC-AGI-3 Environment Wrapper
Provides enhanced functionality and utilities for ARC-AGI environments
"""

import arc_agi
from typing import Any, Dict, Tuple, Optional
import numpy as np


class ARCEnvironmentWrapper:
    """
    Wrapper for ARC-AGI-3 environments providing:
    - Enhanced observation processing
    - Action validation
    - Episode tracking
    - Reward normalization
    - State history
    """
    
    def __init__(self, game_id: str, render_mode: Optional[str] = None):
        """
        Initialize the environment wrapper.
        
        Args:
            game_id: Game identifier
            render_mode: Rendering mode ("terminal", "human", or None)
        """
        self.game_id = game_id
        self.render_mode = render_mode
        self.arcade = arc_agi.Arcade()
        self.env = self.arcade.make(game_id, render_mode=render_mode)
        
        # Tracking
        self.episode_count = 0
        self.step_count = 0
        self.total_reward = 0.0
        self.episode_rewards = []
        self.state_history = []
        self.action_history = []
        
        # Current state
        self.current_observation = None
        self.current_info = None
        self.done = False
    
    def reset(self, **kwargs) -> Tuple[Any, Dict]:
        """
        Reset the environment for a new episode.
        
        Returns:
            Tuple of (observation, info)
        """
        self.episode_count += 1
        self.step_count = 0
        self.done = False
        
        # Store previous episode reward
        if self.total_reward > 0:
            self.episode_rewards.append(self.total_reward)
        self.total_reward = 0.0
        
        # Clear history
        self.state_history = []
        self.action_history = []
        
        # Reset environment
        observation, info = self.env.reset(**kwargs)
        self.current_observation = observation
        self.current_info = info
        
        # Store initial state
        self.state_history.append(observation)
        
        return observation, info
    
    def step(self, action: int) -> Tuple[Any, float, bool, bool, Dict]:
        """
        Take a step in the environment.
        
        Args:
            action: Action to take
            
        Returns:
            Tuple of (observation, reward, terminated, truncated, info)
        """
        if self.done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        
        # Validate action
        if not self.is_valid_action(action):
            print(f"Warning: Invalid action {action}")
        
        # Take step
        observation, reward, terminated, truncated, info = self.env.step(action)
        
        # Update tracking
        self.step_count += 1
        self.total_reward += reward
        self.current_observation = observation
        self.current_info = info
        self.done = terminated or truncated
        
        # Store history
        self.state_history.append(observation)
        self.action_history.append(action)
        
        return observation, reward, terminated, truncated, info
    
    def is_valid_action(self, action: int) -> bool:
        """
        Check if an action is valid.
        
        Args:
            action: Action to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Actions 0-7 are typically valid (RESET, ACTION1-7)
        return 0 <= action <= 7
    
    def get_available_actions(self) -> list:
        """
        Get list of available actions.
        
        Returns:
            List of available action IDs
        """
        # Check if info contains available actions
        if self.current_info and 'available_actions' in self.current_info:
            return self.current_info['available_actions']
        
        # Default: all actions available
        return list(range(8))
    
    def get_observation_shape(self) -> tuple:
        """
        Get the shape of observations.
        
        Returns:
            Observation shape tuple
        """
        if self.current_observation is None:
            return None
        
        if isinstance(self.current_observation, dict):
            if 'grid' in self.current_observation:
                return self.current_observation['grid'].shape
        elif isinstance(self.current_observation, np.ndarray):
            return self.current_observation.shape
        
        return None
    
    def get_episode_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the current episode.
        
        Returns:
            Dictionary of episode statistics
        """
        return {
            'episode': self.episode_count,
            'steps': self.step_count,
            'total_reward': self.total_reward,
            'done': self.done,
            'avg_reward_per_step': self.total_reward / max(1, self.step_count),
            'state_history_length': len(self.state_history),
            'action_history_length': len(self.action_history)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """
        Get all statistics across all episodes.
        
        Returns:
            Dictionary of all statistics
        """
        return {
            'total_episodes': self.episode_count,
            'current_episode_steps': self.step_count,
            'current_episode_reward': self.total_reward,
            'episode_rewards': self.episode_rewards,
            'avg_episode_reward': np.mean(self.episode_rewards) if self.episode_rewards else 0.0,
            'max_episode_reward': max(self.episode_rewards) if self.episode_rewards else 0.0,
            'min_episode_reward': min(self.episode_rewards) if self.episode_rewards else 0.0,
        }
    
    def render(self):
        """Render the environment."""
        if hasattr(self.env, 'render'):
            return self.env.render()
    
    def close(self):
        """Close the environment."""
        if hasattr(self.env, 'close'):
            self.env.close()
    
    def get_state_history(self) -> list:
        """Get the history of states in the current episode."""
        return self.state_history.copy()
    
    def get_action_history(self) -> list:
        """Get the history of actions in the current episode."""
        return self.action_history.copy()
    
    def undo_last_action(self) -> bool:
        """
        Attempt to undo the last action (if supported).
        
        Returns:
            True if successful, False otherwise
        """
        if len(self.action_history) > 0:
            # Submit ACTION7 (undo)
            try:
                observation, reward, terminated, truncated, info = self.step(7)
                return True
            except Exception as e:
                print(f"Undo failed: {e}")
                return False
        return False


# ==================== EXAMPLE USAGE ====================

def example_usage():
    """Example of using the environment wrapper."""
    
    # Create wrapped environment
    env = ARCEnvironmentWrapper("ls20", render_mode="terminal")
    
    print("=== Episode 1 ===")
    observation, info = env.reset()
    print(f"Initial observation shape: {env.get_observation_shape()}")
    print(f"Available actions: {env.get_available_actions()}")
    
    # Take some actions
    for i in range(10):
        action = 1  # ACTION1 (up)
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Step {i+1}: reward={reward:.2f}, done={terminated or truncated}")
        
        if terminated or truncated:
            break
    
    # Get episode stats
    stats = env.get_episode_stats()
    print(f"\nEpisode stats: {stats}")
    
    print("\n=== Episode 2 ===")
    observation, info = env.reset()
    
    # Take different actions
    for i in range(5):
        action = (i % 4) + 1  # Cycle through ACTION1-4
        obs, reward, terminated, truncated, info = env.step(action)
        
        if terminated or truncated:
            break
    
    # Get all stats
    all_stats = env.get_all_stats()
    print(f"\nAll stats: {all_stats}")
    
    # Close environment
    env.close()


if __name__ == "__main__":
    example_usage()

# Made with Bob
