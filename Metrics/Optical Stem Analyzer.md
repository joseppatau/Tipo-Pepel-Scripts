## Optical Stem Analyzer

**Description**
Analyzes optical stem compensation by comparing straight and curved glyph stems, providing suggested adjustments for consistent visual weight.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Measures stem thickness using geometric intersections
* Compares straight vs curved glyphs (H/O, n/o)
* Calculates optical compensation percentage
* Suggests ideal curved stem thickness
* Reports deviations (too thick / too thin / OK)
* Multi-master analysis

---

## Core

* Intersection-based stem measurement
* Interpolated compensation model
* Optical comparison between glyph types

---

## Scope

* Entire font
* All masters
* Predefined glyph pairs (H/O, n/o)

---

## Requirements

* Glyphs App 3.x
* Compatible glyph structure (clear stems)

---

## Usage

1. Open font
2. Click **Analyze Font**
3. Review report
4. Copy results if needed

---

## Output

For each master:

* Straight stem value
* Curved stem value
* Suggested optical value
* Compensation percentage
* Status evaluation

---

## Notes

* Uses midline intersections for measurement
* Ignores extreme outline segments
* Designed for Latin typefaces

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
