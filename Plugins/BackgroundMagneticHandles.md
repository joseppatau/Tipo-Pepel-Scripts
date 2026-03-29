## Background Magnetic Handles

**Description**  
Custom selection tool for Glyphs App that snaps selected nodes and their handles to corresponding positions in the background layer.

Designed to assist in tracing, interpolation corrections, and refining outlines based on reference shapes.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
Apache2

---

## Features

* Magnetic snapping to background nodes
* Moves both on-curve nodes and their handles
* Real-time behavior during dragging
* Adjustable tolerance for snapping sensitivity
* Works seamlessly within the Select Tool workflow
* Preserves curve structure while aligning geometry

---

## Core

* Custom `SelectTool` subclass
* Node proximity detection using tolerance threshold
* Background layer comparison (`layer.background`)
* Handle synchronization (`prevNode`, `nextNode`)
* Real-time interaction via `mouseDragged_`

---

## Scope

* Active layer and its background
* Selected nodes only
* On-curve nodes (handles adjusted automatically)

---

## Requirements

* Glyphs App 3.x
* Background layer with reference outlines

---

## Usage

1. Activate the tool (**shortcut: M**)  
2. Select one or more nodes  
3. Drag nodes near background outlines  
4. Nodes will snap automatically within tolerance  

---

## Output

* Nodes repositioned to match background geometry
* Handles updated to match background curves
* No changes to background layer

---

## Notes

* Snapping is based on proximity (tolerance = 15 units by default)  
* Only affects on-curve nodes directly  
* Handles are updated only if corresponding background handles exist  
* Ideal for tracing, fixing interpolation mismatches, or refining masters  

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry