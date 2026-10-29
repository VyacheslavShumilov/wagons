"""Through-truss railway bridge span from the user's STL of an H0 (1:87) model.

Source: sources/truss_bridge_h0.stl (netfabb, mm, 90 x 108 x 484 mm, 44 824 triangles, 85 pieces:
two truss girders with diagonals, deck with ties and rails). At 1:87 the span is 42 m long,
9.4 m high and 7.8 m wide; the rails are 1490 mm apart inside (H0 track is close to 1520).

Origin = rail top on the track centre line, middle of the span; x along the track, y up,
z across (site axes). Not wired in yet.
"""
try:
    from wagonkit import Kit, site_collection, read_stl, split_pieces
except ImportError:
    pass
import pathlib

OUT = "truss_bridge.glb"
STL_NAME = "sources/truss_bridge_h0.stl"
STL_BYTES = None
S = 0.087
XC, Y0, ZC = -86.6, 136.7, 0.17      # track centre line (STL x), rail top (STL y), middle of the span (STL z)
ROWS = ((0, 0, S, -S * ZC), (0, S, 0, -S * Y0), (-S, 0, 0, S * XC), (0, 0, 0, 1))


def build(collection=None):
    data = STL_BYTES or (pathlib.Path(__file__).resolve().parent / STL_NAME).read_bytes()
    trusses, deck, rails = [], [], []
    for piece in split_pieces(read_stl(data)):
        xs = [p[0] for t in piece for p in t]
        zs = [p[2] for t in piece for p in t]
        w, L = max(xs) - min(xs), max(zs) - min(zs)
        if w < 3 and L > 100:
            rails.extend(piece)
        elif max(xs) - min(xs) < 8 and (max(xs) < -110 or min(xs) > -64):
            trusses.extend(piece)
        else:
            deck.extend(piece)
    objs = []
    for name, part, tris, color, rough, metal in (("bridge_truss", "truss", trusses, 0x4f5a62, 0.6, 0.4),
                                                  ("bridge_deck", "deck", deck, 0x5d6266, 0.75, 0.3),
                                                  ("bridge_rails", "rails", rails, 0x7d858b, 0.45, 0.7)):
        k = Kit(part, name)
        k.mat("m", color, rough=rough, metal=metal)
        k.stl(tris, ROWS)
        objs.append(k.finish(collection, smooth_angle=30))
    return objs


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
