# Future Work: Measuring the Information Loss Boundary in Brain MRI Segmentation

## Motivation

The reproducibility experiments in this paper (cross-scanner variability, n=1
pilot) reveal a gap: we can measure *that* segmentation results differ across
conditions, but we cannot yet measure *why* or *how much input degradation is
recoverable*. The following experimental design addresses this directly.

## Core idea

Current segmentation pipelines give a single point-estimate per scan. We
propose treating segmentation as a **signal recovery problem**: how much can we
degrade the input image and still recover a reference-level estimate?

The key insight from our pilot data: even the same scan produces different
volumes depending on head orientation (~1.2–1.8% CV across ±12° rotations).
This is not physics — it is model instability. The physically-grounded
interpolation floor is **0.05%**. Any gap above 0.05% is recoverable in
principle by a better method.

---

## Proposed experiment design

### Step 1 — Establish a pseudo-reference via TTA

Take one high-quality T1 (≥1 mm isotropic, clean SNR). Generate N augmented
copies (rotations, small intensity perturbations) and segment each with
FastSurfer or SynthSeg. Average the resulting label maps (or volumes).

This TTA-consensus estimate is the **pseudo-reference R**. It is not ground
truth (no in-vivo gold standard exists for subcortical volumes), but it is the
best single-method estimate obtainable, with reduced model instability:

```
R = mean(segment(augment_k(I)))  for k = 1..N
```

**Pilot data (this paper, n=1, SynthSeg, N=9, rotations ±12°):**
- Median CV across angles: **1.24%** (max: amygdala 1.83%)
- Amygdala excursion at ±12°: up to **5.5%** from 0°
- Importantly: most structures are **asymmetric** — TTA reduces bias, not just
  variance. The improvement from TTA is approximately 1.37% → 1.24%, modest,
  because the dominant effect is systematic orientation bias, not random noise.

### Step 2 — Controlled degradation

Apply a controlled degradation operator D_θ to the reference image I:
```
I_θ = D_θ(I)
```
Degradation types to sweep, in order of clinical relevance:

| Operator | Parameter θ | Clinical analogue |
|---|---|---|
| Rotation | 0–45° | head repositioning between sessions |
| Gaussian noise | σ = 0.01–0.5 (normalised) | low-SNR scanner / thin slice |
| Bias field | polynomial order 1–5 | B1 inhomogeneity (1.5T, surface coils) |
| Resolution downsampling | 1 → 2 → 3 → 5 mm | thick-slice clinical protocol |
| Contrast shift | ±20–60% intensity scale | different T1 sequence (FSPGR vs MPRAGE vs SE) |
| k-space subsampling | acceleration ×2–×8 | compressed sensing / accelerated acquisition |

### Step 3 — Recovery with method X, then TTA

For each degradation level θ, apply recovery method X, then compute TTA
consensus:
```
R_θ,X = mean(segment(augment_k(X(I_θ))))  for k = 1..N
```

**Method X candidates (in order of complexity):**
1. No recovery (identity) — baseline degradation curve
2. Simple preprocessing: N4 bias correction, denoising (ANTs, FSL), super-resolution
3. Existing pipeline components: SynthSR (super-resolution to 1mm), FreeSurfer's
   internal normalisation, SynthSeg's contrast-agnostic resampling
4. Generative harmonisation: flow-matching-based synthesis (e.g., MAISI-v2 style
   rectified flow, AAAI 2026); translate degraded scan to reference-contrast domain

### Step 4 — Measure the information loss boundary

For each structure s, degradation type D, and recovery method X, compute:
```
Δ(θ, X, s) = |R(s) - R_θ,X(s)| / R(s)  [%]
```

**Information is preserved** when `Δ(θ, X, s) < ε_interp = 0.05%`
(the physically-grounded interpolation floor measured in this paper).

**Information is partially recoverable** when `ε_interp ≤ Δ < ε_TTA = 0.5%`
(the TTA-reduced model floor).

**Information is lost** when `Δ > ε_TTA` and no method X achieves recovery
below this threshold.

The **information loss boundary** for structure s under degradation D is:
```
θ*(s, D, X) = min θ such that Δ(θ, X, s) > ε_TTA
```

This gives a concrete, quantitative limit: "hippocampal volumes are recoverable
from noise up to σ=0.3 with SynthSR, but not beyond."

---

## Biological validation (proxy signal)

For datasets with repeated single-subject measurements over time (e.g., the
SIMON dataset used in this paper, or IXI/ABIDE test-retest cohorts), a correctly
functioning segmentation pipeline should recover a monotone biological trend:

- Hippocampal volume decreases ~0.5%/year in healthy adults, ~2–4%/year in MCI
- Lateral ventricle volume increases with age

**Proposed test:** given a longitudinal single-subject series processed with
TTA-consensus, does the estimated trajectory:
(a) lie within the expected biological envelope for age/sex?
(b) show less variance across sessions than the single-pass estimate?

This is a *consistency* test, not accuracy vs ground truth. It provides a
second, independent validation that the pipeline is tracking biology rather than
scanner noise.

**Key threshold:** if within-subject session-to-session variance (TTA-corrected)
exceeds the expected annual biological change rate, the pipeline cannot detect
real longitudinal effects in a single subject — it is blind to the signal it was
designed to detect.

From our pilot: SynthSeg cross-sectional session variance ~17% (cross-scanner);
expected annual atrophy signal ~0.5%. The longitudinal pipeline is essential to
bridge this gap.

---

## Why current approaches do not fully solve this

**Longitudinal pipelines** (Reuter et al. 2012) reduce within-scanner
cross-sectional variance from ~2–3% to ~0.4–0.8% by joint estimation across
timepoints. They do not address cross-scanner variance or model instability.

**TTA with rotations** (our pilot, this paper): reduces variance from 1.4% to
~1.2% (median). Improvement modest — because dominant effect is orientation bias
(asymmetric model response), not symmetric random noise. TTA cannot correct
systematic bias.

**Equivariant architectures** (SE(3)-equivariant networks, e.g., using e3nn)
would reduce the rotation component to the physics floor (~0.05%) by
construction. Not yet practical for whole-brain segmentation at clinical scale
(memory/compute cost ~10× standard CNN).

**Generative harmonisation** (flow-matching models, e.g., MAISI-v2 AAAI 2026)
is theoretically promising for cross-scanner recovery but has not been validated
for subcortical volumetry accuracy — only for perceptual image quality. This
is an open research gap.

---

## Practical significance

The numbers from this paper's pilot define concrete, clinically meaningful
thresholds:

| Signal | Value | Method floor (this paper) |
|---|---|---|
| Annual hippocampal atrophy (healthy) | ~0.5%/year | SynthSeg cross-sectional: ~1.4% |
| Annual hippocampal atrophy (MCI) | ~2–4%/year | TTA-corrected: ~1.2% |
| Cross-scanner variability (this paper) | ~17% median, 45% max | — |
| Physics interpolation floor | 0.05% | — |

Single-subject longitudinal tracking with cross-sectional DL segmentation is
statistically underpowered for detecting healthy ageing. The proposed framework
gives a principled way to identify which degradations, recovery methods, and
anatomical structures cross the threshold from "recoverable" to "information
lost."

---

## Related work to position against

- Rotation/augmentation robustness of DL segmenters: Billot et al. 2023 (SynthSeg)
- Longitudinal pipeline for within-subject variance reduction: Reuter et al. 2012
- Test-time augmentation for medical image segmentation: general TTA literature
- Equivariant networks for 3D medical imaging: e3nn-based approaches
- Generative harmonisation: MAISI-v2 (Zhao et al. AAAI 2026), FlowLet (Jan 2026)
- FOMO25 challenge findings: foundation model generalisation under domain shift
- Clinical-ComBat for harmonisation: requires N>20 subjects per site — not
  applicable to single-subject design

---

*Pilot data collected on n=1 (self), 3 scanners (GE 3T 2018, Siemens 1.5T 2022,
Philips 1.5T 2024), SynthSeg robust, FreeSurfer 8.0.0. Scripts in `reprocess_2026/`.*
