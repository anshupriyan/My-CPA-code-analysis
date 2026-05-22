# TraceForge

### Drift-Resilient Side-Channel Analysis Framework for Kyber CPA Attacks

> Rebuilding a first-year undergraduate cryptanalysis project from the ground up using community feedback, stronger statistical validation, and a cleaner experimental methodology.

---

# Overview

TraceForge is a research-oriented Side-Channel Analysis (SCA) framework focused on recovering Kyber secret coefficients under noisy and misaligned trace conditions.

The project began as an experimental undergraduate exploration into:

* Correlation Power Analysis (CPA)
* Leakage modeling
* Trace alignment
* Signal-to-noise optimization
* Statistical recovery pipelines
* Performance-oriented numerical computation

After receiving technical feedback from researchers and competitive reviewers, the project is now being rebuilt with a stronger focus on:

* rigorous validation
* reproducibility
* baseline comparisons
* statistically defensible methodology
* cleaner experimentation

The current direction focuses on adaptive local alignment and segmented CPA under cumulative clock drift conditions.

---

# Core Research Problem

Large trace datasets often suffer from:

* cumulative clock drift
* local desynchronization
* leakage instability
* inconsistent alignment quality
* varying signal-to-noise ratio across acquisition windows

Traditional global alignment strategies degrade as drift accumulates.

TraceForge explores whether:

> Localized alignment + adaptive segmented CPA can outperform global analysis under high-noise conditions.

---

# Current Architecture

```text
Raw Trace Dataset
        ↓
Window Segmentation
        ↓
Local FFT Alignment
        ↓
Leakage Hypothesis Generation
        ↓
Vectorized CPA Engine
        ↓
POI Detection
        ↓
Statistical Validation
        ↓
Key Recovery Evaluation
```

---

# Key Concepts

## 1. Localized Alignment

Instead of globally aligning the entire dataset, TraceForge divides traces into localized windows.

Each segment:

* establishes its own alignment reference
* compensates for local drift
* improves synchronization stability

This transforms the dataset into smaller high-quality "micro-aligned" regions.

---

## 2. FFT-Based Drift Correction

The framework uses FFT cross-correlation for fast trace realignment.

Goals:

* compensate temporal drift
* reduce alignment error
* preserve leakage consistency
* improve CPA convergence

---

## 3. Adaptive Window Search

The framework scans the dataset to locate regions with:

* highest leakage quality
* strongest correlation peaks
* best local signal-to-noise conditions

Rather than assuming uniform leakage quality across the dataset.

---

## 4. Vectorized CPA Engine

Instead of iterative key testing loops, TraceForge uses:

* NumPy broadcasting
* matrix-based Pearson correlation
* vectorized hypothesis computation

to evaluate all key hypotheses simultaneously.

This significantly reduces attack runtime.

---

# Leakage Model

Current implementation targets Kyber pointwise multiplication leakage using:

```text
HW((Input × Key × R^-1) mod Q)
```

Where:

* `Q = 3329`
* `R^-1 = 2704`

The framework currently uses a Hamming Weight leakage assumption.

Future work will explore:

* Hamming Distance models
* hybrid leakage models
* template-based approaches
* mutual information analysis

---

# Research Goals

## Current Goals

* [x] Implement vectorized CPA pipeline
* [x] Add FFT-based local alignment
* [x] Segment datasets into adaptive windows
* [x] Recover coefficients under noisy conditions
* [ ] Add rigorous baseline comparisons
* [ ] Implement SNR-based POI ranking
* [ ] Add guessing entropy evaluation
* [ ] Add success-rate curves
* [ ] Validate reproducibility across datasets

---

# Future Directions

Planned extensions:

* PCA/LDA dimensionality reduction
* automatic POI selection
* alignment quality metrics
* noise robustness benchmarking
* GPU acceleration
* template attacks
* mutual information analysis
* deep-learning-assisted trace classification
* automated experiment tracking

---

# Important Note

This repository is intentionally experimental.

The original version of this project was developed during the author's first undergraduate semester while simultaneously learning:

* cryptography
* signal processing
* statistical analysis
* numerical optimization
* side-channel methodology

Several earlier heuristics and assumptions are being re-evaluated and rebuilt using community feedback and stronger validation methods.

The goal of this rebuild is not just higher recovery performance, but:

> building a more rigorous and reproducible research pipeline.

---

# Tech Stack

* Python
* NumPy
* SciPy
* Pandas
* FFT-based alignment
* Vectorized statistical computation

---


