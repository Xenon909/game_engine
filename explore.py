#explore.py
from engine import init_state, apply_action, is_terminal

# All possible actions the player can take
ACTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'WAIT']


def explore(state, grid, rules, depth, current_path, best_ref, memo):
    # --- Base cases ---
    if depth == 0 or is_terminal(state, rules):
        if best_ref[0] is None or state["score"] > best_ref[0]:
            best_ref[0] = state["score"]
            best_ref[1] = list(current_path)
        return 1
    # --- Memoisation pruning ---
    # Build a hashable fingerprint of the current state
    fingerprint = (state["pos"], frozenset(state["collected"]), state["steps"])
    if fingerprint in memo and memo[fingerprint] >= state["score"]:
        # We have already explored this exact state from an equal or better score:
        # no need to continue — it cannot improve our global best.
        return 0
    memo[fingerprint] = state["score"]
    total_leaves = 0
    # --- Recursive case: try all 5 actions ---
    for action in ACTIONS:
        next_state, event = apply_action(state, action, grid, rules)
        current_path.append(action)

        total_leaves += explore(
            next_state, grid, rules, depth - 1,
            current_path, best_ref, memo
        )
        current_path.pop()
    return total_leaves
def run_explore(grid_info, rules):
    max_depth     = rules["DEPTH_EXPLORATION"]
    initial_state = init_state(grid_info['start_pos'], rules)

    # Shared mutable reference so all recursive branches update one global best
    best_ref = [None, []]
    memo     = {}

    total_leaves = explore(
        initial_state,
        grid_info['grid'],
        rules,
        depth=max_depth,
        current_path=[],
        best_ref=best_ref,
        memo=memo
    )

    best_score, best_path = best_ref

    # --- Display report ---
    print(f"=== Exploration recursive (profondeur max : {max_depth}) ===")
    print(f"Meilleur score trouve : {best_score}")
    print(f"Sequence optimale : {' '.join(best_path)}")
    print(f"Feuilles explorees : {total_leaves:,}")


# --- Local Unit Testing Block ---
if __name__ == "__main__":
    print("--- Testing explore.py module logic ---")

    mock_grid_info = {
        "grid": [
            ['P', '.', 'B'],
            ['.', 'X', '.'],
            ['.', '.', 'T']
        ],
        "N": 3,
        "M": 3,
        "start_pos": (0, 0)
    }
    mock_rules = {
        "MAX_MOVES": 20, "MOVE_COST": 1, "BONUS_POINTS": 10,
        "TARGET_BONUS": 50, "ENEMY_PENALTY": 0, "ENEMY_MODE": "death",
        "HP": 1, "DEPTH_EXPLORATION": 8, "SIMU_COUNT": 10
    }
    run_explore(mock_grid_info, mock_rules)