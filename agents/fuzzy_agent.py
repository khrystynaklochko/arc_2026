"""
Fuzzy Recursive World-Model Agent for ARC-AGI-3

Combines:
- Fuzzy logic for action scoring
- UCB exploration for uncertainty
- Belief/hypothesis updates
- State graph memory
- BFS planning
- Tiny Recursive Model scoring
"""

from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import math
import random
import numpy as np
from typing import Any, Dict, List, Tuple, Optional, Callable
from agents.base_agent import BaseAgent


# ============================================================================
# Core Data Structures
# ============================================================================

class GameAction(Enum):
    """ARC-AGI-3 action space"""
    RESET = 0
    ACTION1 = 1  # Up
    ACTION2 = 2  # Down
    ACTION3 = 3  # Left
    ACTION4 = 4  # Right
    ACTION5 = 5  # Special/Interact
    ACTION6 = 6  # Coordinate-based
    ACTION7 = 7  # Undo


@dataclass(frozen=True)
class State:
    """Symbolic abstraction of game frame"""
    grid_hash: int
    object_count: int
    unique_colors: Tuple[int, ...]
    grid_shape: Tuple[int, int]
    changed_cells: int = 0
    
    @classmethod
    def from_observation(cls, observation: np.ndarray, prev_obs: Optional[np.ndarray] = None):
        """Create state from observation"""
        # Handle FrameDataRaw objects from arc-agi API
        if hasattr(observation, 'frame') and isinstance(observation.frame, list):
            # Extract the grid from FrameDataRaw.frame (list of numpy arrays)
            if len(observation.frame) > 0:
                observation = observation.frame[0]
            else:
                # Fallback to empty grid
                observation = np.zeros((10, 10), dtype=np.int8)
        
        if not isinstance(observation, np.ndarray):
            observation = np.array(observation)
        
        # Also handle prev_obs if it's FrameDataRaw
        if prev_obs is not None:
            if hasattr(prev_obs, 'frame') and isinstance(prev_obs.frame, list):
                if len(prev_obs.frame) > 0:
                    prev_obs = prev_obs.frame[0]
                else:
                    prev_obs = None
        
        grid_hash = hash(observation.tobytes())
        object_count = np.count_nonzero(observation)
        unique_colors = tuple(sorted(set(observation.flatten().tolist())))
        grid_shape = observation.shape
        
        changed_cells = 0
        if prev_obs is not None and isinstance(prev_obs, np.ndarray):
            changed_cells = np.sum(observation != prev_obs)
        
        return cls(
            grid_hash=grid_hash,
            object_count=object_count,
            unique_colors=unique_colors,
            grid_shape=grid_shape,
            changed_cells=changed_cells
        )


@dataclass
class Transition:
    """State transition record"""
    from_state: State
    action: GameAction
    to_state: State
    changed: bool
    reward: float = 0.0
    info: Dict = field(default_factory=dict)


# ============================================================================
# Fuzzy Logic Components
# ============================================================================

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to range"""
    return max(lo, min(hi, x))


def fuzzy_high(x: float, start: float = 0.5, end: float = 1.0) -> float:
    """Fuzzy membership: high"""
    if x <= start:
        return 0.0
    if x >= end:
        return 1.0
    return (x - start) / (end - start)


def fuzzy_low(x: float, start: float = 0.0, end: float = 0.5) -> float:
    """Fuzzy membership: low"""
    if x <= start:
        return 1.0
    if x >= end:
        return 0.0
    return 1.0 - ((x - start) / (end - start))


def fuzzy_medium(x: float, center: float = 0.5, width: float = 0.3) -> float:
    """Fuzzy membership: medium (triangle)"""
    distance = abs(x - center)
    return clamp(1.0 - distance / width)


@dataclass
class ActionFeatures:
    """Features for fuzzy action scoring"""
    novelty: float = 0.5
    progress: float = 0.5
    danger: float = 0.5
    reversibility: float = 0.5
    information_gain: float = 0.5
    loop_risk: float = 0.5
    trm_prior: float = 0.5
    state_value: float = 0.5


def fuzzy_action_score(features: ActionFeatures) -> float:
    """
    Sugeno-style fuzzy inference for action scoring.
    Returns crisp score from 0 to 1.
    """
    # Compute fuzzy memberships
    novelty_high = fuzzy_high(features.novelty)
    progress_high = fuzzy_high(features.progress)
    danger_high = fuzzy_high(features.danger)
    danger_low = fuzzy_low(features.danger)
    reversible_high = fuzzy_high(features.reversibility)
    info_high = fuzzy_high(features.information_gain)
    loop_high = fuzzy_high(features.loop_risk)
    trm_high = fuzzy_high(features.trm_prior)
    value_high = fuzzy_high(features.state_value)
    
    # Fuzzy rules with weights and consequents
    rules = []
    
    # Rule 1: Explore new safe states
    weight = min(novelty_high, danger_low)
    rules.append((weight, 0.80))
    
    # Rule 2: Progress + TRM agreement
    weight = min(progress_high, trm_high)
    rules.append((weight, 0.90))
    
    # Rule 3: Information gain + reversibility
    weight = min(info_high, reversible_high)
    rules.append((weight, 0.75))
    
    # Rule 4: Avoid danger
    weight = danger_high
    rules.append((weight, 0.05))
    
    # Rule 5: Avoid loops
    weight = loop_high
    rules.append((weight, 0.10))
    
    # Rule 6: TRM + safety
    weight = min(trm_high, danger_low)
    rules.append((weight, 0.85))
    
    # Rule 7: High value states
    weight = min(value_high, danger_low)
    rules.append((weight, 0.88))
    
    # Rule 8: Novel + informative
    weight = min(novelty_high, info_high)
    rules.append((weight, 0.70))
    
    # Sugeno defuzzification
    numerator = sum(w * score for w, score in rules)
    denominator = sum(w for w, _ in rules)
    
    if denominator == 0:
        return 0.5
    
    return clamp(numerator / denominator)


# ============================================================================
# UCB Explorer
# ============================================================================

class UCBExplorer:
    """Upper Confidence Bound exploration strategy"""
    
    def __init__(self, c: float = 1.4):
        self.c = c
        self.counts = defaultdict(int)
        self.values = defaultdict(float)
        self.total_visits = 0
    
    def select(self, state: State, actions: List[GameAction]) -> GameAction:
        """Select action using UCB"""
        self.total_visits += 1
        
        best_action = None
        best_score = -float("inf")
        
        for action in actions:
            key = (state.grid_hash, action)
            
            # Prioritize unexplored actions
            if self.counts[key] == 0:
                return action
            
            # UCB formula
            mean_value = self.values[key]
            bonus = self.c * math.sqrt(
                math.log(self.total_visits + 1) / self.counts[key]
            )
            score = mean_value + bonus
            
            if score > best_score:
                best_score = score
                best_action = action
        
        return best_action or random.choice(actions)
    
    def update(self, state: State, action: GameAction, reward: float):
        """Update UCB statistics"""
        key = (state.grid_hash, action)
        self.counts[key] += 1
        
        n = self.counts[key]
        old_value = self.values[key]
        self.values[key] = old_value + (reward - old_value) / n


# ============================================================================
# Hypothesis Bank
# ============================================================================

@dataclass
class Hypothesis:
    """Belief about game mechanics"""
    name: str
    confidence: float = 0.5
    evidence_count: int = 0


class HypothesisBank:
    """Maintains fuzzy beliefs about game rules"""
    
    def __init__(self):
        self.hypotheses: Dict[str, Hypothesis] = {
            "rare_color_is_goal": Hypothesis("rare_color_is_goal", 0.5),
            "changed_object_is_important": Hypothesis("changed_object_is_important", 0.5),
            "repeated_action_matters": Hypothesis("repeated_action_matters", 0.3),
            "color_pattern_matters": Hypothesis("color_pattern_matters", 0.4),
            "new_state_is_progress": Hypothesis("new_state_is_progress", 0.6),
            "object_count_matters": Hypothesis("object_count_matters", 0.5),
            "grid_symmetry_matters": Hypothesis("grid_symmetry_matters", 0.4),
        }
    
    def update(self, transition: Transition):
        """Update hypotheses based on transition"""
        # State changed
        if transition.changed:
            self.increase("changed_object_is_important", 0.08)
            self.increase("new_state_is_progress", 0.04)
        else:
            self.decrease("changed_object_is_important", 0.03)
        
        # Positive reward
        if transition.reward > 0.5:
            self.increase("new_state_is_progress", 0.12)
            if transition.to_state.object_count != transition.from_state.object_count:
                self.increase("object_count_matters", 0.10)
        
        # Negative reward
        if transition.reward < -0.3:
            self.decrease("new_state_is_progress", 0.08)
        
        # Color changes
        if transition.to_state.unique_colors != transition.from_state.unique_colors:
            self.increase("color_pattern_matters", 0.06)
        
        # Repeated action
        if transition.action in [GameAction.ACTION1, GameAction.ACTION2, 
                                GameAction.ACTION3, GameAction.ACTION4]:
            self.increase("repeated_action_matters", 0.02)
    
    def increase(self, name: str, amount: float):
        """Increase hypothesis confidence"""
        h = self.hypotheses[name]
        h.confidence = clamp(h.confidence + amount)
        h.evidence_count += 1
    
    def decrease(self, name: str, amount: float):
        """Decrease hypothesis confidence"""
        h = self.hypotheses[name]
        h.confidence = clamp(h.confidence - amount)
        h.evidence_count += 1
    
    def get(self, name: str) -> float:
        """Get hypothesis confidence"""
        return self.hypotheses[name].confidence
    
    def get_top_hypotheses(self, n: int = 3) -> List[Tuple[str, float]]:
        """Get top N hypotheses by confidence"""
        sorted_hyps = sorted(
            self.hypotheses.items(),
            key=lambda x: x[1].confidence,
            reverse=True
        )
        return [(name, h.confidence) for name, h in sorted_hyps[:n]]


# ============================================================================
# State Graph Memory
# ============================================================================

class StateGraph:
    """Memory of explored states and transitions"""
    
    def __init__(self):
        self.edges: Dict[int, List[Tuple[GameAction, State]]] = defaultdict(list)
        self.states: Dict[int, State] = {}
        self.visit_counts = defaultdict(int)
        self.rewards: Dict[int, List[float]] = defaultdict(list)
    
    def add_state(self, state: State):
        """Add state to graph"""
        self.states[state.grid_hash] = state
        self.visit_counts[state.grid_hash] += 1
    
    def add_transition(self, transition: Transition):
        """Add transition to graph"""
        self.add_state(transition.from_state)
        self.add_state(transition.to_state)
        
        self.edges[transition.from_state.grid_hash].append(
            (transition.action, transition.to_state)
        )
        
        self.rewards[transition.from_state.grid_hash].append(transition.reward)
    
    def is_known(self, state: State) -> bool:
        """Check if state is known"""
        return state.grid_hash in self.states
    
    def visits(self, state: State) -> int:
        """Get visit count for state"""
        return self.visit_counts[state.grid_hash]
    
    def average_reward(self, state: State) -> float:
        """Get average reward from state"""
        rewards = self.rewards[state.grid_hash]
        return sum(rewards) / len(rewards) if rewards else 0.0
    
    def bfs_to_goal(
        self, 
        start: State, 
        goal_fn: Callable[[State], bool],
        max_depth: int = 20
    ) -> Optional[List[GameAction]]:
        """BFS search for goal state"""
        queue = deque()
        queue.append((start, [], 0))
        seen = {start.grid_hash}
        
        while queue:
            state, path, depth = queue.popleft()
            
            if depth > max_depth:
                continue
            
            if goal_fn(state):
                return path
            
            for action, next_state in self.edges.get(state.grid_hash, []):
                if next_state.grid_hash not in seen:
                    seen.add(next_state.grid_hash)
                    queue.append((next_state, path + [action], depth + 1))
        
        return None


# ============================================================================
# Tiny Recursive Model Scorer
# ============================================================================

class TinyRecursiveModelScorer:
    """
    Placeholder for Tiny Recursive Model.
    In production, replace with actual neural model.
    """
    
    def __init__(self):
        self.action_priors = {
            GameAction.ACTION1: 0.55,  # Movement actions
            GameAction.ACTION2: 0.55,
            GameAction.ACTION3: 0.55,
            GameAction.ACTION4: 0.55,
            GameAction.ACTION5: 0.45,  # Special action
            GameAction.ACTION6: 0.35,  # Coordinate action
            GameAction.ACTION7: 0.30,  # Undo
            GameAction.RESET: 0.10,    # Reset
        }
    
    def score_action(self, state: State, action: GameAction) -> float:
        """Score action given state"""
        base_score = self.action_priors.get(action, 0.5)
        
        # Adjust based on state features
        if state.object_count > 10:
            # More objects might need special actions
            if action == GameAction.ACTION5:
                base_score += 0.10
        
        if len(state.unique_colors) > 3:
            # Complex color patterns might need exploration
            if action in [GameAction.ACTION1, GameAction.ACTION2, 
                         GameAction.ACTION3, GameAction.ACTION4]:
                base_score += 0.05
        
        return clamp(base_score)
    
    def score_state_value(self, state: State) -> float:
        """Estimate state value"""
        # Heuristic: more unique colors and objects might indicate progress
        color_score = len(state.unique_colors) / 10.0
        object_score = min(state.object_count / 50.0, 1.0)
        change_score = min(state.changed_cells / 20.0, 1.0)
        
        return clamp((color_score + object_score + change_score) / 3.0)


# ============================================================================
# Feature Extraction
# ============================================================================

def estimate_action_features(
    state: State,
    action: GameAction,
    graph: StateGraph,
    hypotheses: HypothesisBank,
    trm: TinyRecursiveModelScorer,
) -> ActionFeatures:
    """Estimate features for action scoring"""
    
    visits = graph.visits(state)
    
    # Novelty: inverse of visits
    novelty = 1.0 / (1.0 + visits)
    
    # Progress: from hypotheses
    progress = hypotheses.get("new_state_is_progress")
    
    # Danger: low for now (would need failure detection)
    danger = 0.2
    
    # Reversibility: movement is reversible, special actions less so
    reversibility = 0.8 if action in [
        GameAction.ACTION1, GameAction.ACTION2,
        GameAction.ACTION3, GameAction.ACTION4,
    ] else 0.4
    
    # Information gain: inverse of action tries from this state
    tried_count = sum(
        1 for a, _ in graph.edges.get(state.grid_hash, [])
        if a == action
    )
    information_gain = 1.0 / (1.0 + tried_count)
    
    # Loop risk: based on visits
    loop_risk = clamp(visits / 10.0)
    
    # TRM scores
    trm_prior = trm.score_action(state, action)
    state_value = trm.score_state_value(state)
    
    return ActionFeatures(
        novelty=novelty,
        progress=progress,
        danger=danger,
        reversibility=reversibility,
        information_gain=information_gain,
        loop_risk=loop_risk,
        trm_prior=trm_prior,
        state_value=state_value,
    )


# ============================================================================
# Fuzzy Recursive Agent
# ============================================================================

class FuzzyRecursiveAgent(BaseAgent):
    """
    Fuzzy Recursive World-Model Agent
    
    Combines fuzzy logic, UCB exploration, belief updates,
    state graph memory, BFS planning, and TRM scoring.
    """
    
    def __init__(self, name: str = "FuzzyRecursiveAgent"):
        super().__init__(name)
        
        self.graph = StateGraph()
        self.hypotheses = HypothesisBank()
        self.ucb = UCBExplorer(c=1.4)
        self.trm = TinyRecursiveModelScorer()
        
        self.previous_state: Optional[State] = None
        self.previous_action: Optional[GameAction] = None
        self.previous_observation: Optional[np.ndarray] = None
        
        self.plan: List[GameAction] = []
        self.actions = list(GameAction)
    
    def select_action(self, observation: Any, info: Dict) -> int:
        """Select action using fuzzy recursive reasoning"""
        
        # Create state (from_observation handles FrameDataRaw conversion)
        state = State.from_observation(observation, self.previous_observation)
        self.graph.add_state(state)
        
        # Update from previous transition
        if self.previous_state is not None and self.previous_action is not None:
            changed = state.grid_hash != self.previous_state.grid_hash
            reward = self._estimate_reward(
                self.previous_state,
                state,
                changed,
                info
            )
            
            transition = Transition(
                from_state=self.previous_state,
                action=self.previous_action,
                to_state=state,
                changed=changed,
                reward=reward,
                info=info
            )
            
            self.graph.add_transition(transition)
            self.hypotheses.update(transition)
            self.ucb.update(self.previous_state, self.previous_action, reward)
        
        # 1. Follow existing plan
        if self.plan:
            action = self.plan.pop(0)
            self._update_state(state, action, observation)
            # Handle both GameAction enum and int
            return action.value if isinstance(action, GameAction) else action
        
        # 2. Try to plan toward high-value state
        path = self.graph.bfs_to_goal(
            state,
            goal_fn=lambda s: self.trm.score_state_value(s) > 0.75,
            max_depth=15
        )
        
        if path and len(path) > 1:
            self.plan = path[1:]
            action = path[0]
            self._update_state(state, action, observation)
            # Handle both GameAction enum and int
            return action.value if isinstance(action, GameAction) else action
        
        # 3. Fuzzy scoring + UCB
        scored_actions = []
        
        for action in self.actions:
            features = estimate_action_features(
                state=state,
                action=action,
                graph=self.graph,
                hypotheses=self.hypotheses,
                trm=self.trm,
            )
            
            fuzzy_score = fuzzy_action_score(features)
            
            # UCB bonus
            ucb_action = self.ucb.select(state, self.actions)
            ucb_bonus = 0.15 if action == ucb_action else 0.0
            
            final_score = fuzzy_score + ucb_bonus
            
            scored_actions.append((final_score, action, features))
        
        # Select best action
        scored_actions.sort(reverse=True, key=lambda x: x[0])
        best_score, best_action, best_features = scored_actions[0]
        
        self._update_state(state, best_action, observation)
        # Handle both GameAction enum and int
        return best_action.value if isinstance(best_action, GameAction) else best_action
    
    def _update_state(self, state: State, action: GameAction, observation: np.ndarray):
        """Update internal state"""
        self.previous_state = state
        self.previous_action = action
        
        # Extract grid from FrameDataRaw if needed
        if hasattr(observation, 'frame') and isinstance(observation.frame, list):
            if len(observation.frame) > 0:
                self.previous_observation = observation.frame[0].copy()
            else:
                self.previous_observation = np.zeros((10, 10), dtype=np.int8)
        elif isinstance(observation, np.ndarray):
            self.previous_observation = observation.copy()
        else:
            self.previous_observation = np.array(observation)
    
    def _estimate_reward(
        self,
        old_state: State,
        new_state: State,
        changed: bool,
        info: Dict
    ) -> float:
        """Estimate reward from transition"""
        reward = 0.0
        
        # State changed
        if changed:
            reward += 0.2
        
        # Object count changed
        if new_state.object_count != old_state.object_count:
            reward += 0.25
        
        # Colors changed
        if new_state.unique_colors != old_state.unique_colors:
            reward += 0.15
        
        # Many cells changed (significant transformation)
        if new_state.changed_cells > 5:
            reward += 0.20
        
        # Penalize no-op
        if not changed:
            reward -= 0.10
        
        # Use info if available
        if "success" in info and info["success"]:
            reward += 1.0
        
        return clamp(reward, -1.0, 1.0)
    
    def reset(self):
        """Reset agent for new episode"""
        super().reset()
        self.previous_state = None
        self.previous_action = None
        self.previous_observation = None
        self.plan = []
    
    def get_stats(self) -> Dict:
        """Get agent statistics"""
        stats = super().get_stats()
        
        stats.update({
            "states_explored": len(self.graph.states),
            "transitions_recorded": sum(len(edges) for edges in self.graph.edges.values()),
            "top_hypotheses": self.hypotheses.get_top_hypotheses(3),
            "ucb_total_visits": self.ucb.total_visits,
        })
        
        return stats

# Made with Bob
