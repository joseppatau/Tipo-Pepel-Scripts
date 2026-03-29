## Outline Pattern Engine

**Description**
Generates dotted or glyph-based patterns along glyph outlines using adaptive spacing, size variation, and optional rotation for rich contour effects.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Create dotted outlines along glyph contours
* Use circles or custom glyphs as elements
* Supports irregular spacing and size values
* Optional rotation (random or progressive)
* Live preview with custom character input
* Apply to single glyph, selection, or entire font

---

## Core

* Path length analysis and point sampling
* Bezier curve approximation and interpolation
* Adaptive distribution along contours
* Glyph transformation and placement

---

## Scope

* Selected glyphs or entire font
* Specific master selection
* Paths (contours) only

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Enter character for preview
2. Set spacing and size (or irregular values)
3. (Optional) Enable custom glyphs
4. Choose rotation mode
5. Preview and apply

---

## Parameters

* **Spacing** — distance between elements
* **Element size** — diameter or scale
* **Irregular values** — variation patterns
* **Rotation** — none, random, or progressive
* **Glyph input** — custom shape elements

---

## Notes

* Preserves anchors when applying
* Replaces original outlines on apply
* Optimized with curve length caching
* Handles both straight and curved segments

---

## Advanced

* Alternates spacing and size patterns cyclically
* Supports multi-glyph pattern sequences
* Efficient curve sampling with caching
* Real-time preview with custom rendering view

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
