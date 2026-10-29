"""Through-truss railway bridge span from the user's STL of an H0 (1:87) model.

Source: sources/truss_bridge_h0.stl (netfabb, mm, 90 x 108 x 484 mm, 44 824 triangles, 85 pieces:
two Warren truss girders, stringers with a deck plate, ties, rails, walkways with railings and two
lower lateral braces). At 1:87 the span is 42 m long, the trusses are 7.3 m high and 5.3 m apart.

The printed ties and rails lean 0.16 m over the span length (the trusses and the floor are level);
they are levelled here. The print has no upper
bracing, portals or floor beams: these are added from boxes so the span reads like a real one.

Objects (part in glTF extras -> site part id):
  bridge_chords    chord     верхний и нижний пояса ферм
  bridge_web       web       раскосы и опорные стойки ферм
  bridge_bracing   bracing   связи: верхние, портальные, нижние (upper and portal ones added)
  bridge_floor     floor     балочная клетка: продольные балки, поперечные балки (added), настил
  bridge_ties      ties      мостовые брусья
  bridge_rails     rails     рельсы
  bridge_walkway   walkway   тротуары с перилами

Origin = rail top on the track centre line, middle of the span; x along the track, y up,
z across (site axes).
"""
try:
    from wagonkit import Kit, site_collection, read_stl, split_pieces
except ImportError:
    pass
import math
import pathlib

from mathutils import Matrix, Vector

OUT = "truss_bridge.glb"
STL_NAME = "sources/truss_bridge_h0.stl"
STL_BYTES = None
S = 0.087
XC, Y0, ZC = -86.6, 136.7, 0.17      # track centre line (STL x), rail top (STL y), middle of the span (STL z)
ROWS = ((0, 0, S, -S * ZC), (0, S, 0, -S * Y0), (-S, 0, 0, S * XC), (0, 0, 0, 1))
LEVEL = Matrix.Rotation(-0.00377, 4, "Z")   # printed ties and rails drop 0.155 m over 41 m towards -x

STYLE = {  # object: (part, colour, roughness, metalness)
    "bridge_chords": ("chord", 0x4f5a62, 0.6, 0.4),
    "bridge_web": ("web", 0x56626b, 0.6, 0.4),
    "bridge_bracing": ("bracing", 0x5f6b73, 0.6, 0.4),
    "bridge_floor": ("floor", 0x4a5157, 0.7, 0.35),
    "bridge_ties": ("ties", 0x5b4a3e, 0.9, 0.0),
    "bridge_rails": ("rails", 0x7d858b, 0.45, 0.7),
    "bridge_walkway": ("walkway", 0x6b7378, 0.75, 0.3),
}
TOP_Y, BOT_Y = 6.4, 0.2             # truss vertices above TOP_Y are the top chord, below BOT_Y the bottom chord


def site(p, m=Matrix(ROWS)):
    return m @ Vector(p)


def bbox(piece):
    pts = [site(p) for t in piece for p in t]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def classify(pieces):
    groups = {name: [] for name in STYLE}
    trusses = []
    for pc in pieces:
        lo, hi = bbox(pc)
        size = [h - l for l, h in zip(lo, hi)]
        if hi[1] > 5:                                             # the two truss girders
            trusses.append(pc)
        elif size[0] > 8 and size[2] < 0.3 and hi[1] > 0.2:       # railings
            groups["bridge_walkway"].append(pc)
        elif size[0] > 8 and size[2] < 0.3 and hi[1] > -0.15:    # rails
            groups["bridge_rails"].append(pc)
        elif size[0] < 0.6 and size[2] > 2:                       # ties across the track
            groups["bridge_ties"].append(pc)
        elif size[0] > 40 and lo[1] > -1.0 and abs(lo[2] + hi[2]) > 4:   # walkway floors outside the trusses
            groups["bridge_walkway"].append(pc)
        elif size[0] < 10 and size[2] > 5:                        # lower lateral braces
            groups["bridge_bracing"].append(pc)
        else:                                                     # stringers and the deck plate
            groups["bridge_floor"].append(pc)
    chords, web = [], []
    for pc in trusses:
        for t in pc:
            ys = [site(p).y for p in t]
            (chords if min(ys) > TOP_Y or max(ys) < BOT_Y else web).append(t)
    groups["bridge_chords"] = [chords]
    groups["bridge_web"] = [web]
    return groups, trusses


def strut(k, a, b, w, h):
    """Box from point a to point b (site), w across, h high; rotated about y only."""
    a, b = Vector(a), Vector(b)
    d = b - a
    L = math.hypot(d.x, d.z)
    rot = Matrix.Rotation(math.atan2(-d.z, d.x), 4, "Y")
    k.box((L, h, w), at=tuple((a + b) / 2), rot=rot)


def bracing(k, trusses):
    """Upper lateral bracing, portal frames at the end posts (not in the print)."""
    zs = []
    tops = []
    for pc in trusses:
        pts = [site(p) for t in pc for p in t]
        zs.append(sum(p.z for p in pts) / len(pts))
        tops.append([p for p in pts if p.y > TOP_Y])
    zl, zr = max(zs), min(zs)                         # truss centre planes
    top = [p for t in tops for p in t]
    x0, x1 = min(p.x for p in top), max(p.x for p in top)
    yb = TOP_Y + 0.05                                 # under the top chord
    nodes = [x0 + 0.3, (x0 + x1) / 2, x1 - 0.3]
    for x in nodes:                                   # transverse struts at the top chord nodes
        k.box((0.32, 0.42, zl - zr), at=(x, yb + 0.21, (zl + zr) / 2))
    for xa, xb in zip(nodes, nodes[1:]):              # X bracing in the panels between them
        strut(k, (xa, yb + 0.15, zl), (xb, yb + 0.15, zr), 0.16, 0.16)
        strut(k, (xa, yb + 0.15, zr), (xb, yb + 0.15, zl), 0.16, 0.16)
    # portal frames: end posts run from the bearings (x = +-20.6, y = -0.35) up to the top chord ends
    ends = [(-20.58, x0), (20.49, x1)]
    for xe, xt in ends:
        for y in (5.3, 3.9):
            x = xe + (y + 0.35) / (TOP_Y + 0.4 + 0.35) * (xt - xe)
            k.box((0.3, 0.5 if y > 5 else 0.3, zl - zr), at=(x, y, (zl + zr) / 2))
    return zl, zr


def floor_beams(k, zl, zr):
    """Floor beams under the stringers at the bottom chord nodes (not in the print)."""
    for x in (-20.2, -13.75, -7.0, 0.0, 6.9, 13.7, 20.1):
        k.box((0.36, 1.3, zl - zr), at=(x, -1.45, (zl + zr) / 2))
        k.box((0.5, 0.04, zl - zr), at=(x, -0.79, (zl + zr) / 2))
        k.box((0.5, 0.04, zl - zr), at=(x, -2.11, (zl + zr) / 2))


def build(collection=None):
    data = STL_BYTES or (pathlib.Path(__file__).resolve().parent / STL_NAME).read_bytes()
    groups, trusses = classify(split_pieces(read_stl(data)))
    objs, planes = [], None
    for name, (part, color, rough, metal) in STYLE.items():
        k = Kit(part, name)
        k.mat("m", color, rough=rough, metal=metal)
        M = LEVEL @ Matrix(ROWS) if name in ("bridge_ties", "bridge_rails") else Matrix(ROWS)
        k.stl([t for pc in groups[name] for t in pc], M)
        if name == "bridge_bracing":
            planes = bracing(k, trusses)
        elif name == "bridge_floor":
            floor_beams(k, *planes)
        objs.append(k.finish(collection, smooth_angle=30))
    print("truss_bridge:", {n: sum(len(pc) for pc in g) for n, g in groups.items()}, "trusses at z", planes)
    return objs


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
