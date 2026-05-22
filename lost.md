# Project Recovery Notes — TraceForge Rebuild

This document tracks recovered artifacts, missing components, experimental assumptions, and reconstruction progress for the TraceForge Side-Channel Analysis rebuild.

---

# Current Status

The original project was partially lost due to local system issues before the repository was fully pushed and versioned.

The rebuild process focuses on:
- recovering surviving artifacts
- reconstructing the experimental pipeline
- improving statistical rigor
- documenting assumptions properly
- rebuilding reproducible experiments

---

# Recovered Components

## Core CPA Pipeline
- Vectorized Pearson CPA implementation
- Hamming Weight leakage model
- Kyber modular arithmetic flow
- Localized window-based trace segmentation
- FFT-based local alignment
- Parallelized coefficient processing

---

## Recovered Concepts
- Adaptive segmented CPA
- Local alignment under cumulative drift
- Local SNR optimization
- Window scanning methodology
- Peak correlation extraction
- Vectorized hypothesis generation

---

## Recovered Artifacts
- Partial attack scripts
- Experimental screenshots
- Recovery outputs
- Professor/reviewer feedback
- Telegram progress logs
- Trace recovery outputs
- Methodology notes
- Performance optimization fragments

---

# Likely Missing Files

## Validation Scripts
Potentially missing:
- rank evolution analysis
- guessing entropy evaluation
- SNR measurement tools
- statistical comparison scripts
- baseline benchmarking

---

## Visualization Code
Potentially missing:
- correlation-over-time plots
- alignment visualizations
- leakage heatmaps
- window comparison graphs
- signal quality plots

---

## Experimental Variants
Potentially missing:
- alternative window sizes
- stride experiments
- normalization experiments
- denoising attempts
- alternate leakage models
- failed heuristics
- baseline comparison pipelines

---

## Performance Optimization Iterations
Potentially missing:
- early loop-based CPA versions
- profiling experiments
- multiprocessing prototypes
- matrix optimization variants

---

## Dataset Metadata
Need to recover:
- acquisition assumptions
- hardware assumptions
- trace generation details
- sampling conditions
- challenge configuration
- leakage assumptions

---

# Important Research Lessons

## 1. Aggressive Heuristics Need Validation
Earlier versions introduced experimental confidence heuristics that lacked sufficient statistical grounding.

Key lesson:
> intuitive signal-processing ideas must still be experimentally validated.

---

## 2. Local Alignment Was a Stronger Direction
The move toward:
- localized FFT alignment
- adaptive segmented CPA
- local drift correction

was significantly more defensible than earlier overlap-based voting logic.

---

## 3. Baselines Matter
Future experiments must always include:
- classical CPA baselines
- reproducible metrics
- direct comparisons
- controlled evaluation

---

# Reconstruction Priorities

## Phase 1 — Artifact Recovery
- [ ] Recover Telegram logs
- [ ] Recover screenshots
- [ ] Recover output logs
- [ ] Recover notebooks/scripts
- [ ] Recover PDFs/plots
- [ ] Recover challenge documentation

---

## Phase 2 — Baseline Rebuild
- [ ] Rebuild classical CPA pipeline
- [ ] Validate leakage assumptions
- [ ] Verify alignment correctness
- [ ] Establish baseline recovery metrics

---

## Phase 3 — Experimental Extensions
- [ ] Reintroduce local alignment
- [ ] Add adaptive segmentation
- [ ] Add SNR-based POI selection
- [ ] Benchmark against baseline

---

## Phase 4 — Rigorous Validation
- [ ] Guessing entropy evaluation
- [ ] Success-rate curves
- [ ] Reproducibility testing
- [ ] Noise robustness analysis
- [ ] Statistical confidence analysis

---

# Long-Term Goals

Planned future directions:
- PCA/LDA dimensionality reduction
- Mutual Information Analysis
- Template attacks
- Deep-learning-assisted trace analysis
- GPU acceleration
- Automated experiment tracking
- Comparative benchmarking suite

---

# Key Reminder

The goal of this rebuild is NOT only:
> “recover the key faster”

The real goal is:
- building rigorous methodology
- learning reproducible experimentation
- improving statistical reasoning
- understanding SCA research practices properly

---

# Repository Structure (Planned)

```text
traceforge/
├── datasets/
├── recovered_notes/
├── failed_experiments/
├── validation/
├── plots/
├── outputs/
├── alignment/
├── cpa/
├── experiments/
├── benchmarks/
└── docs/