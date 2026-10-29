"""Rebuild every Blender part and export it to ../models/*.glb.

    python3 blender/build.py                 # with the `bpy` module (pip install bpy)
    blender -b -P blender/build.py           # or with the Blender app, headless

Each part script exposes build() -> object and OUT (file name in models/).
"""
import importlib
import pathlib
import sys

import bpy

HERE = pathlib.Path(__file__).resolve().parent
MODELS = HERE.parent / "models"
PARTS = ["brake_cylinder_188b"]          # add new part scripts here

sys.path.insert(0, str(HERE))
import wagonkit  # noqa: E402


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MODELS.mkdir(exist_ok=True)
    for name in PARTS:
        mod = importlib.import_module(name)
        obj = mod.build()
        out = MODELS / mod.OUT
        wagonkit.export_glb([obj], out)
        me = obj.data
        print(f"{name}: {len(me.polygons)} faces, {len(me.vertices)} verts -> {out.name} "
              f"({out.stat().st_size / 1024:.0f} KB)")


main()
