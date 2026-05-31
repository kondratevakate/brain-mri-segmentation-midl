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

---

## Multi-method TTA ensemble: independent errors allow further variance reduction

**Pilot finding (n=1, SynthSeg vs FastSurfer, +3° rotation, 2018 scan):**

The rotation responses of SynthSeg and FastSurfer are nearly **uncorrelated**
(r = −0.068 across 12 subcortical structures). For 4 of 12 structures the two
methods move in *opposite* directions under the same rotation — not because one
is correct, but because their architectures have different orientation sensitivities.

Consequences for ensemble TTA:
- **Independent errors → ensemble works.** Averaging N independent estimators
  reduces variance as 1/√N. For two methods: ~30% variance reduction.
- **Practical estimate:** SynthSeg TTA (9 angles) CV ~1.24%; FastSurfer TTA
  (pending full sweep) ~1.1%. Combined ensemble: theoretical ~0.87%.
- **Caveat:** the methods have systematic offsets (e.g. amygdala: SynthSeg 1.71 mL
  vs FastSurfer 1.47 mL, −14%). The ensemble mean lives in a blended space — valid
  as a pseudo-reference for the information-loss experiment, but not comparable
  with single-method literature norms.

**Proposed extension:** sweep the full 9-angle TTA for FastSurfer, compute
pairwise correlations across all available methods, and identify the minimum
orthogonal subset (maximum diversity, minimum correlation) that yields the most
stable ensemble without redundancy.

---

## Which segmenter is best for which anatomy?

A systematic question this paper does not answer: across available tools, which
achieves the most reproducible estimates for cortical, subcortical, and
white-matter tract measurements?

### Segmenters to compare

**Subcortical** (hippocampus, amygdala, thalamus, basal ganglia):

| Tool | Approach | Status in this study |
|---|---|---|
| SynthSeg (FreeSurfer 8) | DL, contrast/resolution-agnostic | ✅ all 3 scanners |
| FastSurfer VINN | DL, multi-view CNN | ✅ 2018 (2024 failed: IR contrast) |
| FreeSurfer 7.4 | Atlas-based (GCA), talairach-registered | ⏳ running (2018) |
| FIRST (FSL) | Shape + appearance model, subcortical-specific | ❌ not yet run |
| BrainChop | Browser-based DL, multiple model options | ❌ not yet run |

**Cortical** (thickness, parcellation, volume per lobe):

| Tool | Approach | Status |
|---|---|---|
| FreeSurfer 7.4 recon-all | Surface-based, Desikan-Killiany / Destrieux | ⏳ running |
| FastSurfer surface module | Surface-based, faster than FS | ✅ 2018 (full recon done) |
| CAT12 (SPM-based) | Voxel-based morphometry + surface | ❌ not yet run |
| SynthSeg --parc | Cortical parcellation, contrast-agnostic | ❌ not yet run |

**White matter tracts:**

| Tool | Approach | Status |
|---|---|---|
| TractSeg (Wasserthal 2018) | DL bundle segmentation from FOD | ❌ requires ≥30-dir DWI |
| TRACULA (FreeSurfer) | Probabilistic tractography, atlas priors | ❌ requires ≥30-dir DWI |
| AFQ / pyAFQ | Classical streamline-based bundle extraction | ❌ requires ≥30-dir DWI |

**Note on this dataset:** the 2024 session has DWI (701_dw_ssh.nii.gz, b=800,
N=2 directions, 5.5 mm slices). This is a clinical screening acquisition —
insufficient for tractography (minimum ~6 directions required; research-grade
needs ≥30). Any tract comparison would require a dedicated DWI acquisition.

### What is actually unknown

Published comparisons (e.g. Tustison et al., Wachinger et al.) typically evaluate
on T1-MPRAGE at 1 mm isotropic. Cross-scanner reproducibility specifically for
each anatomy type, comparable to our n=1 pilot, has not been reported for the
full method matrix above. The following remain open questions:

1. **Subcortical reproducibility per method** across 1.5T / 3T / different vendors:
   does atlas-based (FS7.4) outperform DL (FastSurfer, SynthSeg) when the input
   diverges from training distribution?

2. **Cortical thickness reproducibility at 5 mm slice thickness** (2022 Siemens):
   all surface-based methods require near-isotropic input; at 5 mm, only
   SynthSeg `--parc` is expected to attempt cortical parcellation. What does
   the information-loss curve look like for cortical vs subcortical?

3. **Optimal ensemble composition:** given pairwise error correlations, what
   is the minimum set of methods that achieves a stable pseudo-reference?
   Pilot data suggests SynthSeg + FastSurfer is already near-orthogonal (r ≈ 0);
   adding an atlas-based method (FS7.4) with a different failure mode
   (orientation-invariant but morphology-dependent) would further diversify.

---

*Pilot data collected on n=1 (self), 3 scanners (GE 3T 2018, Siemens 1.5T 2022,
Philips 1.5T 2024), SynthSeg robust, FreeSurfer 8.0.0. Scripts in `reprocess_2026/`.*
