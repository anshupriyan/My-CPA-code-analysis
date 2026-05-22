import numpy as np
import pandas as pd
import sys
import time

# --- 1. CONFIGURATION ---
print("[-] Loading Data...")
try:
    traces_all = np.load('merged_final_dataset_V1.npy') 
    print(f"    -> Traces loaded: {traces_all.shape}")
    df = pd.read_csv('polynomials_final.csv', header=None)
    inputs_all = df.values
    print(f"    -> Inputs loaded: {inputs_all.shape}")
except:
    print("[!] Error: Files not found.")
    exit()

# CONSTANTS
Q = 3329
R_INV = 2704 
TARGET_INDEXES = [0, 14, 28, 42, 56, 70, 84, 98, 112, 126, 140, 
                  154, 168, 182, 196, 210, 224, 238, 252]

# --- 2. FAST LOOKUP TABLES ---
# Pre-calculate Hamming Weight for every number 0 to 3328.
# This makes looking up the leakage INSTANT (O(1)).
HW_TABLE = np.array([bin(x).count('1') for x in range(Q)], dtype=np.uint8)

# Pre-make the key array for matrix multiplication
KEYS = np.arange(Q, dtype=np.int64)

# --- 3. HELPER FUNCTIONS ---

def align_window(trace_window):
    """Fast FFT Alignment"""
    if len(trace_window) == 0: return trace_window
    
    # We use the FIRST trace as reference
    ref = trace_window[0]
    
    # Pre-compute FFT of reference for speed
    ref_fft = np.fft.fft(ref)
    aligned = []
    
    for t in trace_window:
        # Fast Correlation via FFT
        t_fft = np.fft.fft(t)
        # Multiply in frequency domain = convolution in time
        cross_corr = np.fft.ifft(t_fft * np.conj(ref_fft))
        
        # Find shift
        shift = np.argmax(np.abs(cross_corr))
        if shift > len(t) // 2:
            shift -= len(t)
            
        aligned.append(np.roll(t, -shift))
        
    return np.array(aligned)

# --- 4. THE TURBO SEARCH ---

# PARAMETERS
WINDOW_SIZE = 500
STRIDE = 500        # Full Coverage (No Gaps)
TOTAL_TRACES = traces_all.shape[0]

print(f"\n[*] Starting TURBO Search on {len(TARGET_INDEXES)} keys.")
print(f"[*] Scanning {TOTAL_TRACES} traces with Stride {STRIDE}...")
print("-" * 80)
print(f"{'Idx':<4} | {'Best Window Range':<20} | {'Key':<5} | {'Corr':<8} | {'Sample Pos':<10}")
print("-" * 80)

final_results = {}

total_steps = len(TARGET_INDEXES) * ((TOTAL_TRACES - WINDOW_SIZE) // STRIDE + 1)
current_step = 0
start_time = time.time()

for coeff_idx in TARGET_INDEXES:
    
    global_best = {"range": "None", "corr": 0.0, "key": 0, "pos": 0}
    
    scan_ranges = range(0, TOTAL_TRACES - WINDOW_SIZE, STRIDE)
    
    for start_trace in scan_ranges:
        stop_trace = start_trace + WINDOW_SIZE
        
        # --- PROGRESS UPDATE ---
        current_step += 1
        elapsed = time.time() - start_time
        avg_time = elapsed / current_step if current_step > 0 else 0
        remaining = avg_time * (total_steps - current_step)
        
        sys.stdout.write(f"\r[>] Processing Key {coeff_idx:<3} | Window {start_trace:<5} | {current_step}/{total_steps} | ETA: {remaining:.0f}s   ")
        sys.stdout.flush()
        # -----------------------

        # 1. Slice
        t_raw = traces_all[start_trace:stop_trace]
        i_chunk = inputs_all[start_trace:stop_trace, coeff_idx]
        
        # 2. Align (Still critical!)
        t_clean = align_window(t_raw)
        
        # 3. FAST MATRIX CPA (No loop!)
        # Center traces
        t_mean = np.mean(t_clean, axis=0)
        t_centered = t_clean - t_mean  # Shape: (500, Samples)
        
        # Calculate Hypotheses for ALL 3329 keys at once using Broadcasting
        # Formula: (Input * Key * R_INV) % Q
        # Shape: (500, 1) * (1, 3329) -> (500, 3329)
        intermediate = (np.int64(i_chunk[:, None]) * KEYS[None, :] * np.int64(R_INV)) % Q
        
        # Look up HW instantly
        h_matrix = HW_TABLE[intermediate] # Shape: (500, 3329)
        
        # Center Hypotheses
        h_means = np.mean(h_matrix, axis=0)
        h_centered = h_matrix - h_means[None, :]
        
        # VECTORIZED PEARSON CORRELATION
        # Numerator: Dot product of Traces and Hypotheses
        # We want the max correlation across time samples.
        # This is (Traces.T @ Hypotheses)
        # Shape: (Samples, 500) @ (500, 3329) -> (Samples, 3329)
        numerator = t_centered.T @ h_centered 
        
        # Denominator
        t_norm = np.linalg.norm(t_centered, axis=0) # Shape: (Samples,)
        h_norm = np.linalg.norm(h_centered, axis=0) # Shape: (3329,)
        
        # Divide (Outer product for denominator)
        denominator = t_norm[:, None] * h_norm[None, :]
        
        with np.errstate(divide='ignore', invalid='ignore'):
            c_matrix = np.abs(numerator / denominator)
            c_matrix[np.isnan(c_matrix)] = 0
            
        # Find the single best spike in this entire matrix
        # Flatten to find the absolute max, then unravel to get coordinates
        flat_idx = np.argmax(c_matrix)
        best_pos_idx, best_key_idx = np.unravel_index(flat_idx, c_matrix.shape)
        best_corr = c_matrix[best_pos_idx, best_key_idx]
        
        # 4. Update Winner
        if best_corr > global_best["corr"]:
            global_best["corr"] = best_corr
            global_best["range"] = f"{start_trace}-{stop_trace}"
            global_best["key"] = best_key_idx
            global_best["pos"] = best_pos_idx

    sys.stdout.write("\r" + " "*80 + "\r")
    print(f"{coeff_idx:<4} | {global_best['range']:<20} | {global_best['key']:<5} | {global_best['corr']:.4f}   | {global_best['pos']:<10}")
    
    final_results[coeff_idx] = global_best["key"]

print("-" * 80)
print("FINAL RECOVERED KEYS:")
print(final_results)