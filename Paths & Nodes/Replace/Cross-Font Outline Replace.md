## Replace From Other Font

**Description**
Replaces glyph outlines and related data from another open font, supporting both current master and all masters synchronization.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## ⚠️ Warning

This tool overwrites glyph data.
Use carefully or keep backups before running.

---

## Features

* Replace outlines from another open font
* Supports current master or all masters
* Copies shapes and components
* Copies anchors and metrics (width, LSB, RSB)
* Copies layer color and background images
* Validates glyph existence and master compatibility

---

## Core

* Cross-font glyph mapping
* Master index synchronization
* Deep copy of glyph data

---

## Scope

* Selected glyphs
* Source font → current font

---

## Requirements

* Glyphs App 3.x
* Two open fonts
* Matching glyph names

---

## Usage

1. Open two fonts
2. Select glyphs in target font
3. Choose source font
4. Select mode:

   * Current master
   * All masters
5. Click **Replace Selected Glyphs**

---

## Notes

* Requires matching glyph names
* All masters mode requires equal number of masters
* Overwrites shapes, anchors, and metrics

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
