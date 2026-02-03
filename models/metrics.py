
import numpy as np
from models.costs import build_cost_vectors


def compute_final_totals(price_grid, energy_grid, time_grid,
                         start, goal, slip, xk, sa_list):
    n_rows, n_cols = price_grid.shape
    c_vec, e_vec, t_vec = build_cost_vectors(
        price_grid, energy_grid, time_grid,
        start, goal, n_rows, n_cols, sa_list, slip=slip
    )
    price_raw = float(c_vec @ xk)
    energy_tot = float(e_vec @ xk)
    time_tot = float(t_vec @ xk)
    return price_raw, energy_tot, time_tot


def last(hist, key):
    return float(hist[-1][key]) if len(hist) else float("nan")


def print_summary_2c(hist, baseline, price_grid, energy_grid, time_grid,
                     start, goal, slip, xk, sa_list, Emax, Tmax, betaE, betaT):
    final_price, final_energy, final_time = compute_final_totals(
        price_grid, energy_grid, time_grid, start, goal, slip, xk, sa_list
    )

    lamE = last(hist, "lamE")
    lamT = last(hist, "lamT")

    E_eff = Emax + betaE * lamE
    T_eff = Tmax + betaT * lamT

    print("\n=== SUMMARY ===")
    if baseline is None:
        print("BASELINE: infeasible or not solved.")
    else:
        print("BASELINE:")
        print(f"  price  = {baseline['price']:.6f}")
        print(f"  energy = {baseline['energy']:.6f}  (<= {Emax})")
        print(f"  time   = {baseline['time']:.6f}    (<= {Tmax})")

    print("BARGAINING / PRIMAL-DUAL FINAL:")
    print(f"  lamE   = {lamE:.6f}   => E_eff = {E_eff:.6f} (slackE={E_eff-Emax:.6f})")
    print(f"  lamT   = {lamT:.6f}   => T_eff = {T_eff:.6f} (slackT={T_eff-Tmax:.6f})")
    print(f"  price  = {final_price:.6f}")
    print(f"  energy = {final_energy:.6f}  (violE={max(0.0, final_energy - E_eff):.3e})")
    print(f"  time   = {final_time:.6f}    (violT={max(0.0, final_time - T_eff):.3e})")

    penalty_E = (betaE / 2.0) * lamE**2
    penalty_T = (betaT / 2.0) * lamT**2
    penalty_total = penalty_E + penalty_T

    print("Penalty paid:")
    print(f"  energy slack cost = {penalty_E:.6f}")
    print(f"  time   slack cost = {penalty_T:.6f}")
    print(f"  total  penalty    = {penalty_total:.6f}")

    final_total = final_price + penalty_total
    print("FINAL (raw):", final_price)
    print("Penalty:", penalty_total)
    print("FINAL (all-in):", final_total)

    # return a structured dict for saving
    return {
        "baseline": baseline,
        "final": {
            "price_raw": final_price,
            "energy": final_energy,
            "time": final_time,
            "lamE": lamE,
            "lamT": lamT,
            "E_eff": E_eff,
            "T_eff": T_eff,
            "slackE": E_eff - Emax,
            "slackT": T_eff - Tmax,
            "penalty_E": penalty_E,
            "penalty_T": penalty_T,
            "penalty_total": penalty_total,
            "all_in": final_total,
        }
    }
