import numpy as np
import cvxpy as cp

from models.indexing import build_sa_index
from models.costs import build_cost_vectors
from models.flow import build_flow_A_b
from envs.gridworld import ACTIONS



def projected_primal_dual_loop(
    price_grid, energy_grid, time_grid, start, goal,
    slip=0.2,
    Emax=3.0,
    Tmax=3.0,
    betaE=5.0,
    betaT=5.0,
    rho=1e-2,
    alpha=0.02,
    etaE=0.02,
    etaT=0.02,
    iters=200,
    lamE0=0.0,
    lamT0=0.0,
    solver=cp.OSQP,
    verbose_every=10,
):
    """
    Primal step: projected gradient on x over X={x>=0, Ax=b}
      grad_x L = c + rho*x + lambda*e   (since e^T x is linear)
      y = x - alpha * grad
      x <- argmin_{x in X} ||x - y||^2   (projection)
    Dual step:
      lambda <- [lambda + eta*(e^T x - (Emax + beta*lambda))]_+
    """

    price_grid = np.asarray(price_grid, float)
    energy_grid = np.asarray(energy_grid, float)
    n_rows, n_cols = price_grid.shape

    states, sa_list, sa_idx = build_sa_index(n_rows, n_cols)
    goal_idx = [sa_idx[(goal, a)] for a in ACTIONS]
    c_vec, e_vec, t_vec = build_cost_vectors(price_grid, energy_grid, time_grid, start, goal, n_rows, n_cols, sa_list, slip = slip)
    A, b = build_flow_A_b(n_rows, n_cols, start, goal, slip, sa_list, sa_idx)

    n = len(sa_list)

    # Initialize x by projecting 0 onto Ax=b, x>=0 (gives a feasible occupancy)
    x = cp.Variable(n, nonneg=True)
    y_param = cp.Parameter(n)
    proj_prob = cp.Problem(cp.Minimize(cp.sum_squares(x - y_param)), [A @ x == b, x[goal_idx] == 0])

    # Start at y=0 projection
    y_param.value = np.zeros(n)
    proj_prob.solve(solver=solver)
    xk = np.array(x.value).reshape(-1)

    lamE = float(lamE0)
    lamT = float(lamT0)
    hist = []

    # baseline hard constraint solve
    x_base = cp.Variable(n, nonneg=True)
    prob_base = cp.Problem(
        cp.Minimize(c_vec @ x_base + (rho/2)*cp.sum_squares(x_base)),
        [A @ x_base == b, e_vec @ x_base <= Emax, t_vec @ x_base <= Tmax,x_base[goal_idx] == 0  ]
    )
    prob_base.solve(solver=solver)
    baseline = None
    if prob_base.status in ("optimal", "optimal_inaccurate") and x_base.value is not None:
        baseline = {
            "x": np.array(x_base.value).reshape(-1),
            "price": float(c_vec @ x_base.value),
            "energy": float(e_vec @ x_base.value),
            "time": float(t_vec @ x_base.value),
            "obj": prob_base.value,
        }
        print("Baseline objective:", baseline["obj"])
        print("Baseline energy:", baseline["energy"])
        print("Baseline time:", baseline["time"])
    else:
        print("Baseline infeasible or not solved.")

    for t in range(1, iters + 1):
        x_prev = xk.copy()  # <-- save previous x for dx
        # gradient of L wrt x: c + rho*x + lam*e
        grad = c_vec + rho * xk + lamE * e_vec + lamT * t_vec

        # primal step + projection
        y = xk - alpha * grad
        y_param.value = y
        proj_prob.solve(solver=solver)
        xk = np.array(x.value).reshape(-1)

        # --- diagnostics on current xk (optional) ---
        price_raw = float(c_vec @ xk)
        price_reg = float(c_vec @ xk + (rho / 2.0) * (xk @ xk))
        energy = float(e_vec @ xk)  # current energy (for logging)
        time = float(t_vec @ xk)

        lamE_old, lamT_old = lamE, lamT

        # --- paper-style dual update uses x_prev ---
        energy_prev = float(e_vec @ x_prev)      # f1(x^{t-1}) part
        E_eff_prev  = Emax + betaE * lamE_old          # s^{t-1} = beta*lambda^{t-1}
        residE_prev  = energy_prev - E_eff_prev


        time_prev = float(t_vec @ x_prev)
        T_eff_prev  = Tmax + betaT * lamT_old
        residT_prev = time_prev   - T_eff_prev

        lamE = max(0.0, lamE_old + etaE * residE_prev)
        lamT = max(0.0, lamT_old + etaT * residT_prev)
        # ---- derived quantities (for logging & plots) ----
        energy      = float(e_vec @ xk)
        time_used = float(t_vec @ xk)
        price_raw  = float(c_vec @ xk)
        reg_term   = (rho / 2.0) * float(xk @ xk)
        price_reg  = price_raw + reg_term

        E_eff = Emax + betaE * lamE
        T_eff = Tmax + betaT * lamT

        slack      = E_eff - Emax
        residE = energy    - E_eff
        residT = time_used - T_eff

        violE = max(0.0, residE)
        violT = max(0.0, residT)

        csE = abs(lamE * residE)
        csT = abs(lamT * residT)
        dx         = np.linalg.norm(xk - x_prev, 1)


        # # convergence metrics
        # r_cur    = float(e_vec @ xk) - (Emax + beta * lam)
        # viol_cur = max(0.0, r_cur)
        # cs       = abs(lam * r_cur)
        dx       = np.linalg.norm(xk - x_prev, 1)


        hist.append({
    "t": t,

    # primal values
    "price_raw": price_raw,
    "price_reg": price_reg,
    "reg_term": reg_term,
    "energy": energy,
    "time": time_used,

    "lamE": lamE,
    "lamT": lamT,
    "E_eff": E_eff,
    "T_eff": T_eff,
    "energy_prev": energy_prev,
    "time_prev": time_prev,
    "E_eff_prev": E_eff_prev,
    "T_eff_prev": T_eff_prev,
    "residE_prev": residE_prev,
    "residT_prev": residT_prev,
    "residE": residE,
    "residT": residT,
    "violE": violE,
    "violT": violT,
    "csE": csE,
    "csT": csT,

    # convergence
    "dx1": dx,
        })
        if dx < 1e-6 and max(violE, violT) < 1e-4 and max(csE, csT) < 1e-6:
            print(f"Converged at t={t}: violE={violE:.2e}, violT={violT:.2e}, "
                  f"csE={csE:.2e}, csT={csT:.2e}, dx={dx:.2e}, lamE={lamE:.4f}, lamT={lamT:.4f}")
            break

        if verbose_every and (t % verbose_every == 0 or t == 1):
                print(f"t={t:03d} lamE={lamE:8.4f} lamT={lamT:8.4f} "
                          f"E_prev={energy_prev:8.4f} Eeff_prev={E_eff_prev:8.4f} rE_prev={residE_prev:+9.4f} "
                          f"T_prev={time_prev:8.4f} Teff_prev={T_eff_prev:8.4f} rT_prev={residT_prev:+9.4f} "
                          f"price_reg={price_reg:8.4f}")

    return hist, xk, (states, sa_list, sa_idx), baseline