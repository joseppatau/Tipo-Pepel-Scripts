Move Nodes & components (All Masters)

**Description**
Moves selected nodes, anchors, and components across all master layers simultaneously, enabling synchronized editing in multi-master fonts.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Move selected nodes across all masters
* Move selected anchors across all masters
* Move selected components across all masters
* Directional controls (↑ ↓ ← →)
* Keyboard shortcut support (Q + arrow keys)
* Floating window for quick access
* Preserves component transformations (rotation, scale, skew)

---

## Core

* Node index mapping between masters
* Anchor synchronization by name
* Component transformation matrix handling
* Real-time multi-master transformation
* Support for both `layer.components` and `layer.shapes` (Glyphs 3 compatibility)

---

## Scope

* Selected nodes and anchors
* Selected components
* All master layers

---

## Requirements

* Glyphs App 3.x
* Selected nodes, anchors, or components

---

## Usage

1. Select nodes, anchors, or components
2. Set movement value (in points)
3. Use buttons or keyboard shortcuts:
   - **Arrow buttons** — Click on-screen buttons
   - **Q + arrow keys** — Hold Q and press arrow keys
4. Apply movement across all masters simultaneously

### Component Movement

When moving components, the script:
- Detects selected components in the current layer
- Locates corresponding components in each master
- Updates the component's transformation matrix (tx, ty values)
- Preserves any existing rotation, scale, or skew

---

## Notes

* Requires consistent node structure across masters for node movement
* Components are matched by name across masters
* Anchors are matched by name across masters
* Ideal for variable font workflows
* Supports undo (all operations grouped by glyph)
* Works with both local and global guides
* Debug output shows count of moved nodes, anchors, and components

---

## Technical Details

### Component Transformation

Components are moved by updating their transformation matrix:

Original transform: [a, b, c, d, tx, ty]
New transform: [a, b, c, d, tx + dx, ty + dy]


Where:
- `a, d` = scale
- `b, c` = rotation/skew
- `tx, ty` = translation

### Component Detection

The script supports two methods of component access:
- `layer.components` — Primary method for Glyphs 3
- `layer.shapes` — Fallback for compatibility

---

## Version History

### 1.1 (Current)
- Added component movement support
- Component transformation matrix handling
- Improved cross-master component matching
- Debug output for components moved

### 1.0
- Initial release
- Node and anchor movement
- Keyboard shortcuts
- Floating window interface

---

## Support the Author

If you find this script useful, you can show your appreciation by purchasing any font at:  
[https://www.myfonts.com/collections/tipo-pepel-foundry](https://www.myfonts.com/collections/tipo-pepel-foundry)

Your support helps fund continued development and maintenance of tools like this.

---

## License

Copyright 2024 Josep Patau Bellart

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
