import numpy as np
import matplotlib.pyplot as plt


def plot_grid_with_labels(grid, title, start=None, goal=None, fmt="{:.0f}", out_path=None):
    n_rows, n_cols = grid.shape
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(grid)

    ax.set_title(title)
    ax.set_xticks(range(n_cols))
    ax.set_yticks(range(n_rows))
    ax.set_xticklabels([f"c{j}" for j in range(n_cols)])
    ax.set_yticklabels([f"r{i}" for i in range(n_rows)])

    ax.set_xticks(np.arange(-.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-.5, n_rows, 1), minor=True)
    ax.grid(which="minor", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)

    for r in range(n_rows):
        for c in range(n_cols):
            ax.text(c, r, fmt.format(grid[r, c]), ha="center", va="center", fontsize=12)

    if start is not None:
        ax.text(start[1], start[0], "S", ha="center", va="center", fontsize=14, weight="bold")
    if goal is not None:
        ax.text(goal[1], goal[0], "G", ha="center", va="center", fontsize=14, weight="bold")

    fig.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=200)
        plt.close(fig)
    else:
        plt.show()


def plot_policy_arrows(pi, n_rows, n_cols, start=None, goal=None, title="Policy", out_path=None):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_title(title)

    ax.set_xlim(-0.5, n_cols - 0.5)
    ax.set_ylim(n_rows - 0.5, -0.5)

    ax.set_xticks(range(n_cols))
    ax.set_yticks(range(n_rows))
    ax.set_xticklabels([f"c{j}" for j in range(n_cols)])
    ax.set_yticklabels([f"r{i}" for i in range(n_rows)])

    ax.set_xticks(np.arange(-.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-.5, n_rows, 1), minor=True)
    ax.grid(which="minor", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)

    arrow = {"U": (0, -0.45), "D": (0, 0.45), "L": (-0.45, 0), "R": (0.45, 0)}

    for (r, c), probs in pi.items():
        if goal is not None and (r, c) == goal:
            continue
        for a, p in probs.items():
            if p > 1e-3:
                dx, dy = arrow[a]
                ax.arrow(
                    c, r, dx * p, dy * p,
                    head_width=0.10, head_length=0.10,
                    length_includes_head=True,
                    alpha=0.9
                )

    if start is not None:
        ax.text(start[1], start[0], "S", ha="center", va="center", fontsize=14, weight="bold")
    if goal is not None:
        ax.text(goal[1], goal[0], "G", ha="center", va="center", fontsize=14, weight="bold")

    fig.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=200)
        plt.close(fig)
    else:
        plt.show()
