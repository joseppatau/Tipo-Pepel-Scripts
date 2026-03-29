## Random Node Movement

**Description**
Randomly offsets selected nodes using a percentage of local segment distances, allowing controlled distortion while preserving structural relationships.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Randomly moves selected nodes
* Uses local segment distances for proportional offsets
* Keeps coincident nodes grouped together
* Adjustable intensity via slider
* Supports multiple selected glyphs

---

## Core

* Node grouping by position
* Distance-based displacement calculation
* Random offset generation
* Undo-safe batch processing

---

## Scope

* Selected nodes only
* Selected glyphs
* Current layers

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Select nodes
2. Run the script
3. Adjust intensity
4. Click **Apply**

---

## Notes

* Maintains relative grouping of overlapping nodes
* Adds slight offset to avoid exact overlap
* Higher intensity = stronger distortion

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
