"""Friction wedge of the 18-100 bogie snubber with the insert on its inclined face, from the user's STL.

Source: sources/wedge_18100_print.stl (two pieces: the wedge casting and the insert), taken as
1:10 (about 186 x 194 x 211 mm). Site use: BOGIE_DET, part "wedge".
Origin = bottom of the vertical friction face, at mid-width. The wedge reaches from that face
towards -x (towards the bolster), inclined face up; y up, z across.
"""
try:
    from wagonkit import Kit, site_collection, read_stl, split_pieces
except ImportError:          # pasted after wagonkit.py into a single script
    pass
import pathlib

OUT = "wedge_18100.glb"
STL_NAME = "sources/wedge_18100_print.stl"
STL_BYTES = None
ROWS = ((0, -0.01, 0, 0.0455), (0, 0, 0.01, 0), (-0.01, 0, 0, 0.093), (0, 0, 0, 1))


def build(collection=None):
    data = STL_BYTES or (pathlib.Path(__file__).resolve().parent / STL_NAME).read_bytes()
    body, insert = split_pieces(read_stl(data))[:2]
    k = Kit("wedge", "Клин_фрикционный_18-100")
    k.mat("cast", 0x4b5157, rough=0.6, metal=0.35)
    k.stl(body, ROWS)
    k.mat("insert", 0xc0563f, rough=0.8, metal=0.0)       # wear insert on the inclined face
    k.stl(insert, ROWS)
    return k.finish(collection, smooth_angle=40)


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
