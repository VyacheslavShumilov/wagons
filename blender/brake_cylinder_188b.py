"""Brake cylinder No. 188B (Ø356 mm / 14") of a freight car.

Site use: BRAKE_RIG in index.html, part "brake_cylinder".
Origin = middle of the cylinder body; axis along site x, rod (front cover) towards +x.
The site places it at ((C0+C1)/2, BR_YC, BR_ZC) and keeps its own piston rod, rear-cover
lever bracket (hl_bracket) and pins, so those are NOT modelled here.

Key sizes (site metres): body R .178, front cover face at x=+.30, rod guide to x=+.37,
rear cover face at x=-.30, mounting pads under the car frame at y≈+.21.
"""
import math
from mathutils import Matrix
try:
    from wagonkit import Kit, site_collection
except ImportError:          # pasted after wagonkit.py into a single script
    pass

PART = "brake_cylinder"
OUT = "brake_cylinder_188b.glb"
R = 0.178            # body radius
HL = 0.27            # half length of the body tube


def build(collection=None):
    k = Kit(PART, "ТЦ_188Б")

    # ---- cast body -------------------------------------------------------------
    k.mat("body", 0x3b4e5c, rough=0.55, metal=0.35)
    k.cyl(R, 2 * HL, axis="x", seg=64, bevel=0.004)
    for x in (-0.13, 0.0, 0.13):                          # cast stiffening rings
        k.cyl(R + 0.012, 0.022, at=(x, 0, 0), axis="x", seg=64, bevel=0.004)
    # mounting pads with gussets: the cylinder hangs from the car frame on them
    for x in (-0.165, 0.165):
        k.box((0.10, 0.034, 0.40), at=(x, R + 0.017, 0), bevel=0.006)
        for z in (-0.105, 0.105):
            k.box((0.085, 0.07, 0.016), at=(x, R - 0.01, z), bevel=0.003)
        k.box((0.016, 0.05, 0.24), at=(x, R - 0.005, 0), bevel=0.003)
    # air inlet boss on the rear end, on top
    k.cyl(0.032, 0.06, at=(-HL + 0.05, R + 0.01, 0.09), axis="y", seg=24, bevel=0.003)
    # cast lugs for the nameplate
    k.box((0.13, 0.07, 0.012), at=(0.0, -0.02, R + 0.008), bevel=0.002)

    # ---- covers and flanges ----------------------------------------------------
    k.mat("cover", 0x56707f, rough=0.5, metal=0.35)
    # front: flange on the body + bolted cover with rod guide
    k.cyl(0.212, 0.03, at=(HL - 0.012, 0, 0), axis="x", seg=64, bevel=0.004)
    k.cyl(0.206, 0.026, at=(HL + 0.017, 0, 0), axis="x", seg=64, bevel=0.005)
    k.cyl(0.15, 0.022, at=(HL + 0.04, 0, 0), axis="x", r2=0.11, seg=48, bevel=0.004)
    k.cyl(0.074, 0.07, at=(HL + 0.076, 0, 0), axis="x", seg=32, bevel=0.004)
    k.ring(0.082, 0.052, 0.014, at=(HL + 0.108, 0, 0), axis="x", seg=32, bevel=0.002)
    for i in range(6):                                   # ribs between cover and rod guide
        a = 2 * math.pi * i / 6 + math.pi / 6
        k.box((0.05, 0.012, 0.09),
              at=(HL + 0.045, 0.125 * math.cos(a), 0.125 * math.sin(a)),
              rot=Matrix.Rotation(a - math.pi / 2, 4, "X"),
              bevel=0.002)
    # rear: flange + slightly dished cover (the lever bracket on it is built by the site)
    k.cyl(0.212, 0.03, at=(-HL + 0.012, 0, 0), axis="x", seg=64, bevel=0.004)
    k.cyl(0.206, 0.024, at=(-HL - 0.016, 0, 0), axis="x", seg=64, bevel=0.005)
    k.cyl(0.17, 0.012, at=(-HL - 0.034, 0, 0), axis="x", r2=0.14, seg=64, bevel=0.003)

    # ---- fasteners and fittings ------------------------------------------------
    k.mat("steel", 0x2b3136, rough=0.45, metal=0.6)
    k.bolt_circle(12, 0.194, 0.0125, 0.012, HL + 0.035, phase=math.pi / 12)
    k.bolt_circle(12, 0.194, 0.0125, 0.012, -HL - 0.033, phase=math.pi / 12)
    for x in (-0.165, 0.165):                            # nuts of the frame bolts
        for z in (-0.15, 0.15):
            k.hexnut(0.016, 0.014, at=(x, R - 0.005, z), axis="y")
            k.cyl(0.009, 0.03, at=(x, R + 0.045, z), axis="y", seg=12)
    k.hexnut(0.024, 0.02, at=(-HL + 0.05, R + 0.05, 0.09), axis="y")     # inlet union nut
    k.cyl(0.016, 0.07, at=(-HL + 0.05, R + 0.09, 0.09), axis="y", seg=16)  # pipe stub
    k.hexnut(0.017, 0.016, at=(0.05, -R - 0.006, 0), axis="y")          # drain plug

    k.mat("plate", 0xc9cfd4, rough=0.35, metal=0.7)
    k.box((0.11, 0.055, 0.003), at=(0.0, -0.02, R + 0.0155), bevel=0.001)

    return k.finish(collection)


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
