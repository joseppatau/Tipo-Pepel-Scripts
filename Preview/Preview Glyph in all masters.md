## Preview Glyph in All Masters

**Description**  
Interactive preview tool for Glyphs App that displays a selected glyph across all masters in a single unified view.

Includes zoom, scrolling, and direct navigation to specific master layers, making it ideal for interpolation review and design consistency checks.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
MIT

---

## Features

* Preview selected glyph across all masters simultaneously
* Real-time update when changing glyph selection
* Adjustable zoom with slider or CMD + scroll
* Drag navigation (spacebar or option key)
* Double-click to open glyph in specific master
* Scalable layout based on master metrics
* Smooth scrolling with horizontal navigation

---

## Core

* Custom NSView rendering system
* Bezier path drawing via `completeBezierPath`
* Dynamic layout generation per master
* Zoom scaling based on ascender/descender metrics
* Glyphs callback system (`UPDATEINTERFACE`)

---

## Scope

* Active glyph selection
* All masters in the font
* Visual preview only (non-destructive)

---

## Requirements

* Glyphs App 3.x
* Open font with multiple masters

---

## Usage

1. Select a glyph in Glyphs  
2. Run the script  
3. Use controls:
   * Zoom slider or CMD + scroll  
   * Drag (spacebar or option) to navigate  
   * Double-click a preview to open that master  

---

## Output

* Visual preview of glyph across all masters
* Interactive navigation and inspection
* No changes to glyph data

---

## Notes

* Preview uses `completeBezierPath`, including components  
* Layout is dynamically scaled per master metrics  
* Designed for interpolation QA and visual consistency checks  
* Works best with consistent vertical metrics  

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry