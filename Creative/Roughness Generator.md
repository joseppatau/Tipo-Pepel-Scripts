## Glyph Roughness Engine

**Description**
Applies equidistant node distribution and controlled roughness to glyph outlines, creating organic or structured distortion effects.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Adds equidistant nodes to paths (lines and curves)
* Applies roughness deformation (random or regular)
* Option to remove handles and flatten paths
* Live preview with character input
* Apply to single glyph, selection, or entire font

---

## Core

* Curve length approximation and node distribution
* Perpendicular displacement for roughness
* Mixed segment handling (lines + curves)
* Path simplification (handle removal)

---

## Scope

* Selected glyphs or entire font
* Selected master
* Paths only

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Enter character for preview
2. Adjust spacing (node density)
3. Set roughness amount
4. Choose mode (regular or random)
5. Preview and apply

---

## Parameters

* **Spacing** — distance between generated nodes
* **Roughness** — displacement intensity
* **Mode** — regular (alternating) or random

---

## Notes

* Converts curves into straight segments (flattened result)
* Higher spacing = fewer nodes
* Roughness is applied perpendicular to path direction
* Works best on clean outlines

---

## Advanced

* Alternates displacement direction in regular mode
* Uses curve subdivision for consistent node spacing
* Optimized for mixed path types
* Non-destructive preview workflow

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
