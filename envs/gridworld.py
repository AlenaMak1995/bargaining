ACTIONS = ["U", "D", "L", "R"]
DIR = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
LEFT_OF = {"U": "L", "D": "R", "L": "D", "R": "U"}
RIGHT_OF = {"U": "R", "D": "L", "L": "U", "R": "D"}


def in_grid(r, c, n_rows, n_cols):
    return 0 <= r < n_rows and 0 <= c < n_cols


def step_det(s, a, n_rows, n_cols):
    """Deterministic step; if you hit a wall, you stay in place."""
    r, c = s
    dr, dc = DIR[a]
    rr, cc = r + dr, c + dc
    if in_grid(rr, cc, n_rows, n_cols):
        return (rr, cc)
    return (r, c)
