def build_sa_index(n_rows, n_cols):
    states = [(r, c) for r in range(n_rows) for c in range(n_cols)]
    sa_list = [(s, a) for s in states for a in ACTIONS]
    idx = {sa: k for k, sa in enumerate(sa_list)}
    return states, sa_list, idx