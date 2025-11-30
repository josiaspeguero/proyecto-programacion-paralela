import numpy as np
import argparse
from multiprocessing import Process, Pipe
import time

SUS = 0
INF = 1
REC = 2

###########################################
#   Worker: actualiza un bloque de la grilla
###########################################
def worker_proc(conn, beta, gamma, mu, N, cols_range):
    while True:
        msg = conn.recv()
        if msg == "STOP":
            break

        grid, ghost_left, ghost_right = msg

        local = grid.copy()
        rows = local.shape[0]

        new_local = local.copy()

        for x in range(rows):
            for y in range(local.shape[1]):
                cell = local[x, y]

                if cell == INF:
                    # vecinos: arriba/abajo/izquierda/derecha

                    # arriba
                    if x > 0 and local[x-1, y] == SUS and np.random.rand() < beta:
                        new_local[x-1, y] = INF

                    # abajo
                    if x < rows-1 and local[x+1, y] == SUS and np.random.rand() < beta:
                        new_local[x+1, y] = INF

                    # izquierda
                    gy = cols_range[0] + y
                    if y == 0:
                        if ghost_left is not None and ghost_left[x] == SUS and np.random.rand() < beta:
                            ghost_left[x] = INF
                    else:
                        if local[x, y-1] == SUS and np.random.rand() < beta:
                            new_local[x, y-1] = INF

                    # derecha
                    if y == local.shape[1]-1:
                        if ghost_right is not None and ghost_right[x] == SUS and np.random.rand() < beta:
                            ghost_right[x] = INF
                    else:
                        if local[x, y+1] == SUS and np.random.rand() < beta:
                            new_local[x, y+1] = INF

                    # recuperación
                    if np.random.rand() < gamma:
                        new_local[x, y] = REC

        # stats del bloque
        S_count = np.sum(new_local == SUS)
        I_count = np.sum(new_local == INF)
        R_count = np.sum(new_local == REC)

        conn.send((new_local, ghost_left, ghost_right,
                   S_count, I_count, R_count))
    conn.close()

###########################################
#   Divide la grilla para los workers
###########################################
def split_ranges(N, workers):
    block = N // workers
    ranges = []
    for w in range(workers):
        start = w * block
        end = (w + 1) * block if w < workers-1 else N
        ranges.append((start, end))
    return ranges

###########################################
#   Main paralelo
###########################################
def simulate_parallel(N, days, beta, gamma, mu, init_frac, seed, workers):
    np.random.seed(seed)

    # inicialización
    grid = np.zeros((N, N), dtype=np.uint8)
    num_initial = int(N*N * init_frac)
    idx = np.random.choice(N*N, num_initial, replace=False)
    grid.flat[idx] = INF

    ranges = split_ranges(N, workers)

    # Crear procesos
    processes = []
    parents = []
    for w in range(workers):
        p_conn, c_conn = Pipe()
        cols_range = ranges[w]
        p = Process(target=worker_proc,
                    args=(c_conn, beta, gamma, mu, N, cols_range))
        p.start()
        parents.append(p_conn)
        processes.append(p)

    stats = {
        "S": [], "I": [], "R": [],
        "new_infections": [],
        "R0": []
    }

    for day in range(days):
        S_prev = np.sum(grid == INF)

        # preparar mensajes para cada worker
        messages = []
        for w in range(workers):
            c0, c1 = ranges[w]
            block = grid[:, c0:c1]

            ghost_left = None
            ghost_right = None

            if w > 0:
                gl0, gl1 = ranges[w - 1]
                ghost_left = grid[:, gl1 - 1].copy()

            if w < workers - 1:
                gr0, gr1 = ranges[w + 1]
                ghost_right = grid[:, gr0].copy()

            messages.append((block, ghost_left, ghost_right))

        # enviar trabajo
        for w in range(workers):
            parents[w].send(messages[w])

        # recibir resultados
        new_blocks = []
        totalS = totalI = totalR = 0
        ghost_updates = []

        for w in range(workers):
            new_block, gL, gR, s, i, r = parents[w].recv()
            new_blocks.append(new_block)
            totalS += s
            totalI += i
            totalR += r
            ghost_updates.append((gL, gR))

        # reconstruir grid
        new_grid = np.zeros_like(grid)
        for w in range(workers):
            c0, c1 = ranges[w]
            new_grid[:, c0:c1] = new_blocks[w]

        # aplicar ghost updates entre bloques
        for w in range(workers):
            gL, gR = ghost_updates[w]

            if w > 0 and gL is not None:
                gl0, gl1 = ranges[w - 1]
                left_col = gl1 - 1
                new_grid[:, left_col] = gL

            if w < workers - 1 and gR is not None:
                gr0, gr1 = ranges[w + 1]
                right_col = gr0
                new_grid[:, right_col] = gR

        grid = new_grid

        new_inf_today = max(0, totalI - S_prev)
        R0_today = new_inf_today / (S_prev + 1e-9)

        stats["S"].append(totalS)
        stats["I"].append(totalI)
        stats["R"].append(totalR)
        stats["new_infections"].append(new_inf_today)
        stats["R0"].append(R0_today)

    # detener workers
    for p in parents:
        p.send("STOP")
    for p in processes:
        p.join()

    return grid, stats

###########################################
#   Main CLI
###########################################
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=1000)
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--beta", type=float, default=0.25)
    ap.add_argument("--gamma", type=float, default=0.05)
    ap.add_argument("--mu", type=float, default=0.00)
    ap.add_argument("--init_frac", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", type=str)
    args = ap.parse_args()

    t0 = time.time()

    grid, stats = simulate_parallel(
        args.size, args.days,
        args.beta, args.gamma, args.mu,
        args.init_frac, args.seed,
        args.workers
    )

    t1 = time.time()
    print(f"Parallel finished in {t1 - t0} seconds with {args.workers} workers.")

    np.savez(args.out, grid=grid, stats=stats)
