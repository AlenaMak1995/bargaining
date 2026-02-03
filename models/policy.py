from envs.gridworld import ACTIONS


def policy_from_x_fast(xk, states, sa_idx, goal, tol=1e-12):
    """
    Recover pi(a|s) from occupancy measure xk using sa_idx mapping.
    """
    pi = {}
    for s in states:
        if s == goal:
            continue
        masses = {a: float(xk[sa_idx[(s, a)]]) for a in ACTIONS}
        total = sum(masses.values())
        if total <= tol:
            pi[s] = {a: 0.0 for a in ACTIONS}
        else:
            pi[s] = {a: masses[a] / total for a in ACTIONS}
    return pi
