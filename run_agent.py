"""
Run an agent on ARC-AGI-3 environments
"""

import arc_agi
from arcengine import GameAction
from agents import RandomAgent
from agents.llm_agent import LLMAgent, OpenAIAgent, AnthropicAgent


def run_episode(env, agent, max_steps: int = 100, render: bool = True):
    """
    Run a single episode with an agent.
    
    Args:
        env: ARC-AGI environment
        agent: Agent to run
        max_steps: Maximum steps per episode
        render: Whether to render the environment
        
    Returns:
        Total reward for the episode
    """
    observation, info = env.reset()
    agent.reset()
    
    total_reward = 0
    done = False
    step = 0
    
    print(f"\n{'='*60}")
    print(f"Starting episode with {agent.name}")
    print(f"{'='*60}\n")
    
    while not done and step < max_steps:
        # Agent selects action
        action = agent.select_action(observation, info)
        
        # Take action in environment
        next_observation, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        
        # Update agent
        agent.update(observation, action, reward, next_observation, done, info)
        
        # Update state
        observation = next_observation
        total_reward += reward
        step += 1
        
        if render and step % 10 == 0:
            print(f"Step {step}: Action={action}, Reward={reward:.2f}, Total={total_reward:.2f}")
    
    print(f"\nEpisode finished after {step} steps")
    print(f"Total reward: {total_reward:.2f}")
    print(f"{'='*60}\n")
    
    return total_reward


def main():
    """Main function to run agents."""
    
    # Initialize ARC-AGI
    arc = arc_agi.Arcade()
    
    # Create environment (with terminal rendering for visualization)
    print("Creating ARC-AGI-3 environment...")
    env = arc.make("ls20", render_mode="terminal")
    
    # Test different agents
    agents_to_test = [
        RandomAgent(num_actions=10, name="RandomAgent"),
        # Uncomment to test LLM agents (requires API keys)
        # OpenAIAgent(model="gpt-4", name="GPT-4 Agent"),
        # AnthropicAgent(model="claude-3-opus-20240229", name="Claude Agent"),
    ]
    
    results = {}
    
    for agent in agents_to_test:
        print(f"\n{'#'*60}")
        print(f"Testing: {agent.name}")
        print(f"{'#'*60}")
        
        # Run multiple episodes
        num_episodes = 3
        episode_rewards = []
        
        for episode in range(num_episodes):
            print(f"\n--- Episode {episode + 1}/{num_episodes} ---")
            reward = run_episode(env, agent, max_steps=50, render=True)
            episode_rewards.append(reward)
        
        # Calculate statistics
        avg_reward = sum(episode_rewards) / len(episode_rewards)
        results[agent.name] = {
            'episodes': episode_rewards,
            'average': avg_reward,
            'stats': agent.get_stats()
        }
        
        print(f"\n{agent.name} Results:")
        print(f"  Episodes: {episode_rewards}")
        print(f"  Average Reward: {avg_reward:.2f}")
        print(f"  Agent Stats: {agent.get_stats()}")
    
    # Print final scorecard
    print("\n" + "="*60)
    print("FINAL SCORECARD")
    print("="*60)
    print(arc.get_scorecard())
    
    # Print comparison
    print("\n" + "="*60)
    print("AGENT COMPARISON")
    print("="*60)
    for agent_name, result in results.items():
        print(f"\n{agent_name}:")
        print(f"  Average Reward: {result['average']:.2f}")
        print(f"  Total Episodes: {result['stats']['episodes']}")


if __name__ == "__main__":
    main()

# Made with Bob
