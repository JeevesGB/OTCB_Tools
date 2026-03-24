#!/usr/bin/env python3
"""
MDT Model Extractor for Option Tuning Car Battle 1 (PS1)
Converts .MDT car model files to Wavefront .OBJ + .MTL

Usage:
    python mdt_to_obj.py <input.mdt> [output_name]

Output:
    <output_name>.obj       - Wavefront OBJ mesh
    <output_name>.mtl       - Material file (vertex colours + texpage refs)
    <output_name>_debug.txt - Full parse log

-- MDT FILE ARCHITECTURE (fully reverse engineered) --

  0x0000-0x000F  Main header (16 bytes)
                   [0x00] u32 file_id
                   [0x04] u32 = 12 (constant)
                   [0x08] u32 raw_block_count = 260 (size of block in s16 pairs)
                   [0x0C] u32 table_offset (VRAM texture table near EOF)

  0x0010-0x001B  Sub-header (12 bytes)
                   [0x10] u16 flags/index
                   [0x12] u16 param
                   [0x14] u16 bbox_x  (half-extents in 100-unit chunks)
                   [0x16] u16 bbox_y
                   [0x18] u16 bbox_z
                   [0x1A] u16 wheel_param

  0x001C-0x062F  Raw block (260 * 6 = 1560 bytes). Contains mixed data:
                   - Wheel geometry verts (small, indices 0-7, 48 bytes)
                   - 1D car profile curves (u16 height samples)
                   - Physics/performance parameters
                   - INLINE BODY VERTEX POOL (148 verts, 6 bytes each)
                     This pool is located immediately before the polygon data
                     at offset: 0x0630 - (body_pool_size * 6 + 4)
                     Body polygons reference this pool with local indices.

  0x0630+        Polygon data stream:
                   - Body quads/tris (reference the inline body pool)
                   - Wheel face sections (each preceded by their own inline pool)
                   - Shadow/LOD face sections

  near EOF       VRAM texture coordinate table

-- VERTEX POOL STRATEGY --

The body polygon section uses an inline vertex pool embedded WITHIN the
raw block at 0x001C. We find this pool by scanning backwards from the
polygon start (0x0630) to find a contiguous run of plausible XYZ s16 triplets.
All face indices in the body section are LOCAL to this pool.

Wheel sections have their own inline pools detected in the polygon stream.

-- POLYGON RECORD LAYOUTS (confirmed) --

  QUAD_TEX   (0C 0A 01 3D)  44 bytes
    [4]U0 [5]V0 [6]texpage [7]CLUT  [8]U1 [9]V1  [10-11]pad
    [12-19] VRAM ref  [20-35] 4×RGBA colour
    [36-43] 4×u16 vertex indices

  TRI_TEX    (09 08 01 35)  36 bytes
    [4]U0 [5]V0 [6]texpage [7]CLUT  [8]U1 [9]V1  [10-11]pad
    [12-15] VRAM ref  [16-27] 3×RGBA colour
    [28-35] 3×u16 vertex indices + u16 pad

  QUAD_WHEEL (09 07 01 2D)  32 bytes
    [20-23] RGBA colour (flat)  [24-31] 4×u16 vertex indices

  TRI_SMALL  (05 03 01 29 / 05 03 01 2B)  20 bytes
    [4-7] RGBA colour  [8-13] 3×u16 vertex indices

Tested with: Option Tuning Car Battle 1 (JAP PS1, 1997)
"""

import struct, sys, os, math

COORD_SCALE = 1000.0   # PS1 units; body verts confirmed plausible at this scale
POLY_START  = 0x0630   # Confirmed first polygon header address
RAW_BLOCK_START = 0x1C # Confirmed first vertex byte

def u16(d,o): return struct.unpack_from('<H',d,o)[0]
def s16(d,o): return struct.unpack_from('<h',d,o)[0]
def u32(d,o): return struct.unpack_from('<I',d,o)[0]


class MDTParser:

    QUAD_TEX    = (0x0C, 0x0A, 0x01, 0x3D)
    TRI_TEX     = (0x09, 0x08, 0x01, 0x35)
    QUAD_WHEEL  = (0x09, 0x07, 0x01, 0x2D)
    TRI_SMALL   = (0x05, 0x03, 0x01, 0x29)
    TRI_SMALL_B = (0x05, 0x03, 0x01, 0x2B)

    def __init__(self, data, debug=False):
        self.data     = data
        self.debug    = debug
        self.log      = []
        self.warnings = []
        self.all_verts   = []
        self.body_pool   = []
        self.body_base   = 0
        self.faces       = []
        self.materials   = {}

    def _log(self, m):
        if self.debug: self.log.append(m)

    # ------------------------------------------------------------------
    def parse_header(self):
        d = self.data
        self.file_id      = u32(d, 0x00)
        self.raw_count    = u32(d, 0x08)   # 260 for all cars
        self.table_offset = u32(d, 0x0C)
        self.bbox_x = u16(d, 0x14)
        self.bbox_y = u16(d, 0x16)
        self.bbox_z = u16(d, 0x18)
        self._log(f"File ID:      0x{self.file_id:08X}")
        self._log(f"Table offset: 0x{self.table_offset:04X}")
        self._log(f"BBox (×100u): {self.bbox_x} × {self.bbox_y} × {self.bbox_z}")

    # ------------------------------------------------------------------
    def _read_pool(self, offset, count):
        """Read count XYZ s16 triplets from offset."""
        d, v = self.data, []
        for i in range(count):
            o = offset + i * 6
            if o + 6 > len(d): break
            v.append((s16(d, o), s16(d, o+2), s16(d, o+4)))
        return v

    def _is_plausible_vert(self, x, y, z, limit=8192):
        return abs(x) < limit and abs(y) < limit and abs(z) < limit

    def find_body_pool(self):
        """
        The inline body vertex pool sits immediately before the polygon data
        at POLY_START=0x0630.  Its header is 4 bytes (u16 count + u16 flags),
        then count×6 bytes of s16 XYZ triplets.

        We find the pool by scanning backwards from POLY_START, testing
        how many consecutive plausible-geometry triplets fit before the header.
        The pool that allows the highest used face index to be valid wins.
        """
        d = self.data

        # From body face analysis: max used index ≈ 147
        # Try pool sizes 100-200 and pick the one with most valid geometry
        best = None
        best_score = -1

        for count in range(80, 210):
            pool_data_off = POLY_START - count * 6
            pool_hdr_off  = pool_data_off - 4

            if pool_hdr_off < RAW_BLOCK_START:
                continue

            # Check header bytes: u16 count must match, u16 flags reasonable
            hdr_count = u16(d, pool_hdr_off)
            if hdr_count != count:
                continue

            # Count how many valid triplets exist
            valid = 0
            for i in range(count):
                o = pool_data_off + i * 6
                x, y, z = s16(d,o), s16(d,o+2), s16(d,o+4)
                if self._is_plausible_vert(x, y, z, 4096):
                    valid += 1
                else:
                    break

            score = valid
            if score > best_score:
                best_score = score
                best = (count, pool_hdr_off, pool_data_off)

        if best:
            count, hdr_off, data_off = best
            self.body_pool = self._read_pool(data_off, count)
            self.body_base = len(self.all_verts)
            self.all_verts.extend(self.body_pool)
            self._log(f"Body pool: {count} verts @ 0x{hdr_off:04X}, base={self.body_base}")
            return True

        # Fallback: scan for longest plausible run just before 0x0630
        self._log("Body pool scan failed, trying fallback run detection")
        off = POLY_START - 6
        run = []
        while off >= RAW_BLOCK_START:
            x, y, z = s16(d,off), s16(d,off+2), s16(d,off+4)
            if self._is_plausible_vert(x, y, z, 4096):
                run.insert(0, (x,y,z))
                off -= 6
            else:
                break
        if run:
            self.body_pool = run
            self.body_base = len(self.all_verts)
            self.all_verts.extend(self.body_pool)
            self._log(f"Body pool (fallback): {len(run)} verts, base={self.body_base}")
            return True

        self.warnings.append("Could not locate body vertex pool")
        return False

    # ------------------------------------------------------------------
    def _col(self, d, o):  return (d[o], d[o+1], d[o+2])
    def _avg(self, cols):
        n = len(cols)
        return tuple(sum(c[i] for c in cols)//n for i in range(3))
    def _is_glass(self, cols):
        for r,g,b in cols:
            if r > 180 and g < 120 and b > 180: return True
        return False
    def _mat(self, colour, glass, texpage, idx):
        r,g,b = colour
        name = f"mat_{'glass_' if glass else ''}{r:02X}{g:02X}{b:02X}_{idx}"
        self.materials[name] = {'colour':colour, 'glass':glass, 'texpage':texpage}
        return name
    def _chk(self, pool, idx, note=""):
        if 0 <= idx < len(pool): return idx
        self.warnings.append(f"Index {idx} OOB (pool={len(pool)}) {note}")
        return 0

    # ------------------------------------------------------------------
    def _parse_quad_tex(self, off, pool, base, midx):
        d = self.data
        if off + 44 > len(d): return None, 4
        u0,v0   = d[off+4], d[off+5]
        texpage = d[off+6]
        u1,v1   = d[off+8], d[off+9]
        cols    = [self._col(d, off+20+i*4) for i in range(4)]
        li      = [self._chk(pool, u16(d,off+36+i*2), f"QUAD@{off:X}") for i in range(4)]
        gi      = [base + i for i in li]
        mat     = self._mat(self._avg(cols), self._is_glass(cols), texpage, midx)
        self._log(f"  QUAD @0x{off:04X} li={li} gi={gi} tp={texpage}")
        return {'type':'quad','local':li,'global':gi,'material':mat,
                'uv':[(u0/255.,1.-v0/255.),(u1/255.,1.-v1/255.)]}, 44

    def _parse_tri_tex(self, off, pool, base, midx):
        d = self.data
        if off + 36 > len(d): return None, 4
        u0,v0   = d[off+4], d[off+5]
        texpage = d[off+6]
        u1,v1   = d[off+8], d[off+9]
        cols    = [self._col(d, off+16+i*4) for i in range(3)]
        li      = [self._chk(pool, u16(d,off+28+i*2), f"TRI@{off:X}") for i in range(3)]
        gi      = [base + i for i in li]
        mat     = self._mat(self._avg(cols), self._is_glass(cols), texpage, midx)
        self._log(f"  TRI  @0x{off:04X} li={li} gi={gi} tp={texpage}")
        return {'type':'tri','local':li,'global':gi,'material':mat,
                'uv':[(u0/255.,1.-v0/255.),(u1/255.,1.-v1/255.)]}, 36

    def _parse_quad_wheel(self, off, pool, base, midx):
        d = self.data
        if off + 32 > len(d): return None, 4
        u0,v0   = d[off+4], d[off+5]
        texpage = d[off+6]
        col     = self._col(d, off+20)
        li      = [self._chk(pool, u16(d,off+24+i*2), f"WHL@{off:X}") for i in range(4)]
        gi      = [base + i for i in li]
        mat     = self._mat(col, False, texpage, midx)
        self._log(f"  WHLQ @0x{off:04X} li={li} gi={gi} tp={texpage}")
        return {'type':'quad','local':li,'global':gi,'material':mat,
                'uv':[(u0/255.,1.-v0/255.)]}, 32

    def _parse_tri_small(self, off, pool, base, midx):
        d = self.data
        if off + 20 > len(d): return None, 4
        col = self._col(d, off+4)
        li  = [self._chk(pool, u16(d,off+8+i*2), f"SML@{off:X}") for i in range(3)]
        gi  = [base + i for i in li]
        mat = self._mat(col, False, 0, midx)
        self._log(f"  SMLT @0x{off:04X} li={li} gi={gi}")
        return {'type':'tri','local':li,'global':gi,'material':mat,'uv':[]}, 20

    # ------------------------------------------------------------------
    def _try_inline_pool(self, off):
        """Detect an inline wheel/sub vertex pool at off."""
        d = self.data
        if off + 4 > len(d): return None, 0
        count = u16(d, off)
        if not (4 <= count <= 128): return None, 0
        h = (d[off], d[off+1], d[off+2], d[off+3])
        known = {self.QUAD_TEX, self.TRI_TEX, self.QUAD_WHEEL,
                 self.TRI_SMALL, self.TRI_SMALL_B}
        if h in known: return None, 0
        needed = off + 4 + count * 6
        if needed > len(d): return None, 0
        verts = []
        for i in range(min(count, 16)):
            vo = off + 4 + i*6
            x,y,z = s16(d,vo), s16(d,vo+2), s16(d,vo+4)
            if not self._is_plausible_vert(x, y, z, 8192):
                return None, 0
            verts.append((x,y,z))
        all_v = self._read_pool(off + 4, count)
        return all_v, 4 + count * 6

    # ------------------------------------------------------------------
    def parse_polygons(self):
        d    = self.data
        stop = min(self.table_offset, len(d))

        # Current pool starts as the body pool found earlier
        cur_pool = self.body_pool
        cur_base = self.body_base
        midx     = 0
        off      = POLY_START

        self._log(f"\nPoly scan: 0x{off:04X}–0x{stop:04X}")
        self._log(f"Starting with body pool: {len(cur_pool)} verts, base={cur_base}")

        while off < stop - 4:
            h = (d[off], d[off+1], d[off+2], d[off+3])

            if   h == self.QUAD_TEX:    face, sz = self._parse_quad_tex(off, cur_pool, cur_base, midx)
            elif h == self.TRI_TEX:     face, sz = self._parse_tri_tex(off, cur_pool, cur_base, midx)
            elif h == self.QUAD_WHEEL:  face, sz = self._parse_quad_wheel(off, cur_pool, cur_base, midx)
            elif h == self.TRI_SMALL:   face, sz = self._parse_tri_small(off, cur_pool, cur_base, midx)
            elif h == self.TRI_SMALL_B: face, sz = self._parse_tri_small(off, cur_pool, cur_base, midx)
            else:
                pool_v, pool_sz = self._try_inline_pool(off)
                if pool_v and pool_sz > 0:
                    new_base = len(self.all_verts)
                    self.all_verts.extend(pool_v)
                    cur_pool = pool_v
                    cur_base = new_base
                    self._log(f"  POOL @0x{off:04X}: {len(pool_v)} verts, base={new_base}")
                    off += pool_sz
                else:
                    off += 1
                continue

            if face:
                self.faces.append(face)
                midx += 1
            off += sz

        self._log(f"Faces: {len(self.faces)}, total verts: {len(self.all_verts)}")

    # ------------------------------------------------------------------
    def parse(self):
        self.parse_header()
        self.find_body_pool()
        self.parse_polygons()
        return len(self.all_verts), len(self.faces)


# ------------------------------------------------------------------
class OBJWriter:
    def __init__(self, parser, name):
        self.p = parser
        self.name = name

    def write_mtl(self, path):
        seen = set()
        with open(path, 'w') as f:
            f.write(f"# MTL: {self.name}\n# Option Tuning Car Battle 1 (PS1 1997)\n\n")
            for mn, mat in self.p.materials.items():
                if mn in seen: continue
                seen.add(mn)
                r,g,b  = mat['colour']
                rf,gf,bf = r/255., g/255., b/255.
                f.write(f"newmtl {mn}\n")
                f.write(f"Kd {rf:.4f} {gf:.4f} {bf:.4f}\n")
                f.write(f"Ka {rf*.2:.4f} {gf*.2:.4f} {bf*.2:.4f}\n")
                f.write(f"Ks 0.1 0.1 0.1\nNs 8.0\n")
                f.write(f"d {'0.4' if mat.get('glass') else '1.0'}\n")
                f.write(f"illum {'4' if mat.get('glass') else '2'}\n")
                tp = mat.get('texpage', 0)
                if tp > 0:
                    f.write(f"# texpage {tp} -> TIM_{tp:03d}.png\n")
                    f.write(f"map_Kd TIM_{tp:03d}.png\n")
                f.write("\n")

    def write_obj(self, obj_path, mtl_path):
        p = self.p
        with open(obj_path, 'w') as f:
            f.write(f"# OBJ: {self.name}\n# Option Tuning Car Battle 1 (PS1 1997)\n")
            f.write(f"# Verts: {len(p.all_verts)}  Faces: {len(p.faces)}\n\n")
            f.write(f"mtllib {os.path.basename(mtl_path)}\n\n")

            f.write("# Vertices\n")
            for x,y,z in p.all_verts:
                f.write(f"v {x/COORD_SCALE:.6f} {y/COORD_SCALE:.6f} {-z/COORD_SCALE:.6f}\n")

            f.write("\n# UV coordinates\n")
            for face in p.faces:
                for u,v in face.get('uv', []):
                    f.write(f"vt {u:.6f} {v:.6f}\n")

            f.write("\no car\n")
            cur_mat = None
            uv_idx  = 1

            for face in p.faces:
                mat = face['material']
                if mat != cur_mat:
                    f.write(f"usemtl {mat}\n")
                    cur_mat = mat

                gv  = [v+1 for v in face['global']]  # OBJ 1-based
                uvs = face.get('uv', [])
                nuv = len(uvs)

                if face['type'] == 'quad':
                    v0,v1,v2,v3 = gv
                    if nuv >= 2:
                        u0,u1 = uv_idx, uv_idx+1
                        f.write(f"f {v0}/{u0} {v2}/{u0} {v1}/{u1}\n")
                        f.write(f"f {v1}/{u1} {v2}/{u0} {v3}/{u1}\n")
                        uv_idx += nuv
                    else:
                        f.write(f"f {v0} {v2} {v1}\n")
                        f.write(f"f {v1} {v2} {v3}\n")
                else:
                    v0,v1,v2 = gv
                    if nuv >= 2:
                        u0,u1 = uv_idx, uv_idx+1
                        f.write(f"f {v0}/{u0} {v2}/{u0} {v1}/{u1}\n")
                        uv_idx += nuv
                    else:
                        f.write(f"f {v0} {v2} {v1}\n")


# ------------------------------------------------------------------
def write_debug(parser, path, src):
    with open(path, 'w') as f:
        f.write("=== MDT Parse Debug Log ===\n\n")
        f.write(f"Source:      {src}\n")
        f.write(f"File size:   {len(parser.data)} (0x{len(parser.data):X})\n")
        f.write(f"Body pool:   {len(parser.body_pool)} verts @ base {parser.body_base}\n")
        f.write(f"All verts:   {len(parser.all_verts)}\n")
        f.write(f"Faces:       {len(parser.faces)}\n")
        f.write(f"Materials:   {len(parser.materials)}\n\n")
        if parser.warnings:
            f.write(f"=== WARNINGS ({len(parser.warnings)}) ===\n")
            for w in parser.warnings: f.write(f"  ! {w}\n")
            f.write("\n")
        else:
            f.write("=== NO WARNINGS ===\n\n")
        f.write("=== LOG ===\n")
        for l in parser.log: f.write(l + "\n")
        f.write("\n=== BODY POOL VERTICES (first 30) ===\n")
        for i,(x,y,z) in enumerate(parser.body_pool[:30]):
            f.write(f"  [{i:03d}] ({x:7d},{y:7d},{z:7d})  "
                    f"-> ({x/COORD_SCALE:.3f}, {y/COORD_SCALE:.3f}, {z/COORD_SCALE:.3f})m\n")
        f.write("\n=== FACES (first 20) ===\n")
        for i,face in enumerate(parser.faces[:20]):
            f.write(f"  [{i:03d}] {face['type']:4s} "
                    f"local={face['local']} global={face['global']} "
                    f"mat={face['material']}\n")
        f.write("\n=== TEXTURE PAGES ===\n")
        pages = sorted(set(m['texpage'] for m in parser.materials.values() if m['texpage']>0))
        for pg in pages:
            n = sum(1 for m in parser.materials.values() if m['texpage']==pg)
            f.write(f"  page {pg:3d} -> TIM_{pg:03d}.png  ({n} faces)\n")


# ------------------------------------------------------------------
def convert(mdt_path, output_name=None):
    if not os.path.exists(mdt_path):
        print(f"Error: not found: {mdt_path}"); sys.exit(1)

    with open(mdt_path, 'rb') as f:
        data = bytearray(f.read())

    if output_name is None:
        output_name = os.path.splitext(os.path.basename(mdt_path))[0]

    obj_path   = output_name + ".obj"
    mtl_path   = output_name + ".mtl"
    debug_path = output_name + "_debug.txt"

    print(f"Reading:   {mdt_path}  ({len(data)} bytes)")
    parser = MDTParser(data, debug=True)
    verts, faces = parser.parse()
    wc = len(parser.warnings)

    print(f"Body pool: {len(parser.body_pool)} verts")
    print(f"All verts: {verts}")
    print(f"Faces:     {faces}")
    print(f"Materials: {len(parser.materials)}")
    print(f"Warnings:  {wc}  {'(see debug)' if wc else '✓ clean'}")

    OBJWriter(parser, output_name).write_obj(obj_path, mtl_path)
    OBJWriter(parser, output_name).write_mtl(mtl_path)
    write_debug(parser, debug_path, mdt_path)

    pages = sorted(set(m['texpage'] for m in parser.materials.values() if m['texpage']>0))
    print(f"\nTexture pages: {pages}")
    print(f"  Place TIM_NNN.png alongside the OBJ for textures")
    print(f"\nOutput: {obj_path}  {mtl_path}  {debug_path}")
    print(f"Blender: File > Import > Wavefront (.obj)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    convert(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)