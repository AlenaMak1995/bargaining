from .gridworld import ACTIONS, LEFT_OF, RIGHT_OF, step_det

def slip_transitions(s, a, slip, n_rows, n_cols, goal=None):
    if goal is not None and s == goal:
        return {goal: 1.0}
    probs = {}
    for aa, p in [(a, 1 - slip), (LEFT_OF[a], slip / 2), (RIGHT_OF[a], slip / 2)]:
        s2 = step_det(s, aa, n_rows, n_cols)
        probs[s2] = probs.get(s2, 0.0) + p
    return probs