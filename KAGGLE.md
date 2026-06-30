# Kaggle Competition Guide - ARC Prize 2026 - ARC-AGI-3

Complete guide for submitting to the [ARC Prize 2026 - ARC-AGI-3](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3) competition.

## Quick Start

### 1. Setup Environment

```bash
# Ensure Python 3.12+
python --version

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your keys
```

### 2. Test Your Agent

```bash
# Test on a single game
python play.py

# Test with an agent
python run_agent.py
```

### 3. Generate Submission

```bash
# Using Random Agent (baseline)
python kaggle_submission.py --agent random

# Using OpenAI GPT-4
python kaggle_submission.py --agent openai --model gpt-4

# Using Anthropic Claude
python kaggle_submission.py --agent anthropic --model claude-3-opus-20240229

# Specific games only
python kaggle_submission.py --agent random --games ls20 ls21 ls22
```

### 4. Validate Submission

```bash
python kaggle_submission.py --validate-only submissions/submission_*.json
```

### 5. Upload to Kaggle

1. Go to [competition page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3)
2. Click "Submit Predictions"
3. Upload your `submission_*.json` file
4. Wait for evaluation results

## Submission Format

The submission file is a JSON with this structure:

```json
{
  "agent": "AgentName",
  "timestamp": "2026-06-30 20:00:00",
  "results": [
    {
      "game_id": "ls20",
      "success": true,
      "total_reward": 100.0,
      "steps": 15,
      "actions": [1, 2, 3, ...],
      "final_observation": [...]
    }
  ],
  "summary": {
    "total_games": 100,
    "successful_games": 75,
    "total_reward": 7500.0
  }
}
```

## Evaluation Pipeline

### Batch Evaluation

Evaluate your agent on multiple games with detailed metrics:

```bash
# Full evaluation
python batch_evaluator.py --agent openai --model gpt-4

# Specific games
python batch_evaluator.py --agent random --games ls20 ls21 ls22

# Save results
python batch_evaluator.py --agent random --output-json my_eval.json --output-csv my_eval.csv

# Quiet mode (no progress output)
python batch_evaluator.py --agent random --quiet
```

### Evaluation Metrics

The evaluator tracks:
- **Success Rate**: Percentage of games solved
- **Total Reward**: Sum of all rewards
- **Average Reward**: Mean reward per game
- **Total Steps**: Sum of all steps taken
- **Average Steps**: Mean steps per game
- **Time Metrics**: Total and average time per game
- **Games/Second**: Throughput metric

### Output Files

**JSON Format** (`evaluations/evaluation_*.json`):
```json
{
  "agent": "AgentName",
  "timestamp": "2026-06-30 20:00:00",
  "results": [...],
  "metrics": {
    "total_games": 100,
    "successful_games": 75,
    "success_rate": 0.75,
    "total_reward": 7500.0,
    "average_reward": 75.0,
    "total_steps": 1500,
    "average_steps": 15.0,
    "total_time": 300.0,
    "average_time": 3.0,
    "games_per_second": 0.33
  }
}
```

**CSV Format** (`evaluations/evaluation_*.csv`):
```csv
game_id,success,total_reward,steps,time_taken,final_score,error
ls20,True,100.0,15,2.5,100.0,
ls21,False,0.0,0,0.1,,Timeout
```

## Agent Development

### Creating a Custom Agent

1. **Inherit from BaseAgent**:

```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, name="MyAgent"):
        super().__init__(name)
        # Your initialization
    
    def select_action(self, observation, info):
        # Your logic here
        return action
```

2. **Test Locally**:

```python
from agents import MyAgent
from batch_evaluator import BatchEvaluator

agent = MyAgent()
evaluator = BatchEvaluator(agent)
evaluator.evaluate_batch(game_ids=["ls20"])
```

3. **Generate Submission**:

```python
from kaggle_submission import KaggleSubmission
from agents import MyAgent

agent = MyAgent()
submission = KaggleSubmission(agent)
submission.run_on_all_games()
submission.save_submission()
```

### Using LLM Agents

**OpenAI GPT Models**:
```bash
export OPENAI_API_KEY="sk-..."
python kaggle_submission.py --agent openai --model gpt-4
```

**Anthropic Claude Models**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python kaggle_submission.py --agent anthropic --model claude-3-opus-20240229
```

**Available Models**:
- OpenAI: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- Anthropic: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`

## Competition Strategy

### 1. Baseline Performance

Start with the RandomAgent to establish a baseline:

```bash
python batch_evaluator.py --agent random
```

This gives you a performance floor to beat.

### 2. Iterative Improvement

1. Analyze failed games
2. Improve agent logic
3. Re-evaluate
4. Compare metrics

```python
from batch_evaluator import BatchEvaluator
from agents import RandomAgent, MyAgent

# Baseline
baseline = BatchEvaluator(RandomAgent())
baseline.evaluate_batch()

# Your agent
evaluator = BatchEvaluator(MyAgent())
evaluator.evaluate_batch()

# Compare
comparison = evaluator.compare_agents(baseline)
print(comparison)
```

### 3. Focus on High-Value Games

Some games may be worth more points. Prioritize:
- Games with higher reward potential
- Games your agent performs well on
- Games with clear patterns

### 4. Optimize for Speed

Competition may have time limits:
- Remove `render_mode` for faster execution
- Cache LLM responses for similar states
- Use simpler models for easier games
- Parallelize game evaluation

```python
# Fast mode - no rendering
env = arcade.make("ls20")  # No render_mode

# Batch processing
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(evaluate_game, game_ids)
```

## Toolkit Features

All toolkit features are available for your agent:

### List Games
```python
from toolkit import ARCToolkit

toolkit = ARCToolkit()
games = toolkit.list_games()
print(f"Available games: {len(games)}")
```

### List Actions
```python
actions = toolkit.list_actions()
for action in actions:
    print(f"{action['name']}: {action['description']}")
```

### Submit Action
```python
result = toolkit.submit_action(env, action=1)
print(f"Reward: {result['reward']}")
```

### Scorecards
```python
# Create scorecard
scorecard_id = toolkit.create_scorecard("my_run")

# Get scorecard
scorecard = toolkit.get_scorecard(scorecard_id)
print(scorecard)

# Close scorecard
toolkit.close_scorecard(scorecard_id)
```

### Render Games
```python
# Terminal rendering
toolkit.render_game("ls20", mode="terminal")

# RGB array for processing
rgb_array = toolkit.render_game("ls20", mode="rgb_array")
```

## Troubleshooting

### Python Version Error
```
Error: arc-agi requires Python 3.12+
```

**Solution**: Upgrade Python
```bash
# macOS
brew install python@3.12

# Ubuntu
sudo apt install python3.12

# Windows
# Download from python.org
```

### API Key Errors
```
Error: OpenAI API key not found
```

**Solution**: Set environment variables
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or add to `.env` file:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Import Errors
```
ModuleNotFoundError: No module named 'arc_agi'
```

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Submission Validation Failed
```
❌ Missing required field: results
```

**Solution**: Check submission format
```bash
python kaggle_submission.py --validate-only submissions/your_file.json
```

## Performance Tips

### 1. Fast Iteration
```bash
# Test on subset of games first
python batch_evaluator.py --agent myagent --games ls20 ls21 ls22

# Then full evaluation
python batch_evaluator.py --agent myagent
```

### 2. Memory Management
```python
# Clear agent memory between episodes
agent.reset()

# Limit conversation history for LLM agents
agent.max_history = 10
```

### 3. Action Caching
```python
# Cache LLM responses for similar states
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_action_for_state(state_hash):
    return agent.select_action(state)
```

### 4. Parallel Processing
```python
from concurrent.futures import ProcessPoolExecutor

def evaluate_game_wrapper(game_id):
    agent = create_agent("random")
    evaluator = BatchEvaluator(agent)
    return evaluator.evaluate_game(game_id)

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(evaluate_game_wrapper, game_ids))
```

## Resources

- [Competition Page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3)
- [ARC Prize Documentation](https://docs.arcprize.org)
- [Agent Quickstart](https://docs.arcprize.org/agents-quickstart)
- [Toolkit Reference](https://docs.arcprize.org/toolkit)
- [Game List](https://arcprize.org/tasks)

## Support

For issues or questions:
1. Check this documentation
2. Review example scripts
3. Check competition discussion forum
4. Review ARC Prize documentation

## License

This code is provided for the ARC Prize 2026 competition. Check competition rules for usage restrictions.