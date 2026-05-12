def evaluate_state(runs_left, balls_left, wickets_left):
    if runs_left <= 0:
        return 100  # win
    if balls_left == 0 or wickets_left == 0:
        return -100  # lose

    # Heuristic evaluation
    run_rate_needed = runs_left / balls_left
    return 50 - (run_rate_needed * 5) + (wickets_left * 3)


def minimax(runs_left, balls_left, wickets_left, depth, is_maximizing):
    if depth == 0 or balls_left == 0 or wickets_left == 0:
        return evaluate_state(runs_left, balls_left, wickets_left)

    if is_maximizing:  # Batting team
        best = -float("inf")
        for run in [0, 1, 2, 4, 6]:
            score = minimax(
                runs_left - run,
                balls_left - 1,
                wickets_left,
                depth - 1,
                False
            )
            best = max(best, score)
        return best
    else:  # Bowling team
        worst = float("inf")
        for outcome in ["dot", "wicket"]:
            if outcome == "wicket":
                score = minimax(
                    runs_left,
                    balls_left - 1,
                    wickets_left - 1,
                    depth - 1,
                    True
                )
            else:
                score = minimax(
                    runs_left,
                    balls_left - 1,
                    wickets_left,
                    depth - 1,
                    True
                )
            worst = min(worst, score)
        return worst


def get_strategy(runs_left, balls_left, wickets_left):
    strategies = {
        "Aggressive": [0, 2, 4, 6],
        "Balanced": [0, 1, 2, 4],
        "Defensive": [0, 1]
    }

    best_strategy = None
    best_score = -float("inf")

    for name, shots in strategies.items():
        score = 0
        for shot in shots:
            score += evaluate_state(
                runs_left - shot,
                balls_left - 1,
                wickets_left
            )
        if score > best_score:
            best_score = score
            best_strategy = name

    return best_strategy, best_score
