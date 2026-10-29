"""Load-sensing brake valve (грузовой авторежим) No. 265A-1.

Site use: BRAKE_RIG in index.html, part "autoreg" (not wired in yet).
Sizes follow the assembly drawing: overall 284 x 204 x 370 mm, the stop with its
hex nut comes 98 mm out of the body, two G 3/4 ports in the mounting flange.
Round damper chamber with a round bolted cover; the relay part is two round sections
(valve and piston) with gaskets, as on the manufacturer's render.

Origin = tip of the stop (упор 2), which rests on the support plate on the bogie.
Local axes as on the site: y up along the body, x from the body towards the relay part
and its mounting flange (which bolts to the bracket on the car frame), z across (204 mm).
"""
import math
try:
    from wagonkit import Kit, site_collection
except ImportError:          # pasted after wagonkit.py into a single script
    pass

PART = "autoreg"
OUT = "autoregime_265a1.glb"
MM = 0.001


def build(collection=None):
    k = Kit(PART, "Авторежим_265А-1")
    m = lambda v: v * MM

    # x: body axis 0, round damper chamber centred at +10, relay sections to the flange, port bosses to +200
    YU, RU = 306, 52          # upper valve section (axis height, radius)
    YL, RL = 222, 46          # lower piston section
    ang = [math.radians(a) for a in (40, 140, 220, 320)]

    # ---- body casting ------------------------------------------------------------
    k.mat("body", 0x3f5d73, rough=0.6, metal=0.3)
    k.cyl(m(42), m(181), at=(0, m(213.5), 0), axis="y", seg=48, bevel=m(3))        # main body Ø84
    k.cyl(m(36), m(26), at=(0, m(110), 0), axis="y", seg=48, bevel=m(2))           # lower shoulder
    k.cyl(m(42), m(24), at=(m(4), m(292), 0), axis="y", r2=m(72), seg=48)          # flare to the chamber
    k.cyl(m(88), m(52), at=(m(10), m(330), 0), axis="y", seg=64, bevel=m(6))       # round damper chamber
    k.cyl(m(94), m(10), at=(m(10), m(351), 0), axis="y", seg=64, bevel=m(3))       # chamber flange
    k.box((m(70), m(130), m(56)), at=(m(42), m(250), 0), bevel=m(10))              # web body -> relay part
    # relay part: two round sections joined by a web, each with its own flange
    for y, r in ((YU, RU), (YL, RL)):
        k.cyl(m(r), m(95), at=(m(102), m(y), 0), axis="x", seg=48, bevel=m(6))
        k.cyl(m(r + 6), m(12), at=(m(144), m(y), 0), axis="x", seg=48, bevel=m(3))
    k.box((m(95), m(84), m(64)), at=(m(102), m((YU + YL) / 2), 0), bevel=m(12))
    # mounting flange part: two round lobes with the port bosses, ears for the bracket bolts
    for y, r in ((YU, RU), (YL, RL)):
        k.cyl(m(r + 6), m(24), at=(m(164), m(y), 0), axis="x", seg=48, bevel=m(4))
        k.ring(m(22), m(12), m(24), at=(m(188), m(y), 0), axis="x", seg=32, bevel=m(2))   # G 3/4 boss
    k.box((m(24), m(84), m(80)), at=(m(164), m((YU + YL) / 2), 0), bevel=m(10))
    for s in (1, -1):
        k.box((m(18), m(40), m(70)), at=(m(166), m(290), s * m(80)), bevel=m(8))
        k.ring(m(26), m(11), m(18), at=(m(166), m(290), s * m(116)), axis="x", seg=32, bevel=m(2))
    # bolt lugs around both sections
    for y, r in ((YU, RU), (YL, RL)):
        for a in ang:
            k.cyl(m(10), m(46), at=(m(156), m(y) + m(r + 12) * math.sin(a), m(r + 12) * math.cos(a)),
                  axis="x", seg=16, bevel=m(2))
    # bosses of the two adjusting screws on the body (section Б-Б)
    for s in (1, -1):
        k.cyl(m(13), m(22), at=(m(20), m(228), s * m(40)), axis="z", seg=20, bevel=m(1.5))

    # ---- round cover of the chamber, stop sleeve, gaskets ----------------------------
    k.mat("cover", 0x56707f, rough=0.5, metal=0.35)
    k.cyl(m(102), m(8), at=(m(10), m(360), 0), axis="y", seg=64, bevel=m(2.5))
    k.cyl(m(70), m(6), at=(m(10), m(367), 0), axis="y", r2=m(62), seg=64, bevel=m(1.5))
    k.cyl(m(29), m(34), at=(0, m(81), 0), axis="y", seg=40, bevel=m(2))             # guide sleeve
    k.mat("gasket", 0xb8bec3, rough=0.7, metal=0.1)
    for y, r in ((YU, RU), (YL, RL)):
        k.cyl(m(r + 5.5), m(2.5), at=(m(151.2), m(y), 0), axis="x", seg=48)

    # ---- stop (упор), nut, fasteners --------------------------------------------
    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    k.hexnut(m(21), m(24), at=(0, m(52), 0), axis="y", bevel=m(1.5))                # lock nut
    k.cyl(m(22), m(30), at=(0, m(25), 0), axis="y", seg=32, bevel=m(1.5))          # stop body
    k.cyl(m(12), m(10), at=(0, m(5), 0), axis="y", r2=m(22), seg=32)                # rounded tip
    for i in range(8):                                                               # cover bolts on a circle
        a = math.pi / 8 + i * math.pi / 4
        k.hexnut(m(8), m(7), at=(m(10) + m(94) * math.cos(a), m(367.5), m(94) * math.sin(a)), axis="y")
    for y, r in ((YU, RU), (YL, RL)):                                                # section bolts
        for a in ang:
            k.hexnut(m(8), m(8), at=(m(183), m(y) + m(r + 12) * math.sin(a), m(r + 12) * math.cos(a)), axis="x")
            k.hexnut(m(8), m(8), at=(m(129), m(y) + m(r + 12) * math.sin(a), m(r + 12) * math.cos(a)), axis="x")
    for s in (1, -1):                                                                # adjusting screws
        k.hexnut(m(8), m(8), at=(m(20), m(228), s * m(55)), axis="z")
    k.mat("dark", 0x22282d, rough=0.6, metal=0.4)
    for s in (1, -1):                                                                # slot of the fork
        k.box((m(12), m(22), m(3)), at=(0, m(27), s * m(21.5)))
    for y in (YU, YL):                                                               # port bores
        k.cyl(m(12.5), m(4), at=(m(198), m(y), 0), axis="x", seg=24)

    return k.finish(collection)


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
