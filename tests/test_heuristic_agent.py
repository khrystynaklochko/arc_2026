import unittest
from agents.heuristic_agent import HeuristicAgent

class TestHeuristicAgent(unittest.TestCase):
    def test_act_returns_action(self):
        agent = HeuristicAgent()
        obs = {'available_actions': [0, 1, 2]}
        action = agent.act(obs)
        self.assertIn(action, [0, 1, 2])

    def test_act_empty_actions(self):
        agent = HeuristicAgent()
        obs = {'available_actions': []}
        action = agent.act(obs)
        self.assertIsNone(action)

if __name__ == '__main__':
    unittest.main()
