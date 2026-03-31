## Alignment (Italic Projection Method)

**Description**  
Advanced alignment tool for Glyphs using an italic-aware projection method.  
Instead of relying on unreliable bounding boxes, it computes alignment using real node geometry, ensuring visually correct results in both roman and italic masters.

Supports multiple alignment modes including global alignment, true width centering, and individual element centering.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* True alignment in italic masters (no bounding box errors)
* Uses geometric projection (italic-aware)
* Intersection-based center calculation
* Multi-sampling across multiple Y positions
* Intelligent fallback when intersections fail
* Automatically keeps the largest element fixed
* Moves the smaller component (e.g. crossbar)
* Supports current master or all masters
* Non-destructive (background is restored after execution)

---

## Core

* Temporary decomposition using background layer (safe context)
* Component → multi-path mapping
* Segment intersection with horizontal scanlines
* Multi-sample averaging for stability
* Global fallback projection when no intersections are found
* De-italicized coordinate system:

```
x' = x - y * tan(angle)
```

---

### Core Alignment

* True alignment in italic masters (no bounding box errors)
* Uses geometric projection (italic-aware)
* Works with paths and components simultaneously
* Global alignment using real geometry (not averaged centers)
* Supports all directions:
  * Up
  * Center Y
  * Down
  * Left
  * Center X
  * Right

---

### True Width Mode

Centers the glyph based on the **actual drawn width**, not bounding boxes.

* Detects overflow outside glyph width
* Uses projected coordinates for accuracy in italic
* Assigns **LSB and RSB directly**
* Matches professional spacing workflow

---

## Scope

* Components in selected glyph(s)
* Current master or all masters
* Automatically detects:

  * Reference shape (largest)
  * Target shape (smaller)

---

## Requirements

* Glyphs App 3.x
* Glyphs with components
* At least two components

---

## Usage

1. Select glyph(s)
2. Ensure components are present (e.g. base + accent/bar)
3. Choose alignment direction (**Center X** recommended)
4. Choose scope:

   * Current master
   * All masters
5. Run the script

---

## Notes

* Designed specifically for italic workflows
* Avoids common misalignment caused by skewed bounding boxes
* Works even when no nodes exist at the target height
* Handles complex outlines (multiple paths, serifs, etc.)
* Background layer is fully restored after execution

---

## Why this works

Instead of aligning bounding boxes, the script:

1. Projects outlines according to italic angle
2. Samples multiple horizontal slices
3. Computes real left/right extremes via intersections
4. Falls back to global projection when needed
5. Calculates a true visual center

This matches how alignment is perceived in professional type design.

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:
https://www.myfonts.com/collections/tipo-pepel-foundry
