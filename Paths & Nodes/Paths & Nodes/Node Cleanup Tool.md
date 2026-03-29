## Node Cleanup Tool

**Description**
Removes curve handles from selected nodes and optionally redistributes them into evenly spaced linear structures.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

### 🔹 Remove Handles

* Converts curves into straight segments
* Removes off-curve nodes
* Applies only to selected nodes

---

### 🔹 Node Distribution

* Aligns nodes along a horizontal line
* Applies fixed spacing between nodes
* Removes handles before distribution
* Optional cleanup for 4-node structures

---

## Core

* Node type transformation (curve → line)
* Off-curve removal
* Position normalization
* Conditional node deletion

---

## Scope

* Selected nodes
* Current layer

---

## Requirements

* Glyphs App 3.x
* Node selection

---

## Usage

1. Select nodes
2. Choose:

   * **Clean curves**
   * **Disperse nodes**
3. Apply

---

## Notes

* Destructive for curve data
* Useful for geometric reconstruction
* Ideal for cleaning imported outlines

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
