## Sync Paths with Background

**Description**
Synchronizes foreground paths with the background layer by copying node positions, optionally including node types, across the current or all masters.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Copy node positions from background to foreground
* Optional copying of node types (LINE / CURVE)
* Process selected paths only or all paths
* Apply to current master or all masters
* Batch processing with summary feedback

---

## Core

* Path index matching between foreground and background
* Node-by-node position synchronization
* Optional node type transfer
* Multi-master processing

---

## Scope

* Selected glyph
* Current master or all masters

---

## Requirements

* Glyphs App 3.x
* Background layer with paths

---

## Usage

1. Select a glyph
2. Ensure background contains valid paths
3. Choose options:

   * Copy node types
   * Selected paths only
   * Apply to all masters
4. Click **Apply**

---

## Notes

* Foreground paths must match background structure
* Only matching node indices are synchronized
* Does not create or delete paths
* Useful for tracing, reconstruction, or restoring geometry

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
