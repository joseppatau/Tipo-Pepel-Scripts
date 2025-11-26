# Kern Tools – README

**Kern Tools** is a multi‑tool panel for **Glyphs App**, designed to streamline and accelerate kerning workflows. It centralizes several advanced features into a single window with multiple tabs, allowing type designers to generate, inspect, clean, and manipulate kerning pairs efficiently.

---

## 1. Pairs Generator
Generate kerning test strings automatically:
- Based on a list of user‑defined base glyphs.
- Supports Latin and Cyrillic, uppercase/lowercase, punctuation, symbols, and numbers.
- Optional filtering using kerning groups to avoid duplicates.
- Adds contextual prefixes/suffixes (HHOH / HOOH) for consistent display.
- Includes classic test‑word collections (Briem, Stephenson Blake, etc.).
- Opens one Glyphs tab per base glyph.

---

## 2. List All Pairs
Create tabs containing **all existing kerning pairs** in the font:
- Categorized as **VALID**, **PARTIAL**, or **MISSING**.
- Displays corrected glyph names when needed.
- Splits output into multiple tabs according to user‑defined batch size.

---

## 3. List Pairs (Turbo)
Fast listing of all pairs related to a single glyph:
- Retrieves left/right kerning pairs.
- Displays kerning values.
- Useful for targeted debugging.

---

## 4. Find Collisions (Turbo)
Generate strings for identifying visual collisions:
- Tests a glyph against selected script/case subsets.
- Ideal for optical review of spacing and kerning issues.

---

## 5. Kern to SC
Transfers kerning between uppercase ↔ small caps:
- Copies values while avoiding duplicated or inconsistent pairs.
- Ensures coherent kerning behavior across case variants.

---

## 6. Sanitizer
Cleanup utilities:
- Normalizes glyph names.
- Removes invalid or broken kerning pairs.
- Clears leftover groups or inconsistent assignments.

---

## 7. Clear & Restore
Kerning reset and recovery tools:
- Saves a backup of current kerning values.
- Clears all kerning.
- Allows full restoration when needed.

---

## 8. Scale %
Apply global scaling to kerning values:
- Adjustable percentage.
- Useful for matching optical behavior between masters.

---

## Additional Features
- Automatic detection and assignment of kerning groups.
- Intelligent script and case classification (Latin/Cyrillic, upper/lower, small caps, numbers, symbols).
- Symmetric trio generation (AVA, WOW, etc.) for consistency checks.
- Unicode ↔ glyph‑name conversion.
- Context‑aware prefixes/suffixes for test strings.

---

### License
MIT License.

### Author
Designed by **Josep Patau Bellart**. Programmed with the assistance of AI tools.

If you find this script useful, consider supporting the author by purchasing a font from **Tipo Pepel** on MyFonts.

