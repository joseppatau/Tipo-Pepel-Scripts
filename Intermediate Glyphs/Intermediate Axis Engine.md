## Intermediate Axis Engine

**Description**
Creates and manages intermediate layers using axis-based coordinates, with continuous interpolation, live preview, and web-based variable font testing.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Create true intermediate (brace) layers using axis coordinates
* Supports multi-axis interpolation
* Continuous preview with real-time updates
* Web-based variable font tester (HTML export)
* Detects and uses existing intermediate layers
* Handles both master and brace interpolation

---

## Core

* Axis-based coordinate system (dict + interpolation structure)
* Multi-layer interpolation logic (masters + brace layers)
* GSInstance fallback for complex cases
* Real-time rendering with custom preview view

---

## Scope

* Selected glyphs
* All axes in font
* Masters and intermediate layers

---

## Requirements

* Glyphs App 3.x
* Variable font setup (axes defined)

---

## Usage

1. Enter axis values (numeric or named format)
2. Generate intermediate layer
3. Preview interpolation live
4. (Optional) Export web preview

---

## Input formats

* **Numeric:** `100,85,85,100`
* **Named:** `Weight=100, Width=85, Optical size=85`

---

## Notes

* Uses Glyphs 3 native intermediate layer structure
* Avoids duplicate layer creation
* Supports both name-based and attribute-based detection
* Includes debug tools for layer inspection

---

## Advanced

* Multi-axis interpolation with distance-based fallback
* Brace layer detection via attributes and naming
* Custom NSView rendering pipeline
* HTML generator with live axis sliders

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
