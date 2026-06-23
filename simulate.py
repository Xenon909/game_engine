import random
from engine import init_state, apply_action, is_terminal
# All possible actions the player can take
ACTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'WAIT']
def run_simulation(grid_info, rules):
    """
    Runs a single random simulation from the starting position.
    Returns the final score, status and number of steps.
    """
    # Initialize player state at starting position
    state = init_state(grid_info['start_pos'], rules)
    # Keep playing until the game reaches a terminal state
    while not is_terminal(state, rules):
        action = random.choice(ACTIONS)
        state, event = apply_action(state, action, grid_info['grid'], rules)
    return state["score"], state["status"], state["steps"]
def run_all_simulations(grid_info, rules):
    """
    Runs all simulations (SIMU_COUNT times) and returns raw results.
    """
    # Fix random seed for reproducibility if defined
    if 'RANDOM_SEED' in rules:
        random.seed(rules['RANDOM_SEED'])
    results = []
    # Run each simulation independently
    for i in range(rules['SIMU_COUNT']):
        score, status, steps = run_simulation(grid_info, rules)
        results.append({
            "score": score,
            "status": status,
            "steps": steps
        })
    return results
def compute_stats(results):
    """
    Calculates and returns a dictionary of statistical indicators
    from all simulation results.
    """
    # Total number of simulations
    n = len(results)
    # Extract scores and steps into separate lists
    scores = [r["score"] for r in results]
    steps  = [r["steps"] for r in results]
    # Count each type of result
    success = sum(1 for r in results if r["status"] == "SUCCESS")
    failure = sum(1 for r in results if r["status"] == "FAILURE")
    limit   = sum(1 for r in results if r["status"] == "LIMIT")
    # Calculate averages
    score_moyen = sum(scores) / n
    pas_moyens  = sum(steps)  / n
    # Calculate standard deviation
    import math
    variance   = sum((s - score_moyen) ** 2 for s in scores) / n
    ecart_type = math.sqrt(variance)
    return {
        "total":       n,
        "success":     success,
        "failure":     failure,
        "limit":       limit,
        "taux_succes": success / n * 100,
        "score_moyen": score_moyen,
        "score_max":   max(scores),
        "score_min":   min(scores),
        "ecart_type":  ecart_type,
        "pas_moyens":  pas_moyens
    }