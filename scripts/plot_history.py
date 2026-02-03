import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", required=True, help="Path to history.csv")
    ap.add_argument("--out", default=None, help="Output PNG path")
    args = ap.parse_args()

    hist_path = Path(args.history)
    df = pd.read_csv(hist_path)

    out = Path(args.out) if args.out else hist_path.parent / "convergence.png"

    # Plot a few key signals
    plt.figure()
    plt.plot(df["t"], df["price_reg"], label="price_reg")
    plt.plot(df["t"], df["energy"], label="energy")
    plt.plot(df["t"], df["time"], label="time")
    plt.xlabel("iteration")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    print(f"✅ saved {out}")

if __name__ == "__main__":
    main()
