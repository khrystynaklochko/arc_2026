#!/usr/bin/env python3
"""
Main submission script for Kaggle ARC Prize 2026
Runs FuzzyRecursiveAgent on all games and generates submission.parquet
"""

import sys
import pandas as pd
from pathlib import Path
import os

# Add current directory and agents to path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'agents'))

# Also try /kaggle/working if running on Kaggle
if os.path.exists('/kaggle/working'):
    sys.path.insert(0, '/kaggle/working')
    sys.path.insert(0, '/kaggle/working/agents')

from agents.baseline_agent import BaselineAgent
import arc_agi

def main():
    """Run agent on all games and generate submission"""
    print("=" * 60)
    print("ARC Prize 2026 - Kaggle Submission")
    print("Agent: BaselineAgent")
    print("=" * 60)
    
    # Initialize
    arcade = arc_agi.Arcade()
    
    # Get all games
    games = arcade.get_environments()
    agent = BaselineAgent()
    print(f"\nRunning on {len(games)} games...")
    
    results = []
    
    # Run on each game
    for i, game_env in enumerate(games, 1):
        game_id = game_env.game_id
        print(f"\n[{i}/{len(games)}] Running: {game_id}")
        
        try:
            # Create environment
            env = arcade.make(game_id, render_mode=None)
            
            # Reset and set baseline actions
            agent.reset()
            agent.baseline_actions = game_env.baseline_actions
            frame_data = env.reset()
            observation = frame_data
            info = {
                'game_id': frame_data.game_id,
                'state': frame_data.state,
            }
            
            # Run episode
            for step in range(100):
                try:
                    action = agent.select_action(observation, info)
                    frame_data = env.step(action)
                except Exception as step_error:
                    print(f"  ⚠️  Step {step} error: {step_error}")
                    # Continue with a random action
                    import random
                    action = random.randint(0, 7)
                    frame_data = env.step(action)
                
                observation = frame_data
                info = {
                    'game_id': frame_data.game_id,
                    'state': frame_data.state,
                    'levels_completed': frame_data.levels_completed,
                }
                
                # Check if done
                if frame_data.state in ["WON", "LOST"]:
                    break
            
            # Record result
            success = frame_data.state == "WON"
            results.append({
                'game_id': game_id,
                'success': success,
                'levels_completed': frame_data.levels_completed,
                'state': frame_data.state
            })
            
            status = "✅ WON" if success else "❌ LOST"
            print(f"  {status} - Levels: {frame_data.levels_completed}")
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append({
                'game_id': game_id,
                'success': False,
                'levels_completed': 0,
                'state': 'ERROR'
            })
    
    # Create submission DataFrame
    df = pd.DataFrame(results)
    
    # Save as parquet
    output_file = 'submission.parquet'
    df.to_parquet(output_file, index=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUBMISSION SUMMARY")
    print("=" * 60)
    print(f"Total Games: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    print(f"\n✅ Submission saved: {output_file}")
    print("=" * 60)
    
    return df

if __name__ == "__main__":
    submission_df = main()
    print("\n🎉 Ready to submit to Kaggle!")

# Made with Bob
