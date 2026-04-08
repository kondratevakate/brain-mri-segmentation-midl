# OpenReview Metadata

Use these values to update the OpenReview camera-ready fields. They are synchronized with the current `midl26_18.tex` source.

OpenReview record:

- Forum ID: `Xogz6ecMlY`
- Submission Number: `18`

## Title

Benchmarking the Reproducibility of Brain Tissue Segmentation Across MRI Scanners

## Abstract

Accurate and reproducible brain morphometry from structural magnetic resonance imaging is critical for monitoring neuroanatomical changes across time and imaging domains. Although deep learning has accelerated segmentation workflows, scanner-induced variability and limited reproducibility remain major obstacles, particularly in longitudinal and multi-site studies. In this study, we benchmark two state-of-the-art segmentation pipelines, *FastSurfer* and *SynthSeg*, integrated into *FreeSurfer*, one of the most widely adopted neuroimaging tools. Using two complementary datasets---a 17-year single-subject longitudinal cohort and a nine-site test--retest cohort---we quantify between-scan segmentation variability with region-wise overlap and distance measures, including the Dice similarity coefficient, surface Dice, the 95th percentile of the Hausdorff distance, and the mean absolute percentage error in regional volumes.

Our results reveal up to 7--8% variation in the volumes of small subcortical structures such as the amygdala and ventral diencephalon, even under controlled test--retest conditions. This level of noise raises a critical question: can we reliably detect subtle longitudinal changes of 5--10% in small brain regions with volumes below 2 milliliters, given the magnitude of scanner- and site-induced morphometric variability? We further analyze how registration choices and interpolation modes contribute additional, although smaller, biases, and we show that surface-based quality filtering can remove outlier segmentations while preserving most scans and maintaining morphometric stability. This work provides a reproducible benchmark of modern FreeSurfer-based segmentation pipelines and highlights the need for harmonization and quality-control strategies to enable robust morphometry in real-world neuroimaging studies.

The code is publicly available at https://github.com/kondratevakate/brain-mri-segmentation

## Keywords

Machine Learning, Brain Morphometry, MRI, Multi-Scanner Variability, Dice, FreeSurfer, SynthSeg, Segmentation, Statistics, Test-Retest, Domain Shift
