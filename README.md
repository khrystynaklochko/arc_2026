# ARC-AGI-3 Development Environment - Kaggle Ready

Complete development environment for the ARC-AGI-3 Interactive Reasoning Benchmark and [Kaggle Competition](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3).

## 🚀 Quick Start for Kaggle

```bash
# Run the quick start script
./quick_start_kaggle.sh
```

**See [KAGGLE.md](KAGGLE.md) for complete Kaggle competition guide.**

---

# ARC-AGI-3 App

This project is set up to work with ARC-AGI-3, an Interactive Reasoning Benchmark designed to measure an AI Agent's ability to generalize in novel, unseen environments.

## Requirements

- **Python 3.12 or higher** (Current system: Python 3.9.13)

⚠️ **Important**: The `arc-agi` package requires Python 3.12+. You'll need to upgrade your Python version to use this toolkit.

## Setup

### 1. Upgrade Python (if needed)

Install Python 3.12 or higher:
- **macOS**: `brew install python@3.12`
- **Linux**: Use your package manager or [pyenv](https://github.com/pyenv/pyenv)
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Your API Key (Optional)

Copy `.env.example` to `.env` and add your API key:

```bash
cp .env.example .env
```

Then edit `.env` and replace `your-api-key-here` with your actual API key from [https://docs.arcprize.org/api-keys](https://docs.arcprize.org/api-keys).

If no key is provided, an anonymous key will be used.

### 4. Run Your First Game

```bash
python play.py
```

You should see the game render in your terminal and a scorecard with your results.

## Using Agents

This project includes several agent implementations:

### Run the Random Agent
```bash
python run_agent.py
```

This runs a baseline random agent that selects actions randomly.

### Available Agents

1. **RandomAgent** - Baseline agent for comparison
2. **OpenAIAgent** - Uses GPT models (requires `OPENAI_API_KEY`)
3. **AnthropicAgent** - Uses Claude models (requires `ANTHROPIC_API_KEY`)


## Kaggle Competition

### Generate Submission

```bash
# Using Random Agent (baseline)
python kaggle_submission.py --agent random

# Using OpenAI GPT-4
python kaggle_submission.py --agent openai --model gpt-4

# Using Anthropic Claude
python kaggle_submission.py --agent anthropic --model claude-3-opus-20240229
```

### Batch Evaluation

```bash
# Evaluate agent on all games
python batch_evaluator.py --agent random

# Evaluate on specific games
python batch_evaluator.py --agent openai --games ls20 ls21 ls22

# Save results
python batch_evaluator.py --agent random --output-json results.json --output-csv results.csv
```

### Validate Submission

```bash
python kaggle_submission.py --validate-only submissions/submission_*.json
```

**See [KAGGLE.md](KAGGLE.md) for complete guide with strategies, tips, and troubleshooting.**

## Project Structure

```
arc/
├── agents/                      # Agent implementations
│   ├── base_agent.py           # Abstract base class
│   ├── random_agent.py         # Random baseline agent
│   └── llm_agent.py            # LLM-powered agents (OpenAI, Anthropic)
├── play.py                     # Basic game example
├── run_agent.py                # Agent runner
├── kaggle_submission.py        # Kaggle submission generator ⭐
├── batch_evaluator.py          # Batch evaluation pipeline ⭐
├── toolkit.py                  # Complete toolkit implementation ⭐
├── environment_wrapper.py      # Enhanced environment wrapper ⭐
├── list_actions_example.py     # Action listing demo
├── submit_action_example.py    # Action submission demo
├── quick_start_kaggle.sh       # Kaggle quick start script ⭐
├── requirements.txt            # Python dependencies
├── .env                        # API keys (create from .env.example)
├── README.md                   # This file
├── KAGGLE.md                   # Kaggle competition guide ⭐
├── AGENTS.md                   # Agent development guide
├── GAME_SCHEMA.md              # Game structure reference
└── ACTIONS.md                  # Actions reference
```

## Documentation

- **[KAGGLE.md](KAGGLE.md)** - Complete Kaggle competition guide
- **[AGENTS.md](AGENTS.md)** - Agent development guide
- **[GAME_SCHEMA.md](GAME_SCHEMA.md)** - Game structure reference
- **[ACTIONS.md](ACTIONS.md)** - Actions reference
- [ARC Prize Docs](https://docs.arcprize.org) - Official documentation

## Competition Links

- [Kaggle Competition](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3)
- [ARC Prize Website](https://arcprize.org)
- [Documentation](https://docs.arcprize.org)
See [AGENTS.md](AGENTS.md) for detailed documentation on creating and using agents.

## Next Steps

- **Make it fast** - Remove `render_mode="terminal"` to hit +2K FPS
- **Try different games** - Change `"ls20"` to other game IDs like `"ft09"`. See available games at [arcprize.org/tasks](https://arcprize.org/tasks)
- **Build your own agent** - See [AGENTS.md](AGENTS.md) for examples and templates
- **Explore the toolkit** - Check out the [ARC-AGI Toolkit](https://docs.arcprize.org/toolkit/overview)

## Resources

- [ARC-AGI-3 Documentation](https://docs.arcprize.org)
- [ARC Prize Website](https://arcprize.org)
- [GitHub Repository](https://github.com/arcprize/arc-agi)