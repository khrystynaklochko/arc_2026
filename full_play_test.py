#!/usr/bin/env python3
"""
Full Play Test - Comprehensive test of ARC-AGI-3 implementation
Based on: https://docs.arcprize.org/full-play-test

This script tests all major components:
- Environment setup
- Agent functionality
- Toolkit features
- Batch evaluation
- Submission generation
"""

import sys
import time
from pathlib import Path

# Check Python version
if sys.version_info < (3, 12):
    print("=" * 60)
    print("⚠️  PYTHON VERSION ERROR")
    print("=" * 60)
    print(f"Current Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print("Required: Python 3.12+")
    print("\nPlease upgrade Python to run this test:")
    print("  macOS: brew install python@3.12")
    print("  Ubuntu: sudo apt install python3.12")
    print("  Windows: Download from python.org")
    print("=" * 60)
    sys.exit(1)

try:
    import arc_agi
    from agents import RandomAgent
    from agents.llm_agent import OpenAIAgent, AnthropicAgent
    from toolkit import ARCToolkit
    from environment_wrapper import ARCEnvironmentWrapper
    from batch_evaluator import BatchEvaluator
    from kaggle_submission import KaggleSubmission
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nPlease install dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


def print_section(title):
    """Print section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_basic_environment():
    """Test 1: Basic environment setup and gameplay."""
    print_section("TEST 1: Basic Environment")
    
    try:
        # Create arcade
        arc = arc_agi.Arcade()
        print("✅ Arcade created")
        
        # Make environment
        env = arc.make("ls20", render_mode="terminal")
        print("✅ Environment created (ls20)")
        
        # Reset environment
        observation, info = env.reset()
        print(f"✅ Environment reset")
        print(f"   Observation shape: {observation.shape}")
        print(f"   Info keys: {list(info.keys())}")
        
        # Take some actions
        total_reward = 0
        for step in range(10):
            action = env.action_space.sample()
            observation, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
            if terminated or truncated:
                print(f"✅ Episode ended at step {step + 1}")
                break
        
        print(f"✅ Total reward: {total_reward}")
        
        # Get scorecard
        scorecard = arc.get_scorecard()
        print(f"✅ Scorecard retrieved")
        print(f"   Games played: {scorecard.get('games_played', 'N/A')}")
        
        env.close()
        print("✅ Environment closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_random_agent():
    """Test 2: Random agent functionality."""
    print_section("TEST 2: Random Agent")
    
    try:
        # Create agent
        agent = RandomAgent(num_actions=8)
        print("✅ Random agent created")
        
        # Create environment
        arc = arc_agi.Arcade()
        env = arc.make("ls20")
        
        # Run episode
        observation, info = env.reset()
        agent.reset()
        print("✅ Agent reset")
        
        total_reward = 0
        for step in range(50):
            action = agent.select_action(observation, info)
            observation, reward, terminated, truncated, info = env.step(action)
            agent.update(observation, action, reward, observation, 
                        terminated or truncated, info)
            total_reward += reward
            
            if terminated or truncated:
                break
        
        # Get stats
        stats = agent.get_stats()
        print(f"✅ Episode completed")
        print(f"   Steps: {stats['total_steps']}")
        print(f"   Reward: {stats['total_reward']}")
        print(f"   Episodes: {stats['episodes']}")
        
        env.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_toolkit():
    """Test 3: Toolkit functionality."""
    print_section("TEST 3: Toolkit")
    
    try:
        toolkit = ARCToolkit()
        print("✅ Toolkit created")
        
        # List games
        games = toolkit.list_games()
        print(f"✅ Listed {len(games)} games")
        
        # List actions
        actions = toolkit.list_actions()
        print(f"✅ Listed {len(actions)} actions")
        for action in actions[:3]:
            print(f"   - {action['name']}: {action['description'][:50]}...")
        
        # Create scorecard
        scorecard_id = toolkit.create_scorecard("test_run")
        print(f"✅ Scorecard created: {scorecard_id}")
        
        # Get scorecard
        scorecard = toolkit.get_scorecard(scorecard_id)
        print(f"✅ Scorecard retrieved")
        
        # Close scorecard
        toolkit.close_scorecard(scorecard_id)
        print(f"✅ Scorecard closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_environment_wrapper():
    """Test 4: Environment wrapper."""
    print_section("TEST 4: Environment Wrapper")
    
    try:
        # Create wrapped environment
        env = ARCEnvironmentWrapper("ls20")
        print("✅ Wrapped environment created")
        
        # Reset
        observation, info = env.reset()
        print("✅ Environment reset")
        
        # Take actions
        for step in range(10):
            action = env.action_space.sample()
            observation, reward, terminated, truncated, info = env.step(action)
            
            if terminated or truncated:
                break
        
        # Get history
        history = env.get_history()
        print(f"✅ History retrieved: {len(history)} steps")
        
        # Get stats
        stats = env.get_episode_stats()
        print(f"✅ Episode stats:")
        print(f"   Total reward: {stats['total_reward']}")
        print(f"   Steps: {stats['steps']}")
        
        env.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_batch_evaluator():
    """Test 5: Batch evaluation."""
    print_section("TEST 5: Batch Evaluator")
    
    try:
        # Create agent
        agent = RandomAgent(name="TestAgent")
        print("✅ Agent created")
        
        # Create evaluator
        evaluator = BatchEvaluator(agent, output_dir="test_evaluations")
        print("✅ Evaluator created")
        
        # Evaluate on small subset
        test_games = ["ls20", "ls21"]
        print(f"✅ Evaluating on {len(test_games)} games...")
        
        metrics = evaluator.evaluate_batch(
            game_ids=test_games,
            max_steps=50,
            verbose=False
        )
        
        print(f"✅ Evaluation complete")
        print(f"   Success rate: {metrics.success_rate:.1%}")
        print(f"   Average reward: {metrics.average_reward:.2f}")
        print(f"   Total time: {metrics.total_time:.2f}s")
        
        # Save results
        json_file = evaluator.save_results("test_results.json")
        print(f"✅ Results saved: {json_file}")
        
        csv_file = evaluator.save_csv("test_results.csv")
        print(f"✅ CSV saved: {csv_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_kaggle_submission():
    """Test 6: Kaggle submission generation."""
    print_section("TEST 6: Kaggle Submission")
    
    try:
        # Create agent
        agent = RandomAgent(name="TestSubmission")
        print("✅ Agent created")
        
        # Create submission handler
        submission = KaggleSubmission(agent, output_dir="test_submissions")
        print("✅ Submission handler created")
        
        # Run on small subset
        test_games = ["ls20", "ls21"]
        print(f"✅ Running on {len(test_games)} games...")
        
        submission.run_on_all_games(
            game_ids=test_games,
            max_steps=50
        )
        
        print(f"✅ Games completed")
        
        # Save submission
        filepath = submission.save_submission("test_submission.json")
        print(f"✅ Submission saved: {filepath}")
        
        # Validate submission
        is_valid = submission.validate_submission(filepath)
        if is_valid:
            print("✅ Submission validated successfully")
        else:
            print("⚠️  Submission validation failed")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_llm_agents():
    """Test 7: LLM agent availability (without API calls)."""
    print_section("TEST 7: LLM Agents")
    
    try:
        # Check OpenAI agent
        try:
            agent = OpenAIAgent(model="gpt-4", name="TestGPT4")
            print("✅ OpenAI agent class available")
            print(f"   Agent name: {agent.name}")
        except Exception as e:
            print(f"⚠️  OpenAI agent: {e}")
        
        # Check Anthropic agent
        try:
            agent = AnthropicAgent(model="claude-3-opus-20240229", name="TestClaude")
            print("✅ Anthropic agent class available")
            print(f"   Agent name: {agent.name}")
        except Exception as e:
            print(f"⚠️  Anthropic agent: {e}")
        
        print("\n⚠️  Note: LLM agents require API keys to run")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 60)
    print("  ARC-AGI-3 FULL PLAY TEST")
    print("  Testing all components")
    print("=" * 60)
    
    start_time = time.time()
    
    tests = [
        ("Basic Environment", test_basic_environment),
        ("Random Agent", test_random_agent),
        ("Toolkit", test_toolkit),
        ("Environment Wrapper", test_environment_wrapper),
        ("Batch Evaluator", test_batch_evaluator),
        ("Kaggle Submission", test_kaggle_submission),
        ("LLM Agents", test_llm_agents),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            results.append((name, False))
    
    elapsed_time = time.time() - start_time
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {name}")
    
    print("\n" + "-" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"Time: {elapsed_time:.2f}s")
    print("-" * 60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ ARC-AGI-3 implementation is working correctly")
        print("\nNext steps:")
        print("  1. Run: python batch_evaluator.py --agent random")
        print("  2. Run: python kaggle_submission.py --agent random")
        print("  3. Upload submission to Kaggle")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("Please check the errors above and fix issues")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

# Made with Bob
