## OpenType Feature Toggle

**Description**
Provides a simple interface to enable or disable OpenType features in the current tab for real-time text rendering testing.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* List all OpenType features in the font
* Toggle features on/off via checkboxes
* Apply selected features to current tab
* Scrollable interface for large feature sets

---

## Core

* Feature extraction from font
* Checkbox-based selection system
* Direct assignment to `tab.features`

---

## Scope

* Current tab
* Active font

---

## Requirements

* Glyphs App 3.x
* OpenType features defined in font

---

## Usage

1. Open a tab with text
2. Launch the panel
3. Select desired features
4. Click **Apply to Tab**

---

## Notes

* Uses feature list (not string) for compatibility
* Does not modify font data
* Ideal for testing ligatures, stylistic sets, and substitutions

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
