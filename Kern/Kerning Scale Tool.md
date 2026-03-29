## Kerning Scale Tool

**Description**
Scales kerning values by a percentage in the active master, with options to increase or decrease values and filter by specific kerning groups.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Scale kerning pairs by percentage
* Increase or decrease values
* Filter by specific kerning groups
* Apply only to active master
* Handles both glyph and group kerning

---

## Core

* Kerning pair iteration and filtering
* Percentage-based value transformation
* Group-aware matching logic

---

## Scope

* Active master
* All kerning pairs or filtered groups

---

## Requirements

* Glyphs App 3.x
* Open font with kerning

---

## Usage

1. Enter percentage value
2. Choose operation (increase or decrease)
3. (Optional) Enter group filters
4. Click **Apply**

---

## Notes

* Accepts values like `10` or `10%`
* Group filter uses space-separated names (e.g. `@A @V`)
* Skips invalid or unresolved kerning pairs
* Rounds values to integers

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
