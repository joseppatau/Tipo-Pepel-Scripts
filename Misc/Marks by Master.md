## Marks by Master

**Description**  
Lightweight color-marking tool for Glyphs App that allows assigning visual status markers to selected glyph layers using native Glyphs color labels.

Designed for fast QA workflows, especially useful when reviewing different masters independently.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
MIT

---

## Features

* Apply Glyphs native color labels to selected layers
* Quick visual marking for review workflows
* Clean and minimal floating UI
* Centered labels for compact interface
* One-click color assignment
* “Clean” button to remove all marks
* Supports multiple selected glyphs

---

## Core

* Uses native `layer.color` system (Glyphs)
* Vanilla-based compact UI
* Batch processing on selected layers
* No external dependencies

---

## Scope

* Selected glyph layers only
* Works per master (layer-based marking)

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Select one or more glyphs
2. Choose a color from the panel
3. Click **Mark** to apply the color
4. Use **Clean** to remove all marks

---

## Output

* Visual color labels applied to glyph layers
* No geometry or data modification
* Non-destructive workflow

---

## Notes

* Colors are assigned per layer (not per glyph globally)
* Useful for marking review status across masters
* Does not affect export or font data
* Uses Glyphs internal color indexing system

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry