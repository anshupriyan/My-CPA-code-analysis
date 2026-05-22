Metamorphosis – Submission Code

Files Required

Place the following dataset files in the same folder as the script before running:

polynomials_15000.csv

output_hw_NTT_15000_much_noisy_traces.csv


The code expects these exact filenames.


---

How to Run

python source_code.py

No additional configuration is required.
The script automatically performs:

Leakage peak detection

Multi-window CPA

Stability-based key ranking

Analysis of the first 10 coefficients



---

Dependencies

Install required libraries with:

pip install numpy pandas scipy tqdm matplotlib

Libraries used:

numpy

pandas

scipy

tqdm

matplotlib

multiprocessing

collections



---

Notes

Execution is CPU-intensive and may take significant time on large datasets.

Output is printed directly to the terminal (sample provided in output_log.txt).



---
