from __future__ import annotations

from typing import Optional

_taichi_module = None
_initialized = False
_init_error: Optional[Exception] = None
_arch = None


def _load_taichi():
    global _taichi_module
    if _taichi_module is None:
        import taichi as ti
        _taichi_module = ti
    return _taichi_module


def get_taichi_runtime(prefer_gpu: bool = True):
    global _initialized, _init_error, _arch

    ti = _load_taichi()
    if _initialized:
        return ti, _arch

    if getattr(ti, "is_initialized", None) and ti.is_initialized():
        _initialized = True
        _arch = getattr(ti.cfg, "arch", None)
        return ti, _arch

    try:
        if prefer_gpu:
            for arch in (ti.cuda, ti.vulkan, ti.metal):
                try:
                    ti.init(arch=arch)
                    _arch = arch
                    _initialized = True
                    return ti, _arch
                except Exception:
                    continue

        ti.init(arch=ti.cpu)
        _arch = ti.cpu
        _initialized = True
        return ti, _arch
    except Exception as exc:
        _init_error = exc
        raise


def taichi_initialized() -> bool:
    return _initialized


def taichi_init_error() -> Optional[Exception]:
    return _init_error
