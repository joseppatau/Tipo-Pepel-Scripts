## Kerning Group Toolkit

**Description**
A multi-purpose toolset for managing kerning groups, including metrics adjustment, group inspection, and metric key analysis.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Adjust LSB and RSB by kerning group
* Use reference glyph values automatically
* View group members in new tabs
* Inspect metric key dependencies
* Interactive multi-tab UI

---

## Tools

### 🔹 Update Metrics by Group

Adjust sidebearings for all glyphs in a kerning group.
Supports increase, decrease, or exact values.

---

### 🔹 Reference-Based Metrics

If no values are provided, uses a glyph with the same name as the group as a reference.
Automatically applies its LSB/RSB.

---

### 🔹 View Group Members

Opens a tab listing all glyphs belonging to a kerning group.
Separates left and right groups.

---

### 🔹 Metric Key Inspector

Finds all glyphs using a specific glyph as a metrics reference.
Helps track dependencies and spacing relationships.

---

## Core

* Kerning group parsing and normalization
* Layer-based metrics modification
* Dependency detection via metrics keys

---

## Scope

* Active master (metrics updates)
* Entire font (group inspection and key analysis)

---

## Requirements

* Glyphs App 3.x
* Kerning groups defined

---

## Usage

1. Enter kerning group or glyph name
2. Choose tool (update, view, inspect)
3. Run operation

---

## Notes

* Supports both group names and @MMK formats
* Metric key detection works on glyph and layer level
* Fully undoable operations

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
