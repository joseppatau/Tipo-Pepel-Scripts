## Character Tuner

**Description**
A shape correction tool that detects misaligned lines and inconsistent stem widths, applying geometric adjustments to improve outline consistency.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

### 🔹 Line Alignment

* Detect horizontal and vertical line structures
* Group nodes by proxiApache2y
* Align to left, center, right (or top/bottom)
* Minimum length filtering

---

### 🔹 Stem Width Correction

* Detect node pairs within width ranges
* Separate handling for:

  * Rectangular stems (all nodes)
  * Curved stems (selected nodes only)
* Apply new target widths

---

### 🔹 Smart Pairing System

* Each node is used only once
* Prevents overlapping corrections
* Ensures stable transformations

---

### 🔹 Controlled Adjustment

* Only the second node is moved
* Preserves structural integrity
* Avoids unintended distortions

---

## Core

* Node grouping by proxiApache2y
* Unique pair detection system
* Axis-based distance evaluation
* Selective transformation logic

---

## Scope

* Current glyph
* Active layer

---

## Requirements

* Glyphs App 3.x
* Glyph with editable outlines

---

## Usage

1. Choose line orientation and alignment
2. Set margin and minimum length
3. Apply line correction
4. Define stem ranges and target widths
5. Apply stem correction

---

## Notes

* Designed for outline cleanup and normalization
* Works best on structured glyphs
* Debug output available in console

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
