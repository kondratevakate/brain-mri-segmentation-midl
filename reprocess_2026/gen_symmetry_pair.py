#!/usr/bin/env python
"""Reuter symmetry test — isolate METHOD variance from scanner/biology variance.

Idea (M. Reuter): take ONE scan, produce two equally-interpolated copies, feed
them as two "timepoints". Since it is the same brain, same acquisition, any
volume difference the pipeline reports is pure METHOD variance (registration +
segmentation + resampling), NOT scanner or biology.

CRITICAL caveat (his): interpolate BOTH copies identically. If only one is
resampled, you measure the interpolation bias of one-vs-none, not method noise.
So we apply opposite small rotations (+theta / -theta), both trilinear-resampled
on the same grid. Neither copy has the "no-interpolation" advantage.

Output: two NIfTIs that then go through the SAME SynthSeg call as the paper.
The within-pair range/min is the method-variance FLOOR to compare against the
cross-scanner range/min already reported.
"""
import sys, os
import numpy as np
import nibabel as nib
from scipy.ndimage import rotate

IN = sys.argv[1]
OUTDIR = sys.argv[2]
THETA = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0  # degrees

os.makedirs(OUTDIR, exist_ok=True)
img = nib.load(IN)
data = np.asarray(img.dataobj, dtype=np.float32)

# Rotate in the axial-ish plane (first two axes). order=1 = trilinear,
# reshape=False keeps the original grid so both copies share geometry.
def make(theta, tag):
    rot = rotate(data, angle=theta, axes=(0, 1), reshape=False, order=1,
                 mode="constant", cval=0.0)
    out = nib.Nifti1Image(rot.astype(np.float32), img.affine, img.header)
    p = os.path.join(OUTDIR, f"2018_sym_{tag}.nii.gz")
    nib.save(out, p)
    print(f"wrote {p}  (theta={theta:+.1f} deg, trilinear, shape={rot.shape})")

make(+THETA, "rotpos")
make(-THETA, "rotneg")
print("Both copies interpolated identically (opposite rotations) — Reuter caveat satisfied.")
