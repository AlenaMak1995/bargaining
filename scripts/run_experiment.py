import argparse
import json
import sys
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]   # repo root
sys.path.insert(0, str(ROOT))

from pathlib import Path
from models.policy import policy_from_x_fast
from models.metrics import print_summary_2c
from plotting.grids import plot_grid_with_labels, plot_policy_arrows
from plotting.history import plot_history_2c


import numpy as np
import pandas as pd
import yaml
import cvxpy as cp

# Expect your function exists here:
from solvers.primal_dual import projected_primal_dual_loop


def load_yaml(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="Path to YAML config")
    args = ap.parse_args()

    cfg = load_yaml(args.config)

    exp_name = cfg.get("experiment_name", "experiment")
    out_dir = ensure_dir(cfg.get("out_dir", f"results/{exp_name}"))

    # --- build inputs ---
    price = np.array(cfg["costs"]["price"], dtype=float)
    energy = np.array(cfg["costs"]["energy"], dtype=float)
    time_grid = np.array(cfg["costs"]["time"], dtype=float)

    slip = float(cfg["env"].get("slip", 0.0))
    start = tuple(cfg["env"]["start"])
    goal = tuple(cfg["env"]["goal"])

    Emax = float(cfg["constraints"]["Emax"])
    Tmax = float(cfg["constraints"]["Tmax"])
    betaE = float(cfg["constraints"]["betaE"])
    betaT = float(cfg["constraints"]["betaT"])

    rho = float(cfg["solver"].get("rho", 1e-6))
    alpha = float(cfg["solver"].get("alpha", 0.02))
    etaE = float(cfg["solver"].get("etaE", 0.02))
    etaT = float(cfg["solver"].get("etaT", 0.02))
    iters = int(cfg["solver"].get("iters", 200))
    lamE0 = float(cfg["solver"].get("lamE0", 0.0))
    lamT0 = float(cfg["solver"].get("lamT0", 0.0))
    verbose_every = int(cfg["solver"].get("verbose_every", 10))

    # CVXPY solver name in YAML (e.g., OSQP, CLARABEL)
    solver_name = cfg["solver"].get("cvxpy_solver", "OSQP")
    cvxpy_solver = getattr(cp, solver_name)

    # --- run ---
    hist, xk, meta, baseline = projected_primal_dual_loop(
        price, energy, time_grid,
        start, goal,
        slip=slip,
        Emax=Emax,
        Tmax=Tmax,
        betaE=betaE,
        betaT=betaT,
        rho=rho,
        alpha=alpha,
        etaE=etaE,
        etaT=etaT,
        iters=iters,
        lamE0=lamE0,
        lamT0=lamT0,
        solver=cvxpy_solver,
        verbose_every=verbose_every,
    )

    states, sa_list, sa_idx = meta
    pi = policy_from_x_fast(xk, states, sa_idx, goal)

    #Save plots into out_dir
    plot_grid_with_labels(price,  "Price",  start=start, goal=goal, out_path=out_dir / "price_grid.png")
    plot_grid_with_labels(energy, "Energy", start=start, goal=goal, out_path=out_dir / "energy_grid.png")
    plot_grid_with_labels(time_grid, "Time", start=start, goal=goal, out_path=out_dir / "time_grid.png")

    plot_policy_arrows(pi, price.shape[0], price.shape[1], start=start, goal=goal,
                   title="Final policy", out_path=out_dir / "policy.png")

    plot_history_2c(hist, Emax=Emax, Tmax=Tmax, betaE=betaE, betaT=betaT, out_dir=str(out_dir))

    summary = print_summary_2c(hist, baseline, price, energy, time_grid, start, goal, slip, xk, sa_list,
                          Emax=Emax, Tmax=Tmax, betaE=betaE, betaT=betaT)


    # --- save outputs ---
    save_cfg = cfg.get("save", {})
    if save_cfg.get("history_csv", True):
        df = pd.DataFrame(hist)
        df.to_csv(out_dir / "history.csv", index=False)

    # A lightweight summary for quick comparisons
    summary = {
        "experiment_name": exp_name,
        "out_dir": str(out_dir),
        "slip": slip,
        "start": list(start),
        "goal": list(goal),
        "Emax": Emax,
        "Tmax": Tmax,
        "betaE": betaE,
        "betaT": betaT,
        "rho": rho,
        "alpha": alpha,
        "etaE": etaE,
        "etaT": etaT,
        "iters_requested": iters,
        "iters_ran": len(hist),
        "baseline": None if baseline is None else {
            "price": float(baseline["price"]),
            "energy": float(baseline["energy"]),
            "time": float(baseline["time"]),
            "obj": float(baseline["obj"]),
        },
        "final": None if len(hist) == 0 else {
            "price_raw": float(hist[-1].get("price_raw", np.nan)),
            "price_reg": float(hist[-1].get("price_reg", np.nan)),
            "energy": float(hist[-1].get("energy", np.nan)),
            "time": float(hist[-1].get("time", np.nan)),
            "lamE": float(hist[-1].get("lamE", np.nan)),
            "lamT": float(hist[-1].get("lamT", np.nan)),
            "E_eff": float(hist[-1].get("E_eff", np.nan)),
            "T_eff": float(hist[-1].get("T_eff", np.nan)),
            "violE": float(hist[-1].get("violE", np.nan)),
            "violT": float(hist[-1].get("violT", np.nan)),
        }
    }

    if save_cfg.get("summary_json", True):
        with open(out_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)

    print(f"\n✅ Done: {exp_name}")
    print(f"   outputs: {out_dir}/history.csv, {out_dir}/summary.json")


if __name__ == "__main__":
    main()
