## Move Elements in Masters

**Description**  
Moves nodes, handles, components, and anchors across selected masters using a directional interface with precise control. Includes smart behavior that automatically moves entire glyphs when no elements are selected.

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
* **Smart behavior:**
  * When elements are selected → moves only selected elements
  * When nothing is selected → moves entire glyphs
* **Debug panel** with detailed selection information
* **Real-time status** showing number of selected glyphs
* **Detailed operation log** showing exactly what was moved

---

## Core

* Robust node + handle movement (Bezier-safe)
* Component offsetting
* Anchor repositioning
* Master-aware layer targeting
* Smart selection detection
* Entire glyph movement capability
* Comprehensive debug output

---

## Scope

* Selected glyphs (in font window or edit view)
* Selected elements:
  * Nodes (with associated handles)
  * Components
  * Anchors (in “Both” mode)
* **If nothing selected → entire glyphs move**
* Current master or **user-defined master selection**

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

### Basic Usage

1. Select glyph(s) in font window or edit view
2. **Either:**
   - Select specific nodes, components, or anchors to move only those
   - Leave nothing selected to move entire glyphs
3. Run the script
4. Choose:
   - What to move (Paths / Components / Both)
   - Where (Current Master or Selected Masters)
5. (Optional) Select specific masters via checkboxes
6. Use arrow buttons to move elements

### Debug Features

* Click **"Debug"** to see detailed information about:
  - Selected glyphs and layers
  - Selected nodes, paths, components, and anchors
  - Current mode settings
  - Selected masters
* The **debug output area** shows detailed logs of each move operation
* Status bar shows how many glyphs are currently selected

---

## Notes

* **Smart behavior:** The script automatically detects what you want to move
  - If you have nodes/paths/components/anchors selected → moves only those
  - If nothing is selected → moves entire glyphs
* Moving nodes automatically includes all associated handles
* Uses a **robust selection system** to avoid handle desync issues
* Supports whole path movement if path is selected
* Anchors move only when selected and in “Both” mode
* Includes undo grouping
* Designed to behave consistently across multiple masters
* **Debug panel helps troubleshoot** when nothing seems to move

---

## Examples

### Moving entire glyphs across masters
1. Select multiple glyphs in font window (e.g., a, b, c...)
2. Run script, select target masters in checkboxes
3. Don't select any nodes in edit view
4. Click arrows → entire glyphs move to all selected masters

### Moving specific nodes
1. Select a glyph, select specific nodes in edit view
2. Run script, select target masters
3. Click arrows → only selected nodes (with their handles) move

### Moving components only
1. Select components in edit view
2. Set mode to "Components"
3. Click arrows → only components move

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry