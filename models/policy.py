from bargaining.envs.gridworld import ACTIONS


def policy_from_x(xk, n_rows, n_cols, sa_idx, goal, tol=1e-10):
    """Recover pi(a|s) from occupancy vector xk."""
    states = [(r, c) for r in range(n_rows) for c in range(n_cols)]
    pi = {}
    # collect action mass per state
    for s in states:
        if s == goal:
            continue
        masses = {}
        total = 0.0
        for a in ACTIONS:
            k = sa_idx.index((s, a))  # ok for tiny grids; for bigger use sa_idx
            v = float(xk[k])
            masses[a] = v
            total += v
        if total <= tol:
            pi[s] = {a: 0.0 for a in ACTIONS}
        else:
            pi[s] = {a: masses[a] / total for a in ACTIONS}
    return pi