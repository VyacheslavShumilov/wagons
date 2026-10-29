"""Load-sensing brake valve (грузовой авторежим) No. 265A-1.

Site use: BRAKE_RIG in index.html, part "autoreg" (not wired in yet).
Sizes follow the assembly drawing: overall 284 x 204 x 370 mm, the stop with its
hex nut comes 98 mm out of the body, two G 3/4 ports in the mounting flange.

Origin = tip of the stop (упор 2), which rests on the support plate on the bogie.
Local axes as on the site: y up along the body, x from the body towards the relay part
and its mounting flange (which bolts to the bracket on the car frame), z across (204 mm).
"""
import math
from mathutils import Matrix
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

    # ---- body casting: damper chamber on top, vertical body, relay housing, flange
    k.mat("body", 0x3f5d73, rough=0.6, metal=0.3)
    k.cyl(m(46), m(190), at=(0, m(205), 0), axis="y", seg=48, bevel=m(3))          # main body Ø92
    k.cyl(m(39), m(26), at=(0, m(110), 0), axis="y", seg=48, bevel=m(2))           # lower shoulder Ø78
    k.cyl(m(46), m(30), at=(0, m(312), 0), axis="y", r2=m(66), seg=48)             # flare to the chamber
    k.box((m(176), m(52), m(176)), at=(m(18), m(330), 0), bevel=m(8))              # damper chamber
    k.box((m(100), m(175), m(140)), at=(m(95), m(232), 0), bevel=m(8))             # relay housing
    k.cyl(m(50), m(90), at=(m(100), m(275), 0), axis="x", seg=40, bevel=m(3))      # upper valve chamber
    k.cyl(m(44), m(90), at=(m(100), m(175), 0), axis="x", seg=40, bevel=m(3))      # lower piston chamber
    # mounting flange with two ears (holes for the bracket bolts)
    k.box((m(18), m(215), m(170)), at=(m(150), m(232), 0), bevel=m(4))
    for s in (1, -1):
        k.box((m(18), m(56), m(50)), at=(m(150), m(272), s * m(100)), bevel=m(3))
        k.ring(m(28), m(11), m(18), at=(m(150), m(272), s * m(118)), axis="x", seg=32, bevel=m(2))
        # gussets from the body to the ears
        k.box((m(70), m(110), m(10)), at=(m(105), m(250), s * m(58)),
              rot=Matrix.Rotation(s * 0.35, 4, "X"), bevel=m(2))
    # bosses of the G 3/4 ports on the flange face
    for y in (210, 300):
        k.ring(m(24), m(13), m(10), at=(m(164), m(y), 0), axis="x", seg=32, bevel=m(1.5))
    # bosses of the two adjusting screws on the body (section Б-Б)
    for s in (1, -1):
        k.cyl(m(13), m(22), at=(m(20), m(228), s * m(40)), axis="z", seg=20, bevel=m(1.5))

    # ---- cover of the damper chamber, stop sleeve -------------------------------
    k.mat("cover", 0x56707f, rough=0.5, metal=0.35)
    k.box((m(184), m(8), m(204)), at=(m(18), m(360), 0), bevel=m(2))
    k.cyl(m(29), m(34), at=(0, m(81), 0), axis="y", seg=40, bevel=m(2))            # guide sleeve

    # ---- stop (упор), nut, fasteners --------------------------------------------
    k.mat("steel", 0x9aa3aa, rough=0.35, metal=0.75)
    k.hexnut(m(21), m(24), at=(0, m(52), 0), axis="y", bevel=m(1.5))                # lock nut
    k.cyl(m(22), m(30), at=(0, m(25), 0), axis="y", seg=32, bevel=m(1.5))          # stop body
    k.cyl(m(12), m(10), at=(0, m(5), 0), axis="y", r2=m(22), seg=32)                # rounded tip
    k.mat("dark", 0x22282d, rough=0.6, metal=0.4)
    for s in (1, -1):                                                                # slot of the fork
        k.box((m(12), m(22), m(3)), at=(0, m(27), s * m(21.5)))
    for s in (1, -1):                                                                # cover bolts 2x4
        for z in (-75, -25, 25, 75):
            k.hexnut(m(8), m(7), at=(m(18 + s * 80), m(367.5), m(z)), axis="y")
    for z in (-60, 60):                                                              # flange bolts
        for y in (165, 300):
            k.hexnut(m(9), m(8), at=(m(163), m(y), m(z)), axis="x")
    for s in (1, -1):                                                                # adjusting screws
        k.hexnut(m(8), m(8), at=(m(20), m(228), s * m(55)), axis="z")
    for y in (210, 300):                                                             # port bores
        k.cyl(m(12.5), m(4), at=(m(160), m(y), 0), axis="x", seg=24)
    k.hexnut(m(9), m(8), at=(m(-48), m(322), m(60)), axis="x")                       # drain plug

    return k.finish(collection)


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
