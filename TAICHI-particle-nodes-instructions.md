# Taichi Particle Nodes Instructions

This guide covers every Taichi particle node in this pack, what each adjustment does, and practical tips for getting the look you want.

## Quick mental model

- **Emitters** define where particles start and how they launch.
- **Paths** define where emitters move.
- **Modulators** let features (audio, motion, etc.) drive emission, size, spread, and bursts.
- **Taichi Particle Mask** runs the simulation and renders the mask + image output.

## Core node chain

1. One or more **emitters** (Taichi Particle Emitter / Emitter On Path / Burst Spots / Emitter From Mask Edges)
2. Optional **modulators** (Audio Reactive Emission, Path Emitter Modulation)
3. **Taichi Particle Mask** to simulate and render

---

## Taichi Particle Mask

Runs the simulation and outputs a **MASK** and **IMAGE**.

**Inputs**
- `emitters`: list of emitter settings from any Taichi emitter node.
- `particle_count`: max particles in the sim. Higher is denser but slower.
- `particle_lifetime`: default lifespan in seconds (emitters can override).
- `wind_strength` / `wind_direction`: global wind force.
- `gravity`: vertical gravity (positive pulls downward).
- `frame_rate`: simulation FPS (affects motion smoothness and speed).
- `start_frame` / `end_frame`: gate emission to a frame range.

**Tips**
- If particles disappear too fast: raise `particle_lifetime` or set emitter-level `particle_lifetime`.
- If simulation looks too slow/fast: adjust `frame_rate` or `particle_speed`.
- If you hit particle caps: increase `particle_count` or use `endless_mode`.

---

## Taichi Particle Emitter

Basic stationary emitter.

**Position**
- `emitter_x`, `emitter_y`: normalized 0..1 position.

**Launch**
- `particle_direction`: base direction in degrees.
- `direction_offset`: extra angle added at emit time.
- `particle_spread`: spread cone in degrees.

**Particle appearance**
- `particle_size`: size in pixels.
- `particle_shape`: `circle`, `square`, or `spark`.
- `spark_length`: only for `spark` shape.
- `color`: RGB string e.g. `(255,255,255)`.

**Dynamics**
- `particle_speed`: speed in pixels/sec.
- `emission_rate`: particles/sec (base).
- `emission_radius`: spawn radius around the emitter.
- `particle_lifetime`: override lifetime for this emitter (0 = use global).
- `endless_mode`: reuse slots to keep emitting even if count is exceeded.

**Timing**
- `start_frame`, `end_frame`: per-emitter time window.

**Optional**
- `emitter_modulation`: connect `Taichi Audio Reactive Emission`.

---

## Taichi Audio Reactive Emission

Modulates emission rate and triggers bursts from a **FEATURE**.

**Emission modulation**
- `scale`: multiplier for the feature value.
- `threshold`: value below which modulation is ignored.
- `mode`: `relative` (multiplies base rate) or `absolute` (adds).

**Bursts**
- `onset_threshold`: delta threshold to trigger a burst.
- `burst_strength`: how many particles per delta.
- `burst_min`, `burst_max`: clamp burst size.

**Tips**
- If you want only bursts: set base `emission_rate` to 0 on the emitter.
- If bursts are too frequent: increase `onset_threshold` or apply feature smoothing.

---

## Taichi Particle Emitter On Path

Moves an emitter along a path. Use `TaichiPathFrom*` nodes to build paths.

**Path controls**
- `path`: the path data.
- `path_speed`: cycles per second (negative reverses).
- `loop_mode`: `loop`, `clamp`, or `pingpong`.
- `align_to_path`: aim emission along the path tangent.
- `use_emitter_origin`: treat path points as offsets from `emitter_x/y`.

**Emitter controls**
Same as `Taichi Particle Emitter`.

**Optional**
- `path_modulation`: connect `Taichi Path Emitter Modulation`.

---

## Taichi Path Emitter Modulation

Modulates path speed and particle properties from features.

**Speed**
- `speed_feature`, `speed_scale`, `speed_offset`, `speed_threshold`, `speed_mode`.

**Size**
- `size_feature`, `size_scale`, `size_offset`, `size_threshold`, `size_mode`.

**Angle**
- `angle_feature`, `angle_scale`, `angle_offset`, `angle_threshold`, `angle_mode`.

**Spread**
- `spread_feature`, `spread_scale`, `spread_offset`, `spread_threshold`, `spread_mode`.

**Bursts**
- `burst_feature` (or falls back to `speed_feature`).
- `onset_threshold`, `burst_strength`, `burst_min`, `burst_max`.

---

## Taichi Path From Points

Build a path from a JSON list of points.

**Inputs**
- `points`: JSON list `[{ "x": 0.2, "y": 0.3 }, ...]`
- `closed`: loop back to the first point.
- Preview: `width`, `height`, `thickness`, `preview_color`.

---

## Taichi Path From Shape

Procedurally generates a path (circle, arc, polygon, etc).

**Shape controls**
`shape_type`, `center_x/y`, `size_x/y`, `rotation`, `sides`, `corner_radius`,
`start_angle`, `end_angle`, `segments`, `polyline_points`.

**Preview**
`preview_mask`, `preview_image`, `preview_width/height/thickness/color`.

---

## Taichi Path Preview

Visualize a path and optionally show an emitter position.

**Inputs**
`show_emitter`, `emitter_progress`, `emitter_size`, `emitter_color`.

---

## Taichi Path From Speed/Direction

Integrates two features into a path over time.

**Inputs**
- `speed_feature`, `direction_feature`
- `frame_rate`, `start_x/y`
- `min_speed`, `max_speed`
- `min_direction`, `max_direction`
- `direction_mode`: `absolute` or `relative`
- `direction_smoothing`, `speed_smoothing`

---

## Taichi Particle Burst Spots

Creates multiple emitters that burst based on a feature.

**Spot placement**
- `spot_count`: number of burst points.
- `position_mode`: `random`, `lock_x`, `lock_y`, `lock_xy`
- `lock_x`, `lock_y`: locked coordinates when using lock modes.
- `random_seed`: deterministic placement.

**Emitter controls**
Same as `Taichi Particle Emitter`, plus built-in feature burst settings:
`scale`, `threshold`, `mode`, `onset_threshold`, `burst_strength`, `burst_min`, `burst_max`.

**Tips**
- Set `emission_rate` to `0.0` for pure bursts.
- Use `lock_x`/`lock_y` to create aligned bursts across the frame.

---

## Taichi Particle Emitter From Mask Edges

Samples edges from a mask and emits outward (or inward) from the boundary.

**Edge sampling**
- `masks`: mask input (single or sequence).
- `spot_count`: number of edge emitters to sample.
- `edge_low_threshold`, `edge_high_threshold`: Canny thresholds.
- `sampling_mode`: `per_frame` (animated masks) or `first_frame` (stable).
- `random_seed`: deterministic edge selection.

**Direction**
- `direction_mode`: `outward` or `inward`.
- `particle_direction`: fallback angle if normals are weak.
- `direction_offset`: extra rotation.

**Emitter controls**
Same as `Taichi Particle Emitter`.

**Tips**
- If you see circular “waves”: reduce `emission_radius` to `0.0`.
- If emission looks noisy: use `first_frame` and reduce `spot_count`.

---

## Taichi Reset Cache

Clears cached Taichi buffers if you changed resolution or particle count.

---

## Troubleshooting & tuning tips

- **Particles vanish immediately**
  - Increase `particle_lifetime`, or set emitter `particle_lifetime`.
  - Ensure `end_frame` is 0 or greater than your timeline.

- **Not enough particles**
  - Raise `emission_rate` or burst parameters.
  - Increase `particle_count` in `Taichi Particle Mask`.
  - Enable `endless_mode` on emitters.

- **Too slow or too fast**
  - Adjust `particle_speed` and `frame_rate`.
  - For feature-driven emitters, reduce `scale` or `burst_strength`.

- **Uniform “ring” patterns**
  - Reduce `emission_radius`, `particle_spread`, or add `direction_offset`.
  - For mask-edge emitters, increase `spot_count` and use `per_frame` sampling.

- **Jittery paths**
  - Increase `direction_smoothing` / `speed_smoothing` in `Taichi Path From Speed/Direction`.
  - Reduce `path_speed` or `spread` for emitters on path.

- **Emission doesn’t react to audio/features**
  - Verify the `FEATURE` is connected and has a valid frame count.
  - Lower `threshold` or `onset_threshold`.
  - Use `FeatureInfoNode` to inspect values.

---

## Starter recipes

- **Soft sparkle field**
  - Emitter: `particle_shape = spark`, `spark_length = 10`, `spread = 180`, `emission_rate = 20`.

- **Audio burst fireworks**
  - Emitter: `emission_rate = 0`
  - Modulation: `onset_threshold = 0.05`, `burst_strength = 800`, `burst_min = 50`.

- **Edge glow**
  - Mask Edge Emitter: `spot_count = 100`, `particle_speed = 40`, `spread = 30`, `direction_mode = outward`.
