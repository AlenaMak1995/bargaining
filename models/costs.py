from bargaining.envs.slip import slip_transitions


def build_cost_vectors(price_grid, energy_grid, time_grid, start, goal, n_rows, n_cols, sa_list, slip):
    price_grid = np.asarray(price_grid, float)
    energy_grid = np.asarray(energy_grid, float)
    time_grid = np.asarray(time_grid, float)

    c = np.zeros(len(sa_list))
    e = np.zeros(len(sa_list))
    t = np.zeros(len(sa_list))

    for k, (s, a) in enumerate(sa_list):
        trans = slip_transitions(s, a, slip, n_rows, n_cols, goal=goal)

        ck = 0.0
        ek = 0.0
        tk = 0.0
        for s2, p in trans.items():
            if s2 == goal:
                continue
            r2, c2 = s2
            ck += p * float(price_grid[r2, c2])
            ek += p * float(energy_grid[r2, c2])
            tk += p * float(time_grid[r2, c2])

        c[k] = ck
        e[k] = ek
        t[k] = tk

    return c, e, t