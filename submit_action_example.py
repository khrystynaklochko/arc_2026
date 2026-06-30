"""
Submit Action Example - Demonstrates submitting actions to ARC-AGI-3 games
Based on: https://docs.arcprize.org/toolkit/submit-action
"""

from toolkit import ARCToolkit
from arcengine import GameAction
import time


def basic_action_submission():
    """
    Basic example of submitting actions to a game.
    """
    toolkit = ARCToolkit()
    
    print("=" * 60)
    print("Basic Action Submission Example")
    print("=" * 60)
    
    # Render game
    print("\n1. Rendering game 'ls20'...")
    env = toolkit.render_game("ls20", render_mode="terminal")
    
    if not env:
        print("Error: Could not render game")
        return
    
    # Reset environment
    print("\n2. Resetting environment...")
    observation, info = toolkit.reset_environment()
    print(f"   Initial state received")
    
    # Submit actions
    print("\n3. Submitting actions...")
    actions_to_try = [1, 2, 3, 4, 5]  # ACTION1-5
    
    for i, action in enumerate(actions_to_try):
        print(f"\n   Step {i+1}: Submitting action {action}")
        
        try:
            obs, reward, terminated, truncated, info = toolkit.submit_action(action)
            print(f"   Result: reward={reward:.2f}, done={terminated or truncated}")
            
            if terminated or truncated:
                print("   Episode ended!")
                break
                
        except Exception as e:
            print(f"   Error: {e}")
            break
    
    print("\n" + "=" * 60)


def action_submission_with_validation():
    """
    Submit actions with validation and error handling.
    """
    toolkit = ARCToolkit()
    
    print("\n" + "=" * 60)
    print("Action Submission with Validation")
    print("=" * 60)
    
    # Setup
    env = toolkit.render_game("ls20", render_mode=None)
    if not env:
        return
    
    observation, info = toolkit.reset_environment()
    
    # Get available actions
    available_actions = info.get('available_actions', list(range(8)))
    print(f"\nAvailable actions: {available_actions}")
    
    # Try valid and invalid actions
    test_actions = [1, 2, 99, -1, 5]  # Mix of valid and invalid
    
    for action in test_actions:
        print(f"\nTrying action {action}...")
        
        # Validate before submitting
        if action in available_actions or not available_actions:
            try:
                obs, reward, terminated, truncated, info = toolkit.submit_action(action)
                print(f"  ✓ Success: reward={reward:.2f}")
                
                if terminated or truncated:
                    break
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
        else:
            print(f"  ✗ Invalid: Action {action} not in available actions")
    
    print("\n" + "=" * 60)


def action_submission_with_gameaction_enum():
    """
    Submit actions using GameAction enum for better readability.
    """
    toolkit = ARCToolkit()
    
    print("\n" + "=" * 60)
    print("Action Submission with GameAction Enum")
    print("=" * 60)
    
    # Setup
    env = toolkit.render_game("ls20", render_mode=None)
    if not env:
        return
    
    observation, info = toolkit.reset_environment()
    
    # Use GameAction enum
    print("\nSubmitting actions using GameAction enum...")
    
    actions = [
        (GameAction.ACTION1, "Up"),
        (GameAction.ACTION2, "Down"),
        (GameAction.ACTION3, "Left"),
        (GameAction.ACTION4, "Right"),
        (GameAction.ACTION5, "Special"),
    ]
    
    for action_enum, description in actions:
        print(f"\n  {description} (GameAction.{action_enum.name})...")
        
        try:
            obs, reward, terminated, truncated, info = toolkit.submit_action(action_enum.value)
            print(f"    Reward: {reward:.2f}")
            
            if terminated or truncated:
                print("    Episode ended!")
                break
                
        except Exception as e:
            print(f"    Error: {e}")
            break
    
    print("\n" + "=" * 60)


def action_submission_loop():
    """
    Complete game loop with action submission.
    """
    toolkit = ARCToolkit()
    
    print("\n" + "=" * 60)
    print("Complete Game Loop with Action Submission")
    print("=" * 60)
    
    # Setup
    env = toolkit.render_game("ls20", render_mode=None)
    if not env:
        return
    
    # Run multiple episodes
    num_episodes = 3
    max_steps = 20
    
    for episode in range(num_episodes):
        print(f"\n--- Episode {episode + 1}/{num_episodes} ---")
        
        observation, info = toolkit.reset_environment()
        episode_reward = 0
        
        for step in range(max_steps):
            # Simple strategy: cycle through actions
            action = (step % 4) + 1  # ACTION1-4
            
            try:
                obs, reward, terminated, truncated, info = toolkit.submit_action(action)
                episode_reward += reward
                
                if step % 5 == 0:
                    print(f"  Step {step}: action={action}, reward={reward:.2f}, total={episode_reward:.2f}")
                
                if terminated or truncated:
                    print(f"  Episode ended at step {step}")
                    break
                    
            except Exception as e:
                print(f"  Error at step {step}: {e}")
                break
        
        print(f"  Episode {episode + 1} total reward: {episode_reward:.2f}")
    
    # Get final scorecard
    print("\n--- Final Scorecard ---")
    scorecard = toolkit.get_scorecard()
    
    print("\n" + "=" * 60)


def action_submission_with_undo():
    """
    Demonstrate action submission with undo functionality.
    """
    toolkit = ARCToolkit()
    
    print("\n" + "=" * 60)
    print("Action Submission with Undo (ACTION7)")
    print("=" * 60)
    
    # Setup
    env = toolkit.render_game("ls20", render_mode=None)
    if not env:
        return
    
    observation, info = toolkit.reset_environment()
    
    print("\nSubmitting actions with undo...")
    
    # Submit some actions
    print("\n1. Submit ACTION1 (up)")
    obs, reward, terminated, truncated, info = toolkit.submit_action(1)
    print(f"   Reward: {reward:.2f}")
    
    print("\n2. Submit ACTION2 (down)")
    obs, reward, terminated, truncated, info = toolkit.submit_action(2)
    print(f"   Reward: {reward:.2f}")
    
    print("\n3. Submit ACTION7 (undo)")
    obs, reward, terminated, truncated, info = toolkit.submit_action(7)
    print(f"   Reward: {reward:.2f}")
    print("   Previous action undone!")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run all examples
    basic_action_submission()
    action_submission_with_validation()
    action_submission_with_gameaction_enum()
    action_submission_loop()
    action_submission_with_undo()
    
    print("\n✓ All action submission examples completed!")

# Made with Bob
