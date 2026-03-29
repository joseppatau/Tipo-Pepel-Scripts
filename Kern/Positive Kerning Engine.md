## Positive Kerning Engine

**Description**
Detects collisions between glyph pairs and applies positive kerning adjustments to ensure minimum spacing, providing a structured workflow for collision correction and spacing refinement.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Collision detection between glyph outlines
* Applies only positive kerning adjustments
* Interactive UI with collision list and selection
* Auto-kerning within custom text blocks (`#...#`)
* Kerning pair visualization and tab generation
* Integrated kerning tools and group management

---

## Core

* Geometry-based collision detection (segment distance)
* Positive kerning enforcement logic
* Tab-based pair extraction and processing
* Group-aware kerning workflows

---

## Tools

### 🔹 Collision Detector

Detects collisions between glyph pairs using geometric distance calculations.
Displays results in an interactive list with selectable pairs.

### 🔹 Auto Kern (#...# blocks)

Applies kerning automatically to pairs defined inside `#...#` blocks in a tab.
Processes only the specified context.

### 🔹 Pair Generator & Viewer

Lists kerning pairs with graphical representation and contextual preview.
Supports search, filtering, and direct tab generation.

### 🔹 Group Manager

Displays and edits kerning groups.
Allows reordering glyphs within groups and saving custom group order.

### 🔹 Positive Kerning Apply

Applies spacing corrections only when pairs are below a target margin.
Prevents overcorrection by skipping already valid pairs.

### 🔹 JSON Pair Import

Imports kerning pairs from external JSON files and generates test tabs.

---

## Scope

* Active master
* Selected glyphs or tab-defined pairs
* Kerning pairs within collision or custom blocks

---

## Requirements

* Glyphs App 3.x
* Open font with kerning

---

## Usage

1. Enter glyphs or generate pairs
2. Run collision detection
3. Select problematic pairs
4. Apply positive kerning adjustments
5. Review results in new tabs

---

## Notes

* Only increases spacing (no negative kerning applied)
* Skips pairs already above target margin
* Uses geometric proxiApache2y for collision detection
* Supports custom test strings and scripts

---

## Advanced

* Segment-based distance calculations for precision
* Turbo caching for fast kerning pair handling
* Context-aware pair formatting for tab previews
* Modular toolset integrated in a single interface

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
