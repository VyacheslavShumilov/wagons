"""Air distributor (воздухораспределитель) No. 483-000 of a freight car, three parts.

Site use: BRAKE_RIG in index.html, parts "vr_chamber", "vr_main", "vr_line" (not wired in yet).

Construction (Руководство ПКБ ЦВ № 922-2021, п. 2.1; РГУПС, ЛР № 7 «ВР 483: устройство»;
Асадченко, «Автоматические тормоза»), shape after the manufacturer's renders:
- two-chamber reservoir 295.001 (РК 6.0 L, ЗК 4.5 L): a tall cast box under a wide top plate
  that bolts to the frame bracket with four vertical M20 bolts in cast bosses; the brake pipe,
  auxiliary reservoir and brake cylinder are connected by three unions on its front face;
  the load-mode switch shaft comes out of the front face (handle removed on cars with
  an autoregime); round flange for the main part on one side, square flange for the line part
  on the other;
- main part 270.023: mating flange, waisted body 37 with a plugged boss on top, cover 1 on four
  bolts with the release valve cap at the bottom and its brass pusher (поводок) pointing down;
- line part 483.010: square flange, body 28 with a plugged boss, big round flange to the conical
  cover 25 that ends in the boss of the «Р/Г» release-mode switch with crank handle 22.
Overall sizes are not given in the sources; proportions follow the renders (reservoir ≈ 400 mm high).

Origin = centre of the reservoir. Local axes as on the site: x along the car, the line part
towards -x and the main part towards +x, y up, z across (pipe unions on the +z face).
"""
import math
try:
    from wagonkit import Kit, site_collection, sd_rrect, outline
except ImportError:          # pasted after wagonkit.py into a single script
    pass

OUT = "air_distributor_483.glb"
YP = 20          # height of the axis of the main and line parts


def m(v):
    return v * 0.001


def plate(k, w, h, r, depth, at, axis, bevel):
    """Rounded rectangular plate (w x h in the plate's own plane)."""
    k.prism([(m(a), m(b)) for a, b in outline(sd_rrect(0, 0, w, h, r), (-w / 2 - 6, -h / 2 - 6, w / 2 + 6, h / 2 + 6), 2)],
            m(depth), at=tuple(m(v) for v in at), axis=axis, bevel=m(bevel))


def reservoir(col):
    k = Kit("vr_chamber", "ВР483_Резервуар_295.001")
    k.mat("body", 0x3e6e8c, rough=0.65, metal=0.25)
    # tall cast box: x 230 (along the car), z 230, y -200..+170
    plate(k, 230, 370, 26, 230, (0, -15, 0), "z", 6)
    plate(k, 250, 300, 20, 30, (0, 185, 0), "y", 6)              # top plate to the frame bracket (x 250, z 300)
    for sx in (1, -1):                                            # vertical M20 bolt bosses, front and back
        for sz in (1, -1):
            k.ring(m(24), m(11), m(140), at=(sx * m(70), m(130), sz * m(126)), axis="y", seg=28, bevel=m(3))
            k.box((m(30), m(140), m(16)), at=(sx * m(70), m(130), sz * m(114)), bevel=m(3))
    k.cyl(m(100), m(10), at=(m(120), m(YP), 0), axis="x", seg=64, bevel=m(2))      # flange for the main part
    plate(k, 190, 190, 24, 10, (-120, YP, 0), "x", 2)             # flange for the line part
    for y in (140, -130):                                         # round cast pads (chamber plugs)
        k.cyl(m(28), m(6), at=(m(118), m(y), 0), axis="x", seg=40, bevel=m(1.5))
        k.cyl(m(28), m(6), at=(m(-118), m(y), 0), axis="x", seg=40, bevel=m(1.5))
    k.cyl(m(18), m(14), at=(m(10), m(40), m(119)), axis="z", seg=24, bevel=m(2))   # load-mode switch boss
    for x, y in ((-55, -60), (5, -80), (65, -100)):               # union bosses on the front face
        k.cyl(m(26), m(10), at=(m(x), m(y), m(119)), axis="z", seg=32, bevel=m(2))

    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    for sx in (1, -1):                                            # M20 bolts with crown nuts
        for sz in (1, -1):
            k.hexnut(m(16), m(13), at=(sx * m(70), m(207), sz * m(126)), axis="y")
            k.cyl(m(10), m(175), at=(sx * m(70), m(130), sz * m(126)), axis="y", seg=16)
            k.hexnut(m(16), m(16), at=(sx * m(70), m(52), sz * m(126)), axis="y")
    k.mat("dark", 0x1d2226, rough=0.55, metal=0.4)                 # unions, nipples, switch shaft
    for x, y in ((-55, -60), (5, -80), (65, -100)):
        k.hexnut(m(23), m(32), at=(m(x), m(y), m(140)), axis="z", bevel=m(2))
        k.cyl(m(14), m(34), at=(m(x), m(y), m(172)), axis="z", seg=24, bevel=m(2))
    k.cyl(m(8), m(32), at=(m(10), m(40), m(140)), axis="z", seg=16)
    k.box((m(12), m(12), m(10)), at=(m(10), m(40), m(158)), bevel=m(1))
    return k.finish(col)


def main_part(col):
    k = Kit("vr_main", "ВР483_Главная_часть_270.023")
    k.mat("body", 0x4f7f9c, rough=0.6, metal=0.3)
    k.cyl(m(95), m(16), at=(m(133), m(YP), 0), axis="x", seg=64, bevel=m(3))       # mating flange
    k.cyl(m(76), m(36), at=(m(159), m(YP), 0), axis="x", r2=m(60), seg=56, bevel=m(2))   # waisted body 37
    k.cyl(m(60), m(26), at=(m(190), m(YP), 0), axis="x", r2=m(80), seg=56, bevel=m(2))
    k.cyl(m(22), m(56), at=(m(176), m(YP + 76), 0), axis="y", seg=28, bevel=m(3))  # boss with plug
    k.cyl(m(92), m(14), at=(m(210), m(YP), 0), axis="x", seg=64, bevel=m(3))       # body flange
    k.mat("cover", 0x5a8aa8, rough=0.55, metal=0.3)
    k.cyl(m(88), m(34), at=(m(234), m(YP), 0), axis="x", seg=64, bevel=m(9))       # cover 1
    k.box((m(40), m(56), m(60)), at=(m(254), m(YP - 52), 0), bevel=m(8))           # release valve cap
    k.cyl(m(26), m(54), at=(m(270), m(YP - 58), 0), axis="y", seg=32, bevel=m(4))
    k.cyl(m(26), m(10), at=(m(270), m(YP - 26), 0), axis="y", r2=m(16), seg=32)
    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    for i in range(4):
        a = math.pi / 4 + i * math.pi / 2
        y, z = m(YP) + m(84) * math.sin(a), m(84) * math.cos(a)
        k.hexnut(m(10), m(9), at=(m(146), y, z), axis="x")                          # flange nuts
        k.hexnut(m(10), m(9), at=(m(221), y, z), axis="x")                          # cover nuts
    k.mat("dark", 0x1d2226, rough=0.55, metal=0.4)
    k.hexnut(m(19), m(14), at=(m(176), m(YP + 110), 0), axis="y")                  # plug
    k.mat("brass", 0xc9b27a, rough=0.35, metal=0.8)
    k.cyl(m(6), m(80), at=(m(270), m(YP - 125), 0), axis="y", seg=16)              # release valve pusher
    k.ring(m(16), m(12), m(3.5), at=(m(270), m(YP - 172), 0), axis="z", seg=24)    # ring for the chain
    return k.finish(col)


def line_part(col):
    k = Kit("vr_line", "ВР483_Магистральная_часть_483.010")
    k.mat("body", 0x4f7f9c, rough=0.6, metal=0.3)
    plate(k, 186, 186, 24, 16, (-133, YP, 0), "x", 3)            # square flange of body 28
    k.cyl(m(56), m(60), at=(m(-171), m(YP), 0), axis="x", seg=48, bevel=m(4))      # body
    for y in (62, -62):                                           # cast air channels
        k.cyl(m(16), m(62), at=(m(-171), m(YP + y), m(10)), axis="x", seg=24, bevel=m(3))
    k.box((m(60), m(150), m(26)), at=(m(-171), m(YP), m(-30)), bevel=m(6))        # web
    k.cyl(m(20), m(44), at=(m(-160), m(YP + 72), 0), axis="y", seg=28, bevel=m(3)) # boss with plug
    k.cyl(m(118), m(30), at=(m(-216), m(YP), 0), axis="x", seg=72, bevel=m(5))     # diaphragm flange
    k.mat("cover", 0x5a8aa8, rough=0.55, metal=0.3)
    k.cyl(m(96), m(95), at=(m(-278), m(YP), 0), axis="x", r2=m(34), seg=64, bevel=m(3))  # conical cover 25
    k.cyl(m(30), m(46), at=(m(-345), m(YP), 0), axis="x", seg=40, bevel=m(4))      # switch boss
    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    for sy in (1, -1):                                            # square flange bolts
        for sz in (1, -1):
            k.hexnut(m(10), m(9), at=(m(-145), m(YP) + sy * m(70), sz * m(70)), axis="x")
    for i in range(6):                                            # diaphragm flange bolts, both sides
        a = math.pi / 2 + i * math.pi / 3
        y, z = m(YP) + m(106) * math.sin(a), m(106) * math.cos(a)
        k.hexnut(m(10), m(9), at=(m(-197), y, z), axis="x")
        k.hexnut(m(10), m(9), at=(m(-235), y, z), axis="x")
        k.cyl(m(5.5), m(54), at=(m(-216), y, z), axis="x", seg=12)
    k.mat("dark", 0x1d2226, rough=0.55, metal=0.4)
    k.hexnut(m(19), m(14), at=(m(-160), m(YP + 100), 0), axis="y")                 # plug
    k.mat("brass", 0xc9b27a, rough=0.35, metal=0.8)                 # «Р/Г» crank handle 22
    k.cyl(m(7), m(30), at=(m(-380), m(YP), 0), axis="x", seg=16)
    k.box((m(12), m(70), m(14)), at=(m(-395), m(YP - 30), 0), bevel=m(3))
    k.cyl(m(8), m(50), at=(m(-395), m(YP - 62), m(25)), axis="z", seg=20, bevel=m(2))
    return k.finish(col)


def build(collection=None):
    return [reservoir(collection), main_part(collection), line_part(collection)]


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
