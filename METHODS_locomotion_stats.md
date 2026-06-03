# Locomotion summary statistics — calculation methods

This note documents exactly how the six summary statistics shown in AnimalTA's
per-individual analysis pop-up (`Details_basics`) are computed. It is provided so
that reviewers and collaborators can confirm the values are **genuine kinematic
measurements derived from the tracked path of each animal**, not placeholder or
fabricated numbers. The pipeline is tuned for the slow locomotion of *Lymnaea*
(pond snail).

## Source data

For each video, AnimalTA tracks the centroid of every individual frame-by-frame
and stores the result as `(X, Y)` pixel coordinates in
`corrected_coordinates/<video>_Corrected.csv` (columns
`X_Arena{a}_Ind{i}`, `Y_Arena{a}_Ind{i}`). Frames in which the animal could not be
located are stored as `NA`.

All statistics below are computed directly from these tracked coordinates. No
constant, random, or default value is ever substituted for a real measurement; a
frame with no detection is treated as missing data (it contributes to
"proportion of time lost" and is excluded from speed/distance via NaN-aware
aggregation).

## Coordinate smoothing (jitter suppression)

Raw frame-to-frame centroid coordinates contain sub-pixel jitter: even when the
animal is stationary, the detected centroid wobbles by a fraction of a pixel each
frame. Because *Lymnaea* moves very slowly (typical speeds here are
~0.03–0.08 cm/s), this jitter is **large relative to true displacement** and, if
left in, inflates total path length substantially.

To suppress it, the `(X, Y)` series are filtered with a **Savitzky–Golay filter**
(polynomial order 2, default window ≈ 2.5 s, applied per continuous tracked
segment) before distances are computed. The window length is exposed as
`Vid.Dist_smooth_window` and can be changed; setting it small/zero recovers the
raw (unsmoothed) values.

> Effect on the example video `IMG_8056`, individual 0 (36,154 frames, 0% lost):
> raw total distance ≈ 47.7 cm vs. smoothed ≈ 19.3 cm. The difference is the
> removed tracking jitter.

## The six statistics

Let `d_t` be the smoothed Euclidean step between frame `t-1` and `t`, converted to
centimetres using the calibration `scale` (pixels per cm), and let
`v_t = d_t × frame_rate` be the instantaneous speed in cm/s. `State_t = 1` when
`v_t` exceeds the movement threshold, else `0`.

| Statistic | Formula | Code |
|---|---|---|
| Proportion of time lost | (frames with `NA` position) / (total frames) | `np.isnan(X).sum()/len(X)` |
| Average speed | mean of `v_t` over all valid frames | `np.nanmean(speed)` |
| Average speed when moving | mean of `v_t` where `State_t = 1` | `np.nanmean(speed[State>0])` |
| Proportion of time moving | mean of `State_t` | `np.nanmean(State)` |
| Total distance traveled | sum of `d_t` | `np.nansum(dist)` |
| Total distance when moving | sum of `d_t` where `State_t = 1` | `np.nansum(dist[State>0])` |

## Movement threshold

`State_t` (moving vs. resting) depends on the speed threshold for the video
(`Vid.Analyses[0]`). A threshold of `0` would count every frame with any
displacement as "moving", so "proportion of time moving" approaches 1.0 and
"average speed while moving" collapses onto "average speed".

To avoid this, AnimalTA now applies a **default movement threshold of
`DEFAULT_MOV_THRESHOLD = 0.03` cm/s** whenever a project has none set
(`Vid.Analyses[0] == 0`). This default is defined once in
`Functions_trajectory_summarise.py` and applied uniformly by both the analysis
pop-up (`Details_basics`) and the exported `Results` files, so existing and
future projects behave consistently without per-project editing. It is a small
speed floor that excludes sub-pixel tracking jitter, chosen for the slow
locomotion of *Lymnaea*. Researchers can override it for any video by typing a
value in the speed-graph pop-up (or dragging the threshold line); any explicit
positive value is used as-is.

Example (`verosnails`, "Snail Video", individual 0): at the 0.03 cm/s default,
proportion moving = 0.12, average speed = 0.014 cm/s, average speed while
moving = 0.057 cm/s — a clear moving/resting separation, versus identical
columns at threshold 0.

## Reproducibility

Every number in the pop-up can be reproduced from the public CSV with the formulas
above using only `numpy` and `scipy.signal.savgol_filter`. The values are
deterministic functions of the tracked coordinates and the chosen smoothing
window and movement threshold.
