import numpy as np
import argparse

SUS = 0
INF = 1
REC = 2

def simulate_sequential(N, days, beta, gamma, mu, init_frac, seed):
    np.random.seed(seed)

    grid = np.zeros((N, N), dtype=np.uint8)
    num_initial = int(N*N * init_frac)
    idx = np.random.choice(N*N, num_initial, replace=False)
    grid.flat[idx] = INF

    snap = []
    stats = {
        "S": [], "I": [], "R": [],
        "new_infections": [],
        "R0": []
    }

    for day in range(days):
        S_prev = np.sum(grid == INF)

        new_grid = grid.copy()

        infected = np.argwhere(grid == INF)
        for x, y in infected:
            for nx, ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if 0 <= nx < N and 0 <= ny < N:
                    if grid[nx, ny] == SUS and np.random.rand() < beta:
                        new_grid[nx, ny] = INF

            if np.random.rand() < gamma:
                new_grid[x, y] = REC

        S_after = np.sum(new_grid == INF)
        new_inf_today = max(0, S_after - S_prev)
        R0_today = (new_inf_today / (S_prev+1e-9))

        grid = new_grid

        stats["S"].append(np.sum(grid==SUS))
        stats["I"].append(np.sum(grid==INF))
        stats["R"].append(np.sum(grid==REC))
        stats["new_infections"].append(new_inf_today)
        stats["R0"].append(R0_today)

    return grid, stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=1000)
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--beta", type=float, default=0.25)
    ap.add_argument("--gamma", type=float, default=0.05)
    ap.add_argument("--mu", type=float, default=0.00)
    ap.add_argument("--init_frac", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=str)
    args = ap.parse_args()

    grid, stats = simulate_sequential(
        args.size, args.days,
        args.beta, args.gamma, args.mu,
        args.init_frac, args.seed
    )

    np.savez(args.out, grid=grid, stats=stats)
    print("Sequential simulation completed.")
