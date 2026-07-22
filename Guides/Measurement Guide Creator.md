## Measurement Guide Creator

**Description**
Creates and manages horizontal measurement guides at specified Y positions, with support for applying across current or all masters and clearing existing guides.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Create horizontal measurement guides at custom Y values
* Apply to current master or all masters
* Avoid duplicate guides automatically
* Clear all or specific guides by position
* Stores user preferences (Y values and mode)
* Displays measurement values on guides

---

## Core

* Guide generation and validation
* Preference persistence (Glyphs defaults)
* Layer targeting (current vs all masters)
* Duplicate detection logic

---

## Scope

* Selected glyphs
* Current or all masters
* Horizontal guides only

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Select glyph(s)
2. Enter Y positions (comma-separated)
3. Choose target (current or all masters)
4. Click **Apply** or **Clear Guides**

---

## Notes

* Skips guides that already exist at the same Y position
* Supports partial clearing (specific Y values)
* Measurement display depends on Glyphs version
* Uses undo grouping per glyph

---

## Advanced

* Automatically groups operations by glyph
* Handles both full and selective guide cleanup
* Compatible fallback for measurement property (Glyphs versions)

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
