"""Aggregate car (агрегатный вагон) of a refrigerator section, from the user's STL.

Source: sources/reefer_aggregate_car_model.stl - a whole-car scale model (netfabb, units mm,
152.9 x 27.9 x 44.7 mm, 77 435 triangles, body, underframe equipment, bogies and couplers in one
mesh). Scale taken as 1:112: it makes the wheel tread spacing ≈1590 mm (1520 gauge), body width
3.12 m and height above rail 5.0 m. The car is then 17.1 m over couplers, bogie centres 11.1 m.

Origin = centre of the car at rail level; x along the car, y up, z across (site axes).
Below 1.25 m above rail (bogies, underframe, equipment) is painted dark, the body light.
Site use: not wired in yet (part "aggregate_car").
"""
try:
    from wagonkit import Kit, site_collection, read_stl
except ImportError:          # pasted after wagonkit.py into a single script
    pass
import pathlib

PART = "aggregate_car"
OUT = "reefer_aggregate_car.glb"
STL_NAME = "sources/reefer_aggregate_car_model.stl"
STL_BYTES = None
S = 0.112                                   # STL mm -> site m at 1:112
X0, Y0, Z0 = 856.34, 3434.93, 585.23        # car centre (x, across) and rail level in the STL
ROWS = ((S, 0, 0, -S * X0), (0, 0, S, -S * Z0), (0, -S, 0, S * Y0), (0, 0, 0, 1))
SPLIT = Z0 + 1.25 / S                       # height in STL units where the body colour starts
DECIMATE = 0.5


def build(collection=None):
    data = STL_BYTES or (pathlib.Path(__file__).resolve().parent / STL_NAME).read_bytes()
    tris = read_stl(data)
    low = [t for t in tris if max(p[2] for p in t) < SPLIT]
    high = [t for t in tris if max(p[2] for p in t) >= SPLIT]
    k = Kit(PART, "Агрегатный_вагон_рефсекции")
    k.mat("under", 0x2f3438, rough=0.7, metal=0.3)
    k.stl(low, ROWS)
    k.mat("body", 0xd2cfc6, rough=0.55, metal=0.15)
    k.stl(high, ROWS)
    o = k.finish(collection, smooth_angle=35)
    d = o.modifiers.new("Decimate", "DECIMATE")
    d.ratio = DECIMATE
    return o


if __name__ == "__main__" or "__file__" not in globals():
    build(site_collection("Сайт_детали"))
