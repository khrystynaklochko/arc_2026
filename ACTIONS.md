# ARC-AGI-3 Actions Reference

This document describes the available actions in ARC-AGI-3 games.

## Action Types

| Action | Description |
|--------|-------------|
| `RESET` | Initialize or restart the game/level state |
| `ACTION1` | Simple action - varies by game (semantically mapped to **up**) |
| `ACTION2` | Simple action - varies by game (semantically mapped to **down**) |
| `ACTION3` | Simple action - varies by game (semantically mapped to **left**) |
| `ACTION4` | Simple action - varies by game (semantically mapped to **right**) |
| `ACTION5` | Simple action - varies by game (e.g., interact, select, rotate, attach/detach, execute, etc.) |
| `ACTION6` | Complex action requiring x,y coordinates (0-63 range) |
| `ACTION7` | Simple action - Undo (e.g., interact, select) |

## Using Actions in Code

### Python (arc-agi package)

```python
from arcengine import GameAction

# Simple directional actions
env.step(GameAction.ACTION1)  # Up
env.step(GameAction.ACTION2)  # Down
env.step(GameAction.ACTION3)  # Left
env.step(GameAction.ACTION4)  # Right

# Special action
env.step(GameAction.ACTION5)  # Interact/Select

# Coordinate-based action (if supported)
env.step(GameAction.ACTION6)  # Requires x,y coordinates

# Undo action
env.step(GameAction.ACTION7)  # Undo last action

# Reset game
env.step(GameAction.RESET)  # Restart game
```

### Action Integers

Actions can also be referenced by integer:

```python
# 0 = RESET
# 1 = ACTION1 (up)
# 2 = ACTION2 (down)
# 3 = ACTION3 (left)
# 4 = ACTION4 (right)
# 5 = ACTION5 (special)
# 6 = ACTION6 (coordinate-based)
# 7 = ACTION7 (undo)

env.step(1)  # Same as ACTION1
```

## Human Player Keybindings

When playing games manually in the ARC-AGI-3 UI, you can use these keyboard shortcuts:

### WASD + Space Control Scheme

| Key | Action |
|-----|--------|
| `W` | ACTION1 (up) |
| `S` | ACTION2 (down) |
| `A` | ACTION3 (left) |
| `D` | ACTION4 (right) |
| `Space` | ACTION5 (special) |
| Mouse Click | ACTION6 (coordinate) |
| CTRL/CMD+Z | ACTION7 (undo) |

### Arrow Keys + F Control Scheme

| Key | Action |
|-----|--------|
| `↑` | ACTION1 (up) |
| `↓` | ACTION2 (down) |
| `←` | ACTION3 (left) |
| `→` | ACTION4 (right) |
| `F` | ACTION5 (special) |
| Mouse Click | ACTION6 (coordinate) |
| CTRL/CMD+Z | ACTION7 (undo) |

## Game-Over State

When a game reaches a game-over state, **only `RESET` is valid**. Sending any other action (ACTION1-ACTION7) will return a `400 Bad Request` error.

If you encounter a `400` error during gameplay:
1. Check if the game has ended
2. Issue a `RESET` to start a new game

**Note:** A `400` error indicates game-over state. A `500` error indicates a server-side issue.

## Available Actions Per Game

Each game explicitly defines which actions are available. This ensures clarity for both human and AI participants.

### Checking Available Actions

The metadata of each returned frame indicates which actions are currently available:

```python
observation, reward, terminated, truncated, info = env.step(action)

# Check available actions in info
available_actions = info.get('available_actions', [])
print(f"Available actions: {available_actions}")
```

Agents can use this information to narrow the action space and develop effective strategies.

**Note:** ACTION6 does not provide explicit X/Y coordinates for active areas. If ACTION6 is available, only its availability will be indicated, without specifying which coordinates are active.

## Action Strategy Tips

### For Agents

1. **Check availability**: Always verify which actions are available before selecting
2. **Learn patterns**: Different games use actions differently
3. **Handle game-over**: Detect terminated/truncated states and reset appropriately
4. **Coordinate actions**: ACTION6 requires spatial reasoning
5. **Use undo wisely**: ACTION7 can help explore alternative paths

### Example Agent Action Selection

```python
def select_action(self, observation, info):
    """Select action based on available actions."""
    available = info.get('available_actions', [])
    
    # Filter to only available actions
    if not available:
        # All actions available
        return self.choose_best_action(observation)
    else:
        # Only choose from available actions
        valid_actions = [a for a in self.possible_actions if a in available]
        return self.choose_from_valid(valid_actions, observation)
```

## Game-Specific Action Meanings

While actions have semantic mappings (up, down, left, right), their exact behavior varies by game:

- **Navigation games**: Actions move objects
- **Transformation games**: Actions apply transformations
- **Pattern games**: Actions manipulate patterns
- **Logic puzzles**: Actions represent logical operations

Always check the specific game documentation at [arcprize.org/tasks](https://arcprize.org/tasks) for exact action meanings.

## Resources

- [ARC-AGI-3 Documentation](https://docs.arcprize.org)
- [Actions Documentation](https://docs.arcprize.org/actions)
- [Game List](https://arcprize.org/tasks)
- [Agent Examples](./AGENTS.md)