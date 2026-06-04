# AnimalTA — Lymnaea build (v3.2.2-lymnaea)

A build of [AnimalTA](https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.14115)
with fixes and refinements for analysing **_Lymnaea_ (pond snail) locomotion**.
Based on AnimalTA 3.2.2 by Chiara & Kim (2023).

## Install (recommended — no Python required)

1. Go to the **[Releases page](https://github.com/Xyrex69/AnimalTA-Lymnaea/releases)**.
2. Download `AnimalTA.exe` from the latest release.
3. Double-click it. That is all — no Python, no package installation, no terminal.

> The `.exe` is a single self-contained file (it bundles Python and all
> libraries). Windows may warn that the app is unrecognised because the file is
> not code-signed; choose **More info → Run anyway**. First launch can take a
> few seconds while it unpacks.

## What this build changes vs. standard AnimalTA

- **Fixes the per-individual analysis pop-up** that previously displayed `0.0`
  for all six summary statistics: each metric is now computed independently so a
  single error can no longer blank them all.
- **Fixes a packaged-build crash on video load** (the `decord` video library's
  native DLLs were not bundled).
- **Applies a default movement threshold** (0.03 cm/s) when a project has none
  set, so "average speed while moving" and "proportion of time moving" are
  meaningful instead of identical to the overall average. Researchers can still
  override it per video in the speed-graph pop-up.
- **Adds a transparency note** in the pop-up and a methods document so the
  computed values are clearly traceable to the tracked coordinates.

The exact computation of speed, distance, and movement is documented in
[`METHODS_locomotion_stats.md`](METHODS_locomotion_stats.md). All values are
deterministic functions of the tracked coordinates — nothing is fabricated.

## Run or build from source (only if you want to modify the code)

Requires Python 3.9 and the dependencies AnimalTA uses (numpy, scipy, opencv,
scikit-image, scikit-learn, matplotlib, pandas, decord, Pillow, etc.).

```
# Run from source
python cli.py

# Rebuild the standalone .exe (output appears in dist/)
pip install pyinstaller
pyinstaller AnimalTA.spec
```


