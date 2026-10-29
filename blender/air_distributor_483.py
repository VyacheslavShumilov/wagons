"""Air distributor (воздухораспределитель) No. 483 of a freight car, three parts.

Site use: BRAKE_RIG in index.html, parts "vr_chamber", "vr_main", "vr_line" (not wired in yet).

Construction (Руководство ПКБ ЦВ № 922-2021, п. 2.1; Асадченко, «Автоматические тормоза»):
- two-chamber reservoir 295.001: working chamber 6.0 L, spool chamber 4.5 L; bolted to the
  bracket on the car frame with four M20 bolts; carries the load-mode switch (порожний /
  средний / гружёный) and the pipe connections to the brake pipe, the auxiliary reservoir
  and the brake cylinder;
- main part 270.023 on one flange of the reservoir: body and cover, release valve with its
  pull lever (поводок) for manual release;
- line part 483.010 on the opposite, identical flange: body and diaphragm cover with the
  release-mode handle «Р/Г» (равнинный / горный).
Overall sizes are not given in these sources; they are estimated (≈540 x 300 x 300 mm).

Origin = centre of the reservoir. Local axes as on the site: x along the car, the line part
towards -x and the main part towards +x (as the primitives in BRAKE_RIG), y up, z across.
"""
import math
from mathutils import Matrix
try:
    from wagonkit import Kit, site_collection, sd_circle, sd_rrect, sd_union, outline
except ImportError:          # pasted after wagonkit.py into a single script
    pass

PART = "vr_chamber"
OUT = "air_distributor_483.glb"
MM = 0.001


def m(v):
    return v * MM


def bolt_ring(k, n, radius, x, r_head=8, depth=8, phase=0.0):
    for i in range(n):
        a = phase + 2 * math.pi * i / n
        k.hexnut(m(r_head), m(depth), at=(m(x), m(radius) * math.sin(a), m(radius) * math.cos(a)), axis="x")


def reservoir(col):
    k = Kit("vr_chamber", "ВР483_Резервуар_295.001")
    k.mat("body", 0x3e6e8c, rough=0.6, metal=0.3)
    # cast body: rounded block with a waist between the two chambers
    side = sd_union([sd_rrect(0, 0, 300, 250, 46), sd_rrect(0, -40, 230, 230, 40)], k=24)
    k.prism([(m(x), m(y)) for x, y in outline(side, (-170, -170, 170, 140), 2)], m(270), axis="z", bevel=m(8))
    for z in (-70, 70):                                         # cast ribs on the top
        k.box((m(250), m(16), m(14)), at=(0, m(128), m(z)), bevel=m(4))
    # identical mating flanges for the main and line parts
    for s in (1, -1):
        k.cyl(m(100), m(18), at=(s * m(159), 0, 0), axis="x", seg=64, bevel=m(3))
    # mounting pad on top: four lugs for the M20 bolts to the frame bracket
    k.box((m(200), m(22), m(200)), at=(0, m(136), 0), bevel=m(5))
    for sx in (1, -1):
        for sz in (1, -1):
            k.ring(m(24), m(11), m(22), at=(sx * m(110), m(136), sz * m(110)), axis="y", seg=28, bevel=m(2))
            k.box((m(40), m(22), m(26)), at=(sx * m(92), m(136), sz * m(92)),
                  rot=Matrix.Rotation(sx * sz * math.pi / 4, 4, "Y"), bevel=m(3))
    # pipe bosses on the back: brake pipe (through the isolating cock), aux. reservoir, cylinder
    for x, r in ((-80, 26), (0, 22), (80, 22)):
        k.ring(m(r), m(r - 10), m(30), at=(m(x), m(-40), m(-150)), axis="z", seg=32, bevel=m(2))
    # filter plug boss at the bottom
    k.cyl(m(30), m(16), at=(m(-60), m(-160), 0), axis="y", seg=32, bevel=m(2))
    # load-mode switch: boss and sector on the front face
    k.cyl(m(34), m(14), at=(m(60), m(-30), m(141)), axis="z", seg=40, bevel=m(2))
    k.box((m(120), m(70), m(6)), at=(m(60), m(10), m(137)), bevel=m(2))
    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    for sx in (1, -1):                                          # M20 bolts with crown nuts
        for sz in (1, -1):
            k.hexnut(m(16), m(13), at=(sx * m(110), m(153), sz * m(110)), axis="y")
            k.cyl(m(10), m(70), at=(sx * m(110), m(150), sz * m(110)), axis="y", seg=16)
            k.hexnut(m(16), m(16), at=(sx * m(110), m(117), sz * m(110)), axis="y")
    k.hexnut(m(22), m(14), at=(m(-60), m(-175), 0), axis="y")   # filter plug
    k.mat("handle", 0xd9a520, rough=0.45, metal=0.3)            # load-mode handle (yellow, as painted)
    k.cyl(m(14), m(22), at=(m(60), m(-30), m(155)), axis="z", seg=20, bevel=m(1.5))
    k.box((m(18), m(110), m(12)), at=(m(60), m(30), m(160)), bevel=m(3))
    k.cyl(m(13), m(30), at=(m(60), m(88), m(160)), axis="z", seg=20, bevel=m(2))
    k.mat("dark", 0x22282d, rough=0.6, metal=0.4)
    for x, r in ((-80, 26), (0, 22), (80, 22)):                 # pipe thread bores
        k.cyl(m(r - 10), m(4), at=(m(x), m(-40), m(-163)), axis="z", seg=24)
    for i, x in enumerate((25, 60, 95)):                        # marks П / С / Г on the sector
        k.box((m(4), m(14), m(2)), at=(m(x), m(36), m(141)))
    return k.finish(col)


def main_part(col):
    k = Kit("vr_main", "ВР483_Главная_часть_270.023")
    k.mat("body", 0x4f7f9c, rough=0.55, metal=0.3)
    k.cyl(m(100), m(18), at=(m(177), 0, 0), axis="x", seg=64, bevel=m(3))     # mating flange
    k.cyl(m(84), m(80), at=(m(226), m(-6), 0), axis="x", seg=64, bevel=m(6))  # body 37
    k.cyl(m(92), m(14), at=(m(272), m(-6), 0), axis="x", seg=64, bevel=m(3))  # body flange
    k.box((m(80), m(60), m(70)), at=(m(222), m(-80), 0), bevel=m(10))         # release-valve housing
    k.mat("cover", 0x5a8aa8, rough=0.5, metal=0.3)
    k.cyl(m(90), m(16), at=(m(287), m(-6), 0), axis="x", seg=64, bevel=m(4))  # cover 1
    k.cyl(m(60), m(16), at=(m(302), m(-6), 0), axis="x", r2=m(46), seg=48, bevel=m(3))
    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    bolt_ring(k, 8, 88, 188, phase=math.pi / 8)
    for i in range(8):                                          # cover bolts
        a = math.pi / 8 + i * math.pi / 4
        k.hexnut(m(7), m(7), at=(m(298), m(-6) + m(80) * math.sin(a), m(80) * math.cos(a)), axis="x")
    k.cyl(m(8), m(40), at=(m(222), m(-128), 0), axis="y", seg=16)             # release valve pusher
    k.ring(m(17), m(13), m(3.5), at=(m(222), m(-150), 0), axis="z", seg=24)   # ring for the pull chain
    k.mat("lever", 0xb33a2d, rough=0.5, metal=0.2)              # pull lever (поводок), red
    k.box((m(14), m(8), m(150)), at=(m(222), m(-158), m(70)), bevel=m(2))
    return k.finish(col)


def line_part(col):
    k = Kit("vr_line", "ВР483_Магистральная_часть_483.010")
    k.mat("body", 0x4f7f9c, rough=0.55, metal=0.3)
    k.cyl(m(100), m(18), at=(m(-177), 0, 0), axis="x", seg=64, bevel=m(3))   # mating flange
    k.cyl(m(90), m(50), at=(m(-210), 0, 0), axis="x", seg=64, bevel=m(5))    # body 28
    k.cyl(m(118), m(16), at=(m(-243), 0, 0), axis="x", seg=72, bevel=m(4))   # diaphragm flange
    k.mat("cover", 0x5a8aa8, rough=0.5, metal=0.3)
    k.cyl(m(118), m(16), at=(m(-260), 0, 0), axis="x", seg=72, bevel=m(4))   # cover 25
    k.cyl(m(96), m(24), at=(m(-280), 0, 0), axis="x", r2=m(70), seg=64, bevel=m(4))
    k.cyl(m(40), m(24), at=(m(-302), 0, 0), axis="x", seg=40, bevel=m(3))    # mode-switch boss
    k.cyl(m(18), m(16), at=(m(-232), m(-96), m(40)), axis="y", seg=20, bevel=m(1.5))   # atm. plug boss
    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    bolt_ring(k, 8, 88, -188, phase=math.pi / 8)
    for i in range(12):                                         # diaphragm cover bolts
        a = math.pi / 12 + i * math.pi / 6
        k.hexnut(m(7), m(7), at=(m(-272), m(108) * math.sin(a), m(108) * math.cos(a)), axis="x")
        k.hexnut(m(7), m(7), at=(m(-231), m(108) * math.sin(a), m(108) * math.cos(a)), axis="x")
    k.hexnut(m(11), m(10), at=(m(-232), m(-109), m(40)), axis="y")            # atmospheric plug
    k.mat("handle", 0xd9a520, rough=0.45, metal=0.3)            # «Р/Г» handle 22
    k.cyl(m(16), m(14), at=(m(-321), 0, 0), axis="x", seg=24, bevel=m(1.5))
    k.box((m(14), m(16), m(120)), at=(m(-330), 0, m(36)), bevel=m(3))
    k.mat("dark", 0x22282d, rough=0.6, metal=0.4)
    for z in (-34, 34):                                         # marks Р and Г on the boss
        k.box((m(2), m(10), m(12)), at=(m(-314.5), m(28), m(z)))
    return k.finish(col)


def build(collection=None):
    return [reservoir(collection), main_part(collection), line_part(collection)]


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
