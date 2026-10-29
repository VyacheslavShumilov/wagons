"""Automatic coupler SA-3 (автосцепка СА-3): coupler body with the lock and the uncoupling chain.

Site use: part "coupler" (COUPLER_P, shared by all wagons) - not wired in yet.

Shape after the manufacturer's renders: hollow cast head with the coupling contour in plan
(large tooth, throat «зев», small tooth), the lock showing in the throat, ribbed windows on both
side walls, the stop («упор») on top that meets the striker casting, and a hollow rectangular
shank with a cylindrical end face and a vertical slot for the draft-gear key («клин»).
The coupling contour is standardised, but its exact sizes are not in the sources used here:
the proportions are taken from the renders (body ≈ 1100 mm long, head ≈ 340 x 340 mm).

Origin = on the coupler axis at the tip of the large tooth. Local axes as on the site:
x along the car with the head at +x (shank towards -x), y up, z across.
"""
import math
try:
    from wagonkit import Kit, site_collection
except ImportError:          # pasted after wagonkit.py into a single script
    pass

PART = "coupler"
OUT = "coupler_sa3.glb"

# plan contour of the head (x forward, z across), mm: large tooth on -z, throat, small tooth on +z
CONTOUR = [(-400, -160), (-180, -170), (-40, -150), (0, -118), (-8, -92), (-30, -62),
           (-175, -50), (-185, -40), (-185, 60), (-70, 68), (-52, 82), (-48, 110),
           (-60, 165), (-120, 172), (-400, 165)]


def m(v):
    return v * 0.001


def build(collection=None):
    k = Kit(PART, "Автосцепка_СА-3")
    k.mat("body", 0x5f666c, rough=0.5, metal=0.6)
    # head: teeth and throat at full contour (height 260), rear block around the lock pocket (taller)
    k.prism([(m(x), m(z)) for x, z in CONTOUR], m(260), axis="y", bevel=m(6))
    k.box((m(250), m(340), m(330)), at=(m(-275), m(-20), 0), bevel=m(14))
    k.box((m(150), m(50), m(240)), at=(m(-300), m(-205), 0), bevel=m(12))       # lock pocket bottom
    # stop on top of the head (meets the striker casting under compression)
    k.box((m(110), m(80), m(230)), at=(m(-345), m(185), 0), bevel=m(12))
    for dz in (-80, 80):
        k.box((m(70), m(60), m(26)), at=(m(-285), m(170), m(dz)), bevel=m(6))
    # flare from the head into the shank, shank with a cylindrical end face
    k.loft([(m(t), m(w), m(h), m(r)) for t, w, h, r in
            ((0, 320, 300, 46), (-70, 220, 220, 36), (-160, 124, 154, 22))],
           at=(m(-390), 0, 0), axis="x", bevel=m(3))
    k.loft([(0, m(124), m(154), m(22)), (m(-500), m(112), m(146), m(20))],
           at=(m(-550), 0, 0), axis="x", bevel=m(3))
    k.cyl(m(56), m(146), at=(m(-1050), 0, 0), axis="y", seg=48, bevel=m(8))
    for s in (1, -1):                                       # tapering ribs from the head onto the shank
        for y in (-40, 40):
            k.loft([(m(t), m(w), m(h), m(r)) for t, w, h, r in ((0, 14, 22, 5), (-150, 6, 10, 2))],
                   at=(m(-400), m(y), s * m(150)), axis="x", bevel=m(1))

    k.mat("recess", 0x25292c, rough=0.8, metal=0.3)        # cast windows in the side walls
    for s in (1, -1):
        for x0, x1 in ((-390, -300), (-288, -200)):
            for y0, y1 in ((12, 120), (-150, -14)):
                k.box((m(x1 - x0), m(y1 - y0), m(4)), at=(m((x0 + x1) / 2), m((y0 + y1) / 2), s * m(167)))
    k.box((m(4), m(220), m(90)), at=(m(-186), 0, m(5)))     # window for the lock and the lock-lift paw
    k.box((m(60), m(20), m(150)), at=(m(-345), m(206), 0))   # slot in the stop
    for y in (78, -78):                                     # vertical slot for the key, top and bottom
        k.box((m(130), m(4), m(36)), at=(m(-990), m(y), 0))

    k.mat("lock", 0x9aa3aa, rough=0.35, metal=0.75)         # lock showing in the throat
    k.box((m(80), m(200), m(18)), at=(m(-130), 0, m(60)), bevel=m(4))
    k.mat("signal", 0xc8322b, rough=0.6, metal=0.2)         # signal projection, painted red
    k.box((m(30), m(40), m(26)), at=(m(-250), m(-245), m(30)), bevel=m(4))

    k.mat("chain", 0x8b939a, rough=0.4, metal=0.8)          # uncoupling chain with the adjusting bolt
    x, y, z = -330, -232, -120
    for i in range(10):
        k.ring(m(11), m(6), m(4), at=(m(x - i * 6), m(y - i * 19), m(z)), axis="z" if i % 2 else "x", seg=16)
    k.cyl(m(5), m(60), at=(m(x - 63), m(y - 225), m(z)), axis="y", seg=12)
    k.hexnut(m(9), m(9), at=(m(x - 63), m(y - 255), m(z)), axis="y")
    return k.finish(collection)


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
