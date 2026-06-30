# ARC-AGI-3 Agents

This directory contains agent implementations for playing ARC-AGI-3 games.

## Agent Architecture

All agents inherit from the `BaseAgent` abstract class, which provides:
- Action selection interface
- Memory management
- Statistics tracking
- Episode management

## Available Agents

### 1. RandomAgent
A baseline agent that selects random actions.

**Usage:**
```python
from agents import RandomAgent

agent = RandomAgent(num_actions=10)
action = agent.select_action(observation, info)
```

**Use Case:** Baseline for comparing more sophisticated agents.

### 2. LLMAgent (Base Class)
Abstract base for LLM-based agents that use language models to reason about actions.

**Features:**
- Builds prompts from game state
- Maintains conversation history
- Supports multiple LLM providers

### 3. OpenAIAgent
Agent using OpenAI's GPT models (GPT-4, GPT-3.5, etc.).

**Setup:**
```bash
export OPENAI_API_KEY="your-key-here"
```

**Usage:**
```python
from agents.llm_agent import OpenAIAgent

agent = OpenAIAgent(model="gpt-4")
action = agent.select_action(observation, info)
```

### 4. AnthropicAgent
Agent using Anthropic's Claude models.

**Setup:**
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

**Usage:**
```python
from agents.llm_agent import AnthropicAgent

agent = AnthropicAgent(model="claude-3-opus-20240229")
action = agent.select_action(observation, info)
```

## Running Agents

### Quick Start
```bash
python run_agent.py
```

This will run the RandomAgent on the "ls20" game for 3 episodes.

### Custom Agent Run
```python
import arc_agi
from agents import RandomAgent

# Create environment
arc = arc_agi.Arcade()
env = arc.make("ls20", render_mode="terminal")

# Create agent
agent = RandomAgent(num_actions=10)

# Run episode
observation, info = env.reset()
agent.reset()

for step in range(100):
    action = agent.select_action(observation, info)
    observation, reward, terminated, truncated, info = env.step(action)
    agent.update(observation, action, reward, observation, terminated or truncated, info)
    
    if terminated or truncated:
        break

print(agent.get_stats())
```

## Creating Your Own Agent

### Step 1: Inherit from BaseAgent
```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, name="MyAgent"):
        super().__init__(name)
        # Add your initialization here
    
    def select_action(self, observation, info):
        # Implement your action selection logic
        return action
```

### Step 2: Implement Action Selection
The `select_action` method receives:
- `observation`: Current game state
- `info`: Dictionary with additional information

It should return an integer action (0-9 for most games).

### Step 3: Optional: Override Other Methods
```python
def reset(self):
    """Called at the start of each episode"""
    super().reset()
    # Your reset logic
    
def update(self, observation, action, reward, next_observation, done, info):
    """Called after each action"""
    super().update(observation, action, reward, next_observation, done, info)
    # Your learning/update logic
```

## Agent Actions

ARC-AGI-3 games typically support these actions:
- **ACTION1-ACTION4**: Movement/transformation in different directions
- **ACTION5-ACTION8**: Special actions (game-specific)
- **ACTION9**: Submit/confirm action
- **ACTION10**: Reset/undo action

Check the specific game documentation for exact action meanings.

## Performance Tips

1. **Fast Mode**: Remove `render_mode` for +2K FPS
   ```python
   env = arc.make("ls20")  # No rendering
   ```

2. **Batch Processing**: Run multiple episodes in parallel
3. **Memory Management**: Clear agent memory between episodes if needed
4. **Action Caching**: Cache LLM responses for similar states

## Evaluation

Use the scorecard to evaluate agent performance:
```python
print(arc.get_scorecard())
```

This shows:
- Games played
- Success rate
- Average score
- Time taken

## Advanced: Multi-Agent Systems

You can create systems with multiple agents:
```python
from agents import RandomAgent
from agents.llm_agent import OpenAIAgent

# Ensemble of agents
agents = [
    RandomAgent(name="Explorer"),
    OpenAIAgent(model="gpt-4", name="Reasoner")
]

# Vote on actions
votes = [agent.select_action(obs, info) for agent in agents]
action = max(set(votes), key=votes.count)  # Majority vote
```

## Resources

- [ARC-AGI-3 Documentation](https://docs.arcprize.org)
- [Agent Quickstart](https://docs.arcprize.org/agents-quickstart)
- [LLM Agent Templates](https://docs.arcprize.org/llm_agents)
- [Game List](https://arcprize.org/tasks)