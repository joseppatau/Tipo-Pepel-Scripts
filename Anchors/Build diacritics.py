# MenuTitle: Build Diacritics
# -*- coding: utf-8 -*-

import vanilla
from GlyphsApp import *
import re
from AppKit import NSAlert

SIDE_BEARING = 45

# =========================
# SVG PARSER LIMPIO - SOLO CONVERSIÓN BÁSICA, SIN FLIPS
# =========================

def parse_svg_and_build_path(svg_str):
    """Parser SVG con DEBUG y soporte correcto de múltiples subpaths"""

    DEBUG = True

    def log(msg):
        if DEBUG:
            print(msg)

    # -------------------------
    # VIEWBOX
    # -------------------------
    viewbox_match = re.search(r'viewBox=["\']([\d\.\s]+)["\']', svg_str)
    svg_height = 0
    if viewbox_match:
        parts = [float(x) for x in viewbox_match.group(1).split()]
        if len(parts) == 4:
            svg_height = parts[3]

    def convert_y(y):
        return svg_height - y if svg_height else y

    # -------------------------
    # PATH
    # -------------------------
    match = re.search(r'd=["\']([^"\']*)["\']', svg_str)
    if not match:
        log("❌ No path")
        return []

    d = match.group(1)
    log(f"\n--- SVG PATH ---\n{d}\n")

    # -------------------------
    # TOKENIZER PRO (clave)
    # -------------------------
    tokens = re.findall(r'[a-zA-Z][^a-zA-Z]*', d)
    log(f"TOKENS: {tokens}")

    shapes = []
    current_path = None

    curr_x = 0
    curr_y = 0
    start_x = 0
    start_y = 0

    for token in tokens:
        cmd = token[0]
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', token[1:])]

        log(f"\nCMD: {cmd} | nums: {nums}")

        # -------------------------
        # MOVE
        # -------------------------
        if cmd in ['M', 'm']:

            # 👇 guardar anterior SOLO si estaba cerrado
            if current_path and current_path.closed:
                shapes.append(current_path)

            current_path = GSPath()
            idx = 0

            first = True

            while idx + 1 < len(nums):

                if cmd == 'M':
                    curr_x = nums[idx]
                    curr_y = convert_y(nums[idx+1])
                else:
                    curr_x += nums[idx]
                    curr_y += -nums[idx+1]

                if first:
                    node_type = LINE  # Glyphs lo tolera mejor que default
                    start_x, start_y = curr_x, curr_y
                    first = False
                else:
                    # 👇 SVG: después del primer M → es LINE implícito
                    node_type = LINE

                current_path.nodes.append(GSNode((curr_x, curr_y), type=node_type))

                idx += 2

            log(f"Move → nodes: {len(current_path.nodes)}")

        # -------------------------
        # LINE
        # -------------------------
        elif cmd in ['L', 'l']:
            idx = 0
            while idx + 1 < len(nums):
                if cmd == 'L':
                    curr_x = nums[idx]
                    curr_y = convert_y(nums[idx+1])
                else:
                    curr_x += nums[idx]
                    curr_y += -nums[idx+1]

                current_path.nodes.append(GSNode((curr_x, curr_y), type=LINE))
                idx += 2

                
        # -------------------------
        # SMOOTH CUBIC (FIX REAL)
        # -------------------------
        elif cmd == 'S':
            if not current_path:
                continue

            idx = 0
            while idx + 3 < len(nums):

                # REFLEJO del último handle
                if len(current_path.nodes) >= 2:
                    last = current_path.nodes[-1]
                    prev = current_path.nodes[-2]

                    if prev.type == OFFCURVE:
                        h1x = last.x + (last.x - prev.x)
                        h1y = last.y + (last.y - prev.y)
                    else:
                        h1x, h1y = last.x, last.y
                else:
                    h1x, h1y = curr_x, curr_y

                h2x = nums[idx]
                h2y = convert_y(nums[idx+1])
                curr_x = nums[idx+2]
                curr_y = convert_y(nums[idx+3])

                current_path.nodes.append(GSNode((h1x, h1y), type=OFFCURVE))
                current_path.nodes.append(GSNode((h2x, h2y), type=OFFCURVE))
                current_path.nodes.append(GSNode((curr_x, curr_y), type=CURVE))

                idx += 4


        elif cmd == 's':
            if not current_path:
                continue

            idx = 0
            while idx + 3 < len(nums):

                # REFLEJO del último handle
                if len(current_path.nodes) >= 2:
                    last = current_path.nodes[-1]
                    prev = current_path.nodes[-2]

                    if prev.type == OFFCURVE:
                        h1x = last.x + (last.x - prev.x)
                        h1y = last.y + (last.y - prev.y)
                    else:
                        h1x, h1y = last.x, last.y
                else:
                    h1x, h1y = curr_x, curr_y

                h2x = curr_x + nums[idx]
                h2y = curr_y - nums[idx+1]
                curr_x += nums[idx+2]
                curr_y += -nums[idx+3]

                current_path.nodes.append(GSNode((h1x, h1y), type=OFFCURVE))
                current_path.nodes.append(GSNode((h2x, h2y), type=OFFCURVE))
                current_path.nodes.append(GSNode((curr_x, curr_y), type=CURVE))

                idx += 4
                
                
                
        # -------------------------
        # VERTICAL / HORIZONTAL
        # -------------------------
        elif cmd == 'H':
            for x in nums:
                curr_x = x
                current_path.nodes.append(GSNode((curr_x, curr_y), type=LINE))

        elif cmd == 'h':
            for dx in nums:
                curr_x += dx
                current_path.nodes.append(GSNode((curr_x, curr_y), type=LINE))

        elif cmd == 'V':
            for y in nums:
                curr_y = convert_y(y)
                current_path.nodes.append(GSNode((curr_x, curr_y), type=LINE))

        elif cmd == 'v':
            for dy in nums:
                curr_y += -dy
                current_path.nodes.append(GSNode((curr_x, curr_y), type=LINE))

        # -------------------------
        # CUBIC
        # -------------------------
        elif cmd in ['C', 'c']:
            idx = 0
            while idx + 5 < len(nums):
                if cmd == 'C':
                    h1x = nums[idx]
                    h1y = convert_y(nums[idx+1])
                    h2x = nums[idx+2]
                    h2y = convert_y(nums[idx+3])
                    curr_x = nums[idx+4]
                    curr_y = convert_y(nums[idx+5])
                else:
                    h1x = curr_x + nums[idx]
                    h1y = curr_y - nums[idx+1]
                    h2x = curr_x + nums[idx+2]
                    h2y = curr_y - nums[idx+3]
                    curr_x += nums[idx+4]
                    curr_y += -nums[idx+5]

                current_path.nodes.append(GSNode((h1x, h1y), type=OFFCURVE))
                current_path.nodes.append(GSNode((h2x, h2y), type=OFFCURVE))
                current_path.nodes.append(GSNode((curr_x, curr_y), type=CURVE))

                idx += 6

        # -------------------------
        # CLOSE
        # -------------------------
        elif cmd in ['Z', 'z']:
            if current_path:
                current_path.closed = True
                shapes.append(current_path)
                log(f"Closed path with {len(current_path.nodes)} nodes")
                current_path = None

    # último abierto
    if current_path:
        shapes.append(current_path)
        log(f"Open path appended ({len(current_path.nodes)} nodes)")

    log(f"\nTOTAL SHAPES: {len(shapes)}\n")

    return shapes
    
    
# =========================
# NUEVA FUNCIÓN: AJUSTAR yOffset NEGATIVOS (SOLO PARA TRAZADOS Y COMPONENTES)
# =========================

def adjust_negative_yOffset(layer, yOffset):
    """
    Ajusta paths y components hacia abajo cuando yOffset es negativo.
    El anchor NO se modifica.
    """
    if yOffset >= 0:
        return
    
    # Calcular el desplazamiento negativo
    offset_down = abs(yOffset)
    
    # Aplicar desplazamiento vertical a todos los paths
    for shape in layer.shapes:
        shape.applyTransform((1, 0, 0, 1, 0, -offset_down))
    
    # Aplicar desplazamiento vertical a todos los componentes
    for component in layer.components:
        component.applyTransform((1, 0, 0, 1, 0, -offset_down))
    
    print(f"   📉 Ajustado hacia abajo en {offset_down} unidades (yOffset negativo)")


# =========================
# FUNCIÓN DE ALERTA DE CONFIRMACIÓN
# =========================

def show_overwrite_alert(glyph_names):
    """Muestra una alerta preguntando si sobrescribir glifos existentes"""
    if not glyph_names:
        return True
    
    alert = NSAlert.alloc().init()
    alert.setMessageText_("⚠️ Atención: Sobrescritura de glifos")
    
    if len(glyph_names) == 1:
        alert.setInformativeText_(f"El glifo '{glyph_names[0]}' ya existe.\n¿Deseas sobrescribirlo?")
    else:
        names_list = "\n".join([f"  • {name}" for name in glyph_names])
        alert.setInformativeText_(f"Los siguientes glifos ya existen:\n{names_list}\n\n¿Deseas sobrescribirlos?")
    
    alert.addButtonWithTitle_("Sobrescribir")
    alert.addButtonWithTitle_("Cancelar")
    
    response = alert.runModal()
    return response == 1000


# =========================
# DATA - TODOS LOS DIACRÍTICOS
# =========================

glyphData = [
    # BASE DIACRÍTICOS (SVG)
    {
        "name": "dieresis",
        "unicode": "00A8",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 382 168"><path d="M298,168c46,0,84-38,84-84s-38-84-84-84s-85,38-85,84s39,84,85,84ZM85,168c46,0,84-38,84-84s-38-84-84-84s-85,38-85,84s39,84,85,84Z"></path></svg>'
    },
    {
        "name": "dotaccent",
        "unicode": "02D9",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 152 152"><path d="M76,152c42,0,76-34,76-76s-34-76-76-76s-76,34-76,76s34,76,76,76Z"></path></svg>'
    },
    {
        "name": "grave",
        "unicode": "0060",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 193 179"><path d="M179,179l14-14l-112-137c-18-21-29-28-43-28c-24,0-38,18-38,38c0,17,10,29,28,41Z"></path></svg>'
    },
    {
        "name": "acute",
        "unicode": "00B4",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 193 179"><path d="M14,179l151-100c18-12,28-24,28-41c0-20-14-38-38-38c-14,0-25,7-43,28l-112,137Z"></path></svg>'
    },
    {
        "name": "hungarumlaut",
        "unicode": "02DD",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 279 176"><path d="M16,176l111-97c17-14,28-24,28-41c0-20-14-38-38-38c-14,0-29,3-43,28l-74,136ZM140,176l111-97c17-14,28-24,28-41c0-20-14-38-38-38c-14,0-29,3-43,28l-74,136Z"></path></svg>'
    },
    {
        "name": "caroncomb.alt",
        "unicode": None,
        "anchor": "_topright",
        "metric": "capHeight",
        "yOffset": -300,
        "set": "Uppercase",
        "component": "quotesingle"
    },
    {
        "name": "circumflex",
        "unicode": "02C6",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 292 176"><path d="M292,157l-111-157h-69l-112,158l21,18l160-140h-68l158,140Z"></path></svg>'
    },
    {
        "name": "caron",
        "unicode": "02C7",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 317 176"><path d="M0,0l124,176h69l124-176h-44l-146,141h65l-148-141Z"></path></svg>'
    },
    {
        "name": "breve",
        "unicode": "02D8",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 277 157"><path d="M21,0h-21c5,96,61,157,143,157c76,0,128-61,134-157h-21c-5,56-52,92-118,92c-62,0-108-36-117-92Z"></path></svg>'
    },
    {
        "name": "ring",
        "unicode": "02DA",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 204 203"><path d="M102,203c56,0,102-46,102-102s-47-101-102-101s-102,46-102,101c0,56,47,102,102,102ZM102,40c32,0,62,28,62,61s-29,62-62,62s-61-30-61-62s29-61,61-61Z"></path></svg>'
    },
    {
        "name": "tilde",
        "unicode": "02DC",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 342 113"><path d="M342,0h-34c-6,23-24,51-51,51c-21,0-44-12-69-24c-24-12-50-24-77-24c-64,0-101,52-111,110h33c6-27,24-49,54-49c17,0,40,12,64,24c25,12,53,24,79,24c67,0,98-54,112-112Z"></path></svg>'
    },
    {
        "name": "macron",
        "unicode": "00AF",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 257 59"><path d="M0,59h257v-59h-257Z"></path></svg>'
    },
    {
        "name": "cedilla",
        "unicode": "00B8",
        "anchor": "_bottom",
        "metric": "baseline",
        "yOffset": -105,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 210 215"><path d="M86,0l-43,97l14,6c10-3,21-5,31-5c23,0,44,14,44,39c0,33-35,40-60,40c-21,0-40-4-59-11l-13,32c24,9,50,17,76,17c55,0,134-10,134-82c0-51-36-74-83-74c-10,0-21,2-31,5l27-64Z"></path></svg>'
    },
    {
        "name": "ogonek",
        "unicode": "02DB",
        "anchor": "_ogonek",
        "metric": "baseline",
        "yOffset": -65,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 165 135"><path d="M95,0l-32,5c-42,12-63,44-63,66c0,39,28,64,71,64c35,0,72-18,94-47l-7-16c-16,13-37,22-55,22c-27,0-44-15-44-39c0-19,15-40,38-53Z"></path></svg>'
    },
    {
        "name": "dieresiscomb.case",
        "unicode": None,
        "anchor": "_top",
        "metric": "capHeight",
        "yOffset": 65,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 267 106"><path d="M214,106c29,0,53-24,53-53s-24-53-53-53s-54,24-54,53s25,53,54,53ZM54,106c29,0,53-24,53-53s-24-53-53-53s-54,24-54,53s25,53,54,53Z"></path></svg>'
    },
    {
        "name": "gravecomb.case",
        "unicode": None,
        "anchor": "_top",
        "metric": "capHeight",
        "yOffset": 65,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 190 156"><path d="M179,156l11-16l-109-112c-20-20-29-28-43-28c-24,0-38,18-38,38c0,17,9,31,28,41Z"></path></svg>'
    },
    {
        "name": "acutecomb.case",
        "unicode": None,
        "anchor": "_top",
        "metric": "capHeight",
        "yOffset": 65,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 190 156"><path d="M11,156l151-77c19-10,28-24,28-41c0-20-14-38-38-38c-14,0-24,8-43,28l-109,112Z"></path></svg>'
    },
    {
        "name": "hungarumlautcomb.case",
        "unicode": None,
        "anchor": "_top",
        "metric": "capHeight",
        "yOffset": 65,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 267 156"><path d="M14,156l101-77c17-13,28-24,28-41c0-20-14-38-38-38c-14,0-29,2-43,28l-62,115ZM138,156l101-77c17-13,28-24,28-41c0-20-14-38-38-38c-14,0-29,2-43,28l-62,115Z"></path></svg>'
    },
    {
        "name": "circumflexcomb.case",
        "unicode": None,
        "anchor": "_top",
        "metric": "capHeight",
        "yOffset": 65,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 292 156"><path d="M292,137l-111-137h-69l-112,138l21,18l160-120h-68l158,120Z"></path></svg>'
    },
    {
        "name": "caroncomb.case",
        "unicode": None,
        "anchor": "_top",
        "metric": "capHeight",
        "yOffset": 65,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 292 156"><path d="M292,19l-21-19l-158,120h68l-160-120l-21,18l112,138h69Z"></path></svg>'
    },
    {
        "name": "brevecomb.case",
        "unicode": None,
        "anchor": "_top",
        "metric": "capHeight",
        "yOffset": 65,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 277 156"><path d="M21,0h-21c5,89,61,156,143,156c76,0,128-67,134-156h-21c-4,49-51,91-118,91c-63,0-109-42-117-91Z"></path></svg>'
    },
    {
        "name": "tildecomb.case",
        "unicode": None,
        "anchor": "_top",
        "metric": "capHeight",
        "yOffset": 65,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 342 113"><path d="M342,0h-34c-6,23-24,51-51,51c-21,0-44-12-69-24c-24-12-50-24-77-24c-64,0-101,52-111,110h33c6-27,24-49,54-49c17,0,40,12,64,24c25,12,53,24,79,24c67,0,98-54,112-112Z"></path></svg>'
    },
    {
        "name": "macroncomb.case",
        "unicode": None,
        "anchor": "_top",
        "metric": "capHeight",
        "yOffset": 65,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 317 59"><path d="M0,59h317v-59h-317Z"></path></svg>'
    },
    {
        "name": "strokeshortcomb.case",
        "unicode": None,
        "anchor": "_center",
        "metric": "xHeight",
        "yOffset": -130,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 392 25"><path d="M0,0v25h392v-25Z"></path></svg>'
    },
    {
        "name": "strokelongcomb.case",
        "unicode": None,
        "anchor": "_center",
        "metric": "capHeight",
        "yOffset": -180,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 683 25"><path d="M0,0v25h683v-25Z"></path></svg>'
    },
    {
        "name": "slashlongcomb.case",
        "unicode": None,
        "anchor": "_center",
        "metric": "capHeight",
        "yOffset": -358,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 649 732"><path d="M0,714l18,18l102-115l19-8l389-460l28-25l93-107l-17-17l-92,106l-24,20l-390,460l-24,13Z"></path></svg>'
    },
    {
        "name": "dotaccent.case",
        "unicode": None,
        "anchor": "_top",
        "metric": "capHeight",
        "yOffset": 65,
        "set": "Uppercase",
        "svg": '<svg viewBox="0 0 137 136"><path d="M69,136c37,0,68-31,68-68s-31-68-68-68s-69,31-69,68s32,68,69,68Z"></path></svg>'
    },
    {
        "name": "commaaccentcomb",
        "unicode": "0326",
        "anchor": "_bottom",
        "metric": "baseline",
        "yOffset": -122,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 105 169"><path d="M23,152l10,17c21-11,43-34,57-59c9-16,15-39,15-59c0-31-20-51-51-51c-33,0-54,20-54,51c0,29,19,48,49,48c7,0,11-2,11-2c-5,23-20,44-37,55Z"></path></svg>'
    },
    {
        "name": "slashlongcomb",
        "unicode": "0338",
        "anchor": "_center",
        "metric": "xHeight",
        "yOffset": 0,
        "set": "Lowercase",
        "svg": '<svg viewBox="0 0 437 447"><path d="M0,433l15,14l70-71l24-15l232-253l24-19l72-74l-15-15l-69,71l-27,22l-234,255l-20,11Z"></path></svg>'
    },

    # COMPONENTES (comb)
    {
        "name": "dieresiscomb",
        "unicode": "0308",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "dieresis"
    },
    {
        "name": "dotaccentcomb",
        "unicode": "0307",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "dotaccent"
    },
    {
        "name": "gravecomb",
        "unicode": "0300",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "grave"
    },
    {
        "name": "acutecomb",
        "unicode": "0301",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "acute"
    },
    {
        "name": "hungarumlautcomb",
        "unicode": "030B",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "hungarumlaut"
    },
    {
        "name": "circumflexcomb",
        "unicode": "0302",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "circumflex"
    },
    {
        "name": "caroncomb",
        "unicode": "030C",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "caron"
    },
    {
        "name": "brevecomb",
        "unicode": "0306",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "breve"
    },
    {
        "name": "ringcomb",
        "unicode": "030A",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "ring"
    },
    {
        "name": "tildecomb",
        "unicode": "0303",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "tilde"
    },
    {
        "name": "macroncomb",
        "unicode": "0304",
        "anchor": "_top",
        "metric": "xHeight",
        "yOffset": 65,
        "set": "Lowercase",
        "component": "macron"
    },
    {
        "name": "cedillacomb",
        "unicode": "0327",
        "anchor": "_bottom",
        "metric": "baseline",
        "yOffset": 0,
        "set": "Lowercase",
        "component": "cedilla"
    },
    {
        "name": "ogonekcomb",
        "unicode": "0328",
        "anchor": "_ogonek",
        "metric": "baseline",
        "yOffset": 0,
        "set": "Lowercase",
        "component": "ogonek"
    }
]


# =========================
# UI
# =========================

class Builder(object):

    def __init__(self):
        self.w = vanilla.Window((300, 120), "Diacritics FINAL - v16 (Anchor Fixed)")

        self.w.popup = vanilla.PopUpButton((20, 20, -20, 25),
                                           ["Both", "Uppercase", "Lowercase"])
        self.w.popup.set(0)

        self.w.button = vanilla.Button((20, 60, -20, 25),
                                      "Build",
                                      callback=self.build)

        self.w.open()

    def build(self, sender):
        font = Glyphs.font
        if not font:
            print("❌ No hay fuente abierta")
            Glyphs.showNotification("❌ Error", "No hay fuente abierta")
            return
        
        selection = self.w.popup.getItem()
    
        # Verificar sobrescritura
        existing_glyphs = []
        for data in glyphData:
            if selection != "Both" and data["set"] != selection:
                continue
            if font.glyphs[data["name"]]:
                existing_glyphs.append(data["name"])
    
        if existing_glyphs:
            if not show_overwrite_alert(existing_glyphs):
                print("❌ Cancelado")
                return

        count = 0

        for data in glyphData:
            if selection != "Both" and data["set"] != selection:
                continue

            glyph = font.glyphs[data["name"]]
            if not glyph:
                glyph = GSGlyph(data["name"])
                font.glyphs.append(glyph)

            glyph.category = "Mark"
            glyph.subCategory = "Nonspacing"
        
            if data.get("unicode"):
                glyph.unicode = data["unicode"]

            for master in font.masters:
                layer = glyph.layers[master.id]
                layer.clear()
                layer.anchors = []

                # =========================
                # COMPONENTES
                # =========================
                if "component" in data:

                    component_name = data["component"]
                    component_glyph = font.glyphs[component_name]

                    if not component_glyph:
                        print(f"⚠️ Componente '{component_name}' no encontrado")
                        continue

                    component = GSComponent(component_name)
                    component.automaticAlignment = False
                    layer.components.append(component)

                    # Asegurar ancho mínimo antes de alinear
                    layer.width = max(200, component.componentLayer.bounds.size.width + SIDE_BEARING * 2)

                    component_layer = component.componentLayer
                    useAutoAlign = False

                    if component_layer:
                        anchor_names = [a.name for a in component_layer.anchors]

                        if data["anchor"] == "_topright" and "_topright" in anchor_names:
                            useAutoAlign = True
                        elif data["anchor"] == "_top" and "_top" in anchor_names:
                            useAutoAlign = True

                    if useAutoAlign:
                        component.automaticAlignment = True
                        print(f"🔗 AutoAlign: {data['name']} ({data['anchor']})")

                    else:
                        component.automaticAlignment = False

                        if component_layer:
                            bounds = component_layer.bounds

                            if bounds.size.width > 0:

                                if data["anchor"] == "_topright":
                                    # 👉 alineación derecha (NO centrado)
                                    shiftX = (layer.width - SIDE_BEARING) - (bounds.origin.x + bounds.size.width)
                                    print(f"➡️ Right align fallback: {data['name']}")
                                else:
                                    # 👉 centrado normal
                                    shiftX = (layer.width - bounds.size.width) / 2 - bounds.origin.x
                                    print(f"📍 Centrado: {data['name']}")

                                component.applyTransform((1, 0, 0, 1, shiftX, 0))

                    
                        # calcular desplazamiento horizontal
                        if data["anchor"] == "_topright":
                            shiftX = (layer.width - SIDE_BEARING) - (bounds.origin.x + bounds.size.width)
                        else:
                            shiftX = (layer.width - bounds.size.width) / 2 - bounds.origin.x

                        # aplicar X + Y juntos (clave)
                        shiftY = data.get("yOffset", 0)

                        component.applyTransform((1, 0, 0, 1, shiftX, shiftY))
                        
                        # 👇 NUEVO: ajustar yOffset negativo (SOLO para trazados/componentes)
                        adjust_negative_yOffset(layer, shiftY)

                # =========================
                # SVG PATHS
                # =========================
                elif "svg" in data:

                    shapes = parse_svg_and_build_path(data["svg"])
                    if not shapes:
                        print(f"❌ No shapes: {data['name']}")
                        continue

                    # =========================
                    # POSICIÓN BASE (SIN OFFSET)
                    # =========================
                    if data["metric"] == "xHeight":
                        base = master.xHeight
                    elif data["metric"] == "capHeight":
                        base = master.capHeight
                    else:
                        base = 0

                    yOffset = data.get("yOffset", 0)

                    # aplicar SOLO base primero
                    for shape in shapes:
                        shape.applyTransform((1, 0, 0, 1, 0, base))
                        layer.shapes.append(shape)

                    # =========================
                    # MÉTRICAS + CENTRADO X
                    # =========================
                    bounds = layer.bounds

                    if bounds.size.width > 0:
                        layer.width = max(200, bounds.size.width + SIDE_BEARING * 2)

                        shiftX = SIDE_BEARING - bounds.origin.x

                        # aplicar X + YOffset FINAL (CLAVE)
                        for shape in layer.shapes:
                            shape.applyTransform((1, 0, 0, 1, shiftX, yOffset))

                    else:
                        layer.width = SIDE_BEARING * 2
                        
                    # 👇 NUEVO: ajustar yOffset negativo (SOLO para trazados/componentes)
                    adjust_negative_yOffset(layer, yOffset)

                # =========================
                # ANCHORS - AHORA SIN yOffset
                # =========================
                anchor = GSAnchor()
                anchor.name = data["anchor"]

                # X - sin cambios
                if data["anchor"] == "_topright":
                    anchorX = layer.width - SIDE_BEARING
                else:
                    anchorX = layer.width / 2

                # Y - AHORA SIN yOffset, solo métricas de fuente
                if data["anchor"] == "_center":
                    if data["metric"] == "xHeight":
                        anchorY = master.xHeight / 2
                    elif data["metric"] == "capHeight":
                        anchorY = master.capHeight / 2
                    else:
                        anchorY = 0

                elif data["anchor"] in ["_bottom", "_ogonek"]:
                    # Anchor en la baseline SIN yOffset
                    anchorY = 0

                elif data["anchor"] == "_topright":
                    if data["metric"] == "capHeight":
                        anchorY = master.capHeight
                    else:
                        anchorY = master.xHeight

                else:  # _top
                    if data["metric"] == "xHeight":
                        anchorY = master.xHeight
                    elif data["metric"] == "capHeight":
                        anchorY = master.capHeight
                    else:
                        anchorY = 0

                anchor.position = (anchorX, anchorY)
                layer.anchors.append(anchor)
                
                print(f"   📌 Anchor '{data['anchor']}' en Y={anchorY} (sin yOffset)")

            count += 1
            print(f"✅ {data['name']}")

        Glyphs.showNotification("✅ Completado", f"{count} glifos construidos")

Builder()