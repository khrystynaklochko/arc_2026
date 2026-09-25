import logging
import arc_agi
from typing import Any, Dict, Tuple, Optional

logging.basicConfig(filename='submission_run.log', level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

class ARCEnvironmentWrapper:
    def __init__(self, game_id: str, render_mode: Optional[str] = None):
        self.game_id = game_id
        self.arcade = arc_agi.Arcade()
        self.env = self.arcade.make(game_id, render_mode=render_mode)
    
    def reset(self, **kwargs) -> Tuple[Any, Dict]:
        try:
            return self.env.reset(**kwargs)
        except Exception as e:
            logging.error(f"Reset error for {self.game_id}: {e}")
            raise
            
    def step(self, action: int) -> Tuple[Any, float, bool, bool, Dict]:
        try:
            res = self.env.step(action)
            logging.info(f"Action {action} on {self.game_id} successful")
            return res
        except Exception as e:
            logging.error(f"Step error for {self.game_id}: {e}")
            raise

    def close(self):
        self.env.close()