"""Passenger bogie 68-4095 (Tver carriage works), from the user's STL of an H0 (1:87) model.

Source: sources/bogie_68_4095_h0.stl (CHITUBOX export, 352 148 triangles, 80 pieces, assembled,
no wheelsets). Scale 1:87: it gives the 2036 mm spacing of the axle journals; the axle spacing
of the model then comes out at 2.65 m (the real bogie has 2.5 m).
Pieces are sorted into the objects below by their triangle count and position; each object
carries the site part id and is placed separately on the site (explode, highlighting).
Wheelsets and the disc brake are drawn by the site itself.

Origin = bogie centre at rail level; x along the car, y up, z across (site axes).
"""
try:
    from wagonkit import Kit, site_collection, read_stl, split_pieces
except ImportError:          # pasted after wagonkit.py into a single script
    pass
import pathlib

OUT = "bogie_68_4095.glb"
STL_NAME = "sources/bogie_68_4095_h0.stl"
STL_BYTES = None
S = 0.087                    # H0, mm -> m
ZR = 4.01                    # rail level below the STL origin: axle centre z 1.49 minus R 478.5 mm / 87
ROWS = ((S, 0, 0, 0), (0, 0, S, ZR * S), (0, -S, 0, 0), (0, 0, 0, 1))

# object name: (site part, colour, roughness, metalness, decimate ratio)
OBJECTS = {
    "pb_frame": ("frame", 0x3a3f44, 0.75, 0.3, 0.45),
    "pb_bolster": ("bolster", 0x454b51, 0.75, 0.3, 0.45),
    "pb_springs": ("central_spring", 0xb0703f, 0.45, 0.5, 0.12),
    "pb_axlebox_p": ("axle_box", 0x4b5157, 0.6, 0.4, 0.3),
    "pb_axlebox_n": ("axle_box", 0x4b5157, 0.6, 0.4, 0.3),
    "pb_link_p": ("axle_link", 0x5a6066, 0.55, 0.45, 0.25),
    "pb_link_n": ("axle_link", 0x5a6066, 0.55, 0.45, 0.25),
    "pb_blink": ("bolster_link", 0x5a6066, 0.55, 0.45, 0.4),
    "pb_vdamp": ("vert_damper", 0x2b3136, 0.4, 0.6, 0.5),
    "pb_ldamp": ("lat_damper", 0x2b3136, 0.4, 0.6, 0.5),
}


def classify(piece):
    n = len(piece)
    xs = [p[0] for t in piece for p in t]
    ys = [p[1] for t in piece for p in t]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    side = "p" if cx > 0 else "n"
    if n == 40668:
        return "pb_springs"
    if n == 34438:
        return "pb_frame"
    if n == 22950:
        return "pb_bolster"
    if n in (10556, 292, 242, 158):          # axle boxes, their covers and bolts
        return "pb_axlebox_" + side
    if n == 6532:
        return "pb_link_" + side
    if n == 10151:
        return "pb_blink"
    if n == 1597 or (n == 472 and abs(cx) < 1):
        return "pb_vdamp"
    if n == 1752 or n == 472:
        return "pb_ldamp"
    return None


def build(collection=None):
    data = STL_BYTES or (pathlib.Path(__file__).resolve().parent / STL_NAME).read_bytes()
    groups = {name: [] for name in OBJECTS}
    for piece in split_pieces(read_stl(data)):
        name = classify(piece)
        if name:
            groups[name].extend(piece)
    objs = []
    for name, (part, color, rough, metal, ratio) in OBJECTS.items():
        k = Kit(part, name)
        k.mat("m", color, rough=rough, metal=metal)
        k.stl(groups[name], ROWS)
        o = k.finish(collection, smooth_angle=40)
        d = o.modifiers.new("Decimate", "DECIMATE")
        d.ratio = ratio
        objs.append(o)
    return objs


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
