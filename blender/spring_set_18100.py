"""Spring set of the 18-100 bogie: outer and inner coil springs, from the user's STL.

Source: sources/spring_set_18100_print.stl (print model, two springs one inside the other).
The print is taken as 1:10 (outer spring Ø200 mm, bar Ø28 mm, free height 259 mm; inner spring
Ø134 mm, bar Ø19 mm) - the 18-100 outer spring is Ø30 bar, 249 mm free height.

Site use: BOGIE_DET, parts "spring_outer" and "spring_inner". Origin = centre of the spring seat,
springs along +y (the site scales them to the loaded height).
"""
try:
    from wagonkit import Kit, site_collection, read_stl, split_pieces
except ImportError:          # pasted after wagonkit.py into a single script
    pass
import pathlib

OUT = "spring_set_18100.glb"
STL_NAME = "sources/spring_set_18100_print.stl"
STL_BYTES = None
ROWS = ((0.01, 0, 0, -0.1), (0, 0, 0.01, 0), (0, -0.01, 0, 0.1), (0, 0, 0, 1))
DECIMATE = 0.45              # keep 45 % of the triangles: 14 sets are drawn on the site


def build(collection=None):
    data = STL_BYTES or (pathlib.Path(__file__).resolve().parent / STL_NAME).read_bytes()
    pieces = split_pieces(read_stl(data))
    span = lambda tris: max(p[0] for t in tris for p in t) - min(p[0] for t in tris for p in t)
    outer, inner = sorted(pieces[:2], key=span, reverse=True)
    objs = []
    for part, name, color, tris in (("spring_outer", "Пружина_наружная_18-100", 0xb0703f, outer),
                                    ("spring_inner", "Пружина_внутренняя_18-100", 0xc9a24e, inner)):
        k = Kit(part, name)
        k.mat("steel", color, rough=0.45, metal=0.5)
        k.stl(tris, ROWS)
        o = k.finish(collection, smooth_angle=60)
        d = o.modifiers.new("Decimate", "DECIMATE")
        d.ratio = DECIMATE
        objs.append(o)
    return objs


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
