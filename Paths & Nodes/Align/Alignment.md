## Alignment (Italic Projection Method)

**Description**
Aligns components horizontally using a true italic-aware projection method.
Instead of relying on bounding boxes, it computes alignment based on geometric intersections, ensuring visually correct results in italic masters.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* True alignment in italic masters (no bounding box errors)
* Uses geometric projection (italic-aware)
* Intersection-based center calculation
* Automatically keeps the largest element fixed
* Moves the smaller component (e.g. crossbar)
* Supports current master or all masters
* Works directly with components (non-destructive)

---

## Core

* Temporary decomposition (background layer)
* Component ↔ path mapping
* Segment intersection with horizontal scanline
* De-italicized coordinate system:

  * `x' = x - y * tan(angle)`
* Center calculation based on real geometry

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
* At least two elements to align

---

## Usage

1. Select glyph(s)
2. Ensure components are present (e.g. base + accent/bar)
3. Choose alignment direction (usually **Center X**)
4. Choose scope:

   * Current master
   * All masters
5. Run the script

---

## Notes

* Designed for italic workflows
* Avoids common misalignment caused by skewed bounding boxes
* Works even when no nodes exist at the target height
* Based on real contour intersection (not node sampling)

---

## Why this works

Instead of aligning bounding boxes, the script:

1. Projects outlines according to italic angle
2. Intersects them with a horizontal line
3. Measures real left/right extremes
4. Computes the true visual center

This matches how alignment is perceived in type design.

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:
https://www.myfonts.com/collections/tipo-pepel-foundry
