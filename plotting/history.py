import numpy as np
import matplotlib.pyplot as plt


def plot_history_2c(hist, Emax, Tmax, betaE, betaT, title_prefix="", out_dir=None):
    t = np.array([h["t"] for h in hist], dtype=float)

    price_raw = np.array([h["price_raw"] for h in hist], dtype=float)
    price_reg = np.array([h["price_reg"] for h in hist], dtype=float)
    energy    = np.array([h["energy"]    for h in hist], dtype=float)
    time_used = np.array([h["time"]      for h in hist], dtype=float)

    lamE = np.array([h["lamE"] for h in hist], dtype=float)
    lamT = np.array([h["lamT"] for h in hist], dtype=float)

    E_eff = np.array([h.get("E_eff", np.nan) for h in hist], dtype=float)
    T_eff = np.array([h.get("T_eff", np.nan) for h in hist], dtype=float)

    residE_prev = np.array([h.get("residE_prev", np.nan) for h in hist], dtype=float)
    residT_prev = np.array([h.get("residT_prev", np.nan) for h in hist], dtype=float)

    dx1 = np.array([h["dx1"] for h in hist], dtype=float)

    def save_or_show(fig, name):
        fig.tight_layout()
        if out_dir:
            fig.savefig(f"{out_dir}/{name}", dpi=200)
            plt.close(fig)
        else:
            plt.show()

    # 1) Price trace
    fig = plt.figure(figsize=(7, 4))
    plt.title(f"{title_prefix}Price vs iteration")
    plt.plot(t, price_raw, label="price_raw")
    plt.plot(t, price_reg, label="price_reg")
    plt.xlabel("iteration t")
    plt.ylabel("price")
    plt.legend()
    plt.grid(True)
    save_or_show(fig, "price.png")

    # 2) Energy + effective budget
    fig = plt.figure(figsize=(7, 4))
    plt.title(f"{title_prefix}Energy vs iteration")
    plt.plot(t, energy, label="energy(x^t)")
    if np.isfinite(E_eff).any():
        plt.plot(t, E_eff, label="E_eff = Emax + betaE*lamE")
    plt.axhline(Emax, linestyle="--", label="Emax (original)")
    plt.xlabel("iteration t")
    plt.ylabel("energy")
    plt.legend()
    plt.grid(True)
    save_or_show(fig, "energy.png")

    # 3) Time + effective budget
    fig = plt.figure(figsize=(7, 4))
    plt.title(f"{title_prefix}Time vs iteration")
    plt.plot(t, time_used, label="time(x^t)")
    if np.isfinite(T_eff).any():
        plt.plot(t, T_eff, label="T_eff = Tmax + betaT*lamT")
    plt.axhline(Tmax, linestyle="--", label="Tmax (original)")
    plt.xlabel("iteration t")
    plt.ylabel("time")
    plt.legend()
    plt.grid(True)
    save_or_show(fig, "time.png")

    # 4) Dual variables
    fig = plt.figure(figsize=(7, 4))
    plt.title(f"{title_prefix}Dual variables")
    plt.plot(t, lamE, label="lamE")
    plt.plot(t, lamT, label="lamT")
    plt.axhline(0.0, linestyle="--")
    plt.xlabel("iteration t")
    plt.ylabel("lambda")
    plt.legend()
    plt.grid(True)
    save_or_show(fig, "lambdas.png")

    # 5) Residuals used in dual update (prev)
    fig = plt.figure(figsize=(7, 4))
    plt.title(f"{title_prefix}Residuals (paper-style, prev)")
    plt.plot(t, residE_prev, label="residE_prev")
    plt.plot(t, residT_prev, label="residT_prev")
    plt.axhline(0.0, linestyle="--")
    plt.xlabel("iteration t")
    plt.ylabel("residual")
    plt.legend()
    plt.grid(True)
    save_or_show(fig, "residuals.png")

    # 6) Convergence
    fig = plt.figure(figsize=(7, 4))
    plt.title(f"{title_prefix}Convergence")
    plt.plot(t, dx1, label="dx1 = ||x^t - x^{t-1}||_1")
    plt.yscale("log")
    plt.xlabel("iteration t")
    plt.ylabel("dx1")
    plt.legend()
    plt.grid(True)
    save_or_show(fig, "convergence.png")
