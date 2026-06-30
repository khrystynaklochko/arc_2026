# ARC-AGI-3 Game Schema

This document describes the structure and format of ARC-AGI-3 game environments.

## Game Structure

Each ARC-AGI-3 game follows a consistent structure:

### Observation Space

The observation returned by the environment contains:

```python
{
    'grid': np.ndarray,      # Current game grid state
    'width': int,            # Grid width
    'height': int,           # Grid height
    'step': int,             # Current step number
    'max_steps': int,        # Maximum steps allowed
}
```

### Action Space

Games typically support 10 discrete actions (0-9):

- **0-3**: Movement/transformation actions (e.g., up, down, left, right)
- **4-7**: Special game-specific actions
- **8**: Submit/confirm action
- **9**: Reset/undo action

### Info Dictionary

The `info` dictionary provides additional context:

```python
{
    'game_id': str,          # Unique game identifier
    'difficulty': str,       # Game difficulty level
    'description': str,      # Game description
    'success': bool,         # Whether goal was achieved
    'score': float,          # Current score
}
```

## Grid Representation

Grids are represented as 2D numpy arrays where each cell contains an integer representing:

- **0**: Empty/background
- **1-9**: Different colored objects or states
- **10+**: Special game-specific elements

### Example Grid

```python
grid = np.array([
    [0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0],
    [0, 1, 1, 0, 0],
    [0, 0, 0, 2, 0],
    [0, 0, 0, 0, 0]
])
```

## Episode Flow

1. **Reset**: `observation, info = env.reset()`
   - Initializes new game episode
   - Returns initial observation and info

2. **Step**: `observation, reward, terminated, truncated, info = env.step(action)`
   - Takes action in environment
   - Returns new state and feedback

3. **Termination**:
   - `terminated=True`: Goal achieved or failed
   - `truncated=True`: Max steps reached

## Reward Structure

Rewards are game-specific but generally follow:

- **Positive rewards**: Progress toward goal
- **Negative rewards**: Invalid moves or mistakes
- **Large reward**: Goal completion
- **Zero reward**: Neutral actions

## Game Types

### Transformation Games
Transform input grid to match target pattern.

### Navigation Games
Move objects to target positions.

### Pattern Recognition Games
Identify and replicate patterns.

### Logic Puzzles
Solve logical constraints.

## Example Usage

```python
import arc_agi

# Create environment
arc = arc_agi.Arcade()
env = arc.make("ls20")

# Reset environment
observation, info = env.reset()
print(f"Grid shape: {observation['grid'].shape}")
print(f"Game: {info['game_id']}")

# Take action
action = 0  # Move up
observation, reward, terminated, truncated, info = env.step(action)

print(f"Reward: {reward}")
print(f"Done: {terminated or truncated}")
```

## Advanced Features

### Rendering

```python
# Terminal rendering
env = arc.make("ls20", render_mode="terminal")

# No rendering (faster)
env = arc.make("ls20")
```

### Multiple Episodes

```python
for episode in range(10):
    observation, info = env.reset()
    done = False
    
    while not done:
        action = agent.select_action(observation, info)
        observation, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
```

## Game-Specific Schemas

Each game may have unique:
- Grid dimensions
- Action meanings
- Reward structures
- Success criteria

Check individual game documentation at [arcprize.org/tasks](https://arcprize.org/tasks) for specific details.

## Tips for Agents

1. **Analyze the grid**: Understand object positions and patterns
2. **Track changes**: Monitor how actions affect the grid
3. **Learn patterns**: Identify recurring structures
4. **Plan ahead**: Consider multi-step strategies
5. **Handle edge cases**: Account for boundary conditions

## Resources

- [ARC-AGI-3 Documentation](https://docs.arcprize.org)
- [Game List](https://arcprize.org/tasks)
- [Agent Examples](./AGENTS.md)