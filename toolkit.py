"""
ARC-AGI-3 Toolkit - Complete implementation of toolkit features
"""

import os
import arc_agi
from typing import List, Dict, Any, Optional
from arcengine import GameAction


class ARCToolkit:
    """
    Complete toolkit for ARC-AGI-3 operations including:
    - Game management (list, add, edit, render)
    - Action management (list, submit)
    - Scorecard management (create, get, close)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ARC toolkit.
        
        Args:
            api_key: ARC API key (defaults to ARC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ARC_API_KEY")
        self.arcade = arc_agi.Arcade()
        self.current_env = None
        self.scorecard_id = None
        
    # ==================== GAME MANAGEMENT ====================
    
    def list_games(self) -> List[Dict[str, Any]]:
        """
        List all available ARC-AGI-3 games.
        
        Returns:
            List of game info dictionaries with 'id' and 'title' keys
        """
        try:
            # Get available environments from arcade
            envs = self.arcade.available_environments
            games = [{"id": env.game_id, "title": env.title} for env in envs]
            print(f"Available games: {len(games)}")
            return games
        except Exception as e:
            print(f"Error listing games: {e}")
            return []
    
    def add_game(self, game_id: str, game_config: Dict[str, Any]) -> bool:
        """
        Add a custom game to the arcade.
        
        Args:
            game_id: Unique identifier for the game
            game_config: Game configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Custom game addition would use arcade API
            print(f"Adding game: {game_id}")
            # Implementation depends on arcade.add_game() method
            if hasattr(self.arcade, 'add_game'):
                self.arcade.add_game(game_id, game_config)
                return True
            else:
                print("Game addition not supported in current arcade version")
                return False
        except Exception as e:
            print(f"Error adding game: {e}")
            return False
    
    def edit_game(self, game_id: str, updates: Dict[str, Any]) -> bool:
        """
        Edit an existing game configuration.
        
        Args:
            game_id: Game identifier
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Editing game: {game_id}")
            if hasattr(self.arcade, 'edit_game'):
                self.arcade.edit_game(game_id, updates)
                return True
            else:
                print("Game editing not supported in current arcade version")
                return False
        except Exception as e:
            print(f"Error editing game: {e}")
            return False
    
    def render_game(self, game_id: str, render_mode: str = "terminal") -> Any:
        """
        Create and render a game environment.
        
        Args:
            game_id: Game identifier
            render_mode: Rendering mode ("terminal", "human", or None)
            
        Returns:
            Game environment
        """
        try:
            self.current_env = self.arcade.make(game_id, render_mode=render_mode)
            print(f"Rendered game: {game_id} (mode: {render_mode})")
            return self.current_env
        except Exception as e:
            print(f"Error rendering game: {e}")
            return None
    
    # ==================== ACTION MANAGEMENT ====================
    
    def list_actions(self, game_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available actions for a game.
        
        Args:
            game_id: Game identifier (uses current env if None)
            
        Returns:
            List of action dictionaries with name and description
        """
        actions = [
            {"id": 0, "name": "RESET", "description": "Initialize or restart the game/level state"},
            {"id": 1, "name": "ACTION1", "description": "Simple action - varies by game (semantically mapped to up)"},
            {"id": 2, "name": "ACTION2", "description": "Simple action - varies by game (semantically mapped to down)"},
            {"id": 3, "name": "ACTION3", "description": "Simple action - varies by game (semantically mapped to left)"},
            {"id": 4, "name": "ACTION4", "description": "Simple action - varies by game (semantically mapped to right)"},
            {"id": 5, "name": "ACTION5", "description": "Simple action - varies by game (e.g., interact, select, rotate)"},
            {"id": 6, "name": "ACTION6", "description": "Complex action requiring x,y coordinates (0-63 range)"},
            {"id": 7, "name": "ACTION7", "description": "Simple action - Undo (e.g., interact, select)"},
        ]
        
        print(f"Available actions: {len(actions)}")
        for action in actions:
            print(f"  {action['id']}: {action['name']} - {action['description']}")
        
        return actions
    
    def submit_action(self, action: int) -> tuple:
        """
        Submit an action to the current environment.
        
        Args:
            action: Action index (0-9)
            
        Returns:
            Tuple of (observation, reward, terminated, truncated, info)
        """
        if self.current_env is None:
            raise ValueError("No active environment. Call render_game() first.")
        
        try:
            result = self.current_env.step(action)
            print(f"Action {action} submitted. Reward: {result[1]}")
            return result
        except Exception as e:
            print(f"Error submitting action: {e}")
            raise
    
    # ==================== SCORECARD MANAGEMENT ====================
    
    def create_scorecard(self, name: str = "default") -> str:
        """
        Create a new scorecard for tracking performance.
        
        Args:
            name: Scorecard name
            
        Returns:
            Scorecard ID
        """
        try:
            # Scorecard creation through arcade
            if hasattr(self.arcade, 'create_scorecard'):
                self.scorecard_id = self.arcade.create_scorecard(name)
            else:
                # Fallback: use default scorecard
                self.scorecard_id = f"scorecard_{name}"
            
            print(f"Created scorecard: {self.scorecard_id}")
            return self.scorecard_id
        except Exception as e:
            print(f"Error creating scorecard: {e}")
            return None
    
    def get_scorecard(self, scorecard_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get scorecard data.
        
        Args:
            scorecard_id: Scorecard ID (uses current if None)
            
        Returns:
            Scorecard dictionary with performance metrics
        """
        try:
            scorecard = self.arcade.get_scorecard()
            print("Scorecard:")
            print(scorecard)
            return scorecard
        except Exception as e:
            print(f"Error getting scorecard: {e}")
            return {}
    
    def close_scorecard(self, scorecard_id: Optional[str] = None) -> bool:
        """
        Close and finalize a scorecard.
        
        Args:
            scorecard_id: Scorecard ID (uses current if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            sid = scorecard_id or self.scorecard_id
            if hasattr(self.arcade, 'close_scorecard'):
                self.arcade.close_scorecard(sid)
            
            print(f"Closed scorecard: {sid}")
            self.scorecard_id = None
            return True
        except Exception as e:
            print(f"Error closing scorecard: {e}")
            return False
    
    # ==================== UTILITY METHODS ====================
    
    def reset_environment(self) -> tuple:
        """
        Reset the current environment.
        
        Returns:
            Tuple of (observation, info)
        """
        if self.current_env is None:
            raise ValueError("No active environment. Call render_game() first.")
        
        return self.current_env.reset()
    
    def get_action_by_name(self, name: str) -> int:
        """
        Get action ID by name.
        
        Args:
            name: Action name (e.g., "ACTION1", "RESET")
            
        Returns:
            Action ID
        """
        action_map = {
            "RESET": 0,
            "ACTION1": 1,
            "ACTION2": 2,
            "ACTION3": 3,
            "ACTION4": 4,
            "ACTION5": 5,
            "ACTION6": 6,
            "ACTION7": 7,
        }
        return action_map.get(name.upper(), 0)


# ==================== EXAMPLE USAGE ====================

def example_usage():
    """Example of using the ARC toolkit."""
    
    # Initialize toolkit
    toolkit = ARCToolkit()
    
    # List available games
    print("\n=== Listing Games ===")
    games = toolkit.list_games()
    
    # List available actions
    print("\n=== Listing Actions ===")
    actions = toolkit.list_actions()
    
    # Create a scorecard
    print("\n=== Creating Scorecard ===")
    scorecard_id = toolkit.create_scorecard("test_run")
    
    # Render a game
    print("\n=== Rendering Game ===")
    env = toolkit.render_game("ls20", render_mode="terminal")
    
    if env:
        # Reset environment
        print("\n=== Resetting Environment ===")
        observation, info = toolkit.reset_environment()
        
        # Submit some actions
        print("\n=== Submitting Actions ===")
        for i in range(5):
            obs, reward, terminated, truncated, info = toolkit.submit_action(1)
            if terminated or truncated:
                break
        
        # Get scorecard
        print("\n=== Getting Scorecard ===")
        scorecard = toolkit.get_scorecard()
        
        # Close scorecard
        print("\n=== Closing Scorecard ===")
        toolkit.close_scorecard()


if __name__ == "__main__":
    example_usage()

# Made with Bob
