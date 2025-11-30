import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse

def load_frames(path):
    d = np.load(path, allow_pickle=True)
    grid = d["grid"]
    stats = d["stats"].item()
    return grid, stats

ap = argparse.ArgumentParser()
ap.add_argument("seq")
ap.add_argument("par")
ap.add_argument("--out", default="compare.gif")
ap.add_argument("--interval", type=int, default=150)
args = ap.parse_args()

seq, seq_stats = load_frames(args.seq)
par, par_stats = load_frames(args.par)

fig, ax = plt.subplots(1,2, figsize=(10,5))

def update(frame):
    ax[0].imshow(seq)
    ax[0].set_title("Secuencial")
    ax[0].axis("off")

    ax[1].imshow(par)
    ax[1].set_title("Paralelo")
    ax[1].axis("off")

ani = FuncAnimation(fig, update, frames=1, interval=args.interval)
ani.save(args.out, writer="pillow")
