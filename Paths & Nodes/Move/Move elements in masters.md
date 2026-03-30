## Move Elements in Masters

**Description**  
Moves nodes, handles, components, and anchors across selected masters using a directional interface with precise control.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
Apache2

---

## Features

* Move nodes, components, or both
* Moves **handles (off-curves) correctly with their nodes**
* Optional movement of **anchors**
* Works in current master or **custom-selected masters**
* Directional controls (↑ ↓ ← →)
* Custom movement value
* **Next / Previous master navigation (NM / PM)**
* **Always-on-top floating window**
* **Select All / Deselect All masters toggle**

---

## Core

* Robust node + handle movement (Bezier-safe)
* Component offsetting
* Anchor repositioning
* Master-aware layer targeting
* Selection-based movement logic

---

## Scope

* Selected glyphs
* Selected elements:
  * Nodes (with associated handles)
  * Components
  * Anchors (in “Both” mode)
* Current master or **user-defined master selection**

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Select glyph(s)
2. Select nodes, components, and/or anchors
3. Run the script
4. Choose:
   - What to move (Paths / Components / Both)
   - Where (Current Master or Selected Masters)
5. (Optional) Select specific masters via checkboxes
6. Use arrow buttons to move elements

---

## Notes

* Moving nodes automatically includes all associated handles
* Uses a **robust selection system** to avoid handle desync issues
* Supports whole path movement if path is selected
* Anchors move only when selected and in “Both” mode
* Includes undo grouping
* Designed to behave consistently across multiple masters

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry