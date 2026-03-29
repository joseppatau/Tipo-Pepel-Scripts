## Assign Metrics Keys to Small Caps

**Description**
Assigns metrics keys from uppercase glyphs to selected small caps (.sc) glyphs, ensuring consistent spacing by inheriting metrics from their corresponding uppercase forms.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Assign metrics keys to selected `.sc` glyphs
* Automatic mapping from lowercase/small caps to uppercase
* Supports ligatures (e.g. `ae.sc → AE`, `ffi.sc → FFI`)
* Handles special glyph names safely
* Applies left, right, and width metrics keys

---

## Core

* Small caps detection (`.sc` / `.SC`)
* Base name extraction and mapping
* Ligature-aware uppercase conversion
* Metrics key assignment per layer

---

## Scope

* Selected glyphs only
* All master layers

---

## Requirements

* Glyphs App 3.x
* Existing uppercase glyphs in font

---

## Usage

1. Select `.sc` glyphs
2. Run the script
3. Click **Apply**

---

## Notes

* Requires corresponding uppercase glyphs to exist
* Special glyphs are excluded from uppercase conversion
* Metrics keys are assigned as `=A`, `=AE`, etc.
* Helps maintain consistent spacing across small caps

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
