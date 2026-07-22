## Create Small Caps & Numerals Smart Components

**Description**
Generates small caps numerals and related glyphs as components, with optional Smart Component support for interpolation-aware scaling and positioning.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Generate small caps numerals (`.numr`, `.dnom`, `.sups`, `.sinf`)
* Create glyphs using components (linked to base glyphs)
* Optional Smart Component generation
* Automatic vertical positioning (baseline / cap height / centered)
* Adjustable scaling (height and width)
* Supports punctuation, symbols, and custom selections
* Updates existing glyphs or creates new ones

---

## Smart Component Mode

* Detects if the font supports Smart Components
* Allows interpolation-aware scaling
* Uses axis-based values for dynamic behavior
* Falls back to regular components if not available

---

## Core

* Component-based glyph construction
* Scale and transform calculation per form
* Automatic alignment handling
* Category and subcategory assignment
* Metrics key inheritance (`=baseGlyph`)

---

## Generated Forms

* `.numr` → numerator (aligned to cap height)
* `.dnom` → denominator (aligned to baseline)
* `.sups` → superscript (top-aligned / centered)
* `.sinf` → inferior (centered below baseline)

---

## Scope

* Selected glyph sets (numerals, punctuation, symbols, custom)
* Current master
* Entire font structure

---

## Requirements

* Glyphs App 3.x
* Base glyphs must exist (e.g. `zero`, `one`, etc.)

---

## Usage

1. Select glyph categories (numerals, punctuation, symbols…)
2. Define scale percentages for each form
3. Choose component type:

   * Smart Components
   * Regular Components
4. Run the script
5. Review generated or updated glyphs

---

## Notes

* Existing glyphs can be updated or preserved
* Uses component transforms (no outline duplication)
* Maintains consistent spacing via metrics keys
* Ideal for building OpenType features like `numr`, `dnom`, `sups`, `sinf`

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
