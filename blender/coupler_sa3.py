"""Automatic coupler SA-3 (автосцепка СА-3): coupler body from the user's STL.

Source: sources/coupler_sa3_print.stl - a print model of the coupler body split by the horizontal
plane through the coupler axis into two halves lying cut face down (top half with the stop,
18 404 triangles in all). The halves are put back together here: they were matched on their cut
faces (fit error 0.005 STL units), turned into site axes and scaled so that the body is 1100 mm
long (the STL has no units; 1100 mm is an estimate of the SA-3 body length).

Site use: part "coupler" (COUPLER_P, shared by all wagons) - not wired in yet.
Origin = on the coupler axis (the split plane) at the tip of the large tooth; x along the car with
the head at +x, y up, z across - as in the other scripts. The earlier hand-drawn version is
coupler_sa3_draft.py.
"""
import pathlib
import struct
try:
    from wagonkit import Kit, site_collection, SITE_TO_BLENDER
except ImportError:          # pasted after wagonkit.py into a single script
    pass
from mathutils import Matrix, Vector

PART = "coupler"
OUT = "coupler_sa3.glb"
STL_NAME = "sources/coupler_sa3_print.stl"
STL_BYTES = None             # set by the caller when the script runs without its folder (live Blender)

# STL (mm, print bed) -> site (m), per half; halves told apart by their triangle count
HALVES = {
    10470: ((-0.0031048, 0.0031601, 0.0, -0.5779545), (0.0, 0.0, 0.0044301, 0.0),
            (0.0031601, 0.0031048, 0.0, -0.5690737), (0.0, 0.0, 0.0, 1.0)),          # top half
    7934: ((-0.0031601, 0.0031048, 0.0, -0.5600694), (0.0, 0.0, -0.0044301, 0.0),
           (-0.0031048, -0.0031601, 0.0, 0.9819229), (0.0, 0.0, 0.0, 1.0)),          # bottom half
}


def read_stl(data):
    n = struct.unpack_from("<I", data, 80)[0]
    tris = []
    for i in range(n):
        v = struct.unpack_from("<9f", data, 84 + 50 * i + 12)
        tris.append((v[0:3], v[3:6], v[6:9]))
    return tris


def split_halves(tris):
    """Connected pieces of a triangle soup -> {triangle count: [triangles]}."""
    index, parent = {}, []
    def vid(p):
        key = (round(p[0], 4), round(p[1], 4), round(p[2], 4))
        if key not in index:
            index[key] = len(parent)
            parent.append(len(parent))
        return index[key]
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    ids = [tuple(vid(p) for p in t) for t in tris]
    for a, b, c in ids:
        for x, y in ((a, b), (a, c)):
            rx, ry = root(x), root(y)
            if rx != ry:
                parent[rx] = ry
    groups = {}
    for t, (a, _, _) in zip(tris, ids):
        groups.setdefault(root(a), []).append(t)
    return {len(g): g for g in groups.values()}


def build(collection=None):
    data = STL_BYTES
    if data is None:
        data = (pathlib.Path(__file__).resolve().parent / STL_NAME).read_bytes()
    halves = split_halves(read_stl(data))
    k = Kit(PART, "Автосцепка_СА-3")
    k.mat("body", 0x5f666c, rough=0.5, metal=0.6)
    for count, rows in HALVES.items():
        M = SITE_TO_BLENDER @ Matrix(rows)
        verts = {}
        for tri in halves[count]:
            vs = []
            for p in tri:
                key = (round(p[0], 4), round(p[1], 4), round(p[2], 4))
                if key not in verts:
                    verts[key] = k.bm.verts.new(M @ Vector(p))
                vs.append(verts[key])
            if len(set(vs)) == 3:
                try:
                    k.bm.faces.new(vs)
                except ValueError:       # duplicate triangle in the STL
                    pass
    k._claim()
    return k.finish(collection, smooth_angle=35)


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
