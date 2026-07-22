## Glyph Preview Engine

**Description**
A lightweight and extensible glyph preview component for GlyphsApp scripts, supporting multi-master rendering and metric visualization.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Real-time glyph rendering
* Multi-master support
* Character input preview
* Metric guides (baseline, x-height, cap height, ascender, descender)
* Automatic scaling and centering
* Cached drawing for performance

---

## Core

* NSView-based rendering system
* Bezier path extraction or reconstruction
* Transform system (scale + baseline alignment)
* Glyph and layer lookup logic

---

## Integration

* Designed as a reusable component
* Easily embedded into other script UIs
* Supports dynamic updates via:

  * `setCharacter_()`
  * `setMetrics_()`

---

## Scope

* Any script requiring glyph preview
* Works with current font and selected masters

---

## Requirements

* Glyphs App 3.x
* AppKit / Vanilla

---

## Usage

1. Initialize preview panel
2. Set character and master
3. Embed into your script UI

---

## Notes

* Includes fallback path reconstruction
* Handles missing glyphs gracefully
* Optimized for lightweight integration

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
