# Game Recordings - Replay and Analysis

Record, replay, and analyze your agent's gameplay for debugging and improvement.

## Overview

Recordings capture:
- Complete action sequences
- Observations at each step
- Rewards received
- Game state transitions
- Timing information
- Success/failure outcomes

## Recording Games

### Basic Recording

```python
import arc_agi
import json

# Create environment
arc = arc_agi.Arcade()
env = arc.make("ls20")

# Initialize recording
recording = {
    "game_id": "ls20",
    "agent": "MyAgent",
    "timestamp": "2026-06-30T20:00:00Z",
    "frames": []
}

# Play and record
observation, info = env.reset()
recording["frames"].append({
    "step": 0,
    "action": None,
    "observation": observation.tolist(),
    "reward": 0,
    "info": info
})

for step in range(100):
    action = agent.select_action(observation, info)
    observation, reward, terminated, truncated, info = env.step(action)
    
    # Record frame
    recording["frames"].append({
        "step": step + 1,
        "action": action,
        "observation": observation.tolist(),
        "reward": reward,
        "terminated": terminated,
        "truncated": truncated,
        "info": info
    })
    
    if terminated or truncated:
        break

# Save recording
with open('recording.json', 'w') as f:
    json.dump(recording, f, indent=2)
```

### Using Environment Wrapper

```python
from environment_wrapper import ARCEnvironmentWrapper

# Create wrapped environment
env = ARCEnvironmentWrapper("ls20")

# Play game
observation, info = env.reset()
for step in range(100):
    action = agent.select_action(observation, info)
    observation, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break

# Get recording from history
recording = {
    "game_id": "ls20",
    "history": env.get_history(),
    "stats": env.get_episode_stats()
}

# Save
import json
with open('recording.json', 'w') as f:
    json.dump(recording, f, indent=2)
```

## Recording Format

### Standard Recording Structure

```json
{
  "game_id": "ls20",
  "agent": "GPT-4",
  "timestamp": "2026-06-30T20:00:00Z",
  "metadata": {
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_steps": 100
  },
  "frames": [
    {
      "step": 0,
      "action": null,
      "observation": [[1, 2], [3, 4]],
      "reward": 0,
      "terminated": false,
      "truncated": false,
      "info": {}
    },
    {
      "step": 1,
      "action": 1,
      "observation": [[2, 1], [4, 3]],
      "reward": 10,
      "terminated": false,
      "truncated": false,
      "info": {"score": 10}
    }
  ],
  "summary": {
    "total_steps": 15,
    "total_reward": 100,
    "success": true,
    "duration": 10.5
  }
}
```

## Replaying Recordings

### Basic Replay

```python
import json
import arc_agi

# Load recording
with open('recording.json', 'r') as f:
    recording = json.load(f)

# Create environment
arc = arc_agi.Arcade()
env = arc.make(recording['game_id'], render_mode="terminal")

# Replay actions
env.reset()
for frame in recording['frames'][1:]:  # Skip initial frame
    if frame['action'] is not None:
        env.step(frame['action'])
        # Optionally add delay for visualization
        import time
        time.sleep(0.5)

env.close()
```

### Replay with Validation

```python
import json
import numpy as np

def replay_and_validate(recording_path):
    """Replay recording and validate observations match."""
    with open(recording_path, 'r') as f:
        recording = json.load(f)
    
    # Create environment
    arc = arc_agi.Arcade()
    env = arc.make(recording['game_id'])
    
    # Reset
    observation, info = env.reset()
    
    # Validate initial observation
    expected_obs = np.array(recording['frames'][0]['observation'])
    if not np.array_equal(observation, expected_obs):
        print("⚠️  Initial observation mismatch!")
        return False
    
    # Replay and validate each step
    for i, frame in enumerate(recording['frames'][1:], 1):
        if frame['action'] is None:
            continue
            
        observation, reward, terminated, truncated, info = env.step(frame['action'])
        
        # Validate observation
        expected_obs = np.array(frame['observation'])
        if not np.array_equal(observation, expected_obs):
            print(f"⚠️  Observation mismatch at step {i}")
            return False
        
        # Validate reward
        if reward != frame['reward']:
            print(f"⚠️  Reward mismatch at step {i}: {reward} vs {frame['reward']}")
            return False
    
    print("✅ Replay validated successfully")
    return True
```

## Analyzing Recordings

### Extract Action Patterns

```python
def analyze_actions(recording_path):
    """Analyze action patterns in recording."""
    with open(recording_path, 'r') as f:
        recording = json.load(f)
    
    actions = [f['action'] for f in recording['frames'] if f['action'] is not None]
    
    # Action frequency
    from collections import Counter
    action_counts = Counter(actions)
    
    print("Action Frequency:")
    for action, count in action_counts.most_common():
        print(f"  Action {action}: {count} times ({count/len(actions)*100:.1f}%)")
    
    # Action sequences
    print("\nAction Sequence:")
    print(" -> ".join(str(a) for a in actions[:10]))
    
    # Reward analysis
    rewards = [f['reward'] for f in recording['frames']]
    total_reward = sum(rewards)
    print(f"\nTotal Reward: {total_reward}")
    print(f"Average Reward: {total_reward/len(rewards):.2f}")
```

### Visualize Reward Progress

```python
import matplotlib.pyplot as plt

def plot_rewards(recording_path):
    """Plot reward progression over time."""
    with open(recording_path, 'r') as f:
        recording = json.load(f)
    
    steps = [f['step'] for f in recording['frames']]
    rewards = [f['reward'] for f in recording['frames']]
    cumulative_rewards = np.cumsum(rewards)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Immediate rewards
    ax1.plot(steps, rewards)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Reward')
    ax1.set_title('Immediate Rewards')
    ax1.grid(True)
    
    # Cumulative rewards
    ax2.plot(steps, cumulative_rewards)
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Cumulative Reward')
    ax2.set_title('Cumulative Rewards')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('reward_analysis.png')
    print("✅ Saved reward analysis to reward_analysis.png")
```

### Compare Recordings

```python
def compare_recordings(recording1_path, recording2_path):
    """Compare two recordings."""
    with open(recording1_path, 'r') as f:
        rec1 = json.load(f)
    with open(recording2_path, 'r') as f:
        rec2 = json.load(f)
    
    print("Comparison:")
    print(f"Recording 1: {rec1['agent']}")
    print(f"  Steps: {rec1['summary']['total_steps']}")
    print(f"  Reward: {rec1['summary']['total_reward']}")
    print(f"  Success: {rec1['summary']['success']}")
    
    print(f"\nRecording 2: {rec2['agent']}")
    print(f"  Steps: {rec2['summary']['total_steps']}")
    print(f"  Reward: {rec2['summary']['total_reward']}")
    print(f"  Success: {rec2['summary']['success']}")
    
    # Compare efficiency
    if rec1['summary']['success'] and rec2['summary']['success']:
        if rec1['summary']['total_steps'] < rec2['summary']['total_steps']:
            print(f"\n✅ Recording 1 is more efficient ({rec1['summary']['total_steps']} vs {rec2['summary']['total_steps']} steps)")
        else:
            print(f"\n✅ Recording 2 is more efficient ({rec2['summary']['total_steps']} vs {rec1['summary']['total_steps']} steps)")
```

## Recording Best Practices

### 1. Include Metadata

```python
recording = {
    "game_id": "ls20",
    "agent": "GPT-4",
    "timestamp": datetime.now().isoformat(),
    "metadata": {
        "model": "gpt-4-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "system_prompt": "You are an expert puzzle solver...",
        "python_version": "3.12.0",
        "arc_agi_version": "1.0.0"
    },
    "frames": []
}
```

### 2. Compress Large Recordings

```python
import gzip
import json

# Save compressed
with gzip.open('recording.json.gz', 'wt') as f:
    json.dump(recording, f)

# Load compressed
with gzip.open('recording.json.gz', 'rt') as f:
    recording = json.load(f)
```

### 3. Record Only Key Frames

For long episodes, record only important frames:

```python
# Record every Nth frame or on reward changes
if step % 10 == 0 or reward != 0:
    recording["frames"].append({
        "step": step,
        "action": action,
        "observation": observation.tolist(),
        "reward": reward
    })
```

### 4. Organize Recordings

```python
import os
from datetime import datetime

# Create organized directory structure
date_str = datetime.now().strftime("%Y%m%d")
agent_name = "gpt4"
game_id = "ls20"

recording_dir = f"recordings/{date_str}/{agent_name}/{game_id}"
os.makedirs(recording_dir, exist_ok=True)

# Save with timestamp
timestamp = datetime.now().strftime("%H%M%S")
filename = f"{recording_dir}/recording_{timestamp}.json"
with open(filename, 'w') as f:
    json.dump(recording, f)
```

## Integration with Batch Evaluator

```python
from batch_evaluator import BatchEvaluator
from agents import OpenAIAgent
import json

class RecordingEvaluator(BatchEvaluator):
    """Batch evaluator that saves recordings."""
    
    def __init__(self, agent, output_dir="recordings"):
        super().__init__(agent, output_dir)
        self.recordings = []
    
    def evaluate_game(self, game_id, max_steps=100, verbose=True):
        """Evaluate game and save recording."""
        # Run evaluation
        result = super().evaluate_game(game_id, max_steps, verbose)
        
        # Create recording
        recording = {
            "game_id": game_id,
            "agent": self.agent.name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save recording
        filename = f"{self.output_dir}/{game_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(recording, f, indent=2)
        
        self.recordings.append(filename)
        return result

# Usage
agent = OpenAIAgent(model="gpt-4")
evaluator = RecordingEvaluator(agent)
evaluator.evaluate_batch(game_ids=["ls20", "ls21"])

print(f"Saved {len(evaluator.recordings)} recordings")
```

## Debugging with Recordings

### Find Failure Points

```python
def find_failure_point(recording_path):
    """Find where agent started failing."""
    with open(recording_path, 'r') as f:
        recording = json.load(f)
    
    # Track reward trend
    rewards = [f['reward'] for f in recording['frames']]
    
    # Find where rewards stopped increasing
    max_reward = 0
    failure_step = None
    
    for i, reward in enumerate(rewards):
        if reward > max_reward:
            max_reward = reward
        elif i > 10 and reward == 0:  # No reward for a while
            failure_step = i
            break
    
    if failure_step:
        print(f"⚠️  Agent stopped making progress at step {failure_step}")
        print(f"Last successful action: {recording['frames'][failure_step-1]['action']}")
    else:
        print("✅ Agent maintained progress throughout")
```

### Identify Repeated Mistakes

```python
def find_repeated_patterns(recording_path):
    """Find repeated action patterns that might indicate stuck behavior."""
    with open(recording_path, 'r') as f:
        recording = json.load(f)
    
    actions = [f['action'] for f in recording['frames'] if f['action'] is not None]
    
    # Look for repeated sequences
    for length in range(2, 6):
        for i in range(len(actions) - length * 2):
            pattern = tuple(actions[i:i+length])
            if tuple(actions[i+length:i+length*2]) == pattern:
                print(f"⚠️  Repeated pattern found: {pattern}")
                print(f"   First occurrence: step {i}")
                print(f"   Second occurrence: step {i+length}")
                return pattern
    
    print("✅ No obvious repeated patterns")
    return None
```

## Resources

- [Environment Wrapper](./environment_wrapper.py)
- [Batch Evaluator](./batch_evaluator.py)
- [ARC Prize Documentation](https://docs.arcprize.org)
- [Recordings API](https://docs.arcprize.org/recordings)