"""Railway turnout (стрелочный перевод) from the user's STL.

Source: sources/turnout_print.stl (netfabb, mm, 1144 x 20 x 328 mm, 59 328 triangles, 76 pieces:
rails, switch blades, frog, sleepers, switch machine). Scale taken from the rail gauge: the rails
of the straight end stand 78.7 mm apart inside, so 1:19.3 makes them 1520 mm. The turnout is then
22 m long.

It is a symmetrical turnout (both routes curve away, as on hump yards): the single track with the
switch is at +x, the frog in the middle, the two diverging tracks at -x. A wagon running towards -x
turns left (to +z) or right (to -z).

The print model is schematic: the blades are drawn crossing their stock rails and there are no
guard rails. So the blades are re-posed against the stock rails here and guard rails are added.

Objects (part in glTF extras -> site part id):
  turnout_ties      ties      переводные брусья
  turnout_stock     stock     рамные рельсы
  turnout_blade_l   blade     остряк левый (origin = heel, rest pose: closed = route to the right)
  turnout_blade_r   blade     остряк правый (origin = heel, rest pose: open)
  turnout_closure   closure   переводные кривые и соединительные рельсы
  turnout_frog      frog      крестовина
  turnout_guard     guard     контррельсы (added, not in the STL)
  turnout_rods      rods      переводные тяги
  turnout_machine   machine   стрелочный электропривод (modelled here on the printed box footprint)
Blades carry extras "swing" (rad, rotation.y for the full throw: both blades swing together),
rods carry "shift" (m along z for the full throw).

Origin = rail top on the centre line of the straight track, middle of the turnout; x along the
track, y up, z across (site axes, same as the track on the site).
"""
try:
    from wagonkit import Kit, site_collection, read_stl, split_pieces, SITE_TO_BLENDER
except ImportError:
    pass
import math
import pathlib

from mathutils import Matrix, Vector

OUT = "turnout.glb"
STL_NAME = "sources/turnout_print.stl"
STL_BYTES = None
S = 1.52 / 78.7                      # gauge 78.7 mm -> 1520 mm
X0, Y0, Z0 = 20.38, 120.48, -9.1     # middle of the turnout, rail top, straight-track centre line
ROWS = ((S, 0, 0, -S * X0), (0, S, 0, -S * Y0), (0, 0, S, -S * Z0), (0, 0, 0, 1))
THROW = 0.15                         # how far the blade tip moves, m
FLANGEWAY = 0.046                    # gap between a guard rail and its running rail, m

STYLE = {  # object: (part, colour, roughness, metalness)
    "turnout_ties": ("ties", 0x8a8d8f, 0.9, 0.0),
    "turnout_stock": ("stock", 0x7d858b, 0.45, 0.7),
    "turnout_blade_l": ("blade", 0x9aa2a8, 0.4, 0.75),
    "turnout_blade_r": ("blade", 0x9aa2a8, 0.4, 0.75),
    "turnout_closure": ("closure", 0x737b81, 0.45, 0.7),
    "turnout_frog": ("frog", 0x5f666c, 0.5, 0.6),
    "turnout_guard": ("guard", 0x8f979d, 0.45, 0.7),
    "turnout_rods": ("rods", 0x5a6670, 0.5, 0.5),
    "turnout_machine": ("machine", 0x3e5566, 0.55, 0.35),
}


def site(p, m=Matrix(ROWS)):
    return m @ Vector(p)


def tops(piece):
    """Rail-top vertices of a piece in site metres (the printed rails sag a little, so per 0.25 m bin)."""
    pts = [site(p) for t in piece for p in t]
    if max(p.y for p in pts) < -0.15:
        return []
    hi = {}
    for p in pts:
        b = round(p.x * 4)
        hi[b] = max(hi.get(b, -9), p.y)
    return [p for p in pts if p.y > hi[round(p.x * 4)] - 0.012]


def fit_line(pts):
    """Least squares z = a + b*x."""
    n = len(pts)
    mx = sum(p.x for p in pts) / n
    mz = sum(p.z for p in pts) / n
    b = sum((p.x - mx) * (p.z - mz) for p in pts) / sum((p.x - mx) ** 2 for p in pts)
    return mz - b * mx, b


def end_centre(top, at_min):
    x = min(p.x for p in top) if at_min else max(p.x for p in top)
    near = [p for p in top if abs(p.x - x) < 0.06]
    return Vector((x, 0.0, sum(p.z for p in near) / len(near)))


def z_at(top, x):
    a, b = fit_line(top)
    return a + b * x


def classify(pieces):
    groups = {name: [] for name in STYLE}
    rails = []
    for pc in pieces:
        pts = [site(p) for t in pc for p in t]
        ymax = max(p.y for p in pts)
        if ymax < -0.19 and len(pc) > 400:
            groups["turnout_ties"].append(pc)
        elif ymax < -0.2:
            groups["turnout_rods"].append(pc)
        elif len(pc) < 40:
            groups["turnout_machine"].append(pc)
        else:
            rails.append(pc)
    for pc in rails:
        top = tops(pc)
        xmin, xmax = min(p.x for p in top), max(p.x for p in top)
        if xmin > 7.0:                                   # straight rails at the switch end
            groups["turnout_stock"].append(pc)
        elif xmin > 3.5:                                 # switch panel: stock rail or blade
            heel = end_centre(top, True)
            if abs(heel.z) > 0.8:
                groups["turnout_stock"].append(pc)
            else:
                groups["turnout_blade_l" if heel.z > 0 else "turnout_blade_r"].append(pc)
        elif xmax < -3.5 and xmin > -7.6 and min(abs(p.z) for p in top) < 0.3:
            groups["turnout_frog"].append(pc)
        else:
            groups["turnout_closure"].append(pc)
    return groups


def guard_rails(k, groups, hw):
    """Guard rails inside the outer rails, opposite the frog nose."""
    frog = [fit_line(tops(pc)) for pc in groups["turnout_frog"]]
    (a1, b1), (a2, b2) = frog
    xf = (a2 - a1) / (b1 - b2)                           # theoretical crossing point
    xc, half = xf - 0.4, 1.6                             # guard centre (opposite the nose) and half length
    closure = [p for pc in groups["turnout_closure"] for p in tops(pc)]
    for side in (1, -1):
        outer = [p for p in closure if side * p.z > 0.9 and abs(p.x - xc) < half + 0.6]
        a, b = fit_line(outer)
        off = side * (2 * hw + FLANGEWAY)                # rail centre -> guard centre, towards the track centre
        ang = -math.atan(b)
        rot = Matrix.Rotation(ang, 4, "Y")
        for x0, x1, flare in ((xc - half, xc + half, 0.0), (xc - half - 0.45, xc - half, 1), (xc + half, xc + half + 0.45, -1)):
            xm = (x0 + x1) / 2
            L = (x1 - x0) / math.cos(ang)
            zr = a + b * xm - off
            r = rot
            if flare:                                    # flared ends turn towards the track centre
                zr -= side * 0.018
                r = Matrix.Rotation(ang - flare * side * 0.08, 4, "Y")
            k.box((L, 0.05, 2 * hw), at=(xm, -0.015, zr), rot=r)          # head
            k.box((L, 0.11, 0.022), at=(xm, -0.11, zr), rot=r)            # web
            k.box((L, 0.022, 0.13), at=(xm, -0.177, zr), rot=r)           # foot
        for xb in (xc - 1.1, xc, xc + 1.1):              # spacer blocks to the running rail
            zr = a + b * xb - off / 2
            k.box((0.12, 0.08, abs(off) - 0.02), at=(xb, -0.12, zr), rot=rot)
    return xf


def switch_machine(k, pieces):
    """Electric switch machine on its bed in place of the printed box (same footprint)."""
    pts = [site(p) for pc in pieces for t in pc for p in t]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
    xc, zc, w, d = (x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, z1 - z0
    side = 1 if zc > 0 else -1
    k.box((w + 0.5, 0.05, d * 0.7), at=(xc, -0.33, zc - side * 0.05))                   # bed plate on the ties
    k.box((w, 0.24, d), at=(xc, -0.18, zc), bevel=0.01)                                # housing
    k.mat("lid", 0x4c6577, rough=0.5, metal=0.35)
    k.box((w + 0.04, 0.035, d + 0.04), at=(xc, -0.045, zc), bevel=0.008)               # cover
    k.box((w * 0.5, 0.02, d * 0.3), at=(xc, -0.02, zc - side * d * 0.2))               # cover lock plate
    k.cyl(0.09, 0.22, at=(xc, -0.19, zc + side * (d / 2 + 0.11)), axis="z", seg=20)    # motor end
    k.mat("rod", 0x8a939a, rough=0.35, metal=0.8)
    k.cyl(0.035, 0.3, at=(xc - 0.08, -0.29, zc - side * (d / 2 + 0.15)), axis="z", seg=14)   # throw rod gland
    k.cyl(0.03, 0.3, at=(xc + 0.12, -0.29, zc - side * (d / 2 + 0.15)), axis="z", seg=14)    # detector rod gland
    k.mat("cable", 0x2b2f33, rough=0.8, metal=0.0)
    k.box((0.12, 0.1, 0.16), at=(xc + w / 2 + 0.06, -0.24, zc + side * d * 0.25))     # cable box


def build(collection=None):
    data = STL_BYTES or (pathlib.Path(__file__).resolve().parent / STL_NAME).read_bytes()
    groups = classify(split_pieces(read_stl(data)))
    straight = next(tops(pc) for pc in groups["turnout_stock"] if min(p.x for p in tops(pc)) > 7.0)
    hw = (max(p.z for p in straight) - min(p.z for p in straight)) / 2   # half the rail head width
    stock = {1 if z_at(tops(pc), 7.2) > 0 else -1: tops(pc)
             for pc in groups["turnout_stock"] if min(p.x for p in tops(pc)) < 7.0}

    objs, info = [], {}
    for name, (part, color, rough, metal) in STYLE.items():
        k = Kit(part, name)
        k.mat("m", color, rough=rough, metal=metal)
        origin = Vector((0, 0, 0))
        tris = [t for pc in groups[name] for t in pc]
        if name.startswith("turnout_blade"):
            top = tops(groups[name][0])
            heel, tip = end_centre(top, True), end_centre(top, False)
            side = 1 if name.endswith("_l") else -1
            closed = z_at(stock[side], tip.x) - side * 2 * hw          # tip against the stock rail
            want = closed if side == 1 else closed - side * THROW      # rest pose: left closed, right open
            L = (tip - heel).length
            phi0 = math.atan2(-(tip.z - heel.z), tip.x - heel.x)
            phi1 = math.asin(-(want - heel.z) / L)
            m = Matrix.Rotation(phi1 - phi0, 4, "Y") @ Matrix.Translation(-heel) @ Matrix(ROWS)
            k.stl(tris, m)
            origin = heel
            info[name] = (heel, L)
        elif name == "turnout_guard":
            info["frog_x"] = guard_rails(k, groups, hw)
        elif name == "turnout_machine":
            switch_machine(k, groups[name])
        else:
            k.stl(tris, ROWS)
        o = k.finish(collection, smooth_angle=30)
        o.location = (SITE_TO_BLENDER @ origin.to_4d()).to_3d()
        objs.append(o)

    # full throw: both blade tips move by THROW towards -z (left blade opens, right one closes)
    for o in objs:
        if o.name.startswith("turnout_blade"):
            heel, L = info[o.name]
            o["swing"] = round(math.asin(THROW / L), 5)
        if o.name == "turnout_rods":
            heel, L = info["turnout_blade_l"]
            xr = sum(site(p).x for t in groups["turnout_rods"][0] for p in t) / (3 * len(groups["turnout_rods"][0]))
            o["shift"] = round(-THROW * (xr - heel.x) / L, 4)
    print("turnout: rail head %.3f m, frog crossing x=%.2f, blade %.2f m, swing %.4f rad, rods %.3f m"
          % (2 * hw, info["frog_x"], info["turnout_blade_l"][1],
             next(o["swing"] for o in objs if o.name == "turnout_blade_l"),
             next(o["shift"] for o in objs if o.name == "turnout_rods")))
    return objs


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
