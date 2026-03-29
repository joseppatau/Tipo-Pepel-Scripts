## Remove Overlapping Nodes (All Masters)

**Description**
Removes duplicate nodes that share the exact same position within paths across all master layers, helping clean and optimize glyph outlines.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Detect overlapping (duplicate) nodes
* Remove nodes with identical coordinates
* Process all master layers automatically
* Works across the entire font
* Fast batch cleanup

---

## Core

* Position-based node comparison
* Duplicate detection using coordinate rounding
* Safe node removal per path
* Multi-master iteration

---

## Scope

* Entire font
* All master layers

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Open a font
2. Run the script
3. Review notification with number of removed nodes

---

## Notes

* Only removes nodes with identical positions
* Does not affect path structure beyond duplicates
* Useful for cleaning imported or messy outlines
* Improves interpolation stability and outline efficiency

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
