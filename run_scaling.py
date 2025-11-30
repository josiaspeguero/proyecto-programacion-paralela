import subprocess
import csv
import time
import matplotlib.pyplot as plt

SIZE = 1000
DAYS = 365
INIT_FRAC = 1e-3
SEED = 123

workers_list = [1, 2, 4, 8]
results = []

for w in workers_list:
    out_file = f"results/par_w{w}.npz"
    
    print(f"\n=== Ejecutando parallel.py con {w} workers ===")

    start = time.time()
    subprocess.run([
        "python",
        "parallel.py",
        "--size", str(SIZE),
        "--days", str(DAYS),
        "--workers", str(w),
        "--out", out_file,
        "--seed", str(SEED),
        "--init_frac", str(INIT_FRAC),
        "--snap_interval", "0"
    ])
    end = time.time()

    elapsed = end - start
    print(f"Tiempo: {elapsed:.4f} s")

    results.append((w, elapsed))

# --- Guardar CSV ---
csv_path = "results/scaling.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["workers", "time_seconds", "speedup"])

    t1 = results[0][1]
    for w, t in results:
        writer.writerow([w, t, round(t1 / t, 4)])

print("\nCSV generado en results/scaling.csv")

# --- Generar gráfica ---
workers = [r[0] for r in results]
times = [r[1] for r in results]
speedups = [times[0] / t for t in times]

plt.figure()
plt.plot(workers, speedups, marker="o")
plt.title("Strong Scaling - Speedup vs Workers")
plt.xlabel("Workers")
plt.ylabel("Speedup")
plt.grid(True)
plt.savefig("results/speedup.png")

print("Gráfica guardada en results/speedup.png")
