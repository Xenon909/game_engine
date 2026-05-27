#engine.py
import copy

def is_terminal(state, rules):
    """
    Checks if the game state has reached a terminal condition.
    Returns True if the game is over, False otherwise.
    Updates the status flag if necessary.
    """
    # 1. Check if a final status has already been declared
    if state["status"] in ["SUCCESS", "FAILURE", "LIMIT"]:
        return True

    # 2. Check if the maximum step limit has been hit
    if state["steps"] >= rules["MAX_MOVES"]:
        state["status"] = "LIMIT"
        return True

    # 3. Check health points depletion (only relevant in health mode)
    if rules["ENEMY_MODE"] == "health" and state["hp"] <= 0:
        state["status"] = "FAILURE"
        return True

    return False


def apply_action(state, action, grid, rules):
    """
    Applies an action to a game state and returns a BRAND NEW state dictionary.
    Guarantees deep immutability to prevent recursive side-effects.
    """
    # Strictest constraint from Page 12/15: Always deepcopy the state first!
    next_state = copy.deepcopy(state)
    event = "NONE"
    
    # If the game is already over, do not process actions further
    if is_terminal(next_state, rules):
        return next_state, event

    # 1. Standard increments applied to every action
    next_state["steps"] += 1
    next_state["score"] -= rules["MOVE_COST"]

    current_row, current_col = next_state["pos"]
    N = len(grid)
    M = len(grid[0]) if N > 0 else 0

    # 2. Compute destination coordinates based on the action movement matrix
    next_row, next_col = current_row, current_col
    if action == "UP":
        next_row -= 1
    elif action == "DOWN":
        next_row += 1
    elif action == "LEFT":
        next_col -= 1
    elif action == "RIGHT":
        next_col += 1
    elif action == "WAIT":
        pass  # Position stays exactly the same
    else:
        # Fallback safeguard for untracked manual actions
        return next_state, event

    # 3. Check collision with grid boundaries or obstacle cells 'X'
    # Consistent choice rule: movement is safely ignored, but cost/step are kept
    if not (0 <= next_row < N and 0 <= next_col < M) or grid[next_row][next_col] == 'X':
        # Player stays in original position, check if steps hit limit after this bump
        if next_state["steps"] >= rules["MAX_MOVES"]:
            next_state["status"] = "LIMIT"
        return next_state, event

    # 4. Valid movement confirmed: Update the player's position tracking tuple
    next_state["pos"] = (next_row, next_col)
    cell_type = grid[next_row][next_col]

    # 5. Evaluate the interactive entity matrix on the destination cell
    
    # --- CIBLE (T) ---
    if cell_type == 'T':
        next_state["score"] += rules["TARGET_BONUS"]
        next_state["status"] = "SUCCESS"
        event = f"TARGET (+{rules['TARGET_BONUS']})"

    # --- BONUS (B) ---
    elif cell_type == 'B':
        # Check if this unique coordinate pair was already consumed previously
        if (next_row, next_col) not in next_state["collected"]:
            next_state["score"] += rules["BONUS_POINTS"]
            next_state["collected"].add((next_row, next_col))
            event = f"BONUS (+{rules['BONUS_POINTS']})"

    # --- ENNEMI (E) ---
    elif cell_type == 'E':
        if rules["ENEMY_MODE"] == "death":
            next_state["status"] = "FAILURE"
            event = "ENEMY (death)"
        elif rules["ENEMY_MODE"] == "health":
            next_state["score"] -= rules["ENEMY_PENALTY"]
            next_state["hp"] -= 1
            event = f"ENEMY (-{rules['ENEMY_PENALTY']} HP)"
            if next_state["hp"] <= 0:
                next_state["status"] = "FAILURE"

    # 6. Final safety check: Check if this valid step triggered the step-limit boundary
    if next_state["status"] == "CONTINUE" and next_state["steps"] >= rules["MAX_MOVES"]:
        next_state["status"] = "LIMIT"

    return next_state, event


# --- Local Unit Testing Block ---
if __name__ == "__main__":
    print("--- Testing engine.py module logic ---")
    
    # Mocking standard structures for validation
    mock_grid = [
        ['P', '.', 'B'],
        ['.', 'X', 'E'],
        ['.', '.', 'T']
    ]
    mock_rules = {
        "MAX_MOVES": 5, "MOVE_COST": 1, "BONUS_POINTS": 10,
        "TARGET_BONUS": 50, "ENEMY_PENALTY": 25, "ENEMY_MODE": "health", "HP": 3
    }
    initial_state = {
        "pos": (0, 0), "score": 0, "steps": 0, "collected": set(), "hp": 3, "status": "CONTINUE"
    }

    # Step 1: Move right onto normal cell (0, 1)
    s1 = apply_action(initial_state, "RIGHT", mock_grid, mock_rules)
    print(f"Step 1 (Right): Pos={s1['pos']}, Score={s1['score']}, Steps={s1['steps']}, Status={s1['status']}")

    # Step 2: Move right onto Bonus cell (0, 2)
    s2 = apply_action(s1, "RIGHT", mock_grid, mock_rules)
    print(f"Step 2 (Bonus): Pos={s2['pos']}, Score={s2['score']}, Collected={s2['collected']}")

    # Step 3: Backtrack left onto cell (0, 1)
    s3 = apply_action(s2, "LEFT", mock_grid, mock_rules)
    
    # Step 4: Move right onto same Bonus cell (0, 2) again -> should be treated as empty floor
    s4 = apply_action(s3, "RIGHT", mock_grid, mock_rules)
    print(f"Step 4 (Re-entry Bonus): Score={s4['score']} (Should be 8, no extra 10 pts awarded)")

    # Step 5: Test wall collision behavior -> should bounce back but cost 1 point
    s5 = apply_action(s4, "DOWN", mock_grid, mock_rules) # hit 'X' at (1,1)
    print(f"Step 5 (Wall Collision): Pos={s5['pos']} (Should stay at 0,2), Score={s5['score']} (Should drop to 7)")
def init_state(start_pos, rules):
    return {
        "pos": start_pos,
        "score": 0,
        "steps": 0,
        "collected": set(),
        "hp": rules.get('HP', 1),
        "status": "CONTINUE"
    }