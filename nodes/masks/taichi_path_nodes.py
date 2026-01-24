import json
import math
from typing import List, Tuple

import cv2
import numpy as np
import torch

from ... import RyanOnTheInside
from ...tooltips import apply_tooltips


def _parse_color(color_value: str) -> Tuple[float, float, float]:
    parts = color_value.strip("()").split(",")
    if len(parts) == 3:
        return tuple(float(p.strip()) / 255.0 for p in parts)
    return (1.0, 1.0, 1.0)


def _render_path(points: List[Tuple[float, float]], width: int, height: int, thickness: int, color: Tuple[float, float, float]):
    image = np.zeros((height, width, 3), dtype=np.float32)
    mask = np.zeros((height, width), dtype=np.float32)

    if len(points) < 2:
        return mask, image

    pts = np.array(
        [(int(p[0] * (width - 1)), int(p[1] * (height - 1))) for p in points],
        dtype=np.int32,
    )
    for i in range(len(pts) - 1):
        cv2.line(mask, tuple(pts[i]), tuple(pts[i + 1]), 1.0, thickness)
        cv2.line(image, tuple(pts[i]), tuple(pts[i + 1]), color, thickness)

    return np.clip(mask, 0.0, 1.0), np.clip(image, 0.0, 1.0)


def _generate_shape_points(shape_type: str, **kwargs) -> List[Tuple[float, float]]:
    center_x = kwargs["center_x"]
    center_y = kwargs["center_y"]
    size_x = kwargs["size_x"]
    size_y = kwargs["size_y"]
    rotation = np.deg2rad(kwargs["rotation"])
    cos_r = np.cos(rotation)
    sin_r = np.sin(rotation)

    def _transform_point(px: float, py: float) -> Tuple[float, float]:
        rx = px * cos_r - py * sin_r
        ry = px * sin_r + py * cos_r
        return (center_x + rx, center_y + ry)

    if shape_type == "line":
        return [
            _transform_point(-size_x * 0.5, -size_y * 0.5),
            _transform_point(size_x * 0.5, size_y * 0.5),
        ]
    if shape_type == "circle":
        radius = size_x * 0.5
        segments = kwargs["segments"]
        points = []
        for i in range(segments + 1):
            t = 2 * np.pi * i / segments
            points.append(_transform_point(np.cos(t) * radius, np.sin(t) * radius))
        return points
    if shape_type == "arc":
        radius = size_x * 0.5
        start_angle = np.deg2rad(kwargs["start_angle"])
        end_angle = np.deg2rad(kwargs["end_angle"])
        segments = kwargs["segments"]
        points = []
        for i in range(segments + 1):
            t = start_angle + (end_angle - start_angle) * (i / segments)
            points.append(_transform_point(np.cos(t) * radius, np.sin(t) * radius))
        return points
    if shape_type in ("polygon", "rounded_rect"):
        sides = max(3, int(kwargs["sides"]))
        corner_radius = max(0.0, float(kwargs["corner_radius"]))
        segments = max(4, int(kwargs["segments"]))

        vertices = []
        for i in range(sides):
            angle = (2 * np.pi * i / sides)
            vertices.append(_transform_point(np.cos(angle) * size_x * 0.5, np.sin(angle) * size_y * 0.5))

        vertices.append(vertices[0])
        if corner_radius <= 0.0:
            return vertices

        cr = corner_radius
        if corner_radius <= 1.0:
            cr = corner_radius * min(size_x, size_y) * 0.5

        iterations = max(1, min(6, int(cr * 10)))
        points = vertices[:-1]
        for _ in range(iterations):
            new_points = []
            for i in range(len(points)):
                p0 = np.array(points[i])
                p1 = np.array(points[(i + 1) % len(points)])
                q = 0.75 * p0 + 0.25 * p1
                r = 0.25 * p0 + 0.75 * p1
                new_points.append(tuple(q))
                new_points.append(tuple(r))
            points = new_points

        points.append(points[0])
        return points
    if shape_type == "polyline":
        return kwargs["polyline_points"]
    return []


@apply_tooltips
class TaichiPathFromPoints(RyanOnTheInside):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "points": ("STRING", {"default": "[]"}),
                "interpolation": (["linear"],),
                "closed": ("BOOLEAN", {"default": False}),
                "width": ("INT", {"default": 512, "min": 8, "max": 4096, "step": 1}),
                "height": ("INT", {"default": 512, "min": 8, "max": 4096, "step": 1}),
                "thickness": ("INT", {"default": 2, "min": 1, "max": 50, "step": 1}),
                "preview_color": ("STRING", {"default": "(255,255,255)"}),
            }
        }

    RETURN_TYPES = ("TAICHI_PATH", "MASK", "IMAGE")
    FUNCTION = "create_path"
    CATEGORY = "RyanOnTheInside/ParticleSystems/Taichi/Path"

    def create_path(self, points, interpolation, closed, width, height, thickness, preview_color):
        try:
            point_data = json.loads(points)
        except json.JSONDecodeError:
            point_data = []

        parsed_points: List[Tuple[float, float]] = []
        for point in point_data:
            if isinstance(point, dict) and "x" in point and "y" in point:
                parsed_points.append((float(point["x"]), float(point["y"])))
            elif isinstance(point, (list, tuple)) and len(point) >= 2:
                parsed_points.append((float(point[0]), float(point[1])))

        if closed and len(parsed_points) > 2:
            parsed_points = parsed_points + [parsed_points[0]]

        path = {
            "points": parsed_points,
            "interpolation": interpolation,
            "closed": closed,
        }

        color = _parse_color(preview_color)
        mask, image = _render_path(parsed_points, int(width), int(height), int(thickness), color)
        return (path, mask, image)


@apply_tooltips
class TaichiPathFromShape(RyanOnTheInside):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "shape_type": (["line", "circle", "arc", "polygon", "rounded_rect", "polyline"],),
                "center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "size_x": ("FLOAT", {"default": 0.6, "min": 0.01, "max": 2.0, "step": 0.01}),
                "size_y": ("FLOAT", {"default": 0.6, "min": 0.01, "max": 2.0, "step": 0.01}),
                "rotation": ("FLOAT", {"default": 0.0, "min": -360.0, "max": 360.0, "step": 1.0}),
                "sides": ("INT", {"default": 5, "min": 3, "max": 12, "step": 1}),
                "corner_radius": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "start_angle": ("FLOAT", {"default": 0.0, "min": -720.0, "max": 720.0, "step": 1.0}),
                "end_angle": ("FLOAT", {"default": 360.0, "min": -720.0, "max": 720.0, "step": 1.0}),
                "segments": ("INT", {"default": 64, "min": 4, "max": 2048, "step": 1}),
                "polyline_points": ("STRING", {"default": "[]"}),
                "closed": ("BOOLEAN", {"default": False}),
                "preview_mask": ("BOOLEAN", {"default": True}),
                "preview_image": ("BOOLEAN", {"default": True}),
                "preview_width": ("INT", {"default": 512, "min": 8, "max": 4096, "step": 1}),
                "preview_height": ("INT", {"default": 512, "min": 8, "max": 4096, "step": 1}),
                "preview_thickness": ("INT", {"default": 2, "min": 1, "max": 50, "step": 1}),
                "preview_color": ("STRING", {"default": "(255,255,255)"}),
            }
        }

    RETURN_TYPES = ("TAICHI_PATH", "MASK", "IMAGE")
    FUNCTION = "create_path"
    CATEGORY = "RyanOnTheInside/ParticleSystems/Taichi/Path"

    def create_path(
        self,
        shape_type,
        center_x,
        center_y,
        size_x,
        size_y,
        rotation,
        sides,
        corner_radius,
        start_angle,
        end_angle,
        segments,
        polyline_points,
        closed,
        preview_mask,
        preview_image,
        preview_width,
        preview_height,
        preview_thickness,
        preview_color,
    ):
        polyline_data: List[Tuple[float, float]] = []
        if shape_type == "polyline":
            try:
                parsed = json.loads(polyline_points)
            except json.JSONDecodeError:
                parsed = []
            for point in parsed:
                if isinstance(point, dict) and "x" in point and "y" in point:
                    polyline_data.append((float(point["x"]), float(point["y"])))
                elif isinstance(point, (list, tuple)) and len(point) >= 2:
                    polyline_data.append((float(point[0]), float(point[1])))

        points = _generate_shape_points(
            shape_type,
            center_x=float(center_x),
            center_y=float(center_y),
            size_x=float(size_x),
            size_y=float(size_y),
            rotation=float(rotation),
            sides=int(sides),
            corner_radius=float(corner_radius),
            start_angle=float(start_angle),
            end_angle=float(end_angle),
            segments=int(segments),
            polyline_points=polyline_data,
        )

        if closed and len(points) > 2:
            points = points + [points[0]]

        path = {
            "points": points,
            "interpolation": "linear",
            "closed": closed,
        }

        if preview_mask or preview_image:
            color = _parse_color(preview_color)
            mask, image = _render_path(points, int(preview_width), int(preview_height), int(preview_thickness), color)
            mask_out = torch.from_numpy(mask[None, ...]).float() if preview_mask else torch.zeros((1, int(preview_height), int(preview_width)))
            image_out = torch.from_numpy(image[None, ...]).float() if preview_image else torch.zeros((1, int(preview_height), int(preview_width), 3))
        else:
            mask_out = torch.zeros((1, int(preview_height), int(preview_width)))
            image_out = torch.zeros((1, int(preview_height), int(preview_width), 3))

        return (path, mask_out, image_out)


@apply_tooltips
class TaichiPathPreview(RyanOnTheInside):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("TAICHI_PATH",),
                "width": ("INT", {"default": 512, "min": 8, "max": 4096, "step": 1}),
                "height": ("INT", {"default": 512, "min": 8, "max": 4096, "step": 1}),
                "thickness": ("INT", {"default": 2, "min": 1, "max": 50, "step": 1}),
                "preview_color": ("STRING", {"default": "(255,255,255)"}),
                "show_emitter": ("BOOLEAN", {"default": False}),
                "emitter_progress": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "emitter_size": ("INT", {"default": 6, "min": 1, "max": 50, "step": 1}),
                "emitter_color": ("STRING", {"default": "(255,0,0)"}),
            }
        }

    RETURN_TYPES = ("MASK", "IMAGE")
    FUNCTION = "preview"
    CATEGORY = "RyanOnTheInside/ParticleSystems/Taichi/Path"

    def preview(self, path, width, height, thickness, preview_color, show_emitter, emitter_progress, emitter_size, emitter_color):
        points = path.get("points", []) if isinstance(path, dict) else []
        color = _parse_color(preview_color)
        mask, image = _render_path(points, int(width), int(height), int(thickness), color)

        if show_emitter and len(points) >= 2:
            path_data = _prepare_path(points, int(width), int(height))
            sampled = _sample_path(path_data, float(emitter_progress))
            if sampled[0] is not None:
                (px, py), _ = sampled
                cx = int(px)
                cy = int(py)
                emitter_rgb = _parse_color(emitter_color)
                cv2.circle(mask, (cx, cy), int(emitter_size), 1.0, -1)
                cv2.circle(image, (cx, cy), int(emitter_size), emitter_rgb, -1)

        mask_out = np.expand_dims(mask, axis=0)
        image_out = np.expand_dims(image, axis=0)
        return (torch.from_numpy(mask_out).float(), torch.from_numpy(image_out).float())


@apply_tooltips
class TaichiPathFromSpeedDirection(RyanOnTheInside):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "speed_feature": ("FEATURE",),
                "direction_feature": ("FEATURE",),
                "frame_rate": ("FLOAT", {"default": 30.0, "min": 1.0, "max": 120.0, "step": 1.0}),
                "start_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "start_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "min_speed": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 5.0, "step": 0.01}),
                "max_speed": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 5.0, "step": 0.01}),
                "min_direction": ("FLOAT", {"default": -180.0, "min": -360.0, "max": 360.0, "step": 1.0}),
                "max_direction": ("FLOAT", {"default": 180.0, "min": -360.0, "max": 360.0, "step": 1.0}),
                "direction_mode": (["absolute", "relative"],),
                "direction_smoothing": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                "speed_smoothing": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("TAICHI_PATH",)
    FUNCTION = "create_path"
    CATEGORY = "RyanOnTheInside/ParticleSystems/Taichi/Path"

    def create_path(
        self,
        speed_feature,
        direction_feature,
        frame_rate,
        start_x,
        start_y,
        min_speed,
        max_speed,
        min_direction,
        max_direction,
        direction_mode,
        direction_smoothing,
        speed_smoothing,
    ):
        frame_count = min(speed_feature.frame_count, direction_feature.frame_count)
        dt = 1.0 / max(1.0, float(frame_rate))

        x = float(start_x)
        y = float(start_y)
        points = []
        angles = []
        current_direction = float(min_direction)
        current_speed = float(min_speed)

        speed_min = getattr(speed_feature, "min_value", None)
        speed_max = getattr(speed_feature, "max_value", None)
        dir_min = getattr(direction_feature, "min_value", None)
        dir_max = getattr(direction_feature, "max_value", None)

        for i in range(frame_count):
            speed_val = float(speed_feature.get_value_at_frame(i))
            dir_val = float(direction_feature.get_value_at_frame(i))

            if speed_min is not None and speed_max is not None and speed_max > speed_min:
                speed_val = (speed_val - speed_min) / (speed_max - speed_min)
            if dir_min is not None and dir_max is not None and dir_max > dir_min:
                dir_val = (dir_val - dir_min) / (dir_max - dir_min)

            speed_val = max(0.0, min(1.0, speed_val))
            dir_val = max(0.0, min(1.0, dir_val))

            target_speed = float(min_speed) + speed_val * (float(max_speed) - float(min_speed))
            if direction_mode == "relative":
                target_direction = current_direction + (float(min_direction) + dir_val * (float(max_direction) - float(min_direction)))
            else:
                target_direction = float(min_direction) + dir_val * (float(max_direction) - float(min_direction))

            current_speed = (1.0 - speed_smoothing) * current_speed + speed_smoothing * target_speed
            current_direction = (1.0 - direction_smoothing) * current_direction + direction_smoothing * target_direction

            dx = math.cos(math.radians(current_direction)) * current_speed * dt
            dy = math.sin(math.radians(current_direction)) * current_speed * dt

            next_x = x + dx
            next_y = y + dy

            if next_x < 0.0 or next_x > 1.0:
                current_direction = 180.0 - current_direction
                dx = math.cos(math.radians(current_direction)) * current_speed * dt
                next_x = x + dx
            if next_y < 0.0 or next_y > 1.0:
                current_direction = -current_direction
                dy = math.sin(math.radians(current_direction)) * current_speed * dt
                next_y = y + dy

            next_x = max(0.0, min(1.0, next_x))
            next_y = max(0.0, min(1.0, next_y))

            x = next_x
            y = next_y
            points.append((x, y))
            angles.append(current_direction)

        path = {
            "points": points,
            "frame_points": points,
            "frame_angles": angles,
            "closed": False,
            "frame_count": frame_count,
        }
        return (path,)
