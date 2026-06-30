# Local vs Online Development

Guide to developing and testing ARC-AGI-3 agents locally before deploying online.

## Overview

ARC-AGI-3 supports two development modes:
- **Local (Offline)**: Development and testing on your machine
- **Online**: Deployment to ARC Prize servers or Kaggle

This guide helps you develop locally and transition smoothly to online deployment.

## Local Development

### Advantages

✅ **Fast Iteration**
- No network latency
- Instant feedback
- Quick debugging cycles

✅ **Cost Effective**
- No API rate limits
- Free compute resources
- Unlimited testing

✅ **Full Control**
- Complete environment access
- Detailed logging
- Custom modifications

✅ **Privacy**
- Data stays local
- No external dependencies
- Secure development

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure for local development
cp .env.example .env
# Edit .env - API key optional for local testing
```

### Local Testing

```python
import arc_agi

# Local environment - no API calls
arc = arc_agi.Arcade()
env = arc.make("ls20", render_mode="terminal")

# Test locally
observation, info = env.reset()
for step in range(100):
    action = env.action_space.sample()
    observation, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break

print(arc.get_scorecard())
```

### Local Agent Development

```python
from agents import RandomAgent

# Develop agent locally
agent = RandomAgent()

# Test on single game
env = arc_agi.Arcade().make("ls20")
observation, info = env.reset()
agent.reset()

for step in range(100):
    action = agent.select_action(observation, info)
    observation, reward, terminated, truncated, info = env.step(action)
    agent.update(observation, action, reward, observation, 
                terminated or truncated, info)
    if terminated or truncated:
        break

# Check performance
print(agent.get_stats())
```

### Local Batch Testing

```bash
# Test on multiple games locally
python batch_evaluator.py --agent random --games ls20 ls21 ls22

# Full local evaluation
python batch_evaluator.py --agent random
```

## Online Deployment

### Advantages

✅ **Official Evaluation**
- Real competition metrics
- Leaderboard ranking
- Prize eligibility

✅ **Scalability**
- Cloud compute resources
- Parallel processing
- Large-scale testing

✅ **Validation**
- Official test sets
- Fair comparison
- Standardized environment

### Prerequisites

1. **API Key** (for ARC Prize servers)
```bash
# Get API key from https://docs.arcprize.org/api-keys
export ARC_API_KEY="your-key-here"
```

2. **Kaggle Account** (for competition)
- Sign up at https://www.kaggle.com
- Join competition: https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3

### Online Testing

```python
import arc_agi
import os

# Configure for online
os.environ['ARC_API_KEY'] = 'your-key-here'

# Online environment - uses API
arc = arc_agi.Arcade(online=True)
env = arc.make("ls20")

# Test online (counts toward rate limits)
observation, info = env.reset()
# ... play game ...
```

### Kaggle Submission

```bash
# Generate submission file
python kaggle_submission.py --agent openai --model gpt-4

# Validate submission
python kaggle_submission.py --validate-only submissions/submission_*.json

# Upload to Kaggle
# Go to: https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3
# Click "Submit Predictions"
# Upload your submission_*.json file
```

## Development Workflow

### Recommended Workflow

```
1. Develop Locally
   ↓
2. Test Locally (batch_evaluator.py)
   ↓
3. Validate Locally (multiple runs)
   ↓
4. Test Online (small subset)
   ↓
5. Submit to Kaggle
   ↓
6. Iterate based on results
```

### Step-by-Step

#### 1. Local Development

```bash
# Create and test agent locally
python play.py  # Single game test

# Batch test locally
python batch_evaluator.py --agent myagent --games ls20 ls21 ls22
```

#### 2. Local Validation

```bash
# Run multiple times to check consistency
for i in {1..3}; do
    python batch_evaluator.py --agent myagent --output-json run_$i.json
done

# Compare results
python compare_results.py run_*.json
```

#### 3. Online Testing

```bash
# Test on small subset online
python kaggle_submission.py --agent myagent --games ls20 ls21 ls22

# Check results before full submission
```

#### 4. Full Submission

```bash
# Generate full submission
python kaggle_submission.py --agent myagent

# Validate
python kaggle_submission.py --validate-only submissions/submission_*.json

# Upload to Kaggle
```

## Key Differences

### Environment Behavior

| Feature | Local | Online |
|---------|-------|--------|
| **Speed** | Fast (2000+ FPS) | Slower (network latency) |
| **Cost** | Free | API rate limits |
| **Games** | All available | May be restricted |
| **Rendering** | Terminal/RGB | Limited |
| **Debugging** | Full access | Limited |
| **Persistence** | Local files | Cloud storage |

### API Differences

**Local:**
```python
# No API key needed
arc = arc_agi.Arcade()
env = arc.make("ls20")
```

**Online:**
```python
# API key required
import os
os.environ['ARC_API_KEY'] = 'your-key-here'
arc = arc_agi.Arcade(online=True)
env = arc.make("ls20")
```

### Rate Limits

**Local:**
- No limits
- Unlimited testing
- Instant feedback

**Online:**
- API rate limits apply
- Limited submissions per day
- Network delays

## Best Practices

### 1. Develop Locally First

```python
# Always test locally before online
def test_agent_locally(agent, num_games=10):
    """Test agent on local games first."""
    from batch_evaluator import BatchEvaluator
    
    evaluator = BatchEvaluator(agent)
    metrics = evaluator.evaluate_batch(
        game_ids=[f"ls{20+i}" for i in range(num_games)],
        verbose=True
    )
    
    if metrics.success_rate < 0.5:
        print("⚠️  Agent needs improvement before online testing")
        return False
    
    print("✅ Agent ready for online testing")
    return True
```

### 2. Use Environment Variables

```python
# .env file for configuration
import os
from dotenv import load_dotenv

load_dotenv()

# Switch between local and online
USE_ONLINE = os.getenv('USE_ONLINE', 'false').lower() == 'true'

if USE_ONLINE:
    arc = arc_agi.Arcade(online=True)
else:
    arc = arc_agi.Arcade()
```

### 3. Cache Results Locally

```python
import json
from pathlib import Path

def cache_results(game_id, result):
    """Cache results locally to avoid re-running."""
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)
    
    cache_file = cache_dir / f"{game_id}.json"
    with open(cache_file, 'w') as f:
        json.dump(result, f)

def get_cached_result(game_id):
    """Get cached result if available."""
    cache_file = Path("cache") / f"{game_id}.json"
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None
```

### 4. Gradual Online Testing

```python
# Test progressively
test_sets = {
    "quick": ["ls20", "ls21"],
    "medium": ["ls20", "ls21", "ls22", "ft09", "ft10"],
    "full": None  # All games
}

# Start with quick test
results = test_online(agent, test_sets["quick"])
if results["success_rate"] > 0.7:
    # Move to medium test
    results = test_online(agent, test_sets["medium"])
    if results["success_rate"] > 0.6:
        # Full submission
        results = test_online(agent, test_sets["full"])
```

### 5. Monitor Costs

```python
class CostTracker:
    """Track API costs during online testing."""
    
    def __init__(self):
        self.api_calls = 0
        self.tokens_used = 0
        self.estimated_cost = 0.0
    
    def track_call(self, tokens, cost_per_token=0.00003):
        """Track an API call."""
        self.api_calls += 1
        self.tokens_used += tokens
        self.estimated_cost += tokens * cost_per_token
    
    def report(self):
        """Print cost report."""
        print(f"API Calls: {self.api_calls}")
        print(f"Tokens Used: {self.tokens_used:,}")
        print(f"Estimated Cost: ${self.estimated_cost:.2f}")

# Usage
tracker = CostTracker()
# ... run agent ...
tracker.report()
```

## Troubleshooting

### Local Issues

**Problem**: Games not loading locally
```bash
# Solution: Check installation
pip install --upgrade arc-agi
python -c "import arc_agi; print(arc_agi.__version__)"
```

**Problem**: Slow local performance
```python
# Solution: Disable rendering
env = arc.make("ls20")  # No render_mode
```

### Online Issues

**Problem**: API key not working
```bash
# Solution: Verify key
echo $ARC_API_KEY
# Get new key from https://docs.arcprize.org/api-keys
```

**Problem**: Rate limit exceeded
```python
# Solution: Add delays between calls
import time
time.sleep(1)  # Wait 1 second between games
```

**Problem**: Network timeouts
```python
# Solution: Add retry logic
import time

def run_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

## Migration Checklist

### Local to Online

- [ ] Test agent locally with batch_evaluator.py
- [ ] Achieve target success rate (>50%)
- [ ] Validate on multiple local runs
- [ ] Set up API key in .env
- [ ] Test on small subset online
- [ ] Monitor costs and rate limits
- [ ] Generate full submission
- [ ] Validate submission file
- [ ] Upload to Kaggle
- [ ] Monitor leaderboard results

### Online to Local (for debugging)

- [ ] Download submission results from Kaggle
- [ ] Identify failing games
- [ ] Reproduce failures locally
- [ ] Debug with full logging
- [ ] Fix issues
- [ ] Re-test locally
- [ ] Re-submit online

## Configuration Examples

### Local Development Config

```python
# config_local.py
CONFIG = {
    "mode": "local",
    "render_mode": "terminal",
    "max_steps": 100,
    "verbose": True,
    "save_recordings": True,
    "cache_results": True
}
```

### Online Deployment Config

```python
# config_online.py
CONFIG = {
    "mode": "online",
    "render_mode": None,  # No rendering online
    "max_steps": 100,
    "verbose": False,  # Reduce output
    "save_recordings": False,  # Save bandwidth
    "cache_results": False,  # Use fresh data
    "retry_on_error": True,
    "max_retries": 3
}
```

### Unified Config

```python
# config.py
import os

MODE = os.getenv('MODE', 'local')

if MODE == 'local':
    from config_local import CONFIG
else:
    from config_online import CONFIG

# Usage
from config import CONFIG
env = arc.make("ls20", render_mode=CONFIG["render_mode"])
```

## Resources

- [Quick Start Script](./quick_start_kaggle.sh)
- [Batch Evaluator](./batch_evaluator.py)
- [Kaggle Submission](./kaggle_submission.py)
- [ARC Prize Documentation](https://docs.arcprize.org)
- [Kaggle Competition](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3)