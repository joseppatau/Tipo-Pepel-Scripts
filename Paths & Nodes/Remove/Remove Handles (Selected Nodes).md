## Remove Handles (Selected Nodes)

**Description**
Removes curve handles from selected nodes in the current or all master layers, simplifying outlines while preserving the main node structure.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Remove handles from selected nodes
* Supports current master or all masters
* Preserves node positions and shape integrity
* Uses Glyphs’ `removeNodeCheckKeepShape_` for safe deletion
* Undo support

---

## Core

* Node selection detection
* Handle (off-curve) removal logic
* Multi-master processing
* Safe node manipulation

---

## Scope

* Selected nodes
* Current master or all master layers

---

## Requirements

* Glyphs App 3.x
* Selected nodes

---

## Usage

1. Select nodes in a glyph
2. Choose scope:

   * Current Master
   * All Masters
3. Click **Remove Handles**

---

## Notes

* Only affects off-curve nodes (handles)
* Keeps main nodes intact
* Useful for simplifying curves or preparing geometric shapes
* Safe for interpolation when used across all masters

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
