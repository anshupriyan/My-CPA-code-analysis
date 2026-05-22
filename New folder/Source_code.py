import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from tqdm import tqdm
from collections import Counter
from multiprocessing import Pool, cpu_count


# Parameters

MOD = 3329
N_TRACES = 15000

R_FILE = "polynomials_15000.csv"
TRACES_FILE = "output_hw_NTT_15000_much_noisy_traces.csv"

TOP_N = 10
COEFFS_TO_ATTACK = list(range(10))   # <-- change this list


# Load data ONCE

print("Loading data...")
r = pd.read_csv(R_FILE, nrows=N_TRACES).to_numpy()
traces = pd.read_csv(TRACES_FILE, nrows=N_TRACES).to_numpy()

traces = (traces - np.mean(traces, axis=0)) / np.std(traces, axis=0)

print("r shape:", r.shape)
print("traces shape:", traces.shape)

T = traces.shape[1]


# Leakage model

def hamming_weight(x):
    return bin(int(x) & 0xffffffff).count("1")

def predicted_leakage_for_key(k, r_i):
    return np.array([
        hamming_weight((k * r_i[j]) % MOD)
        for j in range(len(r_i))
    ])

def safe_window(a, b):
    return list(range(max(0, a), min(T, b)))


# Full pipeline per coefficient

def full_attack(coeff_idx):
    r_i = r[:, coeff_idx]

    # -------- Phase 1 --------
    corrs_over_time = []
    for t in tqdm(range(T),
                  desc=f"[Coeff {coeff_idx}] Phase 1",
                  position=coeff_idx % 12,
                  leave=False):
        max_corr = 0.0
        for k in range(MOD):
            pred = predicted_leakage_for_key(k, r_i)
            if np.std(pred) == 0:
                continue
            corr, _ = pearsonr(pred, traces[:, t])
            max_corr = max(max_corr, abs(corr))
        corrs_over_time.append(max_corr)

    corrs_over_time = np.array(corrs_over_time)
    t_peak = int(np.argmax(corrs_over_time))
    peak_val = corrs_over_time[t_peak]

    # -------- Phase 2 --------
    windows = [
        safe_window(t_peak - 1, t_peak + 2),
        safe_window(t_peak - 2, t_peak + 3),
        safe_window(t_peak - 3, t_peak + 4),
        safe_window(t_peak - 4, t_peak + 5),
    ]

    # -------- Phase 3 --------
    window_results = []
    for window in windows:
        correlations = np.zeros(MOD)
        for k in range(MOD):
            pred = predicted_leakage_for_key(k, r_i)
            if np.std(pred) == 0:
                continue
            score = 0.0
            for t in window:
                corr, _ = pearsonr(pred, traces[:, t])
                score += corr * corr
            correlations[k] = score

        top_keys = np.argsort(correlations)[-TOP_N:][::-1]
        window_results.append(top_keys)

    # -------- Phase 4 --------
    counter = Counter()
    for keys in window_results:
        for k in keys:
            counter[k] += 1

    # Final result object
    return {
        "coeff": coeff_idx,
        "t_peak": t_peak,
        "peak_corr": float(peak_val),
        "stability": dict(counter)
    }


# Parallel execution

if __name__ == "__main__":
    workers = min(len(COEFFS_TO_ATTACK), cpu_count() - 2)
    print(f"\nRunning {len(COEFFS_TO_ATTACK)} coefficients using {workers} workers\n")

    with Pool(workers) as p:
        results = p.map(full_attack, COEFFS_TO_ATTACK)

 
    # Clean final output
 
    print("\n\n========== FINAL RESULTS ==========\n")

    for res in sorted(results, key=lambda x: x["coeff"]):
        print(f"Coeff {res['coeff']}")
        print(f"  Peak t = {res['t_peak']} | corr = {res['peak_corr']:.4f}")
        print("  Key stability:")
        for k, c in sorted(res["stability"].items(), key=lambda x: -x[1]):
            print(f"    Key {k}: {c}/4 windows")
        print("-" * 40)
