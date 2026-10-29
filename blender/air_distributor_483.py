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
Overall sizes are not given in the sources; proportions follow the renders (reservoir ≈ 430 mm high
with its top plate). The main and line parts sit off-centre on the two mating faces, the
unions and the switch shaft on a raised pad on the main-part face, to the right of the main
part when you face it (as on the render).

Origin = centre of the reservoir. Local axes as on the site: x along the car, the line part
towards -x and the main part towards +x, y up, z across (pipe unions on the +z face).
"""
import math
try:
    from wagonkit import Kit, site_collection, sd_rrect, outline
except ImportError:          # pasted after wagonkit.py into a single script
    pass

OUT = "air_distributor_483.glb"
HX = 100         # half size of the reservoir along x: its two mating faces are at x = ±HX
YP, ZP = -25, 40    # axis of the main and line parts on those faces (off-centre, as on the renders)


def m(v):
    return v * 0.001


def rr(k, w, h, r, depth, at, axis, bevel):
    """Rounded rectangular plate (w x h in the plate's own plane, see Kit.prism)."""
    k.prism([(m(a), m(b)) for a, b in outline(sd_rrect(0, 0, w, h, r), (-w / 2 - 6, -h / 2 - 6, w / 2 + 6, h / 2 + 6), 2)],
            m(depth), at=tuple(m(v) for v in at), axis=axis, bevel=m(bevel))


def reservoir(col):
    k = Kit("vr_chamber", "ВР483_Резервуар_295.001")
    k.mat("body", 0x3e6e8c, rough=0.65, metal=0.25)
    rr(k, 2 * HX, 230, 30, 405, (0, -12.5, 0), "y", 12)          # tall cast body, y -215..+190
    rr(k, 300, 300, 24, 26, (0, 203, 0), "y", 6)                 # top plate to the frame bracket
    rr(k, 300, 230, 22, 22, (0, 80, 0), "y", 5)                  # shelf under the bolt channels
    for sx in (1, -1):                                            # open channels for the M20 bolts:
        for sz in (1, -1):                                        # a pair of ribs around each bolt
            for dz in (-30, 30):
                k.box((m(50), m(100), m(14)), at=(sx * m(HX + 25), m(140), m(sz * 62 + dz)), bevel=m(4))
    k.cyl(m(85), m(8), at=(m(HX + 4), m(YP), m(ZP)), axis="x", seg=64, bevel=m(2))       # mating pad, main part
    rr(k, 180, 180, 22, 8, (-HX - 4, YP, ZP), "x", 2)                                     # mating pad, line part
    for y in (135, -165):                                         # round cast pockets above and below
        k.cyl(m(26), m(5), at=(m(HX + 2), m(y), m(ZP)), axis="x", seg=40, bevel=m(1.5))
        k.cyl(m(26), m(5), at=(m(-HX - 2), m(y), m(ZP)), axis="x", seg=40, bevel=m(1.5))
    rr(k, 80, 150, 16, 18, (HX + 9, -100, -80), "x", 4)           # raised pad: switch shaft and unions
    k.cyl(m(17), m(14), at=(m(HX + 22), m(20), m(-85)), axis="x", seg=24, bevel=m(2))      # switch boss

    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    for sx in (1, -1):                                            # M20 bolts: head on the plate, nut under the shelf
        for sz in (1, -1):
            x, z = sx * m(HX + 25), sz * m(62)
            k.hexnut(m(16), m(13), at=(x, m(223), z), axis="y")
            k.cyl(m(10), m(180), at=(x, m(140), z), axis="y", seg=16)
            k.hexnut(m(16), m(16), at=(x, m(61), z), axis="y")
    k.mat("dark", 0x1d2226, rough=0.55, metal=0.4)                 # unions ТМ, ЗР, ТЦ and the switch shaft
    for y, z in ((-150, -58), (-110, -83), (-70, -106)):
        k.hexnut(m(20), m(30), at=(m(HX + 33), m(y), m(z)), axis="x", bevel=m(2))
        k.cyl(m(13), m(32), at=(m(HX + 64), m(y), m(z)), axis="x", seg=24, bevel=m(2))
    k.cyl(m(8), m(34), at=(m(HX + 44), m(20), m(-85)), axis="x", seg=16)
    k.box((m(10), m(12), m(12)), at=(m(HX + 63), m(20), m(-85)), bevel=m(1))
    return k.finish(col)


def main_part(col):
    k = Kit("vr_main", "ВР483_Главная_часть_270.023")
    x0 = HX + 8
    k.mat("body", 0x4f7f9c, rough=0.6, metal=0.3)
    k.cyl(m(85), m(16), at=(m(x0 + 8), m(YP), m(ZP)), axis="x", seg=64, bevel=m(3))          # mating flange
    k.cyl(m(68), m(60), at=(m(x0 + 46), m(YP), m(ZP)), axis="x", seg=56, bevel=m(6))         # body 37
    k.cyl(m(22), m(80), at=(m(x0 + 52), m(YP - 40), m(ZP - 30)), axis="x", seg=28, bevel=m(4))  # cast channel
    k.cyl(m(24), m(80), at=(m(x0 + 44), m(YP + 88), m(ZP)), axis="y", seg=28, bevel=m(4))    # boss with plug
    k.cyl(m(80), m(12), at=(m(x0 + 82), m(YP), m(ZP)), axis="x", seg=64, bevel=m(3))         # body flange
    k.mat("cover", 0x5a8aa8, rough=0.55, metal=0.3)
    k.cyl(m(98), m(54), at=(m(x0 + 115), m(YP), m(ZP)), axis="x", seg=72, bevel=m(14))       # cover 1 (drum)
    k.box((m(34), m(64), m(50)), at=(m(x0 + 150), m(YP - 58), m(ZP + 50)), bevel=m(10))      # release valve cap
    k.cyl(m(30), m(76), at=(m(x0 + 166), m(YP - 58), m(ZP + 50)), axis="y", seg=36, bevel=m(4))
    k.cyl(m(30), m(12), at=(m(x0 + 166), m(YP - 14), m(ZP + 50)), axis="y", r2=m(18), seg=36)
    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    for i in range(4):
        a = math.pi / 4 + i * math.pi / 2
        y, z = m(YP) + m(73) * math.sin(a), m(ZP) + m(73) * math.cos(a)
        k.hexnut(m(10), m(9), at=(m(x0 + 20), y, z), axis="x")                                # flange nuts
        y, z = m(YP) + m(84) * math.sin(a), m(ZP) + m(84) * math.cos(a)
        k.hexnut(m(10), m(9), at=(m(x0 + 146), y, z), axis="x")                               # cover nuts
    k.cyl(m(5), m(3), at=(m(x0 + 143), m(YP + 30), m(ZP - 12)), axis="x", seg=16)             # lead seal
    k.cyl(m(0.8), m(55), at=(m(x0 + 144), m(YP + 58), m(ZP - 14)), axis="y", seg=6)           # seal wire
    k.mat("dark", 0x1d2226, rough=0.55, metal=0.4)
    k.hexnut(m(20), m(16), at=(m(x0 + 44), m(YP + 136), m(ZP)), axis="y")                     # plug
    k.cyl(m(7), m(2), at=(m(x0 + 166), m(YP - 7), m(ZP + 50)), axis="y", seg=16)              # vent hole
    k.mat("brass", 0xc9b27a, rough=0.35, metal=0.8)
    k.cyl(m(10), m(4), at=(m(x0 + 166), m(YP - 98), m(ZP + 50)), axis="y", seg=20)            # washer
    k.cyl(m(6), m(80), at=(m(x0 + 166), m(YP - 136), m(ZP + 50)), axis="y", seg=16)           # release pusher
    return k.finish(col)


def line_part(col):
    k = Kit("vr_line", "ВР483_Магистральная_часть_483.010")
    x0 = -HX - 8
    k.mat("body", 0x4f7f9c, rough=0.6, metal=0.3)
    rr(k, 186, 186, 24, 16, (x0 - 8, YP, ZP), "x", 3)                                       # square flange of body 28
    k.cyl(m(56), m(60), at=(m(x0 - 46), m(YP), m(ZP)), axis="x", seg=48, bevel=m(4))         # body
    for y in (62, -62):                                                                       # cast air channels
        k.cyl(m(16), m(62), at=(m(x0 - 46), m(YP + y), m(ZP + 10)), axis="x", seg=24, bevel=m(3))
    k.box((m(60), m(150), m(26)), at=(m(x0 - 46), m(YP), m(ZP - 30)), bevel=m(6))           # web
    k.cyl(m(20), m(44), at=(m(x0 - 35), m(YP + 72), m(ZP)), axis="y", seg=28, bevel=m(3))   # boss with plug
    k.cyl(m(118), m(30), at=(m(x0 - 91), m(YP), m(ZP)), axis="x", seg=72, bevel=m(5))       # diaphragm flange
    k.mat("cover", 0x5a8aa8, rough=0.55, metal=0.3)
    k.cyl(m(96), m(95), at=(m(x0 - 153), m(YP), m(ZP)), axis="x", r2=m(34), seg=64, bevel=m(3))  # conical cover 25
    k.cyl(m(30), m(46), at=(m(x0 - 220), m(YP), m(ZP)), axis="x", seg=40, bevel=m(4))       # switch boss
    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    for sy in (1, -1):                                                                        # square flange bolts
        for sz in (1, -1):
            k.hexnut(m(10), m(9), at=(m(x0 - 20), m(YP) + sy * m(70), m(ZP) + sz * m(70)), axis="x")
    for i in range(6):                                                                        # diaphragm flange bolts
        a = math.pi / 2 + i * math.pi / 3
        y, z = m(YP) + m(106) * math.sin(a), m(ZP) + m(106) * math.cos(a)
        k.hexnut(m(10), m(9), at=(m(x0 - 72), y, z), axis="x")
        k.hexnut(m(10), m(9), at=(m(x0 - 110), y, z), axis="x")
        k.cyl(m(5.5), m(54), at=(m(x0 - 91), y, z), axis="x", seg=12)
    k.mat("dark", 0x1d2226, rough=0.55, metal=0.4)
    k.hexnut(m(19), m(14), at=(m(x0 - 35), m(YP + 100), m(ZP)), axis="y")                   # plug
    k.mat("brass", 0xc9b27a, rough=0.35, metal=0.8)                                           # «Р/Г» crank handle 22
    k.cyl(m(7), m(30), at=(m(x0 - 255), m(YP), m(ZP)), axis="x", seg=16)
    k.box((m(12), m(70), m(14)), at=(m(x0 - 270), m(YP - 30), m(ZP)), bevel=m(3))
    k.cyl(m(8), m(50), at=(m(x0 - 270), m(YP - 62), m(ZP + 25)), axis="z", seg=20, bevel=m(2))
    return k.finish(col)


def build(collection=None):
    return [reservoir(collection), main_part(collection), line_part(collection)]


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
