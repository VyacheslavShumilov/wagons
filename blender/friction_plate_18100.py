"""Friction plate (планка фрикционная 100.00.008-2) of the 18-100 bogie side frame, from the user's STL.

Source: sources/friction_plate_18100_print.stl, taken as 1:10 (plate 260 x 215 x 10 mm, four
bolt holes in corner lugs). Site use: BOGIE_DET, part "friction_plate".
Origin = centre of the plate; the plate is vertical: thickness along x, long side along y.
"""
try:
    from wagonkit import Kit, site_collection, read_stl
except ImportError:          # pasted after wagonkit.py into a single script
    pass
import pathlib

OUT = "friction_plate_18100.glb"
STL_NAME = "sources/friction_plate_18100_print.stl"
STL_BYTES = None
ROWS = ((0, 0, 0.01, -0.005), (0.01, 0, 0, -0.13), (0, 0.01, 0, -0.1075), (0, 0, 0, 1))


def build(collection=None):
    data = STL_BYTES or (pathlib.Path(__file__).resolve().parent / STL_NAME).read_bytes()
    k = Kit("friction_plate", "Планка_фрикционная_100.00.008-2")
    k.mat("steel", 0x7b848a, rough=0.4, metal=0.6)
    k.stl(read_stl(data), ROWS)
    return k.finish(collection, smooth_angle=40)


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
