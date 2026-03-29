## Kerning Master Manager

**Description**
Provides a set of utilities to manage kerning at the master level, including deletion, backup, restoration, and cleanup of small-value pairs.

**Author**
Josep Patau Bellart (with AI assistance)

**License**
Apache2

---

## Features

* Delete kerning for a selected master
* Create JSON backups before deletion
* Restore kerning from backup files
* Remove small-value kerning pairs
* Optional negative-only cleanup

---

## Core

* Master-specific kerning manipulation
* JSON import/export for kerning data
* Threshold-based filtering system

---

## Tools

### 🔹 Delete Master Kerning

Removes all kerning pairs from the selected master.
Optional backup before deletion.

---

### 🔹 Backup Kerning (JSON)

Exports kerning data to a JSON file for safe storage and reuse.

---

### 🔹 Restore Kerning

Imports kerning pairs from a JSON backup into the selected master.

---

### 🔹 Clean Small Values

Removes kerning pairs below a given threshold.
Supports negative-only filtering for fine cleanup.

---

## Scope

* Selected master
* Kerning pairs only

---

## Requirements

* Glyphs App 3.x
* Open font

---

## Usage

1. Select a master
2. Choose an operation:

   * Delete kerning
   * Backup kerning
   * Restore kerning
   * Clean small values
3. Confirm action

---

## Notes

* Backup is recommended before deletion
* JSON files can be reused across fonts
* Small-value cleanup helps refine kerning quality

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
