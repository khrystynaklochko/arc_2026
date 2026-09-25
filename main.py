import sys
from pathlib import Path
from agents.random_agent import RandomAgent
import arc_agi

def main(game_subset=None):
    arcade = arc_agi.Arcade()
    games = game_subset or [g.game_id for g in arcade.get_environments()[:5]]
    agent = RandomAgent()
    for game_id in games:
        print(f"Executing {game_id}...")
        env = arcade.make(game_id)
        obs = env.reset()
        action = agent.select_action(obs, {})
        env.step(action)
        env.close()
    print("Test cycle complete.")

if __name__ == "__main__":
    main()