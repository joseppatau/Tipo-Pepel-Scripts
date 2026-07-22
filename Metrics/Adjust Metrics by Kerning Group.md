## Group Metrics Tool

**Description**
Adjusts sidebearings (LSB and RSB) for glyphs based on kerning group membership, allowing consistent spacing control across selected masters.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Adjust LSB and RSB by kerning group
* Supports increase, decrease, or exact values
* Multi-master selection
* Group-aware processing (left and right)
* Undo support

---

## Core

* Kerning group detection (left/right)
* Layer-based metrics modification
* Mode-based value transformation

---

## Scope

* Glyphs belonging to selected kerning group
* Selected masters only

---

## Requirements

* Glyphs App 3.x
* Kerning groups defined

---

## Usage

1. Enter kerning group name
2. Set LSB and/or RSB values
3. Choose mode (increase, decrease, exact)
4. Select masters
5. Click **Run**

---

## Notes

* Applies changes only to matching group members
* Works independently for left and right groups
* Supports full undo (⌘Z)

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
