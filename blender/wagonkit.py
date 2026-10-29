"""Shared helpers for modelling site parts in Blender.

Every part script builds its geometry in SITE coordinates (the three.js scene of index.html):
  x - along the car, y - up, z - across the car; metres.
The helpers convert to Blender's Z-up space (Blender = (x, -z, y)), so the glTF exporter
(+Y up) writes the model back in exactly the site coordinates.

A part is one bmesh with a few materials. Faces get the material that was current when
they were created, so the builder reads like a list of primitives:

    k = Kit("brake_cylinder")
    k.mat("body", 0x3b4e5c, rough=.55, metal=.35)
    k.cyl(.178, .54, axis="x")                  # body
    k.mat("cover", 0x56707f)
    k.cyl(.205, .03, at=(.285, 0, 0), axis="x")  # front cover
    obj = k.finish()                            # mesh object with part="brake_cylinder"

Runs both inside the Blender app (Scripting tab / MCP) and headless with the `bpy` module.
"""
import math
import bmesh
import bpy
from mathutils import Matrix, Vector

SITE_TO_BLENDER = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
AXIS_ROT = {  # rotate a primitive whose own axis is Z so that it points along a site axis
    "x": Matrix.Rotation(math.pi / 2, 4, "Y"),
    "y": Matrix.Rotation(-math.pi / 2, 4, "X"),
    "z": Matrix.Identity(4),
}


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_color(h):
    return tuple(srgb_to_linear(((h >> s) & 255) / 255) for s in (16, 8, 0)) + (1.0,)


class Kit:
    def __init__(self, part, name=None):
        self.part = part
        self.name = name or part
        self.bm = bmesh.new()
        self.tag = self.bm.faces.layers.int.new("kit_done")
        self.mats = []
        self.cur = 0

    # ---- materials -------------------------------------------------------------
    def mat(self, name, color, rough=0.6, metal=0.3):
        full = f"{self.name}_{name}"
        m = bpy.data.materials.get(full) or bpy.data.materials.new(full)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = hex_color(color)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        m.diffuse_color = hex_color(color)
        if m not in self.mats:
            self.mats.append(m)
        self.cur = self.mats.index(m)
        return m

    # ---- placement -------------------------------------------------------------
    @staticmethod
    def place(at=(0, 0, 0), axis="z", rot=None, scale=None):
        """Matrix in site space: translate @ extra rotation @ axis rotation @ scale."""
        m = Matrix.Translation(Vector(at))
        if rot:
            m = m @ rot
        m = m @ AXIS_ROT[axis]
        if scale:
            m = m @ Matrix.Diagonal(Vector(scale + (1,)))
        return SITE_TO_BLENDER @ m

    def _claim(self, bevel_width=0.0, bevel_angle=60, segments=2):
        """Give the material to faces made since the last call and bevel their sharp edges."""
        new = [f for f in self.bm.faces if not f[self.tag]]
        if bevel_width > 0:
            fs = set(new)
            edges = [e for e in self.bm.edges
                     if len(e.link_faces) == 2 and all(f in fs for f in e.link_faces)
                     and e.calc_face_angle(0) > math.radians(bevel_angle)]
            if edges:
                bmesh.ops.bevel(self.bm, geom=edges, offset=bevel_width, segments=segments,
                                affect="EDGES", profile=0.5, clamp_overlap=True)
            new = [f for f in self.bm.faces if not f[self.tag]]
        for f in new:
            f[self.tag] = 1
            f.material_index = self.cur
            f.smooth = True

    # ---- primitives (site coordinates) -----------------------------------------
    def cyl(self, r, depth, at=(0, 0, 0), axis="z", r2=None, seg=32, bevel=0.0, rot=None):
        bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r, radius2=r if r2 is None else r2, depth=depth,
                              matrix=self.place(at, axis, rot))
        self._claim(bevel)

    def hexnut(self, r, depth, at=(0, 0, 0), axis="z", bevel=0.0015):
        self.cyl(r, depth, at, axis, seg=6, bevel=bevel)

    def box(self, size, at=(0, 0, 0), rot=None, bevel=0.0):
        bmesh.ops.create_cube(self.bm, size=1.0, matrix=self.place(at, "z", rot, tuple(size)))
        self._claim(bevel)

    def ring(self, r_out, r_in, depth, at=(0, 0, 0), axis="z", seg=48, bevel=0.0):
        """Washer / flange: a tube with closed ends."""
        verts = []
        mat = self.place(at, axis)
        for z in (-depth / 2, depth / 2):
            for r in (r_in, r_out):
                verts.append([self.bm.verts.new(mat @ Vector((r * math.cos(2 * math.pi * i / seg),
                                                              r * math.sin(2 * math.pi * i / seg), z)))
                              for i in range(seg)])
        (bi, bo, ti, to) = verts
        for i in range(seg):
            j = (i + 1) % seg
            self.bm.faces.new((bo[i], bo[j], to[j], to[i]))      # outer wall
            self.bm.faces.new((bi[j], bi[i], ti[i], ti[j]))      # inner wall
            self.bm.faces.new((to[i], to[j], ti[j], ti[i]))      # top
            self.bm.faces.new((bo[j], bo[i], bi[i], bi[j]))      # bottom
        self._claim(bevel)

    def dome(self, r, height, at=(0, 0, 0), axis="z", seg=48, rings=8):
        """Shallow spherical cap, open side at local z=0, apex at z=height."""
        mat = self.place(at, axis)
        rows = []
        for k in range(rings + 1):
            t = k / rings
            rr = r * math.cos(t * math.pi / 2)
            z = height * math.sin(t * math.pi / 2)
            if k == rings:
                rows.append([self.bm.verts.new(mat @ Vector((0, 0, height)))])
                break
            rows.append([self.bm.verts.new(mat @ Vector((rr * math.cos(2 * math.pi * i / seg),
                                                         rr * math.sin(2 * math.pi * i / seg), z)))
                         for i in range(seg)])
        for k in range(rings):
            a, b = rows[k], rows[k + 1]
            for i in range(seg):
                j = (i + 1) % seg
                if len(b) == 1:
                    self.bm.faces.new((a[i], a[j], b[0]))
                else:
                    self.bm.faces.new((a[i], a[j], b[j], b[i]))
        self._claim()

    def bolt_circle(self, n, radius, r_head, depth, x, phase=0.0):
        """Hex bolt heads on a flange face square to the site x axis, centred on y=z=0."""
        for i in range(n):
            a = phase + 2 * math.pi * i / n
            self.hexnut(r_head, depth, at=(x, radius * math.cos(a), radius * math.sin(a)), axis="x")

    # ---- result -----------------------------------------------------------------
    def finish(self, collection=None, smooth_angle=50):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        old = bpy.data.objects.get(self.name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        if "kit_done" in me.attributes:
            me.attributes.remove(me.attributes["kit_done"])
        me.set_sharp_from_angle(angle=math.radians(smooth_angle))
        for m in self.mats:
            me.materials.append(m)
        obj = bpy.data.objects.new(self.name, me)
        obj["part"] = self.part            # exported to glTF extras -> three.js userData.part
        (collection or bpy.context.scene.collection).objects.link(obj)
        return obj


def site_collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def export_glb(objects, path):
    """Write the given objects (and nothing else) to a .glb in site coordinates."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True,
                              export_extras=True, export_yup=True, export_apply=True,
                              export_texcoords=False, export_cameras=False, export_lights=False,
                              export_animations=False)
