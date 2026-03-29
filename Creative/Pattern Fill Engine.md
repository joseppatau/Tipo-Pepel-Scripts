## Pattern Fill Engine

**Description**
Fills glyph shapes with scalable, repeatable patterns using custom glyphs, grid tiling, and advanced controls for spacing, rotation, and composition.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
MIT

---

## Features

* Fill shapes using custom glyph-based patterns
* Multiple pattern layers with independent settings
* Grid-based tiling with offsets and margins
* Global and incremental rotation controls
* Live dual preview (original vs result)
* Apply to current glyph, selection, or entire font

---

## Core

* Tile-based pattern generation
* Multi-layer pattern composition
* Transform pipeline (scale, translate, rotate)
* Boolean intersection with original shapes

---

## Scope

* Selected glyphs or entire font
* Selected master
* Path-based shapes (with optional component preservation)

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Add one or more patterns (glyph names)
2. Adjust scale, spacing, offsets, and margins
3. Set rotation and incremental rotation
4. Preview result
5. Apply to desired scope

---

## Parameters

* **Pattern** — glyph used as tile
* **Scale** — pattern size
* **Rotation** — global rotation
* **Increment** — per-tile rotation variation
* **Offset X/Y** — grid displacement
* **Margins** — spacing around each tile

---

## Notes

* Preserves original width, anchors, and components
* Skips glyphs used as patterns to avoid overwriting
* Uses boolean intersection to clip patterns to shape
* Optimized for multi-pattern workflows

---

## Advanced

* Supports layered pattern composition
* Incremental rotation based on tile position
* Smart bounds calculation for accurate tiling
* Dual preview system for visual comparison

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
