# Option Tuning Car Battle Spec-R — Track File Format (.BIN)

## Overview
Track files are stored in the `CS/` folder on disc. Each track has two variants:
- `*_A1.BIN` / `*_A2.BIN` — Layout variants: forward/reverse

The `.TIX` files alongside each `.BIN` contain the track textures.

## Track List
| File prefix | Track name | Type |
|---|---|---|
| `CIRCU_A1/A2` | Circuit | Circuit (type 0) |
| `EBISU_A3/A4` | Ebisu | Circuit (type 1) |
| `TOUGE_C1-C4` | Mountain/Touge | Touge (type 2/3) |
| `SHUTO_H1/H2` | Shuto Expressway | Wangan (type 4) |
| `WANGA_H3/H4` | Wangan | Wangan (type 4) |

---

## File Header (0x60 bytes)

```
Offset  Size  Description
0x00    4     File size in bytes
0x04    4     Offset to Section 0 (Track Config) = 0x60
0x08    4     Offset to Section 1
0x0c    4     Offset to Section 2
0x10    4     Offset to Section 3 (Packed Segment Data)
0x14    4     Offset to Section 4 (Geometry LOD 0)
0x18    4     Offset to Section 5 (Geometry LOD 1)
0x1c    4     Offset to Section 6 (Geometry LOD 2)
0x20    4     0 (unused)
0x24    4     0 (unused)
0x28    4     Offset to Section 9 (Object Definitions)
0x2c    4     0 (unused)
0x30    4     0 (unused)
0x34    4     Offset to Section 12 (Object Data)
0x38    4     Offset to Section 13 (Object Data 2)
0x3c    4     Offset to Section 14 (Segment Index Table)
0x40    4     Offset to Section 15 (Segment XYZ Coordinates)
0x44    4     Offset to Section 16 (Segment Width Data)
0x48    4     Offset to Section 17 (Segment Length Data)
0x4c    4     Offset to Section 18 (Segment Angle Data)
0x50    4     Offset to Section 19 (Segment Banking Data)
0x54    4     0 (unused)
0x58    4     0 (unused)
0x5c    4     0 (unused)
```

---

## Section 0 — Track Config (24 bytes)

```
Offset  Size  Description
0x00    2     Track type (0=Circuit, 1=Ebisu, 2/3=Touge, 4=Wangan)
0x02    2     Unknown
0x04    2     Segment count (N)
0x06    2     Unknown
0x08    2     Track width (left)   — e.g. 4000 units
0x0a    2     Track width (right)  — e.g. 4000 units
0x0c    2     Unknown
0x0e    2     Unknown
0x10    2     Unknown
0x12    2     Unknown
0x14    2     Unknown
0x16    2     Unknown
```

**CIRCU_A1 example:** type=3, seg_count=366, width=4000/4000

---

## Section 15 — Segment XYZ Coordinates
**Size:** (N+1) × 12 bytes

Each segment has a 3D centre-line position:
```c
struct TrackSegment {
    int32_t x;    // World X coordinate
    int32_t y;    // World Y coordinate (height)
    int32_t z;    // World Z coordinate
};
```

**CIRCU_A1 example (first 3 segments):**
```
Seg 0: X=71637  Y=-3660  Z=71132
Seg 1: X=72894  Y=-3616  Z=71141
Seg 2: X=74150  Y=-3572  Z=71152
```

The track is a **closed loop** — last segment connects back to first.

---

## Section 14 — Segment Index Table
**Size:** N × 2 bytes (uint16 per segment)

Maps each segment to an entry in the packed data table (Section 3).
Values are indices into Section 3.

---

## Section 3 — Packed Segment Data
**Size:** variable (more entries than segments — shared/reused data)

Each entry is a 32-bit packed value containing:
```
bits  6-10  → Track angle index 1  (used with g_TrackAngleTable)
bits 10-14  → Track angle index 2
bits 14-18  → Track slope index 1  (used with g_TrackSlopeTable)
bits 18-22  → Track slope index 2
bits 24-26  → Surface type (0-7)
                0 = Tarmac
                1 = Dirt/gravel
                2 = Grass
                (others unknown)
```

In C:
```c
uint32_t packed = g_PackedSegmentData[g_SegmentIndexTable[segIdx]];
uint16_t angle1  = g_TrackAngleTable[(packed & 0x780)  >> 6];
uint16_t angle2  = g_TrackAngleTable[(packed & 0x7800) >> 10];
uint16_t slope1  = g_TrackSlopeTable[(packed >> 0xe)   & 0x1e];
uint16_t slope2  = g_TrackSlopeTable[(packed >> 0x12)  & 0x1e];
uint8_t  surface = (packed >> 0x18) & 7;
```

---

## Sections 16-19 — Per-Segment Data
**Size each:** (N+2) × 2 bytes (uint16 per segment)

| Section | Description | CIRCU_A1 typical value |
|---|---|---|
| 16 | Road width per segment | ~2044 (decreases on narrow sections) |
| 17 | Segment length | ~2899 (distance to next segment) |
| 18 | Segment angle (signed) | ~-900 (heading direction) |
| 19 | Banking angle | 700 (positive = banked left) |

---

## Section 4/5/6 — Track Geometry LODs
Three levels of detail for track mesh rendering:
- Section 4: **LOD 0** (highest detail, close range) — largest
- Section 5: **LOD 1** (medium detail)
- Section 6: **LOD 2** (lowest detail, far range)

These contain the actual renderable polygons for the track surface, 
barriers, and roadside scenery. Format is a PS1 primitive list.

---

## Section 9 — Object Definitions
**Header:** 
```
Offset  Size  Description
0x00    4     Object count
0x04    4     Data size
```
Followed by object definition entries referencing positions along the track.

---

## Sections 12/13 — Object Data
Track-side objects (barriers, signs, cones, scenery).
Section 12 = primary objects, Section 13 = secondary objects.

---

## CIRCU_A1 vs CIRCU_A2 Comparison
| Property | CIRCU_A1 | CIRCU_A2 |
|---|---|---|
| File size | 710,160 bytes | 613,492 bytes |
| Segment count | 366 | 327 |
| Track width | 4000/4000 | different |

The two variants likely represent **forward and reverse** layouts of the same circuit.

---

## Notes
- All multi-byte values are **little-endian**
- Coordinates use a fixed-point integer system (units ~1mm based on track dimensions)
- The track is always a **closed loop** — segment[N] connects back to segment[0]
- Texture data is stored separately in the `.TIX` file