# visualize.py
import numpy as np
import matplotlib.pyplot as plt
import argparse

"""
Este visualizador funciona con los .npz actuales,
que solo contienen:
    - grid  (estado final)
    - stats (por día)

FUNCIONA EN DOS MODOS:

1) Un archivo:
    python visualize.py seq.npz
   → Muestra el grid final.

2) Dos archivos:
    python visualize.py seq.npz par.npz
   → Muestra ambos grids comparados lado a lado.
"""

def show_one(npz_file):
    data = np.load(npz_file)
    grid = data["grid"]

    plt.figure(figsize=(6,6))
    plt.imshow(grid, vmin=0, vmax=3, cmap="viridis")
    plt.title(f"Final grid: {npz_file}")
    plt.colorbar()
    plt.tight_layout()
    plt.show()


def show_two(npz1, npz2):
    d1 = np.load(npz1)
    d2 = np.load(npz2)

    g1 = d1["grid"]
    g2 = d2["grid"]

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    axes[0].imshow(g1, vmin=0, vmax=3, cmap="viridis")
    axes[0].set_title(f"Sequential\n{npz1}")

    axes[1].imshow(g2, vmin=0, vmax=3, cmap="viridis")
    axes[1].set_title(f"Parallel\n{npz2}")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("npz_files", nargs="+", help="1 o 2 archivos .npz")
    args = parser.parse_args()

    files = args.npz_files

    # MODO 1: un archivo
    if len(files) == 1:
        show_one(files[0])

    # MODO 2: dos archivos → comparación
    elif len(files) == 2:
        show_two(files[0], files[1])

    else:
        print("Error: solo puedes pasar 1 o 2 archivos .npz.")
