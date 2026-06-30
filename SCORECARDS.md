# Scorecards - Performance Tracking

Scorecards provide detailed performance metrics for your ARC-AGI-3 agent runs.

## Overview

Scorecards track:
- Games played
- Success/failure rates
- Scores and rewards
- Time taken
- Action sequences
- Episode statistics

## Using Scorecards

### Basic Usage

```python
import arc_agi

# Create arcade
arc = arc_agi.Arcade()

# Play games
env = arc.make("ls20")
# ... play game ...

# Get scorecard
scorecard = arc.get_scorecard()
print(scorecard)
```

### With Toolkit

```python
from toolkit import ARCToolkit

toolkit = ARCToolkit()

# Create scorecard
scorecard_id = toolkit.create_scorecard("my_experiment")

# Play games...

# Get scorecard
scorecard = toolkit.get_scorecard(scorecard_id)
print(f"Games played: {scorecard['games_played']}")
print(f"Success rate: {scorecard['success_rate']}")

# Close scorecard
toolkit.close_scorecard(scorecard_id)
```

## Scorecard Structure

### Basic Scorecard

```json
{
  "id": "scorecard_123",
  "name": "my_experiment",
  "created_at": "2026-06-30T20:00:00Z",
  "games_played": 10,
  "successful_games": 7,
  "failed_games": 3,
  "success_rate": 0.70,
  "total_score": 750,
  "average_score": 75.0,
  "total_time": 120.5,
  "average_time": 12.05
}
```

### Detailed Scorecard

```json
{
  "id": "scorecard_123",
  "name": "my_experiment",
  "created_at": "2026-06-30T20:00:00Z",
  "games": [
    {
      "game_id": "ls20",
      "success": true,
      "score": 100,
      "steps": 15,
      "time": 10.5,
      "actions": [1, 2, 3, 5, 1, 2, 9],
      "final_state": "completed"
    },
    {
      "game_id": "ls21",
      "success": false,
      "score": 0,
      "steps": 50,
      "time": 25.0,
      "actions": [1, 1, 1, 2, 2, 3, ...],
      "final_state": "failed"
    }
  ],
  "summary": {
    "games_played": 10,
    "successful_games": 7,
    "success_rate": 0.70,
    "total_score": 750,
    "average_score": 75.0
  }
}
```

## Scorecard Operations

### Create Scorecard

```python
from toolkit import ARCToolkit

toolkit = ARCToolkit()

# Create new scorecard
scorecard_id = toolkit.create_scorecard(
    name="gpt4_experiment",
    metadata={
        "agent": "GPT-4",
        "model": "gpt-4-turbo",
        "temperature": 0.7
    }
)
```

### Get Scorecard

```python
# Get current scorecard
scorecard = toolkit.get_scorecard()

# Get specific scorecard
scorecard = toolkit.get_scorecard(scorecard_id)

# Print summary
print(f"Success Rate: {scorecard['success_rate']:.1%}")
print(f"Average Score: {scorecard['average_score']:.2f}")
```

### Update Scorecard

Scorecards are automatically updated as you play games:

```python
# Each game updates the scorecard
env = toolkit.arcade.make("ls20")
observation, info = env.reset()

for step in range(100):
    action = agent.select_action(observation, info)
    observation, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break

# Scorecard now includes this game's results
scorecard = toolkit.get_scorecard()
```

### Close Scorecard

```python
# Close and finalize scorecard
final_scorecard = toolkit.close_scorecard(scorecard_id)

# Closed scorecards are read-only
print(f"Final success rate: {final_scorecard['success_rate']:.1%}")
```

## Metrics Explained

### Success Rate

Percentage of games successfully completed:
```
success_rate = successful_games / total_games
```

### Average Score

Mean score across all games:
```
average_score = total_score / total_games
```

### Average Time

Mean time per game in seconds:
```
average_time = total_time / total_games
```

### Steps Per Game

Average number of actions taken:
```
average_steps = total_steps / total_games
```

## Comparing Scorecards

### Compare Two Agents

```python
from toolkit import ARCToolkit

toolkit = ARCToolkit()

# Run agent 1
scorecard1_id = toolkit.create_scorecard("random_agent")
# ... run random agent ...
scorecard1 = toolkit.get_scorecard(scorecard1_id)

# Run agent 2
scorecard2_id = toolkit.create_scorecard("gpt4_agent")
# ... run GPT-4 agent ...
scorecard2 = toolkit.get_scorecard(scorecard2_id)

# Compare
print("Comparison:")
print(f"Random Agent: {scorecard1['success_rate']:.1%}")
print(f"GPT-4 Agent:  {scorecard2['success_rate']:.1%}")
print(f"Improvement:  {(scorecard2['success_rate'] - scorecard1['success_rate']):.1%}")
```

### Using Batch Evaluator

```python
from batch_evaluator import BatchEvaluator
from agents import RandomAgent, OpenAIAgent

# Evaluate random agent
random_agent = RandomAgent()
random_eval = BatchEvaluator(random_agent)
random_eval.evaluate_batch()

# Evaluate GPT-4 agent
gpt4_agent = OpenAIAgent(model="gpt-4")
gpt4_eval = BatchEvaluator(gpt4_agent)
gpt4_eval.evaluate_batch()

# Compare
comparison = gpt4_eval.compare_agents(random_eval)
print(comparison)
```

## Exporting Scorecards

### JSON Export

```python
import json

scorecard = toolkit.get_scorecard()

# Save to file
with open('scorecard.json', 'w') as f:
    json.dump(scorecard, f, indent=2)
```

### CSV Export

```python
import csv

scorecard = toolkit.get_scorecard()

# Export game results to CSV
with open('scorecard.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['game_id', 'success', 'score', 'steps', 'time'])
    
    for game in scorecard['games']:
        writer.writerow([
            game['game_id'],
            game['success'],
            game['score'],
            game['steps'],
            game['time']
        ])
```

### Using Batch Evaluator Export

```python
from batch_evaluator import BatchEvaluator
from agents import RandomAgent

agent = RandomAgent()
evaluator = BatchEvaluator(agent)
evaluator.evaluate_batch()

# Export to JSON
evaluator.save_results('results.json')

# Export to CSV
evaluator.save_csv('results.csv')
```

## Scorecard Best Practices

### 1. Name Your Scorecards

Use descriptive names to track experiments:
```python
scorecard_id = toolkit.create_scorecard(
    name=f"gpt4_temp0.7_run{run_number}"
)
```

### 2. Add Metadata

Include relevant information:
```python
scorecard_id = toolkit.create_scorecard(
    name="experiment_1",
    metadata={
        "agent": "GPT-4",
        "model": "gpt-4-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "date": "2026-06-30",
        "notes": "Testing with higher temperature"
    }
)
```

### 3. Close When Done

Finalize scorecards after experiments:
```python
final_scorecard = toolkit.close_scorecard(scorecard_id)
```

### 4. Track Multiple Runs

Compare across multiple runs:
```python
scorecards = []
for run in range(5):
    scorecard_id = toolkit.create_scorecard(f"run_{run}")
    # ... run experiment ...
    scorecard = toolkit.close_scorecard(scorecard_id)
    scorecards.append(scorecard)

# Analyze variance
success_rates = [s['success_rate'] for s in scorecards]
print(f"Mean: {sum(success_rates)/len(success_rates):.1%}")
print(f"Std:  {statistics.stdev(success_rates):.1%}")
```

## Integration with Kaggle

### Track Submission Performance

```python
from kaggle_submission import KaggleSubmission
from agents import OpenAIAgent

# Create agent
agent = OpenAIAgent(model="gpt-4")

# Create submission with scorecard tracking
submission = KaggleSubmission(agent)

# Run on all games (automatically tracked)
submission.run_on_all_games()

# Get scorecard from results
scorecard = {
    "games_played": len(submission.results),
    "successful_games": sum(1 for r in submission.results if r['success']),
    "success_rate": sum(1 for r in submission.results if r['success']) / len(submission.results),
    "total_reward": sum(r['total_reward'] for r in submission.results)
}

print(f"Submission Scorecard:")
print(f"  Success Rate: {scorecard['success_rate']:.1%}")
print(f"  Total Reward: {scorecard['total_reward']}")
```

## Troubleshooting

### Scorecard Not Updating

**Problem**: Scorecard doesn't reflect recent games

**Solution**: Ensure you're getting the latest scorecard:
```python
# Refresh scorecard
scorecard = toolkit.get_scorecard(scorecard_id)
```

### Missing Game Data

**Problem**: Some games not in scorecard

**Solution**: Check if games completed successfully:
```python
# Verify game completion
if terminated or truncated:
    print("Game completed, should be in scorecard")
```

### Scorecard Conflicts

**Problem**: Multiple scorecards interfering

**Solution**: Use explicit scorecard IDs:
```python
# Create separate scorecards
scorecard1 = toolkit.create_scorecard("experiment_1")
scorecard2 = toolkit.create_scorecard("experiment_2")

# Get specific scorecard
results1 = toolkit.get_scorecard(scorecard1)
results2 = toolkit.get_scorecard(scorecard2)
```

## Resources

- [ARC Prize Documentation](https://docs.arcprize.org)
- [Scorecards API](https://docs.arcprize.org/scorecards)
- [Batch Evaluator](./batch_evaluator.py)
- [Kaggle Submission](./kaggle_submission.py)