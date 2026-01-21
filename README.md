# My-CPA-code-analysis

```python
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
```
# Breakdowns
## Imports

```python
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from tqdm import tqdm
from collections import Counter
from multiprocessing import Pool, cpu_count
```

**Why these are used:**

* **numpy** → all heavy math happens here (arrays for traces, leakage, correlations, etc.)
* **pandas** → used only for loading CSV files easily
* **pearsonr (scipy)** → this is the actual correlation function used for CPA
* **tqdm** → just for progress bars so I know the code isn’t stuck
* **Counter** → used later to count how often a key guess appears across windows (stability idea)
* **multiprocessing** → to run attacks on multiple coefficients in parallel and save time

---

## Parameters

```python
MOD = 3329
N_TRACES = 15000

R_FILE = "polynomials_15000.csv"
TRACES_FILE = "output_hw_NTT_15000_much_noisy_traces.csv"

TOP_N = 10
COEFFS_TO_ATTACK = list(range(10))
```

**What each parameter means:**

* **MOD = 3329**
  Kyber works modulo 3329, so this is used in the leakage model
  (`k * r mod 3329`).

* **N_TRACES = 15000**
  The real dataset contains 15,000 power traces.

* **R_FILE**
  CSV file containing the public polynomial values (`r`) for each trace.

* **TRACES_FILE**
  CSV file containing the measured power traces
  (15000 traces × ~640 time samples).

* **TOP_N = 10**
  For each CPA run, I keep the top 10 key candidates instead of only the best one.
  This helps later when checking which keys stay stable across windows.

* **COEFFS_TO_ATTACK**
  Kyber polynomials have 256 coefficients.
  For testing and analysis, I currently attack only coefficients 0–9.
  This can be changed to any list of indices.

---

## Leakage model

```python
def hamming_weight(x):
    return bin(int(x) & 0xffffffff).count("1")
```

This function just counts the number of 1-bits in a value.
In side-channel attacks, a common assumption is:

> Power consumption ≈ Hamming Weight of intermediate values

So this becomes the base of the leakage model.

---

### Predicted leakage for a key guess

```python
def predicted_leakage_for_key(k, r_i):
    return np.array([
        hamming_weight((k * r_i[j]) % MOD)
        for j in range(len(r_i))
    ])
```

What this does:

* `r_i` = all public values of one coefficient across all traces
* `k` = one guess for the secret coefficient
* For each trace:

  * compute `(k * r_i[j]) mod 3329`
  * take its Hamming Weight

This gives a vector like:

> “If the secret was k, this is what the device *should* leak across all traces.”

Later, this vector is correlated with the real power traces using CPA.

---

### Safe window helper

```python
def safe_window(a, b):
    return list(range(max(0, a), min(T, b)))
```

This is just a helper to avoid index errors.

When creating windows around the peak time (like `t_peak - 3` to `t_peak + 3`),
this function makes sure the window always stays inside valid trace boundaries.


---

## Full attack pipeline (per coefficient)

```python
def full_attack(coeff_idx):
    r_i = r[:, coeff_idx]
```

For each coefficient:

* `r` contains all polynomial values (shape: traces × coefficients)
* This line extracts **one coefficient across all traces**
* We attack one secret coefficient at a time (like subkeys in AES CPA)

---

### Phase 1 – Finding where leakage happens (POI detection)

```python
corrs_over_time = []
for t in range(T):
    max_corr = 0.0
    for k in range(MOD):
        pred = predicted_leakage_for_key(k, r_i)
        corr = corr(pred, traces[:, t])
        max_corr = max(max_corr, abs(corr))
    corrs_over_time.append(max_corr)
```

Idea:

* For every time sample `t`
* Try **all key guesses**
* Measure correlation between:

  * predicted leakage
  * actual power at time `t`

We store only the **maximum correlation over all keys**.

Why this?

> We are not trying to guess the key yet.
> We are trying to find *where in time* the device leaks information.

This gives us a curve of "how much leakage exists" at each time sample.

```python
t_peak = np.argmax(corrs_over_time)
```

This picks the time sample where leakage is strongest.
This is called the **Point of Interest (POI)**.

---

### Phase 2 – Creating windows around the peak

```python
windows = [
    safe_window(t_peak - 1, t_peak + 2),
    safe_window(t_peak - 2, t_peak + 3),
    safe_window(t_peak - 3, t_peak + 4),
    safe_window(t_peak - 4, t_peak + 5),
]
```

Instead of trusting one exact time sample, we create multiple windows around the peak.

Why?

* Real traces are noisy
* The true leakage might be slightly shifted
* Using multiple windows makes the attack more robust

Each window is just a slightly larger neighborhood around `t_peak`.

---

### Phase 3 – CPA inside each window

```python
for k in range(MOD):
    pred = predicted_leakage_for_key(k, r_i)
    score = 0.0
    for t in window:
        corr = pearsonr(pred, traces[:, t])
        score += corr * corr
    correlations[k] = score
```

For each window and each key guess:

* Compute correlation between predicted leakage and real traces
* Square the correlation
* Sum across the window

So each key gets a final score like:

> "How consistently does this key correlate across the window?"

This is more stable than using only a single time sample.

Then:

```python
top_keys = np.argsort(correlations)[-TOP_N:]
```

We keep only the top candidates for this window.

---

### Phase 4 – Stability analysis across windows

```python
counter = Counter()
for keys in window_results:
    for k in keys:
        counter[k] += 1
```

Now we check:

* Which key guesses appear in **multiple windows**
* Keys that appear in 4/4 or 3/4 windows are much more likely to be correct
* Random noise usually doesn’t survive across windows

This gives a simple but effective **confidence measure**.

---

### Returned result

```python
return {
    "coeff": coeff_idx,
    "t_peak": t_peak,
    "peak_corr": peak_val,
    "stability": dict(counter)
}
```

For each coefficient, we save:

* Where the leakage occurs
* How strong it is
* Which keys look most stable

This makes it easy to analyze results later.

---


## Parallel execution

```python
if __name__ == "__main__":
```

This is needed for Python multiprocessing to work properly (especially on Windows).

```python
workers = min(len(COEFFS_TO_ATTACK), cpu_count() - 2)
```

This decides how many CPU cores to use:

* Don’t use more workers than coefficients
* Leave 2 cores free so the system doesn’t freeze

Just a practical performance choice.

---

### Running the attack in parallel

```python
with Pool(workers) as p:
    results = p.map(full_attack, COEFFS_TO_ATTACK)
```

Each coefficient attack is independent, so they can run in parallel.

This means:

* Coefficient 0 runs on one core
* Coefficient 1 on another
* And so on

This makes the whole experiment much faster without changing any logic.

---

## Final output formatting

```python
for res in sorted(results, key=lambda x: x["coeff"]):
```

Just sorts results so coefficients are printed in order.

```python
print(f"Coeff {res['coeff']}")
print(f"  Peak t = {res['t_peak']} | corr = {res['peak_corr']:.4f}")
```

For each coefficient, we print:

* The time index where leakage was strongest
* The peak correlation value

```python
for k, c in sorted(res["stability"].items(), key=lambda x: -x[1]):
    print(f"    Key {k}: {c}/4 windows")
```

This prints key guesses ordered by stability:

* Keys that appear in 4/4 windows
* Then 3/4
* Then 2/4, etc.

The idea is:

> The more windows a key survives, the more likely it is to be correct.

---



