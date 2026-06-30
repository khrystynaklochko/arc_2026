#!/usr/bin/env python3
"""
Kaggle Submission Script for ARC Prize 2026 - ARC-AGI-3
https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3

This script runs your agent on all test games and generates a submission file.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import arc_agi
from agents import RandomAgent
from agents.llm_agent import OpenAIAgent, AnthropicAgent
from toolkit import ARCToolkit


class KaggleSubmission:
    """Handles Kaggle submission generation for ARC-AGI-3."""
    
    def __init__(self, agent, output_dir: str = "submissions"):
        """
        Initialize Kaggle submission handler.
        
        Args:
            agent: Agent to use for solving tasks
            output_dir: Directory to save submission files
        """
        self.agent = agent
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.toolkit = ARCToolkit()
        self.results = []
        
    def run_on_game(self, game_id: str, max_steps: int = 100) -> Dict[str, Any]:
        """
        Run agent on a single game and collect results.
        
        Args:
            game_id: Game identifier
            max_steps: Maximum steps per episode
            
        Returns:
            Dictionary with game results
        """
        print(f"\n{'='*60}")
        print(f"Running on game: {game_id}")
        print(f"{'='*60}")
        
        try:
            # Create environment
            env = self.toolkit.arcade.make(game_id, render_mode=None)
            
            # Reset agent and environment
            self.agent.reset()
            observation, info = env.reset()
            
            # Track episode
            episode_actions = []
            episode_rewards = []
            total_reward = 0
            
            # Run episode
            for step in range(max_steps):
                # Select action
                action = self.agent.select_action(observation, info)
                episode_actions.append(action)
                
                # Take step
                next_observation, reward, terminated, truncated, info = env.step(action)
                episode_rewards.append(reward)
                total_reward += reward
                
                # Update agent
                self.agent.update(
                    observation, action, reward, next_observation,
                    terminated or truncated, info
                )
                
                observation = next_observation
                
                # Check if done
                if terminated or truncated:
                    print(f"Episode finished at step {step + 1}")
                    break
            
            # Collect results
            result = {
                "game_id": game_id,
                "success": info.get("success", False),
                "total_reward": total_reward,
                "steps": len(episode_actions),
                "actions": episode_actions,
                "final_observation": observation.tolist() if hasattr(observation, 'tolist') else observation
            }
            
            print(f"Success: {result['success']}")
            print(f"Total Reward: {result['total_reward']}")
            print(f"Steps: {result['steps']}")
            
            env.close()
            return result
            
        except Exception as e:
            print(f"Error running game {game_id}: {e}")
            return {
                "game_id": game_id,
                "success": False,
                "error": str(e),
                "total_reward": 0,
                "steps": 0
            }
    
    def run_on_all_games(self, game_ids: Optional[List[str]] = None, max_steps: int = 100):
        """
        Run agent on all specified games.
        
        Args:
            game_ids: List of game IDs to run on (None = all available)
            max_steps: Maximum steps per game
        """
        # Get game list
        if game_ids is None:
            available_games = self.toolkit.list_games()
            game_ids = [game["id"] for game in available_games]
        
        print(f"\n{'='*60}")
        print(f"Running on {len(game_ids)} games")
        print(f"Agent: {self.agent.name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # Run on each game
        for i, game_id in enumerate(game_ids, 1):
            print(f"\nProgress: {i}/{len(game_ids)}")
            result = self.run_on_game(game_id, max_steps)
            self.results.append(result)
        
        elapsed_time = time.time() - start_time
        
        # Print summary
        self.print_summary(elapsed_time)
    
    def print_summary(self, elapsed_time: float):
        """Print summary of results."""
        print(f"\n{'='*60}")
        print("SUBMISSION SUMMARY")
        print(f"{'='*60}")
        
        total_games = len(self.results)
        successful_games = sum(1 for r in self.results if r.get("success", False))
        total_reward = sum(r.get("total_reward", 0) for r in self.results)
        avg_steps = sum(r.get("steps", 0) for r in self.results) / total_games if total_games > 0 else 0
        
        print(f"Total Games: {total_games}")
        print(f"Successful: {successful_games} ({successful_games/total_games*100:.1f}%)")
        print(f"Total Reward: {total_reward}")
        print(f"Average Steps: {avg_steps:.1f}")
        print(f"Time Elapsed: {elapsed_time:.2f}s")
        print(f"{'='*60}")
    
    def save_submission(self, filename: Optional[str] = None) -> str:
        """
        Save submission file in Kaggle format.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to saved submission file
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"submission_{self.agent.name}_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # Format for Kaggle submission
        submission_data = {
            "agent": self.agent.name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.results,
            "summary": {
                "total_games": len(self.results),
                "successful_games": sum(1 for r in self.results if r.get("success", False)),
                "total_reward": sum(r.get("total_reward", 0) for r in self.results)
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(submission_data, f, indent=2)
        
        print(f"\n✅ Submission saved to: {filepath}")
        return str(filepath)
    
    def validate_submission(self, filepath: str) -> bool:
        """
        Validate submission file format.
        
        Args:
            filepath: Path to submission file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Check required fields
            required_fields = ["agent", "timestamp", "results", "summary"]
            for field in required_fields:
                if field not in data:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            # Check results format
            if not isinstance(data["results"], list):
                print("❌ Results must be a list")
                return False
            
            for result in data["results"]:
                if "game_id" not in result:
                    print("❌ Each result must have a game_id")
                    return False
            
            print("✅ Submission file is valid")
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False


def create_agent(agent_type: str = "random", **kwargs):
    """
    Create an agent for submission.
    
    Args:
        agent_type: Type of agent ("random", "openai", "anthropic")
        **kwargs: Additional arguments for agent initialization
        
    Returns:
        Agent instance
    """
    if agent_type == "random":
        return RandomAgent(name="RandomAgent")
    elif agent_type == "openai":
        model = kwargs.get("model", "gpt-4")
        return OpenAIAgent(model=model, name=f"OpenAI-{model}")
    elif agent_type == "anthropic":
        model = kwargs.get("model", "claude-3-opus-20240229")
        return AnthropicAgent(model=model, name=f"Anthropic-{model}")
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


def main():
    """Main submission script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Kaggle submission for ARC-AGI-3")
    parser.add_argument("--agent", type=str, default="random",
                       choices=["random", "openai", "anthropic"],
                       help="Agent type to use")
    parser.add_argument("--model", type=str, default=None,
                       help="Model name for LLM agents")
    parser.add_argument("--games", type=str, nargs="+", default=None,
                       help="Specific game IDs to run on")
    parser.add_argument("--max-steps", type=int, default=100,
                       help="Maximum steps per game")
    parser.add_argument("--output", type=str, default=None,
                       help="Output filename for submission")
    parser.add_argument("--validate-only", type=str, default=None,
                       help="Only validate an existing submission file")
    
    args = parser.parse_args()
    
    # Validate only mode
    if args.validate_only:
        submission = KaggleSubmission(agent=None)
        submission.validate_submission(args.validate_only)
        return
    
    # Create agent
    agent_kwargs = {}
    if args.model:
        agent_kwargs["model"] = args.model
    
    agent = create_agent(args.agent, **agent_kwargs)
    
    # Create submission handler
    submission = KaggleSubmission(agent)
    
    # Run on games
    submission.run_on_all_games(game_ids=args.games, max_steps=args.max_steps)
    
    # Save submission
    filepath = submission.save_submission(filename=args.output)
    
    # Validate
    submission.validate_submission(filepath)
    
    print("\n✅ Submission ready for Kaggle upload!")
    print(f"📁 File: {filepath}")


if __name__ == "__main__":
    main()

# Made with Bob
