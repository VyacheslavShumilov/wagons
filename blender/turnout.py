"""Railway turnout (стрелочный перевод) from the user's STL.

Source: sources/turnout_print.stl (netfabb, mm, 1144 x 20 x 328 mm, 59 328 triangles, 76 pieces:
rails, switch blades, frog, sleepers, switch machine). Scale taken from the rail gauge: the rails
of the straight end stand 78.7 mm apart inside, so 1:19.3 makes them 1520 mm. The turnout is then
22 m long.

Origin = rail top on the centre line of the straight track, middle of the turnout; x along the
track, y up, z across (site axes, same as the track on the site). Not wired in yet.
"""
try:
    from wagonkit import Kit, site_collection, read_stl, split_pieces
except ImportError:
    pass
import pathlib

OUT = "turnout.glb"
STL_NAME = "sources/turnout_print.stl"
STL_BYTES = None
S = 1.52 / 78.7                      # gauge 78.7 mm -> 1520 mm
X0, Y0, Z0 = 20.38, 120.48, -9.1     # middle of the turnout, rail top, straight-track centre line
ROWS = ((S, 0, 0, -S * X0), (0, S, 0, -S * Y0), (0, 0, S, -S * Z0), (0, 0, 0, 1))


def build(collection=None):
    data = STL_BYTES or (pathlib.Path(__file__).resolve().parent / STL_NAME).read_bytes()
    sleepers, steel = [], []
    for piece in split_pieces(read_stl(data)):
        ys = [p[1] for t in piece for p in t]
        (sleepers if max(ys) < 111 else steel).extend(piece)   # sleepers lie below the rail feet
    objs = []
    for name, part, tris, color, rough, metal in (("turnout_sleepers", "sleepers", sleepers, 0x8a8d8f, 0.9, 0.0),
                                                  ("turnout_rails", "rails", steel, 0x7d858b, 0.45, 0.7)):
        k = Kit(part, name)
        k.mat("m", color, rough=rough, metal=metal)
        k.stl(tris, ROWS)
        objs.append(k.finish(collection, smooth_angle=30))
    return objs


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
