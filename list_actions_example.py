"""
List Actions Example - Demonstrates listing available actions for ARC-AGI-3 games
Based on: https://docs.arcprize.org/toolkit/list-actions
"""

from toolkit import ARCToolkit


def list_all_actions():
    """
    List all available actions in ARC-AGI-3.
    
    Actions are consistent across all games, though their specific
    behavior may vary by game.
    """
    toolkit = ARCToolkit()
    
    print("=" * 60)
    print("ARC-AGI-3 Available Actions")
    print("=" * 60)
    
    actions = toolkit.list_actions()
    
    print(f"\nTotal actions: {len(actions)}")
    print("\nDetailed Action List:")
    print("-" * 60)
    
    for action in actions:
        print(f"\nAction {action['id']}: {action['name']}")
        print(f"  Description: {action['description']}")
    
    print("\n" + "=" * 60)
    print("Action Usage Examples")
    print("=" * 60)
    
    print("\nPython (using GameAction enum):")
    print("  from arcengine import GameAction")
    print("  env.step(GameAction.ACTION1)  # Up")
    print("  env.step(GameAction.ACTION2)  # Down")
    
    print("\nPython (using integers):")
    print("  env.step(1)  # ACTION1 (up)")
    print("  env.step(2)  # ACTION2 (down)")
    
    print("\nKeyboard (WASD scheme):")
    print("  W = ACTION1 (up)")
    print("  S = ACTION2 (down)")
    print("  A = ACTION3 (left)")
    print("  D = ACTION4 (right)")
    print("  Space = ACTION5 (special)")
    print("  Mouse Click = ACTION6 (coordinate)")
    print("  CTRL/CMD+Z = ACTION7 (undo)")
    
    return actions


def list_actions_for_game(game_id: str):
    """
    List actions available for a specific game.
    
    Args:
        game_id: Game identifier (e.g., "ls20", "ft09")
    """
    toolkit = ARCToolkit()
    
    print(f"\n{'=' * 60}")
    print(f"Actions for Game: {game_id}")
    print("=" * 60)
    
    # Render the game
    env = toolkit.render_game(game_id, render_mode=None)
    
    if env:
        # Reset to get initial state
        observation, info = toolkit.reset_environment()
        
        # Get available actions from info if provided
        if 'available_actions' in info:
            available = info['available_actions']
            print(f"\nGame-specific available actions: {available}")
        else:
            print("\nAll actions available (game doesn't restrict actions)")
        
        # List all actions with game context
        actions = toolkit.list_actions(game_id)
        
        print(f"\nNote: Action behavior is game-specific for {game_id}")
        print("Consult game documentation for exact action meanings.")
    else:
        print(f"Error: Could not load game {game_id}")


def demonstrate_action_validation():
    """
    Demonstrate action validation and available actions.
    """
    toolkit = ARCToolkit()
    
    print("\n" + "=" * 60)
    print("Action Validation Example")
    print("=" * 60)
    
    # Valid actions
    valid_actions = [0, 1, 2, 3, 4, 5, 6, 7]
    print(f"\nValid action range: {valid_actions}")
    
    # Invalid actions
    invalid_actions = [-1, 8, 9, 10, 100]
    print(f"Invalid actions: {invalid_actions}")
    
    print("\nAction Name to ID Mapping:")
    action_names = ["RESET", "ACTION1", "ACTION2", "ACTION3", "ACTION4", 
                    "ACTION5", "ACTION6", "ACTION7"]
    
    for name in action_names:
        action_id = toolkit.get_action_by_name(name)
        print(f"  {name:10s} -> {action_id}")


if __name__ == "__main__":
    # List all actions
    list_all_actions()
    
    # List actions for a specific game
    list_actions_for_game("ls20")
    
    # Demonstrate action validation
    demonstrate_action_validation()

# Made with Bob
