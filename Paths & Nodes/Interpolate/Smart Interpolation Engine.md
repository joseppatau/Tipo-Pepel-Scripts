## Smart Interpolation Engine

**Description**
Adjusts node distances intelligently while preserving typographic constraints such as baseline, x-height, cap height, and blue zones.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Distance-based node pairing
* Tolerance-controlled detection
* Axis-based adjustment (X / Y)
* Category filtering (uppercase, lowercase, numbers, symbols, punctuation)
* Debug mode with detailed logs

---

## Smart Behavior

* Detects master lines and blue zones
* Preserves nodes aligned to typographic metrics
* Moves only non-critical nodes when needed
* Prevents distortion of key structural features

---

## Adjustment Modes

* Master node + free node → move free node
* Two master nodes → no movement
* Two free nodes → proportional adjustment

---

## Core

* Distance detection system
* Typographic constraint recognition
* Node classification engine
* Post-adjustment restoration

---

## Scope

* Entire font (filtered by category)
* Active master

---

## Requirements

* Glyphs App 3.x
* Structured outlines

---

## Usage

1. Choose axis (X or Y)
2. Set target and new distance
3. Define tolerance
4. Select glyph categories
5. Click **SMART ADJUST**

---

## Notes

* Designed for interpolation refinement
* Preserves critical typographic structure
* Debug mode provides detailed processing logs

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
