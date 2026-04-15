Full paper camera-ready package for MIDL 2026.

Track assumption used here: validation track (`16` pages for the main body; acknowledgments, references, and appendix do not count toward that limit).

Resolved OpenReview submission number: `18`.

What is already prepared here:

- `midl26_18.tex`
- `midl26_18.bib`
- `midl.cls`
- `orcid.png`
- `images/` with only the figures referenced by the paper

What you still need to do manually:

1. Keep `\jmlrvolume{-- nnn}` unchanged, as requested by the MIDL instructions.
2. Compile with standard `pdflatex` until references are resolved.
3. Sign the PMLR copyright form and upload it separately in OpenReview.
4. Upload the final PDF, the LaTeX zip, and the signed copyright form by April 15, 2026.

Suggested compile sequence:

```powershell
pdflatex -interaction=nonstopmode midl26_18.tex
bibtex midl26_18
pdflatex -interaction=nonstopmode midl26_18.tex
pdflatex -interaction=nonstopmode midl26_18.tex
```

Static checks already addressed in this package:

- `\documentclass{midl}` without `anon`
- camera-ready `\jmlr...` metadata for full papers
- no `times` package
- no `hyperref` override
- no `thebibliography` environment
- bibliography moved to `midl26_18.bib`

Current environment note:

- This repository snapshot was prepared without a LaTeX toolchain available in the current shell, so successful `pdflatex` / `bibtex` compilation still needs to be verified on a machine with TeX installed.
