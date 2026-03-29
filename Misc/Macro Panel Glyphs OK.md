## Macro Panel

**Description**  
Advanced macro recorder and shortcut manager for Glyphs App.  
Allows recording, editing, saving, and replaying sequences of keyboard actions for repetitive workflows.

**Author**  
Josep Patau Bellart (with AI assistance)

**License**  
MIT

---

## Features

* Record keyboard-based macros directly inside Glyphs
* Save and organize reusable macros
* Execute macros with customizable delay and repetition
* Built-in shortcut library with descriptions
* Create and manage custom shortcuts
* Reorder macro steps via drag interaction
* Searchable shortcut picker interface
* JSON import/export for macros and shortcuts

---

## Core

* Event-based key capture system
* Macro playback engine using Quartz events
* JSON persistence system (local storage)
* Dynamic shortcut parsing and formatting
* Safe event monitoring (start/stop handling)

---

## Scope

* Active Glyphs App environment
* All open fonts and layers (via user interaction)

---

## Requirements

* Glyphs App 3.x
* macOS (Quartz event system required)

---

## Permissions (Important)

This script relies on macOS system-level keyboard event control.

You must grant Glyphs the proper permissions:

1. Open **System Settings**
2. Go to **Privacy & Security**
3. Open **Accessibility**
4. Add **Glyphs App** and enable it

(Optional but recommended)

5. Go to **Input Monitoring**
6. Add **Glyphs App** and enable it

Without these permissions, macro recording and playback will not work correctly.

---

## Usage

1. Click **REC** to open the shortcut picker  
2. Double-click shortcuts to build a macro  
3. Click **STOP** to finish recording  
4. Click **▶ PLAY** to execute the macro  
5. Save the macro for reuse  

Optional:
* Adjust delay between actions  
* Create custom shortcuts  
* Export/import macro libraries  

---

## Output

* Executed keyboard sequences inside Glyphs
* Stored macros (JSON)
* Custom shortcut definitions
* Reusable automation workflows

---

## Notes

* Macros are based on keyboard events, not direct API calls  
* Timing between actions is critical for stability  
* Some operations depend on Glyphs UI state  
* Designed for power users and repetitive production tasks  

---

## Support the author

If you find this script useful, you can show your appreciation by purchasing any font at:  
https://www.myfonts.com/collections/tipo-pepel-foundry