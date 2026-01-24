from __future__ import annotations

import math
from typing import List, Tuple

import numpy as np
import torch

from ... import RyanOnTheInside
from ...tooltips import apply_tooltips
from .mask_base import MaskBase
from .taichi_particle_system import EmitterSettings, TaichiParticleSystem, get_cached_system, reset_taichi_cache


def _parse_color(color_value) -> Tuple[float, float, float]:
    if isinstance(color_value, tuple):
        return tuple(float(c) / 255.0 for c in color_value)
    if isinstance(color_value, str):
        parts = color_value.strip("()").split(",")
        if len(parts) == 3:
            return tuple(float(p.strip()) / 255.0 for p in parts)
    return (1.0, 1.0, 1.0)


def _prepare_path(points: List[Tuple[float, float]], width: int, height: int):
    if len(points) < 2:
        return None
    points_px = [(p[0] * width, p[1] * height) for p in points]
    seg_lengths = []
    total = 0.0
    for i in range(len(points_px) - 1):
        dx = points_px[i + 1][0] - points_px[i][0]
        dy = points_px[i + 1][1] - points_px[i][1]
        length = math.hypot(dx, dy)
        seg_lengths.append(length)
        total += length
    return {
        "points": points_px,
        "seg_lengths": seg_lengths,
        "total": total,
    }


def _sample_path(path_data, progress: float):
    if path_data is None or path_data["total"] <= 0:
        return None, 0.0
    target = max(0.0, min(1.0, progress)) * path_data["total"]
    accumulated = 0.0
    points = path_data["points"]
    for i, length in enumerate(path_data["seg_lengths"]):
        if accumulated + length >= target:
            t = (target - accumulated) / max(length, 1e-6)
            x0, y0 = points[i]
            x1, y1 = points[i + 1]
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            angle = math.degrees(math.atan2(y1 - y0, x1 - x0))
            return (x, y), angle
        accumulated += length
    return points[-1], 0.0


@apply_tooltips
class TaichiParticleAudioReactiveEmission(RyanOnTheInside):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "feature": ("FEATURE",),
                "scale": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "threshold": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "mode": (["relative", "absolute"],),
                "onset_threshold": ("FLOAT", {"default": 0.08, "min": 0.0, "max": 1.0, "step": 0.01}),
                "burst_strength": ("FLOAT", {"default": 200.0, "min": 0.0, "max": 5000.0, "step": 10.0}),
                "burst_min": ("INT", {"default": 0, "min": 0, "max": 20000, "step": 10}),
                "burst_max": ("INT", {"default": 0, "min": 0, "max": 20000, "step": 10}),
            }
        }

    RETURN_TYPES = ("TAICHI_EMITTER_MOD",)
    FUNCTION = "create_modulation"
    CATEGORY = "RyanOnTheInside/ParticleSystems/Taichi"

    def create_modulation(self, feature, scale, threshold, mode, onset_threshold, burst_strength, burst_min, burst_max):
        return ({
            "feature": feature,
            "scale": float(scale),
            "threshold": float(threshold),
            "mode": mode,
            "onset_threshold": float(onset_threshold),
            "burst_strength": float(burst_strength),
            "burst_min": int(burst_min),
            "burst_max": int(burst_max),
        },)


@apply_tooltips
class TaichiParticleEmitter(RyanOnTheInside):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "emitter_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "emitter_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "particle_direction": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 1.0}),
                "direction_offset": ("FLOAT", {"default": 0.0, "min": -360.0, "max": 360.0, "step": 1.0}),
                "particle_spread": ("FLOAT", {"default": 45.0, "min": 0.0, "max": 360.0, "step": 1.0}),
                "particle_size": ("FLOAT", {"default": 6.0, "min": 1.0, "max": 100.0, "step": 0.5}),
                "particle_speed": ("FLOAT", {"default": 200.0, "min": 0.0, "max": 1000.0, "step": 1.0}),
                "emission_rate": ("FLOAT", {"default": 10.0, "min": 0.0, "max": 200.0, "step": 0.1}),
                "color": ("STRING", {"default": "(255,255,255)"}),
                "emission_radius": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 200.0, "step": 0.1}),
                "particle_shape": (["circle", "square", "spark"],),
                "spark_length": ("FLOAT", {"default": 12.0, "min": 0.0, "max": 200.0, "step": 1.0}),
                "particle_lifetime": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "endless_mode": ("BOOLEAN", {"default": False}),
                "start_frame": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
                "end_frame": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
            },
            "optional": {
                "previous_emitter": ("TAICHI_EMITTER",),
                "emitter_modulation": ("TAICHI_EMITTER_MOD",),
            },
        }

    RETURN_TYPES = ("TAICHI_EMITTER",)
    FUNCTION = "create_emitter"
    CATEGORY = "RyanOnTheInside/ParticleSystems/Taichi"

    def create_emitter(
        self,
        emitter_x,
        emitter_y,
        particle_direction,
        direction_offset,
        particle_spread,
        particle_size,
        particle_speed,
        emission_rate,
        color,
        emission_radius,
        particle_shape,
        spark_length,
        particle_lifetime,
        endless_mode,
        start_frame,
        end_frame,
        previous_emitter=None,
        emitter_modulation=None,
    ):
        shape_map = {"circle": 0, "square": 1, "spark": 2}
        emitter = {
            "emitter_x": float(emitter_x),
            "emitter_y": float(emitter_y),
            "base_emitter_x": float(emitter_x),
            "base_emitter_y": float(emitter_y),
            "particle_direction": float(particle_direction),
            "base_particle_direction": float(particle_direction),
            "direction_offset": float(direction_offset),
            "particle_spread": float(particle_spread),
            "base_particle_spread": float(particle_spread),
            "particle_size": float(particle_size),
            "base_particle_size": float(particle_size),
            "particle_speed": float(particle_speed),
            "emission_rate": float(emission_rate),
            "color": _parse_color(color),
            "emission_radius": float(emission_radius),
            "particle_shape": shape_map.get(particle_shape, 0),
            "spark_length": float(spark_length),
            "particle_lifetime": float(particle_lifetime),
            "endless_mode": bool(endless_mode),
            "start_frame": int(start_frame),
            "end_frame": int(end_frame),
        }

        if emitter_modulation is not None:
            emitter["audio_modulation"] = emitter_modulation

        if previous_emitter is None:
            emitter_list = [emitter]
        else:
            emitter_list = previous_emitter + [emitter]

        return (emitter_list,)


@apply_tooltips
class TaichiPathEmitterModulation(RyanOnTheInside):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "speed_scale": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.1}),
                "speed_offset": ("FLOAT", {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1}),
                "speed_threshold": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "speed_mode": (["relative", "absolute"],),
                "size_scale": ("FLOAT", {"default": 0.5, "min": -10.0, "max": 10.0, "step": 0.1}),
                "size_offset": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 0.1}),
                "size_threshold": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "size_mode": (["relative", "absolute"],),
                "angle_scale": ("FLOAT", {"default": 45.0, "min": -360.0, "max": 360.0, "step": 1.0}),
                "angle_offset": ("FLOAT", {"default": 0.0, "min": -360.0, "max": 360.0, "step": 1.0}),
                "angle_threshold": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "angle_mode": (["relative", "absolute"],),
                "spread_scale": ("FLOAT", {"default": 30.0, "min": -360.0, "max": 360.0, "step": 1.0}),
                "spread_offset": ("FLOAT", {"default": 0.0, "min": -360.0, "max": 360.0, "step": 1.0}),
                "spread_threshold": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "spread_mode": (["relative", "absolute"],),
                "onset_threshold": ("FLOAT", {"default": 0.08, "min": 0.0, "max": 1.0, "step": 0.01}),
                "burst_strength": ("FLOAT", {"default": 200.0, "min": 0.0, "max": 5000.0, "step": 10.0}),
                "burst_min": ("INT", {"default": 0, "min": 0, "max": 20000, "step": 10}),
                "burst_max": ("INT", {"default": 0, "min": 0, "max": 20000, "step": 10}),
            },
            "optional": {
                "speed_feature": ("FEATURE",),
                "size_feature": ("FEATURE",),
                "angle_feature": ("FEATURE",),
                "spread_feature": ("FEATURE",),
                "burst_feature": ("FEATURE",),
            }
        }

    RETURN_TYPES = ("TAICHI_PATH_MOD",)
    FUNCTION = "create_modulation"
    CATEGORY = "RyanOnTheInside/ParticleSystems/Taichi"

    def create_modulation(
        self,
        speed_scale,
        speed_offset,
        speed_threshold,
        speed_mode,
        size_scale,
        size_offset,
        size_threshold,
        size_mode,
        angle_scale,
        angle_offset,
        angle_threshold,
        angle_mode,
        spread_scale,
        spread_offset,
        spread_threshold,
        spread_mode,
        onset_threshold,
        burst_strength,
        burst_min,
        burst_max,
        speed_feature=None,
        size_feature=None,
        angle_feature=None,
        spread_feature=None,
        burst_feature=None,
    ):
        return ({
            "speed_feature": speed_feature,
            "speed_scale": float(speed_scale),
            "speed_offset": float(speed_offset),
            "speed_threshold": float(speed_threshold),
            "speed_mode": speed_mode,
            "size_feature": size_feature,
            "size_scale": float(size_scale),
            "size_offset": float(size_offset),
            "size_threshold": float(size_threshold),
            "size_mode": size_mode,
            "angle_feature": angle_feature,
            "angle_scale": float(angle_scale),
            "angle_offset": float(angle_offset),
            "angle_threshold": float(angle_threshold),
            "angle_mode": angle_mode,
            "spread_feature": spread_feature,
            "spread_scale": float(spread_scale),
            "spread_offset": float(spread_offset),
            "spread_threshold": float(spread_threshold),
            "spread_mode": spread_mode,
            "onset_threshold": float(onset_threshold),
            "burst_strength": float(burst_strength),
            "burst_min": int(burst_min),
            "burst_max": int(burst_max),
            "burst_feature": burst_feature,
        },)


@apply_tooltips
class TaichiParticleEmitterOnPath(RyanOnTheInside):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("TAICHI_PATH",),
                "emitter_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "emitter_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "path_speed": ("FLOAT", {"default": 0.2, "min": -10.0, "max": 10.0, "step": 0.01}),
                "loop_mode": (["loop", "clamp", "pingpong"],),
                "align_to_path": ("BOOLEAN", {"default": True}),
                "use_emitter_origin": ("BOOLEAN", {"default": True}),
                "particle_direction": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 1.0}),
                "direction_offset": ("FLOAT", {"default": 180.0, "min": -360.0, "max": 360.0, "step": 1.0}),
                "particle_spread": ("FLOAT", {"default": 45.0, "min": 0.0, "max": 360.0, "step": 1.0}),
                "particle_size": ("FLOAT", {"default": 6.0, "min": 1.0, "max": 100.0, "step": 0.5}),
                "particle_speed": ("FLOAT", {"default": 200.0, "min": 0.0, "max": 1000.0, "step": 1.0}),
                "emission_rate": ("FLOAT", {"default": 10.0, "min": 0.0, "max": 200.0, "step": 0.1}),
                "color": ("STRING", {"default": "(255,255,255)"}),
                "emission_radius": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 200.0, "step": 0.1}),
                "particle_shape": (["circle", "square", "spark"],),
                "spark_length": ("FLOAT", {"default": 12.0, "min": 0.0, "max": 200.0, "step": 1.0}),
                "particle_lifetime": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "endless_mode": ("BOOLEAN", {"default": False}),
                "start_frame": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
                "end_frame": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
            },
            "optional": {
                "previous_emitter": ("TAICHI_EMITTER",),
                "emitter_modulation": ("TAICHI_EMITTER_MOD",),
                "path_modulation": ("TAICHI_PATH_MOD",),
            },
        }

    RETURN_TYPES = ("TAICHI_EMITTER",)
    FUNCTION = "create_emitter"
    CATEGORY = "RyanOnTheInside/ParticleSystems/Taichi"

    def create_emitter(
        self,
        path,
        emitter_x,
        emitter_y,
        path_speed,
        loop_mode,
        align_to_path,
        use_emitter_origin,
        particle_direction,
        direction_offset,
        particle_spread,
        particle_size,
        particle_speed,
        emission_rate,
        color,
        emission_radius,
        particle_shape,
        spark_length,
        particle_lifetime,
        endless_mode,
        start_frame,
        end_frame,
        previous_emitter=None,
        emitter_modulation=None,
        path_modulation=None,
    ):
        shape_map = {"circle": 0, "square": 1, "spark": 2}
        emitter = {
            "emitter_x": float(emitter_x),
            "emitter_y": float(emitter_y),
            "base_emitter_x": float(emitter_x),
            "base_emitter_y": float(emitter_y),
            "particle_direction": float(particle_direction),
            "base_particle_direction": float(particle_direction),
            "direction_offset": float(direction_offset),
            "particle_spread": float(particle_spread),
            "base_particle_spread": float(particle_spread),
            "particle_size": float(particle_size),
            "base_particle_size": float(particle_size),
            "particle_speed": float(particle_speed),
            "emission_rate": float(emission_rate),
            "color": _parse_color(color),
            "emission_radius": float(emission_radius),
            "particle_shape": shape_map.get(particle_shape, 0),
            "spark_length": float(spark_length),
            "particle_lifetime": float(particle_lifetime),
            "endless_mode": bool(endless_mode),
            "start_frame": int(start_frame),
            "end_frame": int(end_frame),
            "path": path,
            "path_speed": float(path_speed),
            "base_path_speed": float(path_speed),
            "loop_mode": loop_mode,
            "align_to_path": bool(align_to_path),
            "use_emitter_origin": bool(use_emitter_origin),
        }

        if emitter_modulation is not None:
            emitter["audio_modulation"] = emitter_modulation
        if path_modulation is not None:
            emitter["path_modulation"] = path_modulation

        if previous_emitter is None:
            emitter_list = [emitter]
        else:
            emitter_list = previous_emitter + [emitter]

        return (emitter_list,)
@apply_tooltips
class TaichiParticleMask(MaskBase):
    @classmethod
    def INPUT_TYPES(cls):
        parent_inputs = super().INPUT_TYPES()["required"]
        return {
            "required": {
                **parent_inputs,
                "emitters": ("TAICHI_EMITTER",),
                "particle_count": ("INT", {"default": 10000, "min": 1, "max": 200000, "step": 100}),
                "particle_lifetime": ("FLOAT", {"default": 3.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "wind_strength": ("FLOAT", {"default": 0.0, "min": -500.0, "max": 500.0, "step": 1.0}),
                "wind_direction": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 1.0}),
                "gravity": ("FLOAT", {"default": 150.0, "min": -2000.0, "max": 2000.0, "step": 1.0}),
                "frame_rate": ("FLOAT", {"default": 30.0, "min": 1.0, "max": 120.0, "step": 1.0}),
                "start_frame": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
                "end_frame": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
            }
        }

    RETURN_TYPES = ("MASK", "IMAGE")
    FUNCTION = "main_function"
    CATEGORY = "RyanOnTheInside/ParticleSystems/Taichi"

    def process_mask(self, mask: np.ndarray, strength: float, **kwargs) -> np.ndarray:
        return mask

    def main_function(
        self,
        masks,
        strength,
        invert,
        subtract_original,
        grow_with_blur,
        emitters,
        particle_count,
        particle_lifetime,
        wind_strength,
        wind_direction,
        gravity,
        frame_rate,
        start_frame,
        end_frame,
    ):
        masks_np = masks.cpu().numpy() if isinstance(masks, torch.Tensor) else masks
        num_frames, height, width = masks_np.shape

        end_frame = end_frame if end_frame > 0 else num_frames
        frame_rate = max(1.0, float(frame_rate))
        dt = 1.0 / frame_rate

        gravity_x = float(wind_strength) * math.cos(math.radians(float(wind_direction)))
        gravity_y = float(gravity) + float(wind_strength) * math.sin(math.radians(float(wind_direction)))

        system = get_cached_system(width, height, int(particle_count))
        system.reset()

        emit_accumulators: List[float] = [0.0] * len(emitters)
        feature_prev: List[float] = [0.0] * len(emitters)
        path_progress: List[float] = [0.0] * len(emitters)
        path_direction: List[int] = [1] * len(emitters)
        path_data_list = []

        for emitter in emitters:
            path = emitter.get("path")
            if path is None:
                path_data_list.append(None)
                continue
            if isinstance(path, dict) and path.get("frame_points"):
                path_data_list.append({
                    "frame_points": path.get("frame_points"),
                    "frame_angles": path.get("frame_angles"),
                })
                continue
            points = path.get("points", [])
            if emitter.get("use_emitter_origin", False):
                ex = float(emitter.get("base_emitter_x", emitter.get("emitter_x", 0.5)))
                ey = float(emitter.get("base_emitter_y", emitter.get("emitter_y", 0.5)))
                points = [(ex + (p[0] - 0.5), ey + (p[1] - 0.5)) for p in points]
            points = [(min(1.0, max(0.0, p[0])), min(1.0, max(0.0, p[1]))) for p in points]
            path_data_list.append(_prepare_path(points, width, height))

        mask_frames = []
        image_frames = []

        self.start_progress(num_frames, desc="Processing Taichi particle mask")

        for frame_index in range(num_frames):
            system.clear_image()

            for emitter_index, emitter in enumerate(emitters):
                emitter_start = emitter.get("start_frame", 0)
                emitter_end = emitter.get("end_frame", 0)
                if frame_index < emitter_start:
                    continue
                if emitter_end > 0 and frame_index >= emitter_end:
                    continue
                if frame_index < start_frame or frame_index >= end_frame:
                    continue

                emission_rate = float(emitter["emission_rate"])
                emitter_x = float(emitter.get("base_emitter_x", emitter["emitter_x"]))
                emitter_y = float(emitter.get("base_emitter_y", emitter["emitter_y"]))
                particle_size = float(emitter.get("base_particle_size", emitter["particle_size"]))
                particle_spread = float(emitter.get("base_particle_spread", emitter["particle_spread"]))
                particle_direction = float(emitter.get("base_particle_direction", emitter["particle_direction"]))
                path_speed = float(emitter.get("base_path_speed", emitter.get("path_speed", 0.0)))
                modulation = emitter.get("audio_modulation")
                burst_count = 0
                if modulation is not None:
                    feature = modulation.get("feature")
                    if feature is not None:
                        feature_value = float(feature.get_value_at_frame(frame_index))
                        feature_value = max(0.0, feature_value - float(modulation.get("threshold", 0.0)))
                        scale = float(modulation.get("scale", 1.0))
                        if modulation.get("mode") == "absolute":
                            emission_rate = emission_rate + scale * feature_value
                        else:
                            emission_rate = emission_rate * (1.0 + scale * feature_value)

                        delta = feature_value - feature_prev[emitter_index]
                        onset_threshold = float(modulation.get("onset_threshold", 0.0))
                        if delta >= onset_threshold:
                            burst_strength = float(modulation.get("burst_strength", 0.0))
                            burst_count = int(burst_strength * delta)
                            burst_min = int(modulation.get("burst_min", 0))
                            burst_max = int(modulation.get("burst_max", 0))
                            if burst_min > 0:
                                burst_count = max(burst_min, burst_count)
                            if burst_max > 0:
                                burst_count = min(burst_max, burst_count)
                        feature_prev[emitter_index] = feature_value

                def _apply_mod(base, feature_value, scale, offset, threshold, mode):
                    if feature_value is None:
                        return base
                    value = max(0.0, feature_value - threshold)
                    if mode == "absolute":
                        return base + offset + scale * value
                    return base * (1.0 + scale * value) + offset

                path_modulation = emitter.get("path_modulation")
                if path_modulation is not None:
                    speed_feature = path_modulation.get("speed_feature")
                    speed_value = float(speed_feature.get_value_at_frame(frame_index)) if speed_feature is not None else None
                    path_speed = _apply_mod(
                        path_speed,
                        speed_value,
                        float(path_modulation.get("speed_scale", 1.0)),
                        float(path_modulation.get("speed_offset", 0.0)),
                        float(path_modulation.get("speed_threshold", 0.0)),
                        path_modulation.get("speed_mode", "relative"),
                    )

                    size_feature = path_modulation.get("size_feature")
                    size_value = float(size_feature.get_value_at_frame(frame_index)) if size_feature is not None else None
                    particle_size = _apply_mod(
                        particle_size,
                        size_value,
                        float(path_modulation.get("size_scale", 0.0)),
                        float(path_modulation.get("size_offset", 0.0)),
                        float(path_modulation.get("size_threshold", 0.0)),
                        path_modulation.get("size_mode", "relative"),
                    )

                    angle_feature = path_modulation.get("angle_feature")
                    angle_value = float(angle_feature.get_value_at_frame(frame_index)) if angle_feature is not None else None
                    particle_direction = _apply_mod(
                        particle_direction,
                        angle_value,
                        float(path_modulation.get("angle_scale", 0.0)),
                        float(path_modulation.get("angle_offset", 0.0)),
                        float(path_modulation.get("angle_threshold", 0.0)),
                        path_modulation.get("angle_mode", "relative"),
                    )

                    spread_feature = path_modulation.get("spread_feature")
                    spread_value = float(spread_feature.get_value_at_frame(frame_index)) if spread_feature is not None else None
                    particle_spread = _apply_mod(
                        particle_spread,
                        spread_value,
                        float(path_modulation.get("spread_scale", 0.0)),
                        float(path_modulation.get("spread_offset", 0.0)),
                        float(path_modulation.get("spread_threshold", 0.0)),
                        path_modulation.get("spread_mode", "relative"),
                    )

                    burst_feature = path_modulation.get("burst_feature") or speed_feature
                    if burst_feature is not None:
                        burst_value = float(burst_feature.get_value_at_frame(frame_index))
                        burst_value = max(0.0, burst_value - float(path_modulation.get("speed_threshold", 0.0)))
                        delta = burst_value - feature_prev[emitter_index]
                        onset_threshold = float(path_modulation.get("onset_threshold", 0.0))
                        if delta >= onset_threshold:
                            burst_strength = float(path_modulation.get("burst_strength", 0.0))
                            burst_extra = int(burst_strength * delta)
                            burst_min = int(path_modulation.get("burst_min", 0))
                            burst_max = int(path_modulation.get("burst_max", 0))
                            if burst_min > 0:
                                burst_extra = max(burst_min, burst_extra)
                            if burst_max > 0:
                                burst_extra = min(burst_max, burst_extra)
                            burst_count += burst_extra
                        feature_prev[emitter_index] = burst_value

                path_data = path_data_list[emitter_index]
                if isinstance(path_data, dict) and path_data.get("frame_points"):
                    frame_points = path_data["frame_points"]
                    frame_angles = path_data.get("frame_angles")
                    if frame_points:
                        idx = frame_index % len(frame_points)
                        px, py = frame_points[idx]
                        emitter_x = px
                        emitter_y = py
                        if emitter.get("align_to_path", False) and frame_angles:
                            particle_direction = frame_angles[idx]
                elif path_data is not None:
                    base_speed = path_speed
                    progress = path_progress[emitter_index]
                    direction = path_direction[emitter_index]
                    delta = base_speed * dt
                    loop_mode = emitter.get("loop_mode", "loop")
                    if loop_mode == "loop":
                        progress = (progress + delta) % 1.0
                    elif loop_mode == "clamp":
                        progress = max(0.0, min(1.0, progress + delta))
                    else:
                        progress += delta * direction
                        if progress > 1.0:
                            progress = 2.0 - progress
                            direction = -1
                        elif progress < 0.0:
                            progress = -progress
                            direction = 1
                    path_progress[emitter_index] = progress
                    path_direction[emitter_index] = direction
                    sampled = _sample_path(path_data, progress)
                    if sampled[0] is not None:
                        (px, py), path_angle = sampled
                        emitter_x = px / width
                        emitter_y = py / height
                        if emitter.get("align_to_path", False):
                            particle_direction = path_angle

                emit_accumulators[emitter_index] += max(0.0, emission_rate) * dt
                emit_count = int(emit_accumulators[emitter_index])
                if emit_count > 0:
                    emit_accumulators[emitter_index] -= emit_count
                emit_count += burst_count
                if emit_count > 0:
                    lifetime_override = float(emitter.get("particle_lifetime", 0.0))
                    lifetime = lifetime_override if lifetime_override > 0.0 else float(particle_lifetime)
                    direction_deg = particle_direction + float(emitter.get("direction_offset", 0.0))
                    settings = EmitterSettings(
                        x=emitter_x * width,
                        y=emitter_y * height,
                        direction=math.radians(direction_deg),
                        spread=math.radians(particle_spread),
                        speed=float(emitter["particle_speed"]),
                        size=particle_size,
                        emission_radius=float(emitter.get("emission_radius", 0.0)),
                        color=emitter["color"],
                        particle_life=lifetime,
                        shape=int(emitter.get("particle_shape", 0)),
                        spark_length=float(emitter.get("spark_length", 0.0)),
                        endless=1 if emitter.get("endless_mode", False) else 0,
                    )
                    system.emit(emit_count, settings)

            system.update(dt, gravity_x, gravity_y)
            system.rasterize()

            image = system.get_image()
            particle_mask = np.clip(image[..., 3], 0.0, 1.0)
            particle_image = np.clip(image[..., :3], 0.0, 1.0)

            base_mask = masks_np[frame_index]
            result_mask = np.maximum(base_mask, particle_mask)
            result_image = np.maximum(particle_image, np.stack([base_mask] * 3, axis=-1))

            mask_frames.append(result_mask)
            image_frames.append(result_image)

            self.update_progress()

        self.end_progress()

        processed_masks = torch.from_numpy(np.stack(mask_frames)).float()
        processed_images = torch.from_numpy(np.stack(image_frames)).float()

        result_masks = self.apply_mask_operation(
            processed_masks,
            masks,
            strength,
            invert,
            subtract_original,
            grow_with_blur,
        )

        return (result_masks, processed_images)


@apply_tooltips
class TaichiResetCache(RyanOnTheInside):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ()
    FUNCTION = "reset_cache"
    CATEGORY = "RyanOnTheInside/ParticleSystems/Taichi"

    def reset_cache(self):
        reset_taichi_cache()
        return ()
