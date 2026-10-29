"""Rebuild every Blender part and export it to ../models/*.glb.

    python3 blender/build.py                 # with the `bpy` module (pip install bpy)
    blender -b -P blender/build.py           # or with the Blender app, headless

Each part script exposes build() -> object or list of objects, and OUT (file name in models/).
"""
import importlib
import pathlib
import sys

import bpy

HERE = pathlib.Path(__file__).resolve().parent
MODELS = HERE.parent / "models"
PARTS = ["brake_cylinder_188b", "autoregime_265a1", "air_distributor_483", "coupler_sa3",
         "spring_set_18100", "friction_plate_18100", "wedge_18100", "bogie_68_4095"]          # add new part scripts here

sys.path.insert(0, str(HERE))
import wagonkit  # noqa: E402


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MODELS.mkdir(exist_ok=True)
    for name in PARTS:
        mod = importlib.import_module(name)
        objs = mod.build()
        objs = objs if isinstance(objs, list) else [objs]   # a part may be several objects
        out = MODELS / mod.OUT
        wagonkit.export_glb(objs, out)
        faces = sum(len(o.data.polygons) for o in objs)
        print(f"{name}: {len(objs)} object(s), {faces} faces -> {out.name} "
              f"({out.stat().st_size / 1024:.0f} KB)")


main()
