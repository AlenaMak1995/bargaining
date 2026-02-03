from bargaining.envs.gridworld import ACTIONS
from bargaining.envs.slip import slip_transitions
import numpy as np

def build_flow_A_b(n_rows, n_cols, start, goal, slip, sa_list, sa_idx):
    """
    Build A x = b for occupancy flow constraints (exclude goal row).
    For each state s != goal:
      sum_a x(s,a) - sum_{s',a'} P(s | s',a') x(s',a') = 1{s=start}
    """
    states = [(r, c) for r in range(n_rows) for c in range(n_cols)]
    non_goal_states = [s for s in states if s != goal]

    m = len(non_goal_states)
    n = len(sa_list)

    A = np.zeros((m, n))
    b = np.zeros(m)

    # Precompute P(s_to | s_from, a)
    P = {}
    for (s_from, a) in sa_list:
        P[(s_from, a)] = slip_transitions(s_from, a, slip, n_rows, n_cols, goal=goal)

    row_of = {s: i for i, s in enumerate(non_goal_states)}

    # Outflow terms: +1 on x(s,a)
    for s in non_goal_states:
        i = row_of[s]
        for a in ACTIONS:
            A[i, sa_idx[(s, a)]] += 1.0
        b[i] = 1.0 if s == start else 0.0

    # Inflow terms: -P(s | s_prev,a_prev) on x(s_prev,a_prev)
    for (s_prev, a_prev) in sa_list:
        if s_prev == goal:
            continue
        trans = P[(s_prev, a_prev)]
        for s_to, p in trans.items():
            if s_to == goal:
                continue
            i = row_of[s_to]
            A[i, sa_idx[(s_prev, a_prev)]] -= float(p)

    return A, b