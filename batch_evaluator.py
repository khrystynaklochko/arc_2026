#!/usr/bin/env python3
"""
Batch Evaluation Pipeline for ARC-AGI-3
Evaluates agents across multiple games with detailed metrics.
"""

import os
import json
import time
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import arc_agi
from agents import RandomAgent
from agents.llm_agent import OpenAIAgent, AnthropicAgent
from toolkit import ARCToolkit


@dataclass
class GameResult:
    """Results from a single game evaluation."""
    game_id: str
    success: bool
    total_reward: float
    steps: int
    time_taken: float
    error: Optional[str] = None
    final_score: float = 0.0
    actions_taken: List[int] = None
    
    def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []


@dataclass
class EvaluationMetrics:
    """Aggregate metrics across all games."""
    total_games: int
    successful_games: int
    failed_games: int
    success_rate: float
    total_reward: float
    average_reward: float
    total_steps: int
    average_steps: float
    total_time: float
    average_time: float
    games_per_second: float


class BatchEvaluator:
    """Evaluates agents on multiple games with detailed metrics."""
    
    def __init__(self, agent, output_dir: str = "evaluations"):
        """
        Initialize batch evaluator.
        
        Args:
            agent: Agent to evaluate
            output_dir: Directory for evaluation results
        """
        self.agent = agent
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.toolkit = ARCToolkit()
        self.results: List[GameResult] = []
        
    def evaluate_game(self, game_id: str, max_steps: int = 100, 
                     verbose: bool = True) -> GameResult:
        """
        Evaluate agent on a single game.
        
        Args:
            game_id: Game identifier
            max_steps: Maximum steps allowed
            verbose: Print progress
            
        Returns:
            GameResult with evaluation metrics
        """
        if verbose:
            print(f"\nEvaluating: {game_id}")
        
        start_time = time.time()
        
        try:
            # Create environment
            env = self.toolkit.arcade.make(game_id, render_mode=None)
            
            # Reset
            self.agent.reset()
            reset_result = env.reset()
            if isinstance(reset_result, tuple):
                observation, info = reset_result
            else:
                observation = reset_result
                info = {}
            
            # Track episode
            actions_taken = []
            total_reward = 0.0
            
            # Run episode
            for step in range(max_steps):
                action = self.agent.select_action(observation, info)
                actions_taken.append(action)
                
                step_result = env.step(action)
                if len(step_result) == 5:
                    next_observation, reward, terminated, truncated, info = step_result
                elif len(step_result) == 4:
                    next_observation, reward, terminated, info = step_result
                    truncated = False
                else:
                    # Handle unexpected return format
                    next_observation = step_result[0]
                    reward = step_result[1] if len(step_result) > 1 else 0
                    terminated = step_result[2] if len(step_result) > 2 else False
                    truncated = step_result[3] if len(step_result) > 3 else False
                    info = step_result[4] if len(step_result) > 4 else {}
                total_reward += reward
                
                self.agent.update(
                    observation, action, reward, next_observation,
                    terminated or truncated, info
                )
                
                observation = next_observation
                
                if terminated or truncated:
                    break
            
            time_taken = time.time() - start_time
            success = info.get("success", False)
            final_score = info.get("score", total_reward)
            
            result = GameResult(
                game_id=game_id,
                success=success,
                total_reward=total_reward,
                steps=len(actions_taken),
                time_taken=time_taken,
                final_score=final_score,
                actions_taken=actions_taken
            )
            
            if verbose:
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"  {status} | Reward: {total_reward:.2f} | Steps: {len(actions_taken)} | Time: {time_taken:.2f}s")
            
            env.close()
            return result
            
        except Exception as e:
            time_taken = time.time() - start_time
            if verbose:
                print(f"  ❌ ERROR: {e}")
            
            return GameResult(
                game_id=game_id,
                success=False,
                total_reward=0.0,
                steps=0,
                time_taken=time_taken,
                error=str(e)
            )
    
    def evaluate_batch(self, game_ids: Optional[List[str]] = None,
                      max_steps: int = 100, verbose: bool = True) -> EvaluationMetrics:
        """
        Evaluate agent on multiple games.
        
        Args:
            game_ids: List of game IDs (None = all available)
            max_steps: Maximum steps per game
            verbose: Print progress
            
        Returns:
            EvaluationMetrics with aggregate results
        """
        # Get game list
        if game_ids is None:
            available_games = self.toolkit.list_games()
            game_ids = [g.get("id", g.get("name", f"game_{i}")) 
                       for i, g in enumerate(available_games)]
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"BATCH EVALUATION")
            print(f"Agent: {self.agent.name}")
            print(f"Games: {len(game_ids)}")
            print(f"{'='*60}")
        
        start_time = time.time()
        self.results = []
        
        # Evaluate each game
        for i, game_id in enumerate(game_ids, 1):
            if verbose:
                print(f"\nProgress: {i}/{len(game_ids)}")
            
            result = self.evaluate_game(game_id, max_steps, verbose)
            self.results.append(result)
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        metrics = self._calculate_metrics(total_time)
        
        if verbose:
            self._print_metrics(metrics)
        
        return metrics
    
    def _calculate_metrics(self, total_time: float) -> EvaluationMetrics:
        """Calculate aggregate metrics from results."""
        total_games = len(self.results)
        successful_games = sum(1 for r in self.results if r.success)
        failed_games = total_games - successful_games
        success_rate = successful_games / total_games if total_games > 0 else 0.0
        
        total_reward = sum(r.total_reward for r in self.results)
        average_reward = total_reward / total_games if total_games > 0 else 0.0
        
        total_steps = sum(r.steps for r in self.results)
        average_steps = total_steps / total_games if total_games > 0 else 0.0
        
        average_time = total_time / total_games if total_games > 0 else 0.0
        games_per_second = total_games / total_time if total_time > 0 else 0.0
        
        return EvaluationMetrics(
            total_games=total_games,
            successful_games=successful_games,
            failed_games=failed_games,
            success_rate=success_rate,
            total_reward=total_reward,
            average_reward=average_reward,
            total_steps=total_steps,
            average_steps=average_steps,
            total_time=total_time,
            average_time=average_time,
            games_per_second=games_per_second
        )
    
    def _print_metrics(self, metrics: EvaluationMetrics):
        """Print evaluation metrics."""
        print(f"\n{'='*60}")
        print("EVALUATION RESULTS")
        print(f"{'='*60}")
        print(f"Total Games:       {metrics.total_games}")
        print(f"Successful:        {metrics.successful_games} ({metrics.success_rate*100:.1f}%)")
        print(f"Failed:            {metrics.failed_games}")
        print(f"Total Reward:      {metrics.total_reward:.2f}")
        print(f"Average Reward:    {metrics.average_reward:.2f}")
        print(f"Total Steps:       {metrics.total_steps}")
        print(f"Average Steps:     {metrics.average_steps:.1f}")
        print(f"Total Time:        {metrics.total_time:.2f}s")
        print(f"Average Time:      {metrics.average_time:.2f}s")
        print(f"Games/Second:      {metrics.games_per_second:.2f}")
        print(f"{'='*60}")
    
    def save_results(self, filename: Optional[str] = None) -> str:
        """
        Save evaluation results to JSON file.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_{self.agent.name}_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        data = {
            "agent": self.agent.name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": [asdict(r) for r in self.results],
            "metrics": asdict(self._calculate_metrics(
                sum(r.time_taken for r in self.results)
            ))
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✅ Results saved to: {filepath}")
        return str(filepath)
    
    def save_csv(self, filename: Optional[str] = None) -> str:
        """
        Save evaluation results to CSV file.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_{self.agent.name}_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "game_id", "success", "total_reward", "steps", 
                "time_taken", "final_score", "error"
            ])
            
            for result in self.results:
                writer.writerow([
                    result.game_id,
                    result.success,
                    result.total_reward,
                    result.steps,
                    result.time_taken,
                    result.final_score,
                    result.error or ""
                ])
        
        print(f"✅ CSV saved to: {filepath}")
        return str(filepath)
    
    def compare_agents(self, other_evaluator: 'BatchEvaluator') -> Dict[str, Any]:
        """
        Compare this agent's results with another agent.
        
        Args:
            other_evaluator: Another BatchEvaluator to compare with
            
        Returns:
            Dictionary with comparison metrics
        """
        metrics1 = self._calculate_metrics(sum(r.time_taken for r in self.results))
        metrics2 = other_evaluator._calculate_metrics(
            sum(r.time_taken for r in other_evaluator.results)
        )
        
        comparison = {
            "agent1": {
                "name": self.agent.name,
                "success_rate": metrics1.success_rate,
                "average_reward": metrics1.average_reward,
                "average_steps": metrics1.average_steps
            },
            "agent2": {
                "name": other_evaluator.agent.name,
                "success_rate": metrics2.success_rate,
                "average_reward": metrics2.average_reward,
                "average_steps": metrics2.average_steps
            },
            "differences": {
                "success_rate_diff": metrics1.success_rate - metrics2.success_rate,
                "reward_diff": metrics1.average_reward - metrics2.average_reward,
                "steps_diff": metrics1.average_steps - metrics2.average_steps
            }
        }
        
        return comparison


def main():
    """Main evaluation script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch evaluation for ARC-AGI-3")
    parser.add_argument("--agent", type=str, default="random",
                       choices=["random", "openai", "anthropic"],
                       help="Agent type to evaluate")
    parser.add_argument("--model", type=str, default=None,
                       help="Model name for LLM agents")
    parser.add_argument("--games", type=str, nargs="+", default=None,
                       help="Specific game IDs to evaluate")
    parser.add_argument("--max-steps", type=int, default=100,
                       help="Maximum steps per game")
    parser.add_argument("--output-json", type=str, default=None,
                       help="Output JSON filename")
    parser.add_argument("--output-csv", type=str, default=None,
                       help="Output CSV filename")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress progress output")
    
    args = parser.parse_args()
    
    # Create agent
    from kaggle_submission import create_agent
    agent_kwargs = {}
    if args.model:
        agent_kwargs["model"] = args.model
    
    agent = create_agent(args.agent, **agent_kwargs)
    
    # Create evaluator
    evaluator = BatchEvaluator(agent)
    
    # Run evaluation
    evaluator.evaluate_batch(
        game_ids=args.games,
        max_steps=args.max_steps,
        verbose=not args.quiet
    )
    
    # Save results
    evaluator.save_results(filename=args.output_json)
    evaluator.save_csv(filename=args.output_csv)
    
    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()

# Made with Bob
