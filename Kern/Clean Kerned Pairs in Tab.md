## Clean Kerned Pairs in Tab

**Description**
Removes glyph pairs that already have kerning applied from the active tab, helping you focus on unresolved spacing issues without modifying font data.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Removes pairs with kerning from active tab
* Keeps only pairs without kerning
* Does not modify font kerning data
* Works with group and glyph kerning
* Always-on-top floating UI

---

## Core

* Iterates through tab layer pairs
* Reads kerning via group-aware keys
* Filters pairs based on kerning value

---

## Scope

* Active tab only
* Current master kerning

---

## Requirements

* Glyphs App 3.x
* Active edit tab

---

## Usage

1. Open a tab with glyph pairs
2. Click **Clean pairs with kerning**
3. Review remaining pairs (no kerning applied)

---

## Notes

* Kerning values are NOT deleted
* Only visual filtering in tab
* Useful for kerning QA and cleanup

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
