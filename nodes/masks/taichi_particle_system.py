from dataclasses import dataclass
from typing import Tuple

import numpy as np
import taichi as ti

from .taichi_runtime import get_taichi_runtime

_SYSTEM_CACHE = {}


def get_cached_system(width: int, height: int, max_particles: int):
    global _SYSTEM_CACHE
    key = (int(width), int(height))
    system = _SYSTEM_CACHE.get(key)
    if system is None or system.max_particles < int(max_particles):
        # Drop old cache to avoid growth across multiple sizes.
        _SYSTEM_CACHE = {}
        system = TaichiParticleSystem(int(max_particles), int(width), int(height))
        _SYSTEM_CACHE[key] = system
    return system


def reset_taichi_cache():
    global _SYSTEM_CACHE
    _SYSTEM_CACHE = {}


@dataclass
class EmitterSettings:
    x: float
    y: float
    direction: float
    spread: float
    speed: float
    size: float
    emission_radius: float
    color: Tuple[float, float, float]
    particle_life: float
    shape: int
    spark_length: float
    endless: int


@ti.data_oriented
class TaichiParticleSystem:
    def __init__(self, max_particles: int, width: int, height: int):
        get_taichi_runtime()
        self.max_particles = int(max_particles)
        self.width = int(width)
        self.height = int(height)
        self._build_fields()

    def _build_fields(self) -> None:
        self.pos = ti.Vector.field(2, dtype=ti.f32, shape=self.max_particles)
        self.vel = ti.Vector.field(2, dtype=ti.f32, shape=self.max_particles)
        self.color = ti.Vector.field(3, dtype=ti.f32, shape=self.max_particles)
        self.size = ti.field(dtype=ti.f32, shape=self.max_particles)
        self.shape = ti.field(dtype=ti.i32, shape=self.max_particles)
        self.spark_length = ti.field(dtype=ti.f32, shape=self.max_particles)
        self.age = ti.field(dtype=ti.f32, shape=self.max_particles)
        self.life = ti.field(dtype=ti.f32, shape=self.max_particles)
        self.active = ti.field(dtype=ti.i32, shape=self.max_particles)
        self.emit_cursor = ti.field(dtype=ti.i32, shape=())

        self.image = ti.Vector.field(4, dtype=ti.f32, shape=(self.height, self.width))

    def reset(self) -> None:
        self._reset_particles()
        self.clear_image()

    def clear_image(self) -> None:
        self._clear_image()

    def emit(self, count: int, settings: EmitterSettings) -> None:
        self._emit_particles(
            int(count),
            float(settings.x),
            float(settings.y),
            float(settings.direction),
            float(settings.spread),
            float(settings.speed),
            float(settings.size),
            float(settings.emission_radius),
            float(settings.color[0]),
            float(settings.color[1]),
            float(settings.color[2]),
            float(settings.particle_life),
            int(settings.shape),
            float(settings.spark_length),
            int(settings.endless),
            float(self.width),
            float(self.height),
        )

    def update(self, dt: float, gravity_x: float, gravity_y: float) -> None:
        self._update_particles(
            float(dt),
            float(gravity_x),
            float(gravity_y),
            float(self.width),
            float(self.height),
        )

    def rasterize(self) -> None:
        self._rasterize_particles(float(self.width), float(self.height))

    def get_image(self) -> np.ndarray:
        return self.image.to_numpy()

    def get_mask(self) -> np.ndarray:
        image = self.get_image()
        return np.clip(image[..., 3], 0.0, 1.0)

    @property
    def particle_capacity(self) -> int:
        return self.max_particles

    @property
    def particle_count(self) -> int:
        return int(self.emit_cursor.to_numpy())

    @ti.kernel
    def _reset_particles(self):
        for i in range(self.max_particles):
            self.pos[i] = ti.Vector([0.0, 0.0])
            self.vel[i] = ti.Vector([0.0, 0.0])
            self.color[i] = ti.Vector([0.0, 0.0, 0.0])
            self.size[i] = 0.0
            self.shape[i] = 0
            self.spark_length[i] = 0.0
            self.age[i] = 0.0
            self.life[i] = 0.0
            self.active[i] = 0
        self.emit_cursor[None] = 0

    @ti.kernel
    def _clear_image(self):
        for y, x in self.image:
            self.image[y, x] = ti.Vector([0.0, 0.0, 0.0, 0.0])

    @ti.kernel
    def _emit_particles(
        self,
        count: ti.i32,
        emitter_x: ti.f32,
        emitter_y: ti.f32,
        direction: ti.f32,
        spread: ti.f32,
        speed: ti.f32,
        size: ti.f32,
        emission_radius: ti.f32,
        color_r: ti.f32,
        color_g: ti.f32,
        color_b: ti.f32,
        particle_life: ti.f32,
        shape: ti.i32,
        spark_length: ti.f32,
        endless: ti.i32,
        width: ti.f32,
        height: ti.f32,
    ):
        for _ in range(count):
            raw_idx = ti.atomic_add(self.emit_cursor[None], 1)
            idx = raw_idx
            if endless == 1:
                idx = raw_idx % self.max_particles
            if idx < self.max_particles:
                angle = direction + (ti.random() - 0.5) * spread
                velocity = ti.Vector([ti.cos(angle), ti.sin(angle)]) * speed

                radius = emission_radius * ti.sqrt(ti.random())
                theta = ti.random() * ti.math.pi * 2.0
                offset = ti.Vector([ti.cos(theta), ti.sin(theta)]) * radius

                position = ti.Vector([emitter_x, emitter_y]) + offset

                self.pos[idx] = position
                self.vel[idx] = velocity
                self.color[idx] = ti.Vector([color_r, color_g, color_b])
                self.size[idx] = size
                self.shape[idx] = shape
                self.spark_length[idx] = spark_length
                self.age[idx] = 0.0
                self.life[idx] = particle_life
                self.active[idx] = 1

                if (
                    position.x < 0.0
                    or position.x >= width
                    or position.y < 0.0
                    or position.y >= height
                ):
                    self.active[idx] = 0

    @ti.kernel
    def _update_particles(
        self,
        dt: ti.f32,
        gravity_x: ti.f32,
        gravity_y: ti.f32,
        width: ti.f32,
        height: ti.f32,
    ):
        gravity = ti.Vector([gravity_x, gravity_y])
        for i in range(self.max_particles):
            if self.active[i] == 1:
                self.age[i] += dt
                if self.age[i] >= self.life[i]:
                    self.active[i] = 0
                else:
                    self.vel[i] += gravity * dt
                    self.pos[i] += self.vel[i] * dt

                    if (
                        self.pos[i].x < 0.0
                        or self.pos[i].x >= width
                        or self.pos[i].y < 0.0
                        or self.pos[i].y >= height
                    ):
                        self.active[i] = 0

    @ti.kernel
    def _rasterize_particles(self, width: ti.f32, height: ti.f32):
        for i in range(self.max_particles):
            if self.active[i] == 1:
                x = int(self.pos[i].x)
                y = int(self.pos[i].y)

                if 0 <= x < int(width) and 0 <= y < int(height):
                    shape = self.shape[i]
                    radius = ti.max(1, ti.cast(self.size[i] * 0.5, ti.i32))

                    if shape == 2:
                        length = ti.max(1, ti.cast(self.spark_length[i], ti.i32))
                        dir_vec = self.vel[i]
                        dir_len = ti.sqrt(dir_vec.x * dir_vec.x + dir_vec.y * dir_vec.y) + 1e-6
                        dir_vec = dir_vec / dir_len
                        for s in range(length + 1):
                            px = x + ti.cast(dir_vec.x * s, ti.i32)
                            py = y + ti.cast(dir_vec.y * s, ti.i32)
                            if 0 <= px < int(width) and 0 <= py < int(height):
                                alpha = ti.min(1.0, 1.0 - ti.cast(s, ti.f32) / ti.cast(length, ti.f32))
                                color = self.color[i] * alpha
                                ti.atomic_add(self.image[py, px], ti.Vector([color.x, color.y, color.z, alpha]))
                    elif shape == 1:
                        for oy in range(-radius, radius + 1):
                            for ox in range(-radius, radius + 1):
                                px = x + ox
                                py = y + oy
                                if 0 <= px < int(width) and 0 <= py < int(height):
                                    alpha = 1.0
                                    color = self.color[i] * alpha
                                    ti.atomic_add(self.image[py, px], ti.Vector([color.x, color.y, color.z, alpha]))
                    else:
                        for oy in range(-radius, radius + 1):
                            for ox in range(-radius, radius + 1):
                                px = x + ox
                                py = y + oy
                                if 0 <= px < int(width) and 0 <= py < int(height):
                                    dist = ti.sqrt(ti.cast(ox * ox + oy * oy, ti.f32))
                                    if dist <= ti.cast(radius, ti.f32):
                                        falloff = 1.0 - dist / ti.cast(radius, ti.f32)
                                        alpha = ti.min(1.0, ti.max(0.0, falloff))
                                        color = self.color[i] * alpha
                                        ti.atomic_add(self.image[py, px], ti.Vector([color.x, color.y, color.z, alpha]))
