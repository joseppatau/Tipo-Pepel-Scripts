## Glyph Fill Engine

**Description**
Fills glyph shapes with circles or custom glyphs using an adaptive multi-pass distribution system, ensuring optimal spacing, hierarchy, and visual balance.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
MIT

---

## Features

* Fill shapes with circles or custom glyph components
* Adaptive multi-pass distribution algorithm
* Prevents overlaps with safe spacing
* Supports multiple glyph inputs
* Preview mode with non-destructive layer
* Works on current glyph, selection, or entire font

---

## Core

* Collision detection and spacing control
* Multi-pass size distribution (structure + refinement)
* Outline-aware placement (inside path validation)
* Component scaling and placement

---

## Scope

* Current glyph, selected glyphs, or entire font
* Selected master
* Paths or component-based shapes

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Choose application mode (current / selected / full font)
2. Select master
3. Adjust parameters (size, spacing, passes, etc.)
4. (Optional) Enable custom glyphs
5. Click **Preview** or **Apply**

---

## Parameters

* **Min / Max diameter** — size range
* **Safe area** — spacing between elements
* **Step size** — grid resolution
* **Size drop** — size reduction per pass
* **Structure passes** — large shape distribution
* **Max per size** — repetition control

---

## Notes

* Skips glyphs with only components (no paths)
* Preview creates a temporary layer
* Uses geometric checks to ensure clean placement
* Supports both primitive shapes and glyph-based fills

---

## Advanced

* Alternating scan directions for more organic distribution
* Two-phase algorithm: structure + adaptive fill
* Supports custom glyph libraries for pattern generation
* Dynamic scaling based on glyph bounds

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
