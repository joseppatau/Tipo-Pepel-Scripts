## Glyph Preview Window

**Description**
A detached, real-time glyph preview window that mirrors the current glyph with zoom, pan, and persistent view settings.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Real-time preview of current glyph
* Includes components and final outlines
* Zoom and pan interaction
* Double-click to fit glyph
* Persistent zoom and position settings
* Automatic updates via Glyphs interface

---

## Core

* NSView-based rendering
* `completeBezierPath` for full glyph drawing
* Bounding box scaling and centering
* Glyphs callback system (`UPDATEINTERFACE`)

---

## Interaction

* Drag to move view
* Scroll to zoom
* Double-click to fit glyph
* Save view state

---

## Scope

* Current glyph
* Active font

---

## Requirements

* Glyphs App 3.x

---

## Usage

1. Open the preview window
2. Edit glyph in Glyphs
3. View updates in real time
4. Adjust zoom and position
5. Save preferred view

---

## Notes

* Designed for continuous use during editing
* Ideal as a secondary viewport
* Does not modify glyph data

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
