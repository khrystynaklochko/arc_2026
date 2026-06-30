# Benchmarking Your Agent

Comprehensive guide to benchmarking and evaluating your ARC-AGI-3 agent performance.

## Overview

Benchmarking helps you:
- Measure agent performance objectively
- Compare different approaches
- Identify strengths and weaknesses
- Track improvements over time
- Prepare for competition submission

## Quick Start

### Basic Benchmark

```bash
# Run baseline benchmark
python batch_evaluator.py --agent random

# Run your agent
python batch_evaluator.py --agent openai --model gpt-4
```

### Full Benchmark Suite

```python
from batch_evaluator import BatchEvaluator
from agents import RandomAgent, OpenAIAgent, AnthropicAgent

# Benchmark multiple agents
agents = [
    RandomAgent(name="Random"),
    OpenAIAgent(model="gpt-3.5-turbo", name="GPT-3.5"),
    OpenAIAgent(model="gpt-4", name="GPT-4"),
    AnthropicAgent(model="claude-3-haiku-20240307", name="Claude-Haiku")
]

results = []
for agent in agents:
    evaluator = BatchEvaluator(agent)
    metrics = evaluator.evaluate_batch(verbose=False)
    results.append({
        "agent": agent.name,
        "metrics": metrics
    })
    evaluator.save_results(f"benchmark_{agent.name}.json")

# Print comparison
print("\nBenchmark Results:")
print("-" * 60)
for result in results:
    print(f"{result['agent']:15} | Success: {result['metrics'].success_rate:.1%} | "
          f"Avg Reward: {result['metrics'].average_reward:.2f}")
```

## Benchmark Metrics

### Core Metrics

1. **Success Rate**: Percentage of games solved
   ```python
   success_rate = successful_games / total_games
   ```

2. **Average Reward**: Mean reward across all games
   ```python
   average_reward = total_reward / total_games
   ```

3. **Average Steps**: Mean actions per game
   ```python
   average_steps = total_steps / total_games
   ```

4. **Time Efficiency**: Games per second
   ```python
   games_per_second = total_games / total_time
   ```

### Advanced Metrics

5. **Sample Efficiency**: Success rate vs. steps taken
   ```python
   sample_efficiency = success_rate / average_steps
   ```

6. **Consistency**: Standard deviation of rewards
   ```python
   import statistics
   consistency = 1 / (1 + statistics.stdev(rewards))
   ```

7. **Generalization**: Performance on unseen games
   ```python
   # Split games into train/test
   train_success = evaluate_on(train_games)
   test_success = evaluate_on(test_games)
   generalization = test_success / train_success
   ```

## Benchmark Suites

### Standard Benchmark

Test on all available games:

```python
from batch_evaluator import BatchEvaluator
from agents import OpenAIAgent

agent = OpenAIAgent(model="gpt-4")
evaluator = BatchEvaluator(agent)

# Run on all games
metrics = evaluator.evaluate_batch()

print(f"Success Rate: {metrics.success_rate:.1%}")
print(f"Average Reward: {metrics.average_reward:.2f}")
print(f"Total Time: {metrics.total_time:.2f}s")
```

### Quick Benchmark

Test on subset of games for faster iteration:

```python
# Quick benchmark on 10 games
quick_games = ["ls20", "ls21", "ls22", "ft09", "ft10", 
               "ft11", "ft12", "ft13", "ft14", "ft15"]

metrics = evaluator.evaluate_batch(game_ids=quick_games)
```

### Difficulty-Based Benchmark

Test on games grouped by difficulty:

```python
# Easy games (for initial testing)
easy_games = ["ls20", "ls21", "ls22"]

# Medium games
medium_games = ["ft09", "ft10", "ft11"]

# Hard games
hard_games = ["ft12", "ft13", "ft14"]

# Benchmark by difficulty
for difficulty, games in [("Easy", easy_games), 
                          ("Medium", medium_games), 
                          ("Hard", hard_games)]:
    metrics = evaluator.evaluate_batch(game_ids=games, verbose=False)
    print(f"{difficulty}: {metrics.success_rate:.1%}")
```

## Comparing Agents

### Head-to-Head Comparison

```python
from batch_evaluator import BatchEvaluator
from agents import RandomAgent, OpenAIAgent

# Agent 1
agent1 = RandomAgent()
eval1 = BatchEvaluator(agent1)
eval1.evaluate_batch()

# Agent 2
agent2 = OpenAIAgent(model="gpt-4")
eval2 = BatchEvaluator(agent2)
eval2.evaluate_batch()

# Compare
comparison = eval2.compare_agents(eval1)
print(comparison)
```

### Statistical Comparison

```python
import scipy.stats as stats

def compare_agents_statistically(eval1, eval2):
    """Compare agents with statistical significance."""
    rewards1 = [r.total_reward for r in eval1.results]
    rewards2 = [r.total_reward for r in eval2.results]
    
    # T-test
    t_stat, p_value = stats.ttest_ind(rewards1, rewards2)
    
    print(f"T-statistic: {t_stat:.4f}")
    print(f"P-value: {p_value:.4f}")
    
    if p_value < 0.05:
        if t_stat > 0:
            print(f"✅ {eval1.agent.name} is significantly better")
        else:
            print(f"✅ {eval2.agent.name} is significantly better")
    else:
        print("⚠️  No significant difference")
```

## Performance Profiling

### Time Profiling

```python
import time
from batch_evaluator import BatchEvaluator

class ProfilingEvaluator(BatchEvaluator):
    """Evaluator with detailed time profiling."""
    
    def evaluate_game(self, game_id, max_steps=100, verbose=True):
        times = {
            "total": 0,
            "action_selection": 0,
            "environment_step": 0,
            "agent_update": 0
        }
        
        start_total = time.time()
        
        # Setup
        env = self.toolkit.arcade.make(game_id, render_mode=None)
        self.agent.reset()
        observation, info = env.reset()
        
        for step in range(max_steps):
            # Time action selection
            start = time.time()
            action = self.agent.select_action(observation, info)
            times["action_selection"] += time.time() - start
            
            # Time environment step
            start = time.time()
            next_obs, reward, terminated, truncated, info = env.step(action)
            times["environment_step"] += time.time() - start
            
            # Time agent update
            start = time.time()
            self.agent.update(observation, action, reward, next_obs, 
                            terminated or truncated, info)
            times["agent_update"] += time.time() - start
            
            observation = next_obs
            if terminated or truncated:
                break
        
        times["total"] = time.time() - start_total
        
        print(f"\nTime Profile for {game_id}:")
        print(f"  Total: {times['total']:.3f}s")
        print(f"  Action Selection: {times['action_selection']:.3f}s "
              f"({times['action_selection']/times['total']*100:.1f}%)")
        print(f"  Environment Step: {times['environment_step']:.3f}s "
              f"({times['environment_step']/times['total']*100:.1f}%)")
        print(f"  Agent Update: {times['agent_update']:.3f}s "
              f"({times['agent_update']/times['total']*100:.1f}%)")
        
        return super().evaluate_game(game_id, max_steps, verbose)
```

### Memory Profiling

```python
import tracemalloc

def profile_memory(agent, game_id):
    """Profile memory usage during game."""
    tracemalloc.start()
    
    # Run game
    env = arc_agi.Arcade().make(game_id)
    observation, info = env.reset()
    agent.reset()
    
    for step in range(100):
        action = agent.select_action(observation, info)
        observation, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break
    
    # Get memory stats
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Memory Usage for {game_id}:")
    print(f"  Current: {current / 1024 / 1024:.2f} MB")
    print(f"  Peak: {peak / 1024 / 1024:.2f} MB")
```

## Optimization Strategies

### 1. Baseline Establishment

```python
# Establish baseline with random agent
baseline = BatchEvaluator(RandomAgent())
baseline_metrics = baseline.evaluate_batch()

print(f"Baseline Success Rate: {baseline_metrics.success_rate:.1%}")
print(f"Target: >{baseline_metrics.success_rate * 2:.1%}")
```

### 2. Iterative Improvement

```python
# Track improvements over iterations
improvements = []

for iteration in range(5):
    # Modify agent (e.g., adjust temperature, prompt, etc.)
    agent = OpenAIAgent(model="gpt-4", temperature=0.5 + iteration * 0.1)
    
    evaluator = BatchEvaluator(agent)
    metrics = evaluator.evaluate_batch(verbose=False)
    
    improvements.append({
        "iteration": iteration,
        "temperature": 0.5 + iteration * 0.1,
        "success_rate": metrics.success_rate,
        "average_reward": metrics.average_reward
    })

# Find best configuration
best = max(improvements, key=lambda x: x['success_rate'])
print(f"Best configuration: iteration {best['iteration']}")
print(f"  Temperature: {best['temperature']}")
print(f"  Success Rate: {best['success_rate']:.1%}")
```

### 3. A/B Testing

```python
def ab_test(agent_a, agent_b, num_runs=5):
    """Run A/B test with multiple runs."""
    results_a = []
    results_b = []
    
    for run in range(num_runs):
        # Test agent A
        eval_a = BatchEvaluator(agent_a)
        metrics_a = eval_a.evaluate_batch(verbose=False)
        results_a.append(metrics_a.success_rate)
        
        # Test agent B
        eval_b = BatchEvaluator(agent_b)
        metrics_b = eval_b.evaluate_batch(verbose=False)
        results_b.append(metrics_b.success_rate)
    
    # Compare
    import statistics
    print(f"Agent A: {statistics.mean(results_a):.1%} ± {statistics.stdev(results_a):.1%}")
    print(f"Agent B: {statistics.mean(results_b):.1%} ± {statistics.stdev(results_b):.1%}")
```

## Benchmark Reports

### Generate Report

```python
def generate_benchmark_report(evaluator, output_file="benchmark_report.md"):
    """Generate markdown benchmark report."""
    metrics = evaluator._calculate_metrics(
        sum(r.time_taken for r in evaluator.results)
    )
    
    report = f"""# Benchmark Report

## Agent: {evaluator.agent.name}

### Summary
- **Total Games**: {metrics.total_games}
- **Successful**: {metrics.successful_games} ({metrics.success_rate:.1%})
- **Failed**: {metrics.failed_games}
- **Total Reward**: {metrics.total_reward:.2f}
- **Average Reward**: {metrics.average_reward:.2f}

### Performance
- **Total Steps**: {metrics.total_steps}
- **Average Steps**: {metrics.average_steps:.1f}
- **Total Time**: {metrics.total_time:.2f}s
- **Average Time**: {metrics.average_time:.2f}s
- **Games/Second**: {metrics.games_per_second:.2f}

### Game Results

| Game ID | Success | Reward | Steps | Time |
|---------|---------|--------|-------|------|
"""
    
    for result in evaluator.results:
        status = "✅" if result.success else "❌"
        report += f"| {result.game_id} | {status} | {result.total_reward:.2f} | {result.steps} | {result.time_taken:.2f}s |\n"
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Report saved to {output_file}")
```

## Continuous Benchmarking

### Automated Benchmark Pipeline

```bash
#!/bin/bash
# benchmark_pipeline.sh

# Run benchmarks for all agents
python batch_evaluator.py --agent random --output-json results/random.json
python batch_evaluator.py --agent openai --model gpt-3.5-turbo --output-json results/gpt35.json
python batch_evaluator.py --agent openai --model gpt-4 --output-json results/gpt4.json

# Generate comparison report
python compare_benchmarks.py results/*.json > benchmark_comparison.md

echo "✅ Benchmark pipeline complete"
```

### Track Over Time

```python
import json
from datetime import datetime

def save_benchmark_history(metrics, agent_name):
    """Save benchmark to history file."""
    history_file = f"benchmark_history_{agent_name}.json"
    
    # Load existing history
    try:
        with open(history_file, 'r') as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []
    
    # Add new entry
    history.append({
        "timestamp": datetime.now().isoformat(),
        "success_rate": metrics.success_rate,
        "average_reward": metrics.average_reward,
        "average_steps": metrics.average_steps
    })
    
    # Save
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
```

## Best Practices

### 1. Use Consistent Test Sets

```python
# Define standard test set
STANDARD_TEST_GAMES = [
    "ls20", "ls21", "ls22", "ft09", "ft10",
    "ft11", "ft12", "ft13", "ft14", "ft15"
]

# Always use same games for comparison
metrics = evaluator.evaluate_batch(game_ids=STANDARD_TEST_GAMES)
```

### 2. Run Multiple Times

```python
# Run benchmark multiple times for reliability
num_runs = 3
all_metrics = []

for run in range(num_runs):
    metrics = evaluator.evaluate_batch(verbose=False)
    all_metrics.append(metrics)

# Average results
avg_success_rate = sum(m.success_rate for m in all_metrics) / num_runs
print(f"Average Success Rate: {avg_success_rate:.1%}")
```

### 3. Control for Randomness

```python
import random
import numpy as np

# Set seeds for reproducibility
random.seed(42)
np.random.seed(42)

# Run benchmark
metrics = evaluator.evaluate_batch()
```

### 4. Document Configuration

```python
benchmark_config = {
    "agent": "GPT-4",
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 1000,
    "max_steps": 100,
    "test_games": STANDARD_TEST_GAMES,
    "date": datetime.now().isoformat(),
    "python_version": "3.12.0",
    "arc_agi_version": "1.0.0"
}

# Save with results
with open('benchmark_results.json', 'w') as f:
    json.dump({
        "config": benchmark_config,
        "metrics": asdict(metrics)
    }, f, indent=2)
```

## Resources

- [Batch Evaluator](./batch_evaluator.py)
- [Kaggle Submission](./kaggle_submission.py)
- [Agent Documentation](./AGENTS.md)
- [ARC Prize Documentation](https://docs.arcprize.org)