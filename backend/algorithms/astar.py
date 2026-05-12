import heapq
import random
import math

class State:
    def __init__(self, runs, balls, wickets, cost, path):
        self.runs = runs
        self.balls = balls
        self.wickets = wickets
        self.cost = cost
        self.path = path

    def __lt__(self, other):
        return self.cost < other.cost


def heuristic(remaining_runs, balls, wickets):
    if balls == 0 or wickets == 0:
        return float("inf")
    pressure = remaining_runs / balls
    wicket_penalty = math.exp((10 - wickets) / 5)
    return pressure * wicket_penalty


def get_shot_probabilities(wickets, rrr):
    if wickets <= 2:
        return [(0,0.2),(1,0.4),(2,0.25),(4,0.1),(6,0.02),("W",0.03)]
    if rrr > 8:
        return [(0,0.1),(1,0.25),(2,0.2),(4,0.25),(6,0.15),("W",0.05)]
    return [(0,0.15),(1,0.35),(2,0.25),(4,0.15),(6,0.07),("W",0.03)]


def stochastic_shot(wickets, rrr):
    shots, probs = zip(*get_shot_probabilities(wickets, rrr))
    return random.choices(shots, probs)[0]


def astar_chase(target, current_runs, balls_left, wickets_left):
    pq = []
    start = State(current_runs, balls_left, wickets_left, 0, [])
    heapq.heappush(pq, (0, start))

    while pq:
        _, state = heapq.heappop(pq)

        if state.runs >= target:
            return {
                "success": True,
                "balls_used": len(state.path),
                "path": state.path
            }

        if state.balls == 0 or state.wickets == 0:
            continue

        runs_needed = target - state.runs
        rrr = (runs_needed * 6) / max(state.balls, 1)

        shot = stochastic_shot(state.wickets, rrr)

        new_runs = state.runs
        new_wickets = state.wickets

        if shot == "W":
            new_wickets -= 1
            shot_value = "W"
        else:
            new_runs += shot
            shot_value = shot

        new_state = State(
            new_runs,
            state.balls - 1,
            new_wickets,
            state.cost + 1,
            state.path + [shot_value]
        )

        h = heuristic(target - new_runs, new_state.balls, new_wickets)
        heapq.heappush(pq, (new_state.cost + h, new_state))

def calculate_win_probability(target, current, balls, wickets):
        runs_left = target - current

        if runs_left <= 0:
            return 100

        if balls <= 0 or wickets <= 0:
            return 0

        rrr = (runs_left * 6) / balls

        # Heuristic logic
        prob = 100 - (rrr * 8) - ((10 - wickets) * 4)

        return max(0, min(100, round(prob, 2)))

    return {"success": False}
