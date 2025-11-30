# run_experiments.py
import subprocess
import csv
import time
import os
import argparse

def run_cmd(cmd):
    print("Running:", " ".join(cmd))
    t0 = time.time()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    t = time.time() - t0
    print(proc.stdout)
    if proc.returncode != 0:
        print("Error:", proc.stderr)
    return t

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=200)
    parser.add_argument("--days", type=int, default=100)
    parser.add_argument("--outdir", type=str, default="results")
    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    results = []
    # Run sequential
    seq_cmd = ["python", "sequential.py", "--size", str(args.size), "--days", str(args.days),
               "--out", os.path.join(args.outdir, "seq.npz")]
    t_seq = run_cmd(seq_cmd)
    results.append(("sequential", 1, t_seq))

    for workers in [1,2,4,8]:
        par_cmd = ["python", "parallel.py", "--size", str(args.size), "--days", str(args.days),
                   "--workers", str(workers), "--out", os.path.join(args.outdir, f"par_{workers}.npz")]
        t_par = run_cmd(par_cmd)
        results.append(("parallel", workers, t_par))

    # Save CSV and speed-up plot data
    csv_path = os.path.join(args.outdir, "times.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mode","workers","time_s"])
        for r in results:
            w.writerow(r)
    print("Saved times to", csv_path)
    # You can plot speed-up afterwards using matplotlib (read csv)
