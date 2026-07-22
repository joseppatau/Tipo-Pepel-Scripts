## Delete Glyph Content (Smart)

**Description**  
Flexible cleanup tool for Glyphs App that deletes either all glyph content or only selected elements.

Automatically detects selection and applies the appropriate deletion mode, making it a fast and safe tool for editing workflows.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
Apache2

---

## Features

* Delete all content in glyph layers (paths, components, anchors, guides, hints)
* Delete only selected elements if a selection exists
* Automatic mode detection (selection vs full clear)
* Option to apply changes to all masters
* Works on multiple selected glyphs
* Undo-safe operations per glyph

---

## Core

* Layer content reset via `layer.shapes`, `anchors`, `guides`, `hints`
* Selection-aware deletion system
* Master-aware layer targeting
* Vanilla-based minimal UI

---

## Scope

* Selected glyphs
* Current master or all masters (optional)

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Select one or more glyphs or layers  
2. (Optional) Select specific elements inside glyphs  
3. Enable **Apply to ALL masters** if needed  
4. Click **Apply**

Behavior:
* If something is selected → deletes only selection  
* If nothing is selected → deletes all content  

---

## Output

* Glyph content removed (full or partial)
* No changes to glyph metadata or structure
* Immediate visual update in current tab

---

## Notes

* Destructive operation — use undo if needed  
* Smart behavior avoids accidental full deletion when selection exists  
* Useful for resetting glyphs or cleaning imported outlines  
* Also removes guides and hints  

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry