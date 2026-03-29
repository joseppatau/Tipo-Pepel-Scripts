# MenuTitle: Kern Coach v1
# -*- coding: utf-8 -*-
# Description: Applies negative kerning adjustments to reduce excessive spacing between glyph pairs.  
Uses geometric distance calculations to determine optimal spacing and avoid over-tightening.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

import math
import re
import json
import time
from GlyphsApp import *
from vanilla import *
from AppKit import *
from AppKit import NSAlert, NSAlertStyleInformational, NSAlertFirstButtonReturn
from AppKit import NSAlert, NSInformationalAlertStyle
from GlyphsApp import Glyphs





def _dbg_tab(msg):
    print(f"[TAB DEBUG] {msg}")

def dbg(*args):
    if DEBUG_SWITCH:
        print("[SWITCH DEBUG]", *args)


LATINUPPERCASE = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

LATINLOWERCASE = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

CANONICALNUMBERS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 
                   'eight', 'nine']

CANONICALPUNCTUATION = [
    'hyphen', 'endash', 'emdash', 'underscore',
    'parenleft', 'parenright', 'braceleft', 'braceright',
    'bracketleft', 'bracketright', 'quotesinglbase',
    'quotedblbase', 'quotedblleft', 'quotedblright',
    'quoteleft', 'quoteright', 'guillemetleft', 'guillemetright',
    'guilsinglleft', 'guilsinglright', 'quotedbl', 'quotesingle',
    'period', 'comma', 'colon', 'semicolon', 'ellipsis',
    'exclam', 'exclamdown', 'question', 'questiondown',
    'periodcentered', 'bullet', 'asterisk', 'numbersign',
    'slash', 'backslash'
]



# ============================================================
#         BLOCK / COLUMN LAYOUT POLICY (GLOBAL)
# ============================================================

BLOCK_COLUMNS = 4
BLOCK_GAP_SPACES = 4
BLOCK_GAP = "  " * BLOCK_GAP_SPACES

# ESPAIS PER HIDE EXISTING PAIRS (pots canviar-ho independentment)
HIDE_GAP_SPACES = 7
HIDE_GAP = " " * HIDE_GAP_SPACES


def join_blocks(blocks):
    """Join blocks with gap BEFORE each block (except first)."""
    filtered = [b for b in blocks if b]
    if not filtered:
        return ""
    
    result = filtered[0]
    for block in filtered[1:]:
        result += BLOCK_GAP + block
    
    return result


def normalize_to_columns(items, columns):
    """
    Split items into rows of `columns`.
    ONLY the last row may be padded.
    Padding is added on the LEFT.
    """
    if not items:
        return

    rows = []
    for i in range(0, len(items), columns):
        rows.append(items[i:i + columns])

    last = rows[-1]
    missing = columns - len(last)
    if missing > 0:
        rows[-1] = [""] * missing + last

    for row in rows:
        yield row


def render_pairs_blocks(lines, position, pairs_left, pairs_right):
    def render_block(pairs):
        if not pairs:
            return
        for row in normalize_to_columns(pairs, BLOCK_COLUMNS):
            filtered = [b for b in row if b]
            if filtered:
                line = filtered[0]
                for block in filtered[1:]:
                    line += BLOCK_GAP + block
                lines.append(line)

    if position == "left":
        render_block(pairs_left)

    elif position == "right":
        render_block(pairs_right)

    else:  # both
        render_block(pairs_left)

        if pairs_left and pairs_right:
            lines.append("")

        render_block(pairs_right)




def split_blocks(line):
    """Split a line into blocks using global block gap policy."""
    BLOCK_SPLIT_REGEX = r'\s{3,}'
    return [b for b in re.split(BLOCK_SPLIT_REGEX, line.strip()) if b]




            
            

# ============================================================
#           MOTOR KERN BASE GTP - GEOMETRY OPTIMIZED
# ============================================================

def distance(A, B):
    return math.hypot(B[0]-A[0], B[1]-A[1])

def closestPointOnSegment(A, B, P):
    ABx = B[0] - A[0]
    ABy = B[1] - A[1]

    denom = ABx*ABx + ABy*ABy
    if denom == 0:
        return A

    t = ((P[0] - A[0]) * ABx + (P[1] - A[1]) * ABy) / denom
    t = max(0, min(1, t))

    return (A[0] + t * ABx, A[1] + t * ABy)


def segmentDistance(a1, a2, b1, b2):
    dmin = float("inf")

    for P in (a1, a2):
        Q = closestPointOnSegment(b1, b2, P)
        dmin = min(dmin, distance(P, Q))

    for P in (b1, b2):
        Q = closestPointOnSegment(a1, a2, P)
        dmin = min(dmin, distance(P, Q))

    return dmin


def bbox(p1, p2):
    return (
        min(p1[0], p2[0]),
        min(p1[1], p2[1]),
        max(p1[0], p2[0]),
        max(p1[1], p2[1]),
    )


def bboxOverlap(b1, b2, pad=0):
    return (
        b1[0] <= b2[2] + pad and
        b1[2] >= b2[0] - pad and
        b1[1] <= b2[3] + pad and
        b1[3] >= b2[1] - pad
    )


def getSegments(layer):
    segs = []

    for p in layer.paths:
        nodes = p.nodes
        if not nodes:
            continue

        pts = [(n.x, n.y) for n in nodes]
        count = len(pts)

        if p.closed:
            rng = range(count)
        else:
            rng = range(count - 1)

        for i in rng:
            a = pts[i]
            b = pts[(i + 1) % count]
            segs.append((a, b, bbox(a, b)))

    return segs


def minDistanceBetweenLayers(layer1, layer2, dx, liApache2=10000):
    segs1 = getSegments(layer1)
    segs2_raw = getSegments(layer2)

    if not segs1 or not segs2_raw:
        return liApache2

    segs2 = []
    for a, b, bb in segs2_raw:
        a2 = (a[0] + dx, a[1])
        b2 = (b[0] + dx, b[1])
        segs2.append((a2, b2, bbox(a2, b2)))

    dmin = float("inf")

    for a1, a2, bb1 in segs1:
        for b1, b2, bb2 in segs2:

            if not bboxOverlap(bb1, bb2, pad=dmin):
                continue

            d = segmentDistance(a1, a2, b1, b2)

            if d < dmin:
                dmin = d
                if dmin <= 0:
                    return 0.0

    return dmin


def margin_for_pair(font, masterID, leftName, rightName):
    gL = font.glyphs[leftName]
    gR = font.glyphs[rightName]
    if not gL or not gR:
        return None

    layerL = gL.layers[masterID]
    layerR = gR.layers[masterID]

    try:
        layerL = layerL.copyDecomposedLayer()
    except:
        pass
    try:
        layerR = layerR.copyDecomposedLayer()
    except:
        pass

    dx = layerL.width
    return minDistanceBetweenLayers(layerL, layerR, dx)

# ============================================================
#           MAIN UNIFIED CLASS
# ============================================================

class KernCoach(object):
    
    
    def _debug(self, category, msg):
        """Método centralizado para debug"""
        # Bandera general que activa todo el debug
        DEBUG_ALL = getattr(self, "DEBUG_ALL", False)
    
        # Bandera específica para esta categoría
        category_flag = False
    
        # Mapeo de categorías a banderas
        if category == "EXCLUSION":
            category_flag = getattr(self, "DEBUG_EXCLUSION", True)
        elif category == "HAS_KERNING":
            category_flag = getattr(self, "DEBUG_HAS_KERNING", False) or getattr(self, "DEBUG_HIDE", False)
        elif category == "NO_KERN":
            category_flag = getattr(self, "DEBUG_NO_KERN", False)
        elif category == "HIDE":
            category_flag = getattr(self, "DEBUG_HIDE", True)
        elif category == "ERROR":
            category_flag = True  # Los errores siempre se muestran
        elif category == "GENERAL":
            category_flag = True  # Los mensajes generales siempre se muestran
        elif category == "TAB":
            category_flag = getattr(self, "DEBUG_TAB", True)
    
        if DEBUG_ALL or category_flag:
            print(f"[{category} DEBUG] {msg}")

    def debug_no_kern(self, msg):
        """Función de debug para NoKern - mantenida por compatibilidad"""
        self._debug("NO_KERN", msg)

    def debug_exclusion(self, glyph_name, side, excluded_info, result, reason=""):
        """Debug detallado para exclusiones"""
        if getattr(self, "DEBUG_EXCLUSION", False):
            exglyphs, exgroups = excluded_info
            self._debug("EXCLUSION", f"\nGlyph: {glyph_name}, Side: {side}")
            self._debug("EXCLUSION", f"  Excluded glyphs: {sorted(exglyphs)[:5]}{'...' if len(exglyphs) > 5 else ''}")
            self._debug("EXCLUSION", f"  Excluded groups: {sorted(exgroups)[:5]}{'...' if len(exgroups) > 5 else ''}")
            self._debug("EXCLUSION", f"  Result: {'EXCLUDED' if result else 'NOT excluded'}")
            if reason:
                self._debug("EXCLUSION", f"  Reason: {reason}")
            self._debug("EXCLUSION", "-" * 50)
    
    
    def _filter_for_second_position(self, neighbors, font):
        filtered = []
    
        for name in neighbors:
            if name not in font.glyphs:
                continue
        
            glyph = font.glyphs[name]
            nombre_base = name.split('.')[0]
        
            if hasattr(glyph, 'leftKerningGroup') and glyph.leftKerningGroup:
                grupo_sin_arroba = glyph.leftKerningGroup.lstrip('@')
                if grupo_sin_arroba.lower() == nombre_base.lower():
                    filtered.append(name)
            else:
                pass
    
        return filtered
        
        

    def _filter_for_first_position(self, neighbors, font):
        filtered = []
    
        for name in neighbors:
            if name not in font.glyphs:
                continue
        
            glyph = font.glyphs[name]
            nombre_base = name.split('.')[0]
        
            if hasattr(glyph, 'rightKerningGroup') and glyph.rightKerningGroup:
                grupo_sin_arroba = glyph.rightKerningGroup.lstrip('@')
                if grupo_sin_arroba.lower() == nombre_base.lower():
                    filtered.append(name)
            else:
                pass
    
        return filtered
        
        

    def _filter_for_both_positions(self, neighbors, font):
        filtered = []
    
        for name in neighbors:
            if name not in font.glyphs:
                continue
        
            glyph = font.glyphs[name]
            nombre_base = name.split('.')[0]
        
            has_left_match = False
            has_right_match = False
        
            if hasattr(glyph, 'leftKerningGroup') and glyph.leftKerningGroup:
                left_grupo = glyph.leftKerningGroup.lstrip('@')
                has_left_match = (left_grupo.lower() == nombre_base.lower())
        
            if hasattr(glyph, 'rightKerningGroup') and glyph.rightKerningGroup:
                right_grupo = glyph.rightKerningGroup.lstrip('@')
                has_right_match = (right_grupo.lower() == nombre_base.lower())
        
            if has_left_match and has_right_match:
                filtered.append(name)
    
        return filtered
    
    
    
    def kerning_group_is_used(self, font, master_id, group_key):
        return True 
    
    


    def generatePairsGenerator(self):
        font = Glyphs.font
        if not font:
            self._debug("ERROR", "❌ No hay fuente activa.")
            return

        master_id = font.selectedFontMaster.id
        tabs_created = 0

        # -----------------------------
        # Helpers CORRECTOS para Boss - VERSIÓN CORREGIDA
        # -----------------------------
        def is_boss_first_position(glyph):
            """Glifo en PRIMERA posición → mirar SOLO rightKerningGroup"""
            if not glyph:
                return False
            # Solo verificar rightKerningGroup
            grp = glyph.rightKerningGroup
            if not grp:
                return False
            grupo_limpio = grp.lstrip("@")
            nombre_limpio = self._get_glyph_base(glyph.name)
            return grupo_limpio.lower() == nombre_limpio.lower()

        def is_boss_second_position(glyph):
            """Glifo en SEGUNDA posición → mirar SOLO leftKerningGroup"""
            if not glyph:
                return False
            # Solo verificar leftKerningGroup
            grp = glyph.leftKerningGroup
            if not grp:
                return False
            grupo_limpio = grp.lstrip("@")
            nombre_limpio = self._get_glyph_base(glyph.name)
            return grupo_limpio.lower() == nombre_limpio.lower()

        def is_boss_punctuation(glyph):
            """Para puntuación sin grupos de kerning"""
            if not glyph:
                return False
            nombre_base = self._get_glyph_base(glyph.name)
            # Si no tiene grupos de kerning y es un glifo base (no variación)
            if (not glyph.rightKerningGroup and 
                not glyph.leftKerningGroup and 
                '.' not in glyph.name):
                # Verificar si está en la lista de puntuación canónica
                if nombre_base in CANONICALPUNCTUATION:
                    return True
            return False

        # DEBUG: Mostrar configuración
        position = ["left", "right", "both"][self.tab1.positionPopup.get()]
        hide_existing = bool(self.tab1.hideKernedPairsCheck.get())
        show_only_boss = bool(self.tab1.showOnlyBossCheck.get())
    
        self._debug("GENERAL", f"\n{'='*60}")
        self._debug("GENERAL", f"CONFIGURACIÓN 'show only @ boss':")
        self._debug("GENERAL", f"  Estado del checkbox: {show_only_boss}")
        self._debug("GENERAL", f"  Position: {position}")
        self._debug("GENERAL", f"{'='*60}")

        # -----------------------------

        DEBUG_EXCLUSION_ORIGINAL = getattr(self, "DEBUG_EXCLUSION", False)
        self.DEBUG_EXCLUSION = True

        (ex_first_glyphs, ex_first_groups), (ex_second_glyphs, ex_second_groups) = self._excluded_groups()

        self._debug("TAB", f"Excluded first (glyphs): {sorted(ex_first_glyphs)[:5]}{'...' if len(ex_first_glyphs) > 5 else ''}")
        self._debug("TAB", f"Excluded first (groups): {sorted(ex_first_groups)[:5]}{'...' if len(ex_first_groups) > 5 else ''}")
        self._debug("TAB", f"Excluded second (glyphs): {sorted(ex_second_glyphs)[:5]}{'...' if len(ex_second_glyphs) > 5 else ''}")
        self._debug("TAB", f"Excluded second (groups): {sorted(ex_second_groups)[:5]}{'...' if len(ex_second_groups) > 5 else ''}")

        baseGlyphs = [
            b.strip()
            for b in self.tab1.baseInput.get().split(",")
            if b.strip() and b.strip() in font.glyphs
        ]

        if not baseGlyphs:
            self._debug("WARNING", "⚠️ Ningún glifo base válido.")
            return

        categories = []
        if self.tab1.latinUpperCheck.get(): categories.append("Latin Upper")
        if self.tab1.latinLowerCheck.get(): categories.append("Latin Lower")
        if self.tab1.numCheck.get(): categories.append("Numbers")
        if self.tab1.puncCheck.get(): categories.append("Punctuation")
        if self.tab1.symCheck.get(): categories.append("Symbols")
        if self.tab1.myGlyphsCheck.get(): categories.append("My Glyphs")
        if self.tab1.cyrillicUpperCheck.get(): categories.append("Cyrillic Upper")
        if self.tab1.cyrillicLowerCheck.get(): categories.append("Cyrillic Lower")

        if not categories:
            self._debug("WARNING", "⚠️ No categories selected.")
            return

        # Obtener vecinos para CADA categoría
        category_neighbors = {}
        for category in categories:
            neighbors = self.get_neighbors_by_category(category)
            neighbors = self._filter_out_variations(neighbors, font)
            category_neighbors[category] = neighbors
            
        for base in baseGlyphs:
            self._debug("TAB", f"\n→ Base '{base}'")
        
            if '.' in base:
                self._debug("TAB", f"  Base is a variation, skipping")
                continue
        
            if base not in font.glyphs:
                self._debug("TAB", "  base not in font → skip")
                continue

            base_glyph = font.glyphs[base]
            base_is_sc = base_glyph.subCategory == "Smallcaps"

            # Para CADA categoría, generar las parejas
            for category in categories:
                effective_neighbors = category_neighbors[category]
            
                if base_is_sc:
                    # Si es smallcaps, usar solo vecinos smallcaps
                    effective_neighbors = sorted(
                        g.name for g in font.glyphs if g.subCategory == "Smallcaps"
                    )

                pairs_left = []
                pairs_right = []

                for n in effective_neighbors:
                    if n == base or n not in font.glyphs:
                        continue

                    glyph_n = font.glyphs[n]
                    nombre_base_n = self._get_glyph_base(n)

                    if position in ("left", "both"):
                        # Verificar exclusión
                        excluded_as_second = self._is_glyph_excluded(n, (ex_second_glyphs, ex_second_groups), "second")
                        excluded_base_as_first = self._is_glyph_excluded(base, (ex_first_glyphs, ex_first_groups), "first")
                
                        if excluded_as_second:
                            continue
            
                        if excluded_base_as_first:
                            continue
            
                        if show_only_boss:
                            # CORRECCIÓN IMPORTANTE: Para n como SEGUNDO en el par: 
                            # solo verificar leftKerningGroup (no rightKerningGroup!)
                            if is_boss_second_position(glyph_n) or (category == "Punctuation" and is_boss_punctuation(glyph_n)):
                                # DEBUG: Mostrar qué se encontró
                                self._debug("TAB", f"  [BOSS CHECK] '{n}' como SEGUNDO: leftKerningGroup='{glyph_n.leftKerningGroup}' vs base='{nombre_base_n}' → ACEPTADO")
                                pairs_left.append(self.build_pair_line(base, n))
                            else:
                                self._debug("TAB", f"  [BOSS CHECK] '{n}' como SEGUNDO: leftKerningGroup='{glyph_n.leftKerningGroup}' vs base='{nombre_base_n}' → RECHAZADO")
                        else:
                            pairs_left.append(self.build_pair_line(base, n))

                    if position in ("right", "both"):
                        # Verificar exclusión
                        excluded_as_first = self._is_glyph_excluded(n, (ex_first_glyphs, ex_first_groups), "first")
                        excluded_base_as_second = self._is_glyph_excluded(base, (ex_second_glyphs, ex_second_groups), "second")
                
                        if excluded_as_first:
                            continue
            
                        if excluded_base_as_second:
                            continue
            
                        if show_only_boss:
                            # CORRECCIÓN IMPORTANTE: Para n como PRIMERO en el par:
                            # solo verificar rightKerningGroup (no leftKerningGroup!)
                            if is_boss_first_position(glyph_n) or (category == "Punctuation" and is_boss_punctuation(glyph_n)):
                                # DEBUG: Mostrar qué se encontró
                                self._debug("TAB", f"  [BOSS CHECK] '{n}' como PRIMERO: rightKerningGroup='{glyph_n.rightKerningGroup}' vs base='{nombre_base_n}' → ACEPTADO")
                                pairs_right.append(self.build_pair_line(n, base))
                            else:
                                self._debug("TAB", f"  [BOSS CHECK] '{n}' como PRIMERO: rightKerningGroup='{glyph_n.rightKerningGroup}' vs base='{nombre_base_n}' → RECHAZADO")
                        else:
                            pairs_right.append(self.build_pair_line(n, base))

                pairs_left = sorted(set(pairs_left))
                pairs_right = sorted(set(pairs_right))

                # DEBUG: Resumen
                if show_only_boss:
                    self._debug("TAB", f"  Resultados 'show only @ boss' para categoría '{category}':")
                    self._debug("TAB", f"    Pares izquierda (base + vecino): {len(pairs_left)}")
                    self._debug("TAB", f"    Pares derecha (vecino + base): {len(pairs_right)}")

                if not pairs_left and not pairs_right:
                    continue

                if hide_existing:
                    pairs_left = self.filter_pairs_with_existing_kerning(
                        pairs_left, font, master_id,
                        boss_only=False, base=base,
                        category=category, tab=None
                    )
                    pairs_right = self.filter_pairs_with_existing_kerning(
                        pairs_right, font, master_id,
                        boss_only=False, base=base,
                        category=category, tab=None
                    )

                if not pairs_left and not pairs_right:
                    continue

                self._debug("TAB", "  → creating tab for category")
                new_tab = font.newTab("")

                lines = []
                lines.extend(self.build_info_block(base, category))

                render_pairs_blocks(
                    lines=lines,
                    position=position,
                    pairs_left=pairs_left,
                    pairs_right=pairs_right,
                )

                new_tab.text = "\n".join(lines)
                tabs_created += 1

                try:
                    feature_names = self.getFeatureNames()
                    feature_index = self.tab1.featurePopup.get()
                    if 0 <= feature_index < len(feature_names):
                        fName = feature_names[feature_index]
                        if fName != "No features":
                            new_tab.features = [fName]
                            self._debug("TAB", f"  Feature activada: {fName}")
                except Exception as e:
                    self._debug("ERROR", f"  ⚠️ Error activando feature: {e}")

        # Restaurar estado original del debug
        self.DEBUG_EXCLUSION = DEBUG_EXCLUSION_ORIGINAL

        self._debug("GENERAL", f"\n{'='*80}")
        self._debug("GENERAL", f"✅ TOTAL: Created {tabs_created} tabs")
        if tabs_created == 0:
            self._debug("WARNING", "⚠️ No se crearon tabs.")
            
             
              
                
    
    def _get_glyph_base(self, glyph_name):
        """Obtiene la parte base del nombre del glifo (sin extensión)"""
        if not glyph_name:
            return ""
        return glyph_name.split('.')[0]
        
        
        
    
    def _get_glyph_variants(self, font, base_name):
        """Obtiene todas las variantes de un glifo base"""
        variants = []
    
        for glyph in font.glyphs:
            if glyph.name == base_name:
                continue  # Saltar el glifo base
        
            # Verificar si es una variante del glifo base
            # Ejemplo: base_name = "l", variantes = "l.sc", "l.ss01", "l.alt"
            if glyph.name.startswith(base_name + '.'):
                variants.append(glyph.name)
    
        return variants
    
    def build_info_block(self, base_glyph, category):
        """Construye el bloque de información para la pestaña"""
        lines = []
    
        # Función para añadir espacios entre caracteres
        def spaced_text(text):
            return ' '.join(list(text))
    
        # Línea de categoría con espacios
        lines.append(f"{spaced_text('Category:')} {spaced_text(category)}")
    
        # Línea de glifo base con espacios
        lines.append(f"{spaced_text('BASE:')} /{base_glyph}")
    
        # Obtener configuración de posición
        position_index = self.tab1.positionPopup.get()
        position_names = ["Left", "Right", "Both"]
        position = position_names[position_index] if position_index < len(position_names) else "Both"
        lines.append(f"{spaced_text('Position:')} {spaced_text(position)}")
    
        # Obtener configuración de ocultar pares existentes
        hide_existing = bool(self.tab1.hideKernedPairsCheck.get())
        hide_text = "True" if hide_existing else "False"
        lines.append(f"{spaced_text('Hide existing pairs:')} {spaced_text(hide_text)}")
    
        # Obtener configuración de solo boss
        show_only_boss = bool(self.tab1.showOnlyBossCheck.get())
        boss_text = "True" if show_only_boss else "False"
        lines.append(f"{spaced_text('Show only @ boss:')} {spaced_text(boss_text)}")
    
        # Línea vacía para separación
        lines.append("")
    
        return lines
    
    
    
    def _updateBaseGlyphsFromUI(self):
        try:
            inner = self.tab2.listContainer.innerGroup
            
            for i in range(len(self.baseglyphslist)):
                name_field_name = f"name_{i}"
                if hasattr(inner, name_field_name):
                    name_field = getattr(inner, name_field_name)
                    new_name = name_field.get().strip()
                    if new_name != self.baseglyphslist[i].get('name', ''):
                        self.baseglyphslist[i]['name'] = new_name
                
                cat_field_name = f"cat_{i}"
                if hasattr(inner, cat_field_name):
                    cat_field = getattr(inner, cat_field_name)
                    categories = ["Uppercase", "Lowercase", "Numbers", "Punctuation", 
                                 "Symbols", "My Glyphs", "Cyrillic Upper", "Cyrillic Lower"]
                    cat_index = cat_field.get()
                    if 0 <= cat_index < len(categories):
                        self.baseglyphslist[i]['category'] = categories[cat_index]
                
                cb_field_name = f"cb_{i}"
                if hasattr(inner, cb_field_name):
                    try:
                        cb_field = getattr(inner, cb_field_name)
                        self.baseglyphslist[i]['selected'] = bool(cb_field.get())
                    except Exception:
                        pass
            
        except Exception as e:
            pass
   
    def masterDidChange_(self, notification):
        try:
            self.refreshMargin(None)
        except Exception as e:
            pass

    def getKerningGroupMembers(self, glyph, side="left"):
        font = Glyphs.font
        if not font or not glyph:
            return []

        group = glyph.leftKerningGroup if side == "left" else glyph.rightKerningGroup
        if not group:
            return []

        members = []
        for g in font.glyphs:
            if side == "left" and g.leftKerningGroup == group:
                members.append(g.name)
            elif side == "right" and g.rightKerningGroup == group:
                members.append(g.name)

        return sorted(set(members))



    def replaceGlyphAtCursor(self, newGlyphName):
        font = Glyphs.font
        tab = font.currentTab
        if not font or not tab:
            return

        if newGlyphName not in font.glyphs:
            return

        layers = tab.layers
        sel = tab.selectedRange()
        loc = sel.location

        if loc >= len(layers):
            return

        layers[loc].parent = font.glyphs[newGlyphName]
        tab.layers = layers
        tab.setSelectedRange_(NSRange(loc, 0))
        
        











    def refreshMargin(self, sender):
        font = Glyphs.font

        if not font:
            self.tab1.resultLabel.set("margin: — • kern: —")
            return

        left_text = self.tab1.currentInput.get()
        right_text = self.tab1.currentInputRight.get()

        if not left_text or not right_text:
            self.tab1.resultLabel.set("margin: — • kern: —")
            return

        left_text = left_text.strip()
        right_text = right_text.strip()

        if not left_text or not right_text:
            self.tab1.resultLabel.set("margin: — • kern: —")
            return

        def char_to_glyph(font, c):
            try:
                g = font.glyphForCharacter_(ord(c))
                return g
            except Exception:
                return None

        cL = left_text[0]
        cR = right_text[0]

        gL = char_to_glyph(font, cL)
        gR = char_to_glyph(font, cR)

        if not gL or not gR:
            self.tab1.resultLabel.set("margin: — • kern: —")
            return

        L = gL.name
        R = gR.name

        try:
            master_id = font.selectedFontMaster.id
        except Exception:
            self.tab1.resultLabel.set("margin: ERR • kern: —")
            return

        layerL = gL.layers[master_id]
        layerR = gR.layers[master_id]

        if not layerL or not layerR:
            self.tab1.resultLabel.set("margin: — • kern: —")
            return

        try:
            m = margin_for_pair(font, master_id, L, R)
        except Exception:
            self.tab1.resultLabel.set("margin: ERR • kern: —")
            return

        if m is None or m >= 10000:
            m_disp = "—"
        else:
            m_disp = str(int(round(m)))

        try:
            k = font.kerningForPair(master_id, L, R)
        except Exception:
            k = None

        if k is None:
            k_disp = "—"
        else:
            k_disp = str(int(round(k)))

        result = f"margin: {m_disp} • kern: {k_disp}"
        self.tab1.resultLabel.set(result)


        
                  

    def saveNoKernGroups(self, sender=None):
        try:
            noL, noR = self._get_no_kern_items()
            data = {
                "no_kern_left": list(noL),
                "no_kern_right": list(noR)
            }
            panel = NSSavePanel.savePanel()
            panel.setAllowedFileTypes_(["json"])
            panel.setNameFieldStringValue_("no_kern_groups.json")
            if panel.runModal():
                path = panel.URL().path()
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
        except Exception:
            pass




    def loadNoKernGroups(self, sender=None):
        try:
            panel = NSOpenPanel.openPanel()
            panel.setAllowedFileTypes_(["json"])
            panel.setAllowsMultipleSelection_(False)
            if panel.runModal():
                path = panel.URLs()[0].path()
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.tab1.noKernLeft.set("\n".join(data.get("no_kern_left", [])))
                self.tab1.noKernRight.set("\n".join(data.get("no_kern_right", [])))
        except Exception:
            pass


    def get_context_strings(self, left_name, right_name):
        font = Glyphs.font

        left_glyph = font.glyphs[left_name] if left_name in font.glyphs else None
        right_glyph = font.glyphs[right_name] if right_name in font.glyphs else None

        def glyph_case(g):
            if not g:
                return "UPPER"

            sub = getattr(g, "subCategory", None)
            if sub == "Lowercase":
                return "LOWER"
            if sub in ("Uppercase", "Smallcaps"):
                return "UPPER"

            base = g.name.split(".")[0]
            if base.islower():
                return "LOWER"
            if base.isupper():
                return "UPPER"

            return "UPPER"

        left_case = glyph_case(left_glyph)
        right_case = glyph_case(right_glyph)

        def read_field(tab, *names):
            for n in names:
                if hasattr(tab, n):
                    try:
                        return tab.__dict__[n].get().strip()
                    except Exception:
                        pass
            return ""

        ui_prefix = read_field(
            self.tab1,
            "prefixEdit", "prefixField", "prefixInput", "prefixText"
        )
        ui_suffix = read_field(
            self.tab1,
            "suffixEdit", "suffixField", "suffixInput", "suffixText"
        )

        if not ui_prefix:
            prefix_pattern = ""
        else:
            if left_case == "LOWER":
                prefix_pattern = ui_prefix.lower()
            else:
                prefix_pattern = ui_prefix.upper()

        if not ui_suffix:
            suffix_pattern = ""
        else:
            if right_case == "LOWER":
                suffix_pattern = ui_suffix.lower()
            else:
                suffix_pattern = ui_suffix.upper()

        if prefix_pattern:
            prefix = "".join(f"/{c}" for c in prefix_pattern)
        else:
            prefix = ""

        if suffix_pattern:
            suffix = "".join(f"/{c}" for c in suffix_pattern)
        else:
            suffix = ""

        return prefix, suffix





    def build_pair_line(self, left_name, right_name):
        prefix, suffix = self.get_context_strings(left_name, right_name)
        return f"{prefix}/{left_name}/{right_name}{suffix}"

        
        
        
        
        
        
    def format_context_string(self, pattern, glyph_name, side="left"):
        font = Glyphs.font
        glyph = font.glyphs[glyph_name] if glyph_name in font.glyphs else None

        def glyph_case(g):
            if not g:
                return "UPPER"

            sub = getattr(g, "subCategory", None)
            if sub == "Lowercase":
                return "LOWER"
            if sub in ("Uppercase", "Smallcaps"):
                return "UPPER"

            base = g.name.split(".")[0]
            if base.islower():
                return "LOWER"
            if base.isupper():
                return "UPPER"

            return "UPPER"

        case = glyph_case(glyph)

        if case == "LOWER":
            context_pattern = pattern.lower()
        else:
            context_pattern = pattern.upper()

        context = "".join(f"/{c}" for c in context_pattern)

        return context
        
    def spaced_text(self, text):
        out = []
        for c in text:
            if c == " ":
                out.append("   ")
            else:
                out.append(f"/{c}")
        return " ".join(out)
        
        


        
        
    def removeTabKernCallback(self, sender):
        font = Glyphs.font
        if not font or not font.currentTab:
            return
            
            
            

        layers = font.currentTab.layers
        master_id = font.selectedFontMaster.id
        tab_text = font.currentTab.text or ""

        import re
    
        # REGLA: Si hay algún bloque #...# con el mismo primer/último carácter
        # que aparece en múltiples bloques, eliminar TODO
        hash_matches = list(re.finditer(r'#([^#]+)#', tab_text))
    
        should_remove_all = False
        if hash_matches and len(hash_matches) > 1:
            # Verificar si hay caracteres repetidos en bordes de bloques
            first_chars = []
            last_chars = []
        
            for match in hash_matches:
                content = match.group(1).strip()
                if content:
                    first_chars.append(content[0])
                    last_chars.append(content[-1])
        
            # Si algún carácter aparece más de una vez en primera o última posición
            from collections import Counter
            first_counter = Counter(first_chars)
            last_counter = Counter(last_chars)
        
            for char, count in first_counter.items():
                if count > 1:
                    self._debug("GENERAL", f"✅ REGLA: '{char}' aparece {count} veces como primer carácter en bloques #")
                    should_remove_all = True
                    break
                
            for char, count in last_counter.items():
                if count > 1:
                    self._debug("GENERAL", f"✅ REGLA: '{char}' aparece {count} veces como último carácter en bloques #")
                    should_remove_all = True
                    break
    
        # ELIMINAR KERNING (todo o solo no protegidos)
        removed = 0
        seen = set()
    
        for i in range(len(layers) - 1):
            L = layers[i]
            R = layers[i + 1]
            if not L or not R:
                continue

            left = L.parent.name if L.parent else None
            right = R.parent.name if R.parent else None

            if not left or not right or left not in font.glyphs or right not in font.glyphs:
                continue

            pair_key = (left, right)
            if pair_key in seen:
                continue
            seen.add(pair_key)
        
            # Solo aplicar protección si NO debemos eliminar todo
            if not should_remove_all:
                # Verificar si está dentro de #...#
                is_protected = False
                for match in hash_matches:
                    content = match.group(1).strip()
                    if content and left in content and right in content:
                        # Verificar si son adyacentes en el contenido
                        for j in range(len(content) - 1):
                            if content[j] == left and content[j+1] == right:
                                is_protected = True
                                break
                        if is_protected:
                            break
            
                if is_protected:
                    self._debug("GENERAL", f"🛡️ Protegido: {left} / {right}")
                    continue

            # Eliminar kerning
            gL = font.glyphs[left]
            gR = font.glyphs[right]

            left_keys = {left}
            right_keys = {right}

            if hasattr(gL, 'rightKerningGroup') and gL.rightKerningGroup:
                left_keys.add(f"@MMK_L_{gL.rightKerningGroup}")

            if hasattr(gR, 'leftKerningGroup') and gR.leftKerningGroup:
                right_keys.add(f"@MMK_R_{gR.leftKerningGroup}")
                
                
            # Después de modificar kerning, limpiar cache
            if master_id in self._kerningCache:
                del self._kerningCache[master_id]

            for lk in left_keys:
                for rk in right_keys:
                    try:
                        if font.kerningForPair(master_id, lk, rk) is not None:
                            font.removeKerningForPair(master_id, lk, rk)
                            removed += 1
                            self._debug("GENERAL", f"🗑️ Eliminado: {lk} / {rk}")
                    except:
                        pass
    
        self._debug("GENERAL", f"\n📊 RESUMEN:")
        if should_remove_all:
            self._debug("GENERAL", f"   MODE: ELIMINAR TODO (regla aplicada)")
        else:
            self._debug("GENERAL", f"   MODE: NORMAL (solo no protegidos)")
        self._debug("GENERAL", f"   Total pares procesados: {len(seen)}")
        self._debug("GENERAL", f"   Pares con kerning eliminado: {removed}")
        
        
    def _reconstructTextFromGlyphs(self, glyph_names, font):
        if not glyph_names:
            return ""
    
        valid_glyphs = [g for g in glyph_names if g]
    
        if not valid_glyphs:
            return ""
    
        lines = []
        for i in range(0, len(valid_glyphs), BLOCK_COLUMNS):
            chunk = valid_glyphs[i:i + BLOCK_COLUMNS]
            lines.append(join_blocks(chunk))

        return "\n".join(lines)

        
        
        
        
        
    def _reorganizeTo4ColumnsPreservingLines(self, text):
        if not text:
            return text

        lines = text.split('\n')
        result_lines = []

        for line in lines:
            if not line.strip():
                result_lines.append(line)
                continue
        
            stripped_line = line.strip()
            if (stripped_line.startswith("Category") or 
                stripped_line.startswith("BASE") or 
                stripped_line.startswith("Position") or
                stripped_line.startswith("Hide existing") or
                stripped_line.startswith("Exclude")):
                result_lines.append(line)
                continue
        
            tokens = split_blocks(stripped_line)
        
            for i in range(0, len(tokens), BLOCK_COLUMNS):
                chunk = tokens[i:i + BLOCK_COLUMNS]
                result_lines.append(join_blocks(chunk))

        return '\n'.join(result_lines)


    def saveExcludeGroups(self, sender):
        try:
            left_groups = self.tab1.exLeft.get()
            right_groups = self.tab1.exRight.get()
            
            data = {
                "left_groups": left_groups,
                "right_groups": right_groups,
                "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            panel = NSSavePanel.savePanel()
            panel.setTitle_("Save Exclude Groups")
            panel.setPrompt_("Save")
            panel.setAllowedFileTypes_(["json"])
            panel.setNameFieldStringValue_("exclude_groups.json")
            
            if panel.runModal():
                url = panel.URL()
                if url:
                    file_path = url.path()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    
        except Exception:
            pass
    
    def loadExcludeGroups(self, sender):
        try:
            panel = NSOpenPanel.openPanel()
            panel.setTitle_("Load Exclude Groups")
            panel.setPrompt_("Load")
            panel.setAllowedFileTypes_(["json"])
            panel.setAllowsMultipleSelection_(False)
            
            if panel.runModal():
                urls = panel.URLs()
                if urls and len(urls) > 0:
                    url = urls[0]
                    file_path = url.path()
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.tab1.exLeft.set(data.get("left_groups", ""))
                    self.tab1.exRight.set(data.get("right_groups", ""))
                    
        except Exception:
            pass

    def navigateTabsCallback(self, sender):
        font = Glyphs.font
        if not font:
            return
    
        tabs = font.tabs
        if not tabs:
            return
    
        button_text = sender.getTitle()
    
        if button_text == "◀":
            direction = -1
        elif button_text == "▶":
            direction = 1
        else:
            return
    
        current_tab = font.currentTab
        if not current_tab:
            if direction == 1:
                new_index = 0
            else:
                new_index = len(tabs) - 1
        else:
            current_index = -1
            for i, tab in enumerate(tabs):
                if tab == current_tab:
                    current_index = i
                    break
        
            if current_index == -1:
                return
        
            new_index = current_index + direction
            if new_index < 0:
                new_index = len(tabs) - 1
            elif new_index >= len(tabs):
                new_index = 0
    
        if 0 <= new_index < len(tabs):
            font.currentTab = tabs[new_index]

            
            



            
            
            
            
            
    def getFeatureNames(self):
        font = Glyphs.font
        if not font:
            return ["No font open"]

        features = [f.name for f in font.features]
        return features if features else ["No features"]

    def closeAllTabsCallback(self, sender):
        font = Glyphs.font
        if font:
            while len(font.tabs) > 0:
                font.tabs[-1].close()

    def initializePairsGeneratorCollections(self):
        self.TEST_WORDS_COLLECTIONS = {
            "Symetric Trios": "/H/H/A/V/A/H/H/space/space/space/space/H/H/A/O/A/H/H/space/space/space/space/H/H/A/T/A/H/H/space/space/space/H/H/A/Y/A/H/H/space/space/space/space/H/H/A/S/A/H/H/space/space/space/H/H/A/W/A/H/H/space/space/space/space/H/H/A/U/A/H/H/space/space/space/space/H/H/T/A/T/H/H/space/space/space/space/H/H/T/O/T/H/H/space/space/space/space/H/H/Y/A/Y/H/H/space/space/space/space/H/H/Y/O/Y/H/H/space/space/space/space/H/H/U/A/U/H/H/space/space/space/space/H/H/S/Y/S/H/H/space/space/space/space/H/H/S/A/S/H/H/space/space/space/space/H/H/O/T/O/H/H/space/space/space/space/H/H/O/A/O/H/H/space/space/space/space/H/H/O/V/O/H/H/space/space/space/space/H/H/O/W/O/H/H/space/space/space/space/H/H/O/X/O/H/H/space/space/space/space/H/H/O/Y/O/H/space/space/space/space/H/H/H/M/V/M/H/H/space/space/space/space/H/H/X/O/X/H/H/space/space/space/space/H/H/V/A/V/H/h/h/h/h/o/v/o/h/h/space/space/space/space/h/h/o/w/o/h/h/space/space/space/space/h/h/o/y/o/h/h/space/space/space/space/h/h/o/x/o/h/h/space/space/space/space/h/h/y/o/y/h/h/space/space/space/space/h/h/v/o/v/h/h/space/space/space/space/h/h/w/o/w/h/h/space/space/space/space/h/h/x/o/x/h/h/space/space/space/space/h/h/s/w/s/h/h/space/space/space/space/h/h/s/v/s/h/h/space/space/space/space/h/h/s/y/s/h/h/space/space/space/space/h/h/s/o/s/h/h",
            "Latin Extended": "/T/y/p/e/f/a/c/e\n/T/y/p/o/g/r/a/p/h/y\n/V/i/s/u/a/l\n/A/l/i/g/n/m/e/n/t",
            "Cyrillic Basic": "/Ш/i/р/я/e/в\n/O/б/ъ/я/в/л/e/н/и/e\n/P/o/d/ъ/e/м\n/C/ъ/e/м/k/a",
            "Mixed Scripts": "/H/a/m/b/u/r/g/e/f/o/n/s/t/i/v\n/Ш/i/р/я/e/в\n/T/y/p/e/f/a/c/e\n/O/б/ъ/я/в/л/e/н/и/e"
        }

        self.LATIN_LOWERCASE = [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
        ]

        self.LATIN_UPPERCASE = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
        ]
        
        self.BASIC_NUMBERS = [
            'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'
        ]

        self.PUNCTUATION_GLYPHS = [
            'period', 'comma', 'colon', 'semicolon', 'exclam', 'question', 
            'hyphen', 'endash', 'emdash', 'underscore', 'parenleft', 'parenright'
        ]

        self.SYMBOLS_GLYPHS = [
            'at', 'ampersand', 'paragraph', 'section', 'copyright', 'registered', 
            'trademark', 'degree', 'dollar', 'euro', 'sterling', 'yen'
        ]
        
        self.MY_GLYPHS = []
            
                                                
            
    def debug_group_info(self, font, group_name):
        self._debug("GENERAL", f"\n🔍 DEBUG ESPECÍFICO PARA GRUPO: @{group_name}")
        
        right_members = []
        left_members = []
        
        for glyph in font.glyphs:
            if hasattr(glyph, 'rightKerningGroup') and glyph.rightKerningGroup == group_name:
                right_members.append(glyph.name)
            if hasattr(glyph, 'leftKerningGroup') and glyph.leftKerningGroup == group_name:
                left_members.append(glyph.name)
        
        self._debug("GENERAL", f"  Miembros con rightKerningGroup @{group_name}: {len(right_members)}")
        if right_members:
            self._debug("GENERAL", f"    {', '.join(sorted(right_members)[:15])}")
            if len(right_members) > 15:
                self._debug("GENERAL", f"    ... y {len(right_members)-15} más")
        
        self._debug("GENERAL", f"  Miembros con leftKerningGroup @{group_name}: {len(left_members)}")
        if left_members:
            self._debug("GENERAL", f"    {', '.join(sorted(left_members)[:15])}")
            if len(left_members) > 15:
                self._debug("GENERAL", f"    ... y {len(left_members)-15} más")
            
            
# ============================================================
#                         MAIN ENTRY POINT
# ============================================================

    def spaced_info_line(text):
        out = []
        for c in text:
            if c == " ":
                out.append("   ")
            else:
                out.append(f"/{c}")
                out.append(" ")
        return "".join(out).rstrip()

    def build_tab_header(self, baseGlyph):
        lines = []

        lines.append(f"/{baseGlyph}")
        lines.append("")

        return lines


    def createTabFromCategory(self, category):
        font = Glyphs.font
        glyphs = []
    
        for glyph in font.glyphs:
            name = glyph.name.lower()
        
            if category.lower() == "upper":
                if (name in 'abcdefghijklmnopqrstuvwxyz' or 
                    glyph.name.isupper() or 
                    glyph.name[0].isupper()):
                    glyphs.append(glyph.name)
                
            elif category.lower() == "lower":
                if name.islower() or name in 'abcdefghijklmnopqrstuvwxyz':
                    glyphs.append(glyph.name)
                
            else:
                if (category.lower() in name or 
                    category.lower() in glyph.name.lower()):
                    glyphs.append(glyph.name)
    
        if glyphs:
            tabText = "/".join(glyphs)
            newTab = font.newTab(tabText)
            font.currentTab = newTab
            return newTab
        else:
            return None


                
        

    def get_prefix_suffix_for_base(self, base_char):
        font = Glyphs.font
        
        if base_char in font.glyphs and font.glyphs[base_char].category == "Number":
            return ("H", "H")
    
        user_prefix = self.tab1.prefixInput.get().strip()
        user_suffix = self.tab1.suffixInput.get().strip()
    
        if user_prefix != "HH" or user_suffix != "HH":
            prefix_char = user_prefix[0] if user_prefix else "H"
            suffix_char = user_suffix[0] if user_suffix else "H"
            return (prefix_char, suffix_char)
    
        if base_char.islower():
            return ("h", "h")
        else:
            return ("H", "H")
            
            
    def _is_cyrillic_glyph(self, glyph):
        if not glyph or not glyph.unicode:
            return False, None

        try:
            cp = int(glyph.unicode, 16)
        except Exception:
            return False, None

        cyrillic_ranges = [
            (0x0400, 0x04FF),
            (0x0500, 0x052F),
            (0x2DE0, 0x2DFF),
            (0xA640, 0xA69F),
            (0x1C80, 0x1C8F),
        ]

        is_cyr = any(start <= cp <= end for start, end in cyrillic_ranges)
        if not is_cyr:
            return False, None

        if 0x0410 <= cp <= 0x042F:
            return True, True
        if 0x0430 <= cp <= 0x044F:
            return True, False

        return True, None
            
            

    def _excluded_groups(self):
        raw_first = self.tab1.exLeft.get()
        raw_second = self.tab1.exRight.get()

        def parse_lines(raw_text):
            glyphs = set()
            groups = set()

            for line in raw_text.splitlines():
                txt = line.strip()
                if not txt:
                    continue

                if txt.startswith("@"):
                    # 🔒 grupos SEMPRE amb @ (ahora incluye extensiones)
                    groups.add(txt)
                else:
                    # 🔒 glifs SEMPRE sense @
                    glyphs.add(txt)

            return glyphs, groups

        first_glyphs, first_groups = parse_lines(raw_first)
        second_glyphs, second_groups = parse_lines(raw_second)

        return (first_glyphs, first_groups), (second_glyphs, second_groups)



        
    def get_boss_for_pair_position(self, glyph, position):
        if not glyph:
            return None

        if position == "left":
            return glyph.rightKerningGroup
        else:
            return glyph.leftKerningGroup

        

    def _is_glyph_excluded(self, glyphname, excludedinfo, role):
        """Verifica si un glifo está excluido, considerando grupos con extensiones"""
        font = Glyphs.font
        if not font or glyphname not in font.glyphs:
            return False

        exglyphs, exgroups = excludedinfo
        g = font.glyphs[glyphname]

        # -----------------------------
        # 1. GLIF INDIVIDUAL (match exacto)
        # -----------------------------
        if glyphname in exglyphs:
            self.debug_exclusion(glyphname, role, excludedinfo, True, "Exact glyph match")
            return True

        # -----------------------------
        # 2. BASE del glifo (sin extensión)
        # -----------------------------
        base_name = self._get_glyph_base(glyphname)
        if base_name in exglyphs:
            self.debug_exclusion(glyphname, role, excludedinfo, True, f"Base match: {base_name}")
            return True

        # -----------------------------
        # 3. VARIANTES del glifo
        # -----------------------------
        variants = self._get_glyph_variants(font, base_name)
        for variant in variants:
            if variant in exglyphs:
                self.debug_exclusion(glyphname, role, excludedinfo, True, f"Variant match: {variant}")
                return True

        # -----------------------------
        # 4. VERIFICAR GRUPO ESPECÍFICO DEL LADO CORRECTO
        # -----------------------------
        # IMPORTANTE: role determina qué lado del glifo verificar
        # "first" = glifo en primera posición → verificar rightKerningGroup
        # "second" = glifo en segunda posición → verificar leftKerningGroup
    
        group_to_check = None
        if role == "first":
            # Glifo en primera posición: verificar su grupo DERECHO
            group_to_check = g.rightKerningGroup
            side_desc = "rightKerningGroup"
        elif role == "second":
            # Glifo en segunda posición: verificar su grupo IZQUIERDO
            group_to_check = g.leftKerningGroup
            side_desc = "leftKerningGroup"
    
        if group_to_check:
            group_name_clean = group_to_check.lstrip('@')
        
            # Verificar coincidencia exacta del grupo CON @
            group_key_with_at = f"@{group_name_clean}"
            if group_key_with_at in exgroups:
                self.debug_exclusion(glyphname, role, excludedinfo, True, 
                                   f"Exact {side_desc} match: {group_key_with_at}")
                return True
        
            # Verificar grupo sin @
            if group_name_clean in exgroups:
                self.debug_exclusion(glyphname, role, excludedinfo, True,
                                   f"Group match (no @) for {side_desc}: {group_name_clean}")
                return True
        
            # Verificar base del grupo
            group_base = self._get_glyph_base(group_name_clean)
            if f"@{group_base}" in exgroups:
                self.debug_exclusion(glyphname, role, excludedinfo, True,
                                   f"Group base match for {side_desc}: @{group_base}")
                return True
        
            # Verificar prefijos de grupo
            for excluded_group in exgroups:
                if excluded_group.startswith('@'):
                    excluded_group_clean = excluded_group[1:]
                    if (group_name_clean.startswith(excluded_group_clean + '.') or 
                        group_name_clean == excluded_group_clean):
                        self.debug_exclusion(glyphname, role, excludedinfo, True,
                                           f"Group prefix match: {group_name_clean} starts with {excluded_group_clean}")
                        return True

        # -----------------------------
        # 5. VERIFICAR SI EL GLIFO ES MIEMBRO DE GRUPOS EXCLUIDOS (solo del lado correcto)
        # -----------------------------
        for excluded_group in exgroups:
            if excluded_group.startswith('@'):
                # Verificar si este glifo es miembro del grupo excluido en el LADO CORRECTO
                is_member = False
            
                if role == "first" and g.rightKerningGroup:
                    # Para "first": verificar si su rightKerningGroup coincide
                    is_member = (g.rightKerningGroup.lstrip('@') == excluded_group.lstrip('@'))
            
                elif role == "second" and g.leftKerningGroup:
                    # Para "second": verificar si su leftKerningGroup coincide
                    is_member = (g.leftKerningGroup.lstrip('@') == excluded_group.lstrip('@'))
            
                if is_member:
                    self.debug_exclusion(glyphname, role, excludedinfo, True,
                                       f"Glyph is member of excluded group ({side_desc}): {excluded_group}")
                    return True

        self.debug_exclusion(glyphname, role, excludedinfo, False, "No match found")
        return False
        
        
        

    def get_kerning_group_members(self, group_name_with_at):
        """Obtiene TODOS los glifos que pertenecen a un grupo de kerning (cacheado)"""
        font = Glyphs.font
        if not font:
            return []
    
        # Cache para mejorar rendimiento
        if not hasattr(self, '_group_members_cache'):
            self._group_members_cache = {}
    
        group_name = group_name_with_at.lstrip('@')
    
        # Verificar cache
        if group_name in self._group_members_cache:
            return self._group_members_cache[group_name]
    
        members = set()
    
        for glyph in font.glyphs:
            # Verificar grupo izquierdo
            if hasattr(glyph, 'leftKerningGroup') and glyph.leftKerningGroup:
                if glyph.leftKerningGroup.lstrip('@') == group_name:
                    members.add(glyph.name)
        
            # Verificar grupo derecho
            if hasattr(glyph, 'rightKerningGroup') and glyph.rightKerningGroup:
                if glyph.rightKerningGroup.lstrip('@') == group_name:
                    members.add(glyph.name)
    
        # También verificar subgrupos (ej: @h.sc.alt es subgrupo de @h.sc)
        for glyph in font.glyphs:
            for attr in ['leftKerningGroup', 'rightKerningGroup']:
                group = getattr(glyph, attr, None)
                if group:
                    clean_group = group.lstrip('@')
                    if clean_group.startswith(group_name + '.'):
                        members.add(glyph.name)
    
        result = list(members)
        self._group_members_cache[group_name] = result
    
        return result

        
        
    def activateSelectedFeatureInCurrentTab(self):
        try:
            feature_index = self.tab1.featurePopup.get()
            font = Glyphs.font
            if not font:
                return
            
            current_tab = font.currentTab
            if not current_tab:
                return
            
            feature_names = self.getFeatureNames()
            if 0 <= feature_index < len(feature_names):
                fName = feature_names[feature_index]
            
                if hasattr(current_tab, 'features'):
                    current_tab.features = [fName]
                else:
                    current_tab.setFeaturesString_(fName)
            
        except Exception:
            pass

    def generatePairsGeneratorCallback(self, sender):
        """Callback para el botón Generate Tabs"""
        self.generatePairsGenerator()
        self.activateSelectedFeatureInCurrentTab()
        
    def _get_selected_base(self):
        if hasattr(self.w, "baseEdit"):
            try:
                base = self.w.baseEdit.get().strip()
                if base:
                    return base
            except Exception:
                pass

        if hasattr(self.w, "basePopUp"):
            try:
                idx = self.w.basePopUp.get()
                items = self.w.basePopUp.getItems()
                if items and idx is not None and idx < len(items):
                    base = items[idx]
                    if base:
                        return base
            except Exception:
                pass

        font = Glyphs.font
        if font and font.selectedLayers:
            layer = font.selectedLayers[0]
            if layer and layer.parent:
                return layer.parent.name

        return None

    def listKerningGroupMembersInNewTab(self, sender=None):
        font = Glyphs.font
        if not font or not font.currentTab:
            return

        tab = font.currentTab
        layers = tab.layers
        cursor = tab.textCursor

        if cursor is None or not layers:
            return
    
        if cursor >= len(layers) or cursor - 1 < 0:
            return
    
        right_glyph = layers[cursor].parent if layers[cursor] else None
        left_glyph = layers[cursor - 1].parent if layers[cursor - 1] else None
    
        if not left_glyph or not right_glyph:
            return

        if right_glyph.leftKerningGroup:
            group_name = right_glyph.leftKerningGroup
        elif right_glyph.rightKerningGroup:
            group_name = right_glyph.rightKerningGroup
        else:
            return

        members = self.getKerningGroupMembers(right_glyph, "left" if right_glyph.leftKerningGroup else "right")
        if not members:
            return

        all_pairs = []
    
        for m in members:
            if m in font.glyphs:
                all_pairs.append(self.build_pair_line(left_glyph.name, m))
    
        all_pairs.append("")
    
        for m in members:
            if m in font.glyphs:
                all_pairs.append(self.build_pair_line(m, left_glyph.name))

        new_tab = font.newTab("")
        lines = []
    
        lines.append(f"M e m b e r s    @ {group_name}    ( {len(members)} )")
        lines.append("")
    
        columns = 4
        current_section = []
    
        for pair in all_pairs:
            if pair == "":
                if current_section:
                    for i in range(0, len(current_section), columns):
                        chunk = current_section[i:i + columns]
                        if chunk:
                            line = chunk[0]
                            for block in chunk[1:]:
                                line += "   " + block
                            lines.append(line)
                    lines.append("")
                    current_section = []
            else:
                current_section.append(pair)
    
        if current_section:
            for i in range(0, len(current_section), columns):
                chunk = current_section[i:i + columns]
                if chunk:
                    line = chunk[0]
                    for block in chunk[1:]:
                        line += "   " + block
                    lines.append(line)

        new_tab.text = "\n".join(lines)
        font.currentTab = new_tab




        

    def get_neighbors_by_category(self, category):
        font = Glyphs.font
        if not font:
            return []
    
        neighbors = []
    
        if category == 'Latin Upper':
            for base in LATINUPPERCASE:
                for glyph in font.glyphs:
                    glyphname = glyph.name
                    # COMPTE! Solament agafar la forma base sense extensió
                    if '.' in glyphname:
                        continue  # ⬅️ Saltar variacions (.sc, .ss01, etc.)
                    if glyphname == base:  # ⬅️ Comparació exacta
                        neighbors.append(glyphname)
            self.buildMyGlyphsCollection()
            for glyphdata in self.baseglyphslist:
                if isinstance(glyphdata, dict):
                    glyphname = glyphdata.get('name', '').strip()
                    glyphcategory = glyphdata.get('category', '')
                    if (glyphname and glyphname in font.glyphs and 
                        glyphcategory == 'Uppercase' and '.' not in glyphname):
                        if glyphname not in neighbors:
                            neighbors.append(glyphname)
            return sorted(set(neighbors))
    
        elif category == 'Latin Lower':
            for base in LATINLOWERCASE:
                for glyph in font.glyphs:
                    glyphname = glyph.name
                    if '.' in glyphname:
                        continue  # ⬅️ Saltar variacions
                    if glyphname == base:
                        neighbors.append(glyphname)
            self.buildMyGlyphsCollection()
            for glyphdata in self.baseglyphslist:
                if isinstance(glyphdata, dict):
                    glyphname = glyphdata.get('name', '').strip()
                    glyphcategory = glyphdata.get('category', '')
                    if (glyphname and glyphname in font.glyphs and 
                        glyphcategory == 'Lowercase' and '.' not in glyphname):
                        if glyphname not in neighbors:
                            neighbors.append(glyphname)
            return sorted(set(neighbors))
    
        elif category == 'Numbers':
            # Per números, només agafar les formes canòniques sense extensió
            return sorted([n for n in CANONICALNUMBERS 
                          if n in font.glyphs and '.' not in n])
    
        elif category == 'Punctuation':
            # Per puntuació, només formes sense extensió
            return sorted([n for n in CANONICALPUNCTUATION 
                          if n in font.glyphs and '.' not in n])
    
        elif category == 'Symbols':
            for g in font.glyphs:
                if g.category == 'Symbol' and '.' not in g.name:
                    neighbors.append(g.name)
            return sorted(set(neighbors))
    
        elif category == 'My Glyphs':
            self.buildMyGlyphsCollection()
    
            tab2_glyphs = []
            for glyphdata in self.baseglyphslist:
                if isinstance(glyphdata, dict):
                    name = glyphdata.get('name', '').strip()
                    if (name and name in font.glyphs and 
                        '.' not in name):  # ⬅️ Filtrar variacions
                        tab2_glyphs.append(name)
    
            return sorted(set(tab2_glyphs))
    
        elif category == 'Cyrillic Upper':
            for g in font.glyphs:
                iscyr, isupper = self.iscyrillicglyph(g)
                if iscyr and isupper is True and '.' not in g.name:
                    neighbors.append(g.name)
            return sorted(set(neighbors))
    
        elif category == 'Cyrillic Lower':
            for g in font.glyphs:
                iscyr, isupper = self.iscyrillicglyph(g)
                if iscyr and isupper is False and '.' not in g.name:
                    neighbors.append(g.name)
            return sorted(set(neighbors))
    
        return []


    def iscyrillicglyph(self, glyph):
        """Determina si un glifo es cirílico y si es mayúscula o minúscula"""
        if not glyph or not glyph.unicode:
            return False, None

        try:
            cp = int(glyph.unicode, 16)
        except Exception:
            return False, None

        cyrillic_ranges = [
            (0x0400, 0x04FF),    # Cyrillic
            (0x0500, 0x052F),    # Cyrillic Supplement
            (0x2DE0, 0x2DFF),    # Cyrillic Extended-A
            (0xA640, 0xA69F),    # Cyrillic Extended-B
            (0x1C80, 0x1C8F),    # Cyrillic Extended-C
        ]

        is_cyr = any(start <= cp <= end for start, end in cyrillic_ranges)
        if not is_cyr:
            return False, None

        # Determinar si es mayúscula o minúscula
        if 0x0410 <= cp <= 0x042F:
            return True, True     # Cyrillic uppercase
        if 0x0430 <= cp <= 0x044F:
            return True, False    # Cyrillic lowercase

        # Para otros rangos cirílicos, intentar determinar por el nombre
        glyph_name = glyph.name.lower()
        if any(keyword in glyph_name for keyword in ['cyrillic', 'cyr']):
            # Intentar adivinar por el nombre
            if any(keyword in glyph_name for keyword in ['capital', 'uppercase', 'cap']):
                return True, True
            elif any(keyword in glyph_name for keyword in ['small', 'lowercase', 'lc']):
                return True, False

        return True, None  # Cirílico pero caso indeterminado
        
        


    def _filter_out_variations(self, glyph_list, font):
        """
        Filtra les variacions (.sc, .ss01, etc.) dels glifs base.
        """
        filtered = []
        base_names = set()
    
        for glyph_name in glyph_list:
            if '.' in glyph_name:
                # És una variació, verificar si la base ja està a la llista
                base = glyph_name.split('.')[0]
                if base in glyph_list:
                    # La base ja està a la llista, descartar la variació
                    continue
            filtered.append(glyph_name)
    
        return filtered


    def filter_pairs_with_existing_kerning(
        self,
        pairs,
        font,
        master_id,
        boss_only=False,
        base=None,
        category=None,
        tab=None,
    ):
        if not pairs:
            return []

        # Obtener features activas del tab si está disponible
        active_features = []
        if tab and hasattr(tab, 'features') and tab.features:
            active_features = tab.features

        filtered = []
    
        for pair in pairs:
            try:
                parts = [p for p in pair.split("/") if p]
    
                if len(parts) >= 2:
                    mid = len(parts) // 2
                    left_name = parts[mid - 1]
                    right_name = parts[mid]
                else:
                    filtered.append(pair)
                    continue
            
            except Exception:
                filtered.append(pair)
                continue

            if left_name not in font.glyphs or right_name not in font.glyphs:
                filtered.append(pair)
                continue

            # *** CAMBIO CRÍTICO: Verificar SI el par tiene kerning POR GRUPOS ***
            # Necesitamos una nueva función que solo detecte kerning por grupos
            has_group_kerning = self._has_group_kerning_only(font, master_id, left_name, right_name)
        
            if has_group_kerning:
                # ⛔ Filtrar este par - ya tiene kerning por grupos (candado cerrado)
                self._debug("HIDE", f"🗑️ Filtering pair (has group kerning 🔒): {left_name} / {right_name}")
                continue
            else:
                # ✅ Mantener este par - no tiene kerning por grupos
                # (puede tener kerning específico, pero eso no importa)
                filtered.append(pair)
    
        return filtered

    def _has_group_kerning_only(self, font, master_id, left_name, right_name):
        """
        Retorna True si el parell ja està cobert per QUALSEVOL
        combinació de kerning per grup (grup-grup, grup-glif, glif-grup)
        """
        if left_name not in font.glyphs or right_name not in font.glyphs:
            return False

        left_glyph = font.glyphs[left_name]
        right_glyph = font.glyphs[right_name]

        kerning_dict = font.kerning.get(master_id, {})

        # Claus possibles
        left_keys = {left_name}
        right_keys = {right_name}

        if left_glyph.rightKerningGroup:
            left_keys.add(f"@MMK_L_{left_glyph.rightKerningGroup}")

        if right_glyph.leftKerningGroup:
            right_keys.add(f"@MMK_R_{right_glyph.leftKerningGroup}")

        # Comprovar TOTES les combinacions
        for lk in left_keys:
            if lk not in kerning_dict:
                continue

            rk_dict = kerning_dict.get(lk, {})
            for rk in right_keys:
                if rk in rk_dict:
                    self._debug(
                        "HIDE",
                        f"🔒 Covered by kerning: {lk} / {rk}"
                    )
                    return True

        return False


    def _has_specific_kerning_pair(self, font, master_id, left_name, right_name):
        """Verifica si un par tiene kerning ESPECÍFICO (candado abierto 🔓)"""
        if left_name not in font.glyphs or right_name not in font.glyphs:
            return False
    
        # Verificar par EXACTO (no por grupos)
        try:
            kerning_dict = font.kerning.get(master_id, {})
            if left_name in kerning_dict:
                right_dict = kerning_dict[left_name]
                if right_name in right_dict:
                    self._debug("HIDE", f"       Found SPECIFIC kerning: {left_name} / {right_name}")
                    return True
        
            # También verificar directamente
            kern_value = font.kerningForPair(master_id, left_name, right_name)
            if kern_value is not None:
                # Verificar que NO sea por grupos indirectamente
                left_glyph = font.glyphs[left_name]
                right_glyph = font.glyphs[right_name]
            
                # Si ambos tienen grupos, pero estamos usando nombres específicos, es candado abierto
                left_has_group = hasattr(left_glyph, 'rightKerningGroup') and left_glyph.rightKerningGroup
                right_has_group = hasattr(right_glyph, 'leftKerningGroup') and right_glyph.leftKerningGroup
            
                if left_has_group and right_has_group:
                    # Hay grupos, pero estamos usando nombres específicos → candado abierto
                    return True
        except Exception:
            pass
    
        return False

    def clear_kerning_cache(self, master_id=None):
        """Limpia la cache de kerning"""
        if master_id is None:
            self._kerningCache = {}
        elif master_id in self._kerningCache:
            del self._kerningCache[master_id]


    def updateBaseGlyphsFromUI(self):
        try:
            if not hasattr(self, 'tab2') or not hasattr(self.tab2, 'listContainer'):
                return
            inner = self.tab2.listContainer.innerGroup
            for i in range(len(self.baseglyphslist)):
                name_fieldname = f'name{i}'
                if hasattr(inner, name_fieldname):
                    name_field = getattr(inner, name_fieldname)
                    new_name = name_field.get().strip()
                    if new_name:
                        self.baseglyphslist[i]['name'] = new_name
                cat_fieldname = f'cat{i}'
                if hasattr(inner, cat_fieldname):
                    cat_field = getattr(inner, cat_fieldname)
                    categories = ["Uppercase", "Lowercase", "Numbers", "Punctuation", "Symbols", "My Glyphs", "Cyrillic Upper", "Cyrillic Lower"]
                    cat_index = cat_field.get()
                    if 0 <= cat_index < len(categories):
                        self.baseglyphslist[i]['category'] = categories[cat_index]
                cb_fieldname = f'cb{i}'
                if hasattr(inner, cb_fieldname):
                    cb_field = getattr(inner, cb_fieldname)
                    self.baseglyphslist[i]['selected'] = bool(cb_field.get())
        except Exception:
            pass




    def buildMyGlyphsCollection(self):
        font = Glyphs.font
        self.MYGLYPHS = []
        try:
            self.updateBaseGlyphsFromUI()
            for g in self.baseglyphslist:
                if (isinstance(g, dict) and 
                    g.get('selected', False) and 
                    g.get('category') == 'My Glyphs' and 
                    (name := g.get('name', '').strip()) and 
                    name in font.glyphs):
                    self.MYGLYPHS.append(name)
        except Exception:
            pass


    def checkboxClicked(self, index):
        if 0 <= index < len(self.baseglyphslist):
            self.baseglyphslist[index]['selected'] = not self.baseglyphslist[index].get('selected', False)
            self.updateSelectAllButtonText()
            self.refreshGlyphsList()
    

    def makeGlyphNameCallback(self, index):
        def callback(sender):
            if 0 <= index < len(self.baseglyphslist):
                new_name = sender.get().strip()
                self.baseglyphslist[index]['name'] = new_name
                self.refreshGlyphsList()
        return callback
    
    def makeCategoryCallback(self, index):
        categories = ["Uppercase", "Lowercase", "Numbers", "Punctuation", "Symbols", 
                     "My Glyphs", "Cyrillic Upper", "Cyrillic Lower"]
        def callback(sender):
            if 0 <= index < len(self.baseglyphslist):
                category_idx = sender.get()
                if 0 <= category_idx < len(categories):
                    self.baseglyphslist[index]['category'] = categories[category_idx]
                    self.refreshGlyphsList()
        return callback
    

    
    def updateSelectAllButtonText(self, sender=None):
        if not self.baseglyphslist:
            self.tab2.selectAllButton.setTitle("Select All Glyphs")
            return
            
        all_selected = all(g.get('selected', False) for g in self.baseglyphslist)
        title = "Deselect All Glyphs" if all_selected else "Select All Glyphs"
        self.tab2.selectAllButton.setTitle(title)
    
    def saveListCallback(self, sender):
        try:
            self._updateBaseGlyphsFromUI()
            
            panel = NSSavePanel.savePanel()
            panel.setTitle_("Save Base Glyphs List")
            panel.setPrompt_("Save")
            panel.setAllowedFileTypes_(["json"])
            panel.setNameFieldStringValue_("base_glyphs.json")
            
            if panel.runModal():
                url = panel.URL()
                if url:
                    file_path = url.path()
                    
                    save_data = {
                        "glyphs": self.baseglyphslist,
                        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "version": "1.0"
                    }
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(save_data, f, indent=2)
                    
        except Exception:
            pass
    
    def addGlyphCallback(self, sender):
        try:
            new_glyph = {
                "name": "",
                "category": "Uppercase",
                "selected": False
            }
        
            self.baseglyphslist.append(new_glyph)
            self.refreshGlyphsList()
        
        except Exception:
            pass
            
    
    def deleteSelectedGlyphs(self, sender):
        self.baseglyphslist = [g for g in self.baseglyphslist if not g.get('selected', False)]
        self.refreshGlyphsList()
        
        
        
    def _glyph_is_base_only(self, glyph_name):
        return "." not in glyph_name

        
        
        
        
    def selectAllGlyphsCallback(self, sender):
        try:
            if not self.baseglyphslist:
                return
        
            all_selected = all(g.get('selected', False) for g in self.baseglyphslist)
        
            for glyph in self.baseglyphslist:
                glyph['selected'] = not all_selected
        
            self.refreshGlyphsList()
            self.updateSelectAllButtonText()
        
        except Exception:
            pass
            
    def loadListCallback(self, sender):
        try:
            panel = NSOpenPanel.openPanel()
            panel.setTitle_("Load Base Glyphs List")
            panel.setPrompt_("Load")
            panel.setAllowedFileTypes_(["json"])
            panel.setAllowsMultipleSelection_(False)
            
            if panel.runModal():
                urls = panel.URLs()
                if urls and len(urls) > 0:
                    url = urls[0]
                    file_path = url.path()
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if "glyphs" in data:
                        self.baseglyphslist = data["glyphs"]
                        for glyph in self.baseglyphslist:
                            if "selected" not in glyph:
                                glyph["selected"] = False
                        
                        self.refreshGlyphsList()
                        self.updateSelectAllButtonText()
                    
        except Exception:
            pass
    

    def _createScrollableList(self, parent, frame, content_width, min_height):
        inner = Group((0, 0, content_width, min_height))
        nsInner = inner.getNSView()

        scroll = ScrollView(frame, nsInner)
        scroll.innerGroup = inner

        sv = scroll._nsObject
        sv.setHasVerticalScroller_(True)
        sv.setAutohidesScrollers_(False)

        return scroll

    def _buildTab2Row(self, index, ypos):
        inner = self.tab2.listContainer.innerGroup
        g = self.baseglyphslist[index]

        categories = [
            "Uppercase", "Lowercase", "Numbers", "Punctuation",
            "Symbols", "My Glyphs", "Cyrillic Upper", "Cyrillic Lower"
        ]

        cb = CheckBox(
            (10, ypos + 3, 20, 20),
            "",
            callback=lambda sender, i=index: self.checkboxClicked(i)
        )
        cb.set(g.get("selected", False))
        setattr(inner, f"cb_{index}", cb)

        nameField = EditText(
            (40, ypos + 1, 140, 22),
            g.get("name", ""),
            callback=self.makeGlyphNameCallback(index)
        )
        setattr(inner, f"name_{index}", nameField)

        cat_idx = categories.index(g.get("category", "Uppercase")) if g.get("category") in categories else 0
        catPopup = PopUpButton(
            (190, ypos, 150, 22),
            categories,
            callback=self.makeCategoryCallback(index)
        )
        catPopup.set(cat_idx)
        setattr(inner, f"cat_{index}", catPopup)

        inner.dynamiccontrols.extend([cb, nameField, catPopup])
    
    def loadAdjustmentsFromGlyphs(self, sender):
        font = Glyphs.font
        if not font:
            return
    
        self.adjustments = []
    
        common_glyphs = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                        "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    
        for glyph_name in common_glyphs:
            if glyph_name in font.glyphs:
                new_adjustment = {
                    "active": True,
                    "name": glyph_name,
                    "position": "Both",
                    "mode": "Increase",
                    "percent": 0,
                    "selected": False
                }
                self.adjustments.append(new_adjustment)
    
        self.refreshAdjustmentsList()
        self.updateSelectAllAdjustmentsButtonText()

    def makeAdjustmentNameCallback(self, index):
        def callback(sender):
            if 0 <= index < len(self.adjustments):
                new_name = sender.get().strip()
                self.adjustments[index]['name'] = new_name
                self.refreshAdjustmentsList()
        return callback

    def makePositionCallback(self, index):
        positions = ["Left", "Right", "Both"]
        def callback(sender):
            if 0 <= index < len(self.adjustments):
                pos_idx = sender.get()
                if 0 <= pos_idx < len(positions):
                    self.adjustments[index]['position'] = positions[pos_idx]
                    self.refreshAdjustmentsList()
                    self.refreshPreview()
        return callback

    def updateSelectAllAdjustmentsButtonText(self, sender=None):
        if not self.adjustments:
            self.tab3.selectAllButton.setTitle("Select All")
            return
            
        all_selected = all(adj.get('selected', False) for adj in self.adjustments)
        title = "Deselect All" if all_selected else "Select All"
        self.tab3.selectAllButton.setTitle(title)

    def addAdjustmentCallback(self, sender=None):
        new_adjustment = {
            "active": True,
            "name": "",
            "position": "Both",
            "mode": "Increase",
            "percent": 0.0,
            "selected": False
        }

        self.adjustments.append(new_adjustment)
        self.refreshAdjustmentsList()
        self.updateSelectAllAdjustmentsButtonText()

    def deleteSelectedAdjustments(self, sender=None):
        before = len(self.adjustments)

        self.adjustments = [
            adj for adj in self.adjustments
            if not adj.get("selected", False)
        ]

        removed = before - len(self.adjustments)

        self.refreshAdjustmentsList()
        self.updateSelectAllAdjustmentsButtonText()

    def selectAllAdjustmentsCallback(self, sender=None):
        if not self.adjustments:
            return
            
        all_selected = all(adj.get('selected', False) for adj in self.adjustments)
        
        for adj in self.adjustments:
            adj['selected'] = not all_selected
        
        self.refreshAdjustmentsList()
        self.updateSelectAllAdjustmentsButtonText()

    def saveAdjustmentsCallback(self, sender):
        try:
            self._updateAdjustmentsFromUI()
            
            panel = NSSavePanel.savePanel()
            panel.setTitle_("Save Adjustments List")
            panel.setPrompt_("Save")
            panel.setAllowedFileTypes_(["json"])
            panel.setNameFieldStringValue_("adjustments.json")
            
            if panel.runModal():
                url = panel.URL()
                if url:
                    file_path = url.path()
                    
                    save_data = {
                        "adjustments": self.adjustments,
                        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "version": "1.0"
                    }
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(save_data, f, indent=2)
                    
        except Exception:
            pass

    def loadAdjustmentsCallback(self, sender):
        try:
            panel = NSOpenPanel.openPanel()
            panel.setAllowedFileTypes_(["json"])
            panel.setAllowsMultipleSelection_(False)

            if panel.runModal():
                path = panel.URLs()[0].path()
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.adjustments = data.get("adjustments", [])

                for adj in self.adjustments:
                    adj["active"] = adj.get("active", True)
                    adj["name"] = adj.get("name", "")
                    adj["position"] = adj.get("position", "Both")
                    adj["mode"] = adj.get("mode", "Increase")
                    percent_val = adj.get("percent", 0.0)
                    if isinstance(percent_val, str):
                        percent_val = percent_val.replace('%', '')
                        try:
                            adj["percent"] = float(percent_val)
                        except ValueError:
                            adj["percent"] = 0.0
                    else:
                        adj["percent"] = float(percent_val)
                
                    adj["selected"] = False

                self.refreshAdjustmentsList()
                self.updateSelectAllAdjustmentsButtonText()

        except Exception:
            pass


    def adjustmentCheckboxClicked(self, index):
        if 0 <= index < len(self.adjustments):
            old_value = self.adjustments[index].get('selected', False)
            new_value = not old_value
            self.adjustments[index]['selected'] = new_value
        
            self.updateSelectAllAdjustmentsButtonText()
            self.refreshAdjustmentsList()

    def makeAdjustmentModeCallback(self, index):
        modes = ["Increase", "Decrease"]

        def callback(sender):
            if 0 <= index < len(self.adjustments):
                mode_idx = sender.get()
                if 0 <= mode_idx < len(modes):
                    self.adjustments[index]["mode"] = modes[mode_idx]
                    self.refreshAdjustmentsList()
                    self.refreshPreview()

        return callback

    def testTab3Scroll(self):
        if not hasattr(self.tab3, 'listContainer'):
            return
        
        lc = self.tab3.listContainer
    
        if not hasattr(lc, 'innerGroup'):
            return
        
        inner = lc.innerGroup
    
        try:
            sv = lc._nsObject
            sv_frame = sv.frame()
        
            has_scroller = sv.hasVerticalScroller()
        
            if len(self.adjustments) < 10:
                for i in range(10):
                    new_adj = {
                        "active": True,
                        "name": f"Test{i}",
                        "position": "Both",
                        "mode": "Increase",
                        "percent": float(i * 5),
                        "selected": False
                    }
                    self.adjustments.append(new_adj)
            
                self.refreshAdjustmentsList()
            
        except Exception:
            pass



        
    def get_boss_glyph(self, glyph):
        boss = None

        if glyph.rightKerningGroup:
            boss = glyph.rightKerningGroup.lstrip("@")
        elif glyph.leftKerningGroup:
            boss = glyph.leftKerningGroup.lstrip("@")

        if boss:
            boss = boss.lower()
            if boss == "hypen":
                boss = "hyphen"

        return boss



    def _glyph_allowed_by_feature(self, glyph_name):
        if "." not in glyph_name:
            return True

        try:
            feature_index = self.tab1.featurePopup.get()
        except Exception:
            feature_index = -1

        if feature_index <= 0:
            return False

        return True

    def getPreviewText(self):
        if hasattr(self.tab3, "previewTextInput"):
            return self.tab3.previewTextInput.get().strip()
        return ""

    def testPreviewField(self):
        if hasattr(self.tab3, 'previewTextInput'):
            current_text = self.tab3.previewTextInput.get()

    def _previewVisual(self, font, tab, glyphNames, baseMargin):
        try:
            previewLayer = self.buildPreviewLayer(glyphNames, baseMargin)
            if not previewLayer:
                return
    
            tab.layers = []
            tab.layers.append(previewLayer)
        
            preview_text = self.getPreviewText()
            tab.text = preview_text
        
        except Exception:
            pass

    def clearPreviewKerningCallback(self, sender):
        font = Glyphs.font
        if not font:
            return

        tab = font.currentTab
        if not tab:
            return

        if tab.text and "Kern Coach Preview" in tab.text:
            self._clearKerningInTab(tab)
        else:
            self._clearKerningInTab(tab)

    def _buildPreviewTextWithKerning(self, glyphNames, baseMargin, adjustments, masterID, noL_filter, noR_filter):
        font = Glyphs.font
        if not font:
            return ""
    
        result_parts = []
    
        for i in range(len(glyphNames) - 1):
            left = glyphNames[i]
            right = glyphNames[i + 1]
        
            if self._is_glyph_no_kern(left, noL_filter, "left"):
                result_parts.append(f"/{left}")
                continue
            
            if self._is_glyph_no_kern(right, noR_filter, "right"):
                result_parts.append(f"/{left}")
                continue
        
            result_parts.append(f"/{left}")
        
            target_margin = baseMargin
        
            for adj in adjustments:
                if adj.get("name") == left:
                    position = adj.get("position", "Both")
                    if position in ("Right", "Both"):
                        percent = adj.get("percent", 0.0)
                        mode = adj.get("mode", "Increase")
                        percent_decimal = percent / 100.0
                    
                        if mode == "Increase":
                            target_margin = baseMargin * (1.0 - percent_decimal)
                        elif mode == "Decrease":
                            target_margin = baseMargin * (1.0 + percent_decimal)
                        break
        
            current_margin = margin_for_pair(font, masterID, left, right)
            if current_margin is None or current_margin >= 10000:
                continue
        
            kerning_needed = -(current_margin - target_margin)
            if kerning_needed < 0:
                kerning_needed = int(round(kerning_needed))
            
                left_group = None
                right_group = None
            
                left_glyph_obj = font.glyphs[left]
                right_glyph_obj = font.glyphs[right]
            
                if left_glyph_obj and left_glyph_obj.rightKerningGroup:
                    left_group = f"@MMK_L_{left_glyph_obj.rightKerningGroup}"
                else:
                    left_group = left
            
                if right_glyph_obj and right_glyph_obj.leftKerningGroup:
                    right_group = f"@MMK_R_{right_glyph_obj.leftKerningGroup}"
                else:
                    right_group = right
            
                font.setKerningForPair(masterID, left_group, right_group, kerning_needed)
    
        if glyphNames:
            result_parts.append(f"/{glyphNames[-1]}")
    
        return "".join(result_parts)

    def parsePreviewText(self):
        text = self.getPreviewText()
        font = Glyphs.font
        if not font or not text:
            return []

        glyphNames = []

        if "/" in text:
            parts = text.split("/")
            for name in parts:
                if not name:
                    continue
                if name in font.glyphs:
                    glyphNames.append(name)
        else:
            for char in text:
                g = font.glyphForCharacter_(ord(char))
                if g:
                    glyphNames.append(g.name)

        return glyphNames

    def previewInTabCallback(self, sender=None):
        font = Glyphs.font
        if not font:
            return

        text = self.getPreviewText()
        if not text:
            return

        try:
            baseMargin = float(self.tab1.mValue.get())
        except:
            baseMargin = 80.0

        glyphNames = self.parsePreviewText()
        if not glyphNames:
            return

        masterID = font.selectedFontMaster.id

        noL, noR = self._get_no_kern_items()

        self._updateAdjustmentsFromUI()
        adjustments_to_apply = [
            a for a in self.adjustments
            if a.get("active", True) and a.get("name") and a.get("percent") is not None and a.get("mode")
        ]

        previewTab = None
        for tab in font.tabs:
            if tab.text and "Kern Coach Preview" in tab.text:
                previewTab = tab
                break

        if previewTab is None:
            previewTab = font.newTab()

        self._clearKerningInTab(previewTab)
    
        formatted_text = self._buildPreviewTextWithKerningExtended(
            glyphNames, 
            baseMargin, 
            adjustments_to_apply, 
            masterID,
            noL,
            noR
        )
    
        previewTab.text = f"Kern Coach Preview - Trios Supported\n{formatted_text}"
    
        font.currentTab = previewTab

    def _buildPreviewTextWithKerningExtended(self, glyphNames, baseMargin, adjustments, masterID, noL_filter, noR_filter):
        font = Glyphs.font
        if not font:
            return ""
    
        result_parts = []
    
        if glyphNames:
            result_parts.append(f"/{glyphNames[0]}")
    
        for i in range(len(glyphNames) - 1):
            left = glyphNames[i]
            right = glyphNames[i + 1]
        
            if self._is_glyph_no_kern(left, noL_filter, "left"):
                result_parts.append(f"/{right}")
                continue
            
            if self._is_glyph_no_kern(right, noR_filter, "right"):
                result_parts.append(f"/{right}")
                continue
        
            target_margin = baseMargin
        
            adjustment_applied = False
            for adj in adjustments:
                if adj.get("name") == left:
                    position = adj.get("position", "Both")
                    if position in ("Right", "Both"):
                        percent = adj.get("percent", 0.0)
                        mode = adj.get("mode", "Increase")
                        percent_decimal = percent / 100.0
                    
                        if mode == "Increase":
                            target_margin = baseMargin * (1.0 - percent_decimal)
                        elif mode == "Decrease":
                            target_margin = baseMargin * (1.0 + percent_decimal)
                    
                        adjustment_applied = True
                        break
        
            current_margin = margin_for_pair(font, masterID, left, right)
            if current_margin is None or current_margin >= 10000:
                result_parts.append(f"/{right}")
                continue
        
            kerning_needed = -(current_margin - target_margin)
        
            if kerning_needed < 0:
                kerning_needed = int(round(kerning_needed))
            
                left_group = None
                right_group = None
            
                left_glyph_obj = font.glyphs[left]
                right_glyph_obj = font.glyphs[right]
            
                if left_glyph_obj and left_glyph_obj.rightKerningGroup:
                    left_group = f"@MMK_L_{left_glyph_obj.rightKerningGroup}"
                else:
                    left_group = left
            
                if right_glyph_obj and right_glyph_obj.leftKerningGroup:
                    right_group = f"@MMK_R_{right_glyph_obj.leftKerningGroup}"
                else:
                    right_group = right
            
                font.setKerningForPair(masterID, left_group, right_group, kerning_needed)
            
                result_parts.append(f"/{right}")
            else:
                result_parts.append(f"/{right}")
    
        result = "".join(result_parts)
        return result

    def refreshPreview(self, sender=None):
        try:
            text = self.getPreviewText()
            if not text:
                return

            try:
                baseMargin = float(self.tab1.mValue.get())
            except:
                baseMargin = 80.0

            glyphNames = self.parsePreviewText()

            if not glyphNames:
                return

            self._updateAdjustmentsFromUI()
            active_adjs = [adj for adj in self.adjustments if adj.get("active", True)]

            if active_adjs:
                for adj in active_adjs:
                    pass
        
            for i in range(len(glyphNames) - 1):
                left = glyphNames[i]
                right = glyphNames[i + 1]
                spacing = self.getCharacterAdjustmentDelta(left, right, baseMargin)

        except Exception:
            pass

    def getCharacterAdjustmentDelta(self, leftName, rightName, baseMargin):
        font = Glyphs.font
        if not font:
            return baseMargin

        if self._is_pair_blocked_by_no_kern(leftName, rightName):
            return baseMargin

        masterID = font.selectedFontMaster.id

        currentMargin = margin_for_pair(font, masterID, leftName, rightName)
        if currentMargin is None or currentMargin >= 10000:
            currentMargin = baseMargin

        targetMargin = currentMargin

        for adj in self.adjustments:
            if not adj.get("active", True):
                continue

            name = adj.get("name")
            if not name:
                continue

            pos = adj.get("position", "Both")
            mode = adj.get("mode", "Increase")
            percent = float(adj.get("percent", 0.0))

            match = (
                pos == "Both" and (leftName == name or rightName == name)
                or pos == "Right" and leftName == name
                or pos == "Left" and rightName == name
            )

            if not match:
                continue

            delta = baseMargin * (percent / 100.0)
            targetMargin = (
                baseMargin - delta if mode == "Increase"
                else baseMargin + delta
            )
            break

        return targetMargin

    def buildPreviewLayer(self, glyphNames, baseMargin):
        font = Glyphs.font
        if not font:
            return None

        master = font.selectedFontMaster
        if not master:
            return None

        self._updateAdjustmentsFromUI()

        previewLayer = GSLayer()
        previewLayer.layerId = master.id
        x = 0

        for i, name in enumerate(glyphNames):
            glyph = font.glyphs.get(name)
            if not glyph:
                continue

            layer = glyph.layers.get(master.id)
            if not layer:
                continue

            if i > 0:
                x += self.getCharacterAdjustmentDelta(
                    glyphNames[i - 1],
                    name,
                    baseMargin
                )

            g = layer.copy()
            g.applyTransform((1, 0, 0, 1, x, 0))
            for s in g.shapes:
                previewLayer.shapes.append(s)

            x += layer.width

            if i < len(glyphNames) - 1:
                x += self.getCharacterAdjustmentDelta(
                    name,
                    glyphNames[i + 1],
                    baseMargin
                )

        previewLayer.width = x
        return previewLayer

    def _pair_allowed_for_generation(self, leftName, rightName):
        font = Glyphs.font
        if not font:
            return False
    
        if leftName not in font.glyphs:
            return False
    
        if rightName not in font.glyphs:
            return False
    
        allowed = not self._is_pair_blocked_by_no_kern(leftName, rightName)

        return allowed
        
    def _debug_no_kern(self, msg):
        if getattr(self, "DEBUG_NO_KERN", False):
            self._debug("NO_KERN", msg)









    def _is_pair_blocked_by_no_kern(self, leftName, rightName):
        if self._is_glyph_blocked(leftName, "left"):
            return True

        if self._is_glyph_blocked(rightName, "right"):
            return True

        return False

    def _resolve_kerning_keys(self, leftName, rightName):
        font = Glyphs.font
        if not font:
            return None, None

        if self._is_pair_blocked_by_no_kern(leftName, rightName):
            return None, None

        try:
            gL = font.glyphs[leftName]
            gR = font.glyphs[rightName]
        except Exception:
            return None, None

        leftKey = leftName
        rightKey = rightName

        if gL.rightKerningGroup:
            leftKey = f"@MMK_L_{gL.rightKerningGroup}"

        if gR.leftKerningGroup:
            rightKey = f"@MMK_R_{gR.leftKerningGroup}"

        return leftKey, rightKey


    def _apply_safe_kerning(self, leftName, rightName, kerningValue):
        font = Glyphs.font
        if not font:
            return False

        masterID = font.selectedFontMaster.id

        # Obtenir els glifs
        gL = font.glyphs.get(leftName)
        gR = font.glyphs.get(rightName)
    
        if not gL or not gR:
            return False

        # **SIEMPRE usar grupos si están disponibles**
        leftKey = leftName
        rightKey = rightName

        # Usar grupo derecho del glifo izquierdo si existe
        if gL.rightKerningGroup:
            leftKey = f"@MMK_L_{gL.rightKerningGroup}"
            self._debug("GENERAL", f"  Usando grupo derecho: {gL.rightKerningGroup} → {leftKey}")
    
        # Usar grupo izquierdo del glifo derecho si existe
        if gR.leftKerningGroup:
            rightKey = f"@MMK_R_{gR.leftKerningGroup}"
            self._debug("GENERAL", f"  Usando grupo izquierdo: {gR.leftKerningGroup} → {rightKey}")
    
        # Verificar si ya existe kerning por grupos
        existing_kern = font.kerningForPair(masterID, leftKey, rightKey)
        if existing_kern is not None:
            self._debug("GENERAL", f"  ⚠️ Ya existe kerning por grupos: {leftKey}/{rightKey} = {existing_kern}")
            return True  # Ya existe, no crear duplicado

        try:
            self._debug("GENERAL", f"  Aplicando kerning por GRUPOS: {leftKey} / {rightKey} = {kerningValue}")
            font.setKerningForPair(
                masterID,
                leftKey,
                rightKey,
                int(round(kerningValue))
            )
            return True

        except Exception as e:
            self._debug("ERROR", f"  ❌ Error aplicando kerning: {e}")
            return False
            
            
            

    def testGenerateTabs(self, sender=None):
        font = Glyphs.font
        if font:
            basenames = [n.strip() for n in self.tab1.baseInput.get().split(',') if n.strip()]

    def applyCharacterAdjustments(self, value, glyph_name, side):
        for adj in self.adjustments:
            if not adj.get("active", True):
                continue

            if adj["name"] != glyph_name:
                continue

            if adj["position"] not in (side, "Both"):
                continue

            factor = 1.0 + (adj["percent"] / 100.0)
            value *= factor

        return value

    def getCharacterAdjustmentsFromTab3(self):
        adjustments = []
    
        try:
            list_view = self.tab3.adjustmentsList
        
            if hasattr(list_view, 'getItems') or hasattr(list_view, '_items'):
                items = list_view.getItems() if hasattr(list_view, 'getItems') else list_view._items
            
                for item in items:
                    if isinstance(item, (list, tuple)) and len(item) >= 3:
                        left, right, value = item[0], item[1], float(item[2])
                        adjustments.append((left, right, int(value)))
                    elif isinstance(item, dict):
                        adjustments.append((
                            item.get('left', ''), 
                            item.get('right', ''), 
                            float(item.get('value', 0))
                        ))
        
            if not adjustments and hasattr(self.tab3, 'adjustmentsText'):
                text = self.tab3.adjustmentsText.get()
                for line in text.split('\n'):
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        try:
                            left, right = parts[0], parts[1]
                            value = float(parts[2])
                            adjustments.append((left, right, int(value)))
                        except:
                            pass
        
        except Exception:
            pass
    
        return adjustments

    def swiftCallback(self, sender):
        self._debug("GENERAL", "🔥 SWIFT MODE ACTIVADO - Kerning rápido con Tab 3")
    
        adjustments = self.getCharacterAdjustmentsFromTab3()
    
        if not adjustments:
            return
    
        font = Glyphs.font
        if not font:
            return
    
        master_id = font.selectedFontMaster.id
    
        applied = 0
        for left_glyph, right_glyph, kern_value in adjustments:
            try:
                font.kerningForPair(master_id, left_glyph, right_glyph, kern_value)
                applied += 1
            except:
                try:
                    leftGlyph = font.glyphs[left_glyph]
                    rightGlyph = font.glyphs[right_glyph]
                
                    if leftGlyph.rightKerningGroup and rightGlyph.leftKerningGroup:
                        group_left = f"@MMK_L_{leftGlyph.rightKerningGroup}"
                        group_right = f"@MMK_R_{rightGlyph.leftKerningGroup}"
                        font.kerningForPair(master_id, group_left, group_right, kern_value)
                        applied += 1
                except:
                    pass
    
        self.refreshMargin(sender)

    def refreshAdjustmentsList(self):
        try:
            if not hasattr(self.tab3, 'listContainer'):
                return

            lc = self.tab3.listContainer
            inner = lc.innerGroup

            for key in list(inner.__dict__.keys()):
                if key.startswith(("adj_cb_", "adj_name_", "adj_pos_", "adj_mode_", "adj_percent_", "adj_active_")):
                    delattr(inner, key)

            inner.dynamiccontrols = []

            ypos = 0
            rowHeight = 26

            positions = ["Left", "Right", "Both"]
            modes = ["Increase", "Decrease"]

            for i, adj in enumerate(self.adjustments):
                cb = CheckBox(
                    (15, ypos + 3, 20, 20),
                    "",
                    callback=lambda sender, idx=i: self.adjustmentCheckboxClicked(idx)
                )
                cb.set(adj.get("selected", False))
                setattr(inner, f"adj_cb_{i}", cb)

                nameField = EditText(
                    (35, ypos + 1, 75, 22),
                    adj.get("name", ""),
                    callback=self.makeAdjustmentNameCallback(i)
                )
                setattr(inner, f"adj_name_{i}", nameField)

                pos_val = adj.get("position", "Both")
                pos_idx = positions.index(pos_val) if pos_val in positions else 2
                posPopup = PopUpButton(
                    (120, ypos, 60, 22),
                    positions,
                    callback=self.makePositionCallback(i)
                )
                posPopup.set(pos_idx)
                setattr(inner, f"adj_pos_{i}", posPopup)

                mode_val = adj.get("mode", "Increase")
                mode_idx = modes.index(mode_val) if mode_val in modes else 0
                modePopup = PopUpButton(
                    (190, ypos, 80, 22),
                    modes,
                    callback=self.makeAdjustmentModeCallback(i)
                )
                modePopup.set(mode_idx)
                setattr(inner, f"adj_mode_{i}", modePopup)

                percentField = EditText(
                    (280, ypos + 1, 30, 22),
                    str(adj.get("percent", 0)),
                    callback=self.makeAdjustmentPercentCallback(i)
                )
                setattr(inner, f"adj_percent_{i}", percentField)

                activeCheckbox = CheckBox(
                    (332, ypos + 3, 60, 20),
                    "",
                    callback=lambda sender, idx=i: self.adjustmentActiveChanged(idx, sender)
                )
                activeCheckbox.set(adj.get("active", True))
                setattr(inner, f"adj_active_{i}", activeCheckbox)

                inner.dynamiccontrols.extend([
                    cb, nameField, posPopup, modePopup, percentField, activeCheckbox
                ])

                ypos += rowHeight

            contentHeight = max(ypos, 320)
            inner._nsObject.setFrame_(((0, 0), (355, contentHeight)))

            sv = lc._nsObject
            sv.setDocumentView_(inner._nsObject)
            cv = sv.contentView()
            cv.scrollToPoint_((0, 0))
            sv.reflectScrolledClipView_(cv)

        except Exception:
            pass

    def adjustmentActiveChanged(self, index, sender):
        try:
            val = sender.get()
            self.adjustments[index]["active"] = val
            self.refreshPreview()
        except Exception:
            pass



    def kernAllPairs(self, sender):
        font = Glyphs.font
        if not font:
            return

        tab = font.currentTab
        if not tab:
            return

        try:
            target = float(self.tab1.mValue.get())
        except:
            return

        noL, noR = self._get_no_kern_items()
        mid = font.selectedFontMaster.id
        layers = tab.layers

        applied = 0
        skipped = 0
        skipped_already_has_group_kerning = 0  # Nuevo contador
        seen = set()

        active_adjustments = [
            adj for adj in self.adjustments
            if adj.get("active", True)
               and adj.get("name")
               and adj.get("percent") is not None
        ]

        for i in range(len(layers) - 1):
            L = layers[i]
            R = layers[i + 1]
            if not L or not R:
                continue

            Lg = L.parent.name
            Rg = R.parent.name
            if Lg == "space" or Rg == "space":
                continue

            if self._is_glyph_no_kern(Lg, noL, "left") or self._is_glyph_no_kern(Rg, noR, "right"):
                skipped += 1
                continue

            key = f"{Lg}/{Rg}"
            if key in seen:
                continue
            seen.add(key)

            m = margin_for_pair(font, mid, Lg, Rg)
            if m is None or m >= 10000:
                continue

            needed = -(m - target)
            if needed >= 0:
                continue

            needed = float(needed)

            for adj in active_adjustments:
                name = adj["name"]
                pos = adj.get("position", "Both")

                if name == Lg and pos in ("Right", "Both"):
                    factor = 1.0 + (adj["percent"] / 100.0)
                    needed *= factor

                elif name == Rg and pos in ("Left", "Both"):
                    factor = 1.0 + (adj["percent"] / 100.0)
                    needed *= factor

            needed = int(round(needed))
            if needed >= 0:
                continue

            # **NUNCA crear kerning específic si hay grupos disponibles**
            # Siempre usar la combinación grupo-grupo o grupo-glifo
            left_glyph_obj = font.glyphs[Lg]
            right_glyph_obj = font.glyphs[Rg]
        
            left_key = Lg
            right_key = Rg
        
            # Usar grupo si existe
            if left_glyph_obj and left_glyph_obj.rightKerningGroup:
                left_key = f"@MMK_L_{left_glyph_obj.rightKerningGroup}"
        
            if right_glyph_obj and right_glyph_obj.leftKerningGroup:
                right_key = f"@MMK_R_{right_glyph_obj.leftKerningGroup}"
        
            # Verificar primero si ya existe kerning para esta combinación
            existing = font.kerningForPair(mid, left_key, right_key)
            if existing is not None:
                # Ya existe kerning, no crear duplicado
                skipped_already_has_group_kerning += 1
                continue
        
            try:
                # Aplicar kerning usando siempre grupos cuando estén disponibles
                font.setKerningForPair(mid, left_key, right_key, needed)
                applied += 1
            
                # Debug para mostrar qué tipo de kerning se creó
                if left_key.startswith("@MMK_L") and right_key.startswith("@MMK_R"):
                    self._debug("GENERAL", f"✅ Group-group kerning: {left_key}/{right_key} = {needed}")
                elif left_key.startswith("@MMK_L"):
                    self._debug("GENERAL", f"✅ Group-glyph kerning: {left_key}/{right_key} = {needed}")
                elif right_key.startswith("@MMK_R"):
                    self._debug("GENERAL", f"✅ Glyph-group kerning: {left_key}/{right_key} = {needed}")
                else:
                    self._debug("GENERAL", f"⚠️ Specific kerning (candau obert): {left_key}/{right_key} = {needed}")
                
            except Exception as e:
                self._debug("ERROR", f"❌ Error applying kerning: {e}")

        self.refreshMargin(None)

        # Mostrar resumen
        self._debug("GENERAL", f"\n📊 KERNALLPAIRS SUMMARY")
        self._debug("GENERAL", f"   Total unique pairs: {len(seen)}")
        self._debug("GENERAL", f"   Pairs kerned: {applied}")
        self._debug("GENERAL", f"   Pairs skipped (NoKern): {skipped}")
        self._debug("GENERAL", f"   Pairs skipped (already has group kerning): {skipped_already_has_group_kerning}")
    
        if skipped_already_has_group_kerning > 0:
            self._debug("GENERAL", f"   ✅ No se crearon duplicados de kerning por grupos")










    def _setup_tab3(self):
        y = 10

        self.tab3.adjHeaderSelect = TextBox((18, y, 20, 20), "✓")
        self.tab3.adjHeaderName = TextBox((45, y, 90, 20), "Character")
        self.tab3.adjHeaderPosition = TextBox((135, y, 60, 20), "Position")
        self.tab3.adjHeaderMode = TextBox((210, y, 60, 20), "Mode")
        self.tab3.adjHeaderPercent = TextBox((300, y, 30, 20), "%")
        self.tab3.adjHeaderActive = TextBox((330, y, 70, 20), "Active")

        y += 15
        y += 8

        inner = Group((0, 0, 355, 10))
        nsInner = inner.getNSView()

        self.tab3.listContainer = ScrollView(
            (12, y, 376, 440),
            nsInner
        )
        self.tab3.listContainer.innerGroup = inner

        try:
            sv = self.tab3.listContainer._nsObject
            sv.setHasVerticalScroller_(True)
            sv.setAutohidesScrollers_(False)
            sv.setBorderType_(NSBezelBorder)
        except:
            pass

        y += 325

        self.tab3.previewLabel = TextBox((12, y+190, -12, 20), "Preview in Tab:")
        y += 25

        self.tab3.previewButton = Button(
            (12, y+190, 90, 24),
            "Preview",
            callback=self.previewInTabCallback
        )

        self.tab3.clearPreviewKernButton = Button(
            (110, y+190, 160, 24),
            "🗑️ Delete Kern in Tab",
            callback=self.clearKerningForCurrentTab
        )

        y += 35

        self.tab3.previewTextLabel = TextBox((12, y+70, 100, 20), "Text to test:")
        y += 25

        self.tab3.previewTextInput = EditText(
            (12, y+70, -12, 22),
            "HPAH",
            callback=self.refreshPreview
        )

        y += 40
        self.tab3.separator2 = HorizontalLine((10, y+130, -10, 1))
        y += 15

        bw, bh, m = 140, 28, 8
        lx, rx = 12, 230

        self.tab3.addAdjustmentButton = Button(
            (lx, y+130, bw, bh),
            "Add Character",
            callback=self.addAdjustmentCallback
        )

        self.tab3.saveAdjustmentsButton = Button(
            (rx, y+130, bw, bh),
            "Save Adjustments",
            callback=self.saveAdjustmentsCallback
        )

        y += bh + m

        self.tab3.deleteSelectedButton = Button(
            (lx, y+130, bw, bh),
            "Delete Selected",
            callback=self.deleteSelectedAdjustments
        )

        self.tab3.loadAdjustmentsButton = Button(
            (rx, y+130, bw, bh),
            "Load Adjustments",
            callback=self.loadAdjustmentsCallback
        )

        y += bh + m

        self.tab3.selectAllButton = Button(
            (lx, y+130, bw, bh),
            "Select All",
            callback=self.selectAllAdjustmentsCallback
        )



        y += bh + m




    def applyAdjustmentsToPair(self, left, right, baseMargin):
        target_margin = baseMargin
    
        for adj in self.adjustments:
            if not adj.get("active", True):
                continue
            
            name = adj.get("name", "")
            position = adj.get("position", "Both")
            mode = adj.get("mode", "Increase")
            percent = adj.get("percent", 0.0)
        
            applies = False
            if position == "Both":
                applies = (name == left or name == right)
            elif position == "Right":
                applies = (name == left)
            elif position == "Left":
                applies = (name == right)
            
            if applies:
                factor = percent / 100.0
                if mode == "Increase":
                    target_margin = baseMargin * (1.0 - factor)
                elif mode == "Decrease":
                    target_margin = baseMargin * (1.0 + factor)
                break
    
        return target_margin

    def _updateAdjustmentsFromUI(self):
        try:
            if not hasattr(self.tab3, "listContainer"):
                return

            inner = self.tab3.listContainer.innerGroup
        
            for i, adj in enumerate(self.adjustments):
                nameField = getattr(inner, f"adj_name_{i}", None)
                if nameField:
                    adj["name"] = nameField.get().strip()

                posPopup = getattr(inner, f"adj_pos_{i}", None)
                if posPopup:
                    adj["position"] = posPopup.getItem()

                modePopup = getattr(inner, f"adj_mode_{i}", None)
                if modePopup:
                    adj["mode"] = modePopup.getItem()

                percentField = getattr(inner, f"adj_percent_{i}", None)
                if percentField:
                    try:
                        adj["percent"] = float(percentField.get())
                    except:
                        adj["percent"] = 0.0

                activeCheckbox = getattr(inner, f"adj_active_{i}", None)
                if activeCheckbox:
                    adj["active"] = bool(activeCheckbox.get())

        except Exception:
            pass


    def applyKernWithAdjustments(self, sender=None):
        font = Glyphs.font
        if not font:
            return
    
        self._updateAdjustmentsFromUI()
        active_adjustments = [a for a in self.adjustments if a.get("active", True)]
    
        if not active_adjustments:
            self.kernAllPairs(sender)
            return
    
        self.kernAllPairs(sender)


    def _previewClean(self, font, tab, text):
        tab.text = f"### Kern Coach Preview\n{text}"
        tab.features = ["kern"]

    def _previewDraft(self, font, tab, text):
        glyphNames = self.parsePreviewText()
        if not glyphNames:
            return
    
        formatted = "/" + "/".join(glyphNames)
    
        adj_info = []
        if self.characterAdjustmentsActive:
            self._updateAdjustmentsFromUI()
            for adj in self.adjustments:
                if adj.get("active", True):
                    adj_info.append(f"{adj.get('name')} {adj.get('position')} {adj.get('mode')} {adj.get('percent')}%")
    
        header = "### Kern Coach Preview (Draft)"
        if adj_info:
            header += f"\nAdjustments: {', '.join(adj_info[:3])}"
            if len(adj_info) > 3:
                header += f" ... +{len(adj_info)-3} more"
    
        tab.text = header + "\n" + formatted
        tab.features = ["kern"]

    def refreshPreviewCallback(self, sender=None):
        self.refreshPreview(sender)

    def _is_glyph_no_kern(self, glyph_name, no_kern_set, side="left"):
        font = Glyphs.font
        if not font or glyph_name not in font.glyphs:
            return False

        # 1. Verificar si el glifo individual está excluido (coincidencia EXACTA)
        if glyph_name in no_kern_set:
            return True

        # **IMPORTANTE: Para variantes, ser más estricto**
        if '.' in glyph_name:
            # Para variantes, solo bloquear si el nombre exacto está en el set
            # NO bloquear solo porque la base está en el set
            return False

        # 2. Verificar por grupo de kerning SOLO si empieza con @
        glyph = font.glyphs[glyph_name]
        group_attr = "rightKerningGroup" if side == "left" else "leftKerningGroup"
        group = getattr(glyph, group_attr, None)
    
        if group:
            group_name = group.lstrip('@')
            group_key = f"@{group_name}"
        
            # Solo grupos explícitamente marcados con @
            if group_key in no_kern_set:
                return True

        return False        

    def _get_no_kern_items(self):
        left_items = []
        right_items = []
    
        left_text = self.tab1.noKernLeft.get()
        self.debug_no_kern(f"Raw NoKern Left text:\n{left_text}")
    
        for line in left_text.splitlines():
            item = line.strip()
            if item:
                # **IMPORTANTE: Preservar exactamente lo que el usuario escribió**
                # Si escribió "l", significa SOLO "l", no "l.sc"
                left_items.append(item)
    
        right_text = self.tab1.noKernRight.get()
        self.debug_no_kern(f"Raw NoKern Right text:\n{right_text}")
    
        for line in right_text.splitlines():
            item = line.strip()
            if item:
                # **IMPORTANTE: Preservar exactamente lo que el usuario escribió**
                right_items.append(item)
    
        left_set = set(left_items)
        right_set = set(right_items)
    
        self.debug_no_kern(f"Parsed NoKern Left set: {sorted(left_set)}")
        self.debug_no_kern(f"Parsed NoKern Right set: {sorted(right_set)}")
    
        # **DEBUG ADICIONAL: Mostrar reglas claras**
        self.debug_no_kern(f"\nNO KERN RULES:")
        self.debug_no_kern(f"  - 'l' blocks only 'l' (not 'l.sc')")
        self.debug_no_kern(f"  - 'l.sc' blocks only 'l.sc'")
        self.debug_no_kern(f"  - '@group' blocks all members of '@group'")
        self.debug_no_kern(f"  - Groups apply to base AND variants if they are members")
    
        return left_set, right_set        
        

    def applyCharacterAdjustmentsFromTab(self, sender=None):
        # Activar debug
        self.DEBUG_NO_KERN = True
        self.debug_no_kern("=== START applyCharacterAdjustmentsFromTab ===")
    
        font = Glyphs.font
        if not font:
            self.debug_no_kern("✗ No font open")
            return

        tab = font.currentTab
        if not tab:
            self.debug_no_kern("✗ No tab open")
            return

        try:
            target = float(self.tab1.mValue.get())
            self.debug_no_kern(f"Target margin: {target}")
        except:
            self.debug_no_kern("✗ Invalid target margin")
            return

        # Obtener los conjuntos NoKern UNA SOLA VEZ
        noL, noR = self._get_no_kern_items()
        mid = font.selectedFontMaster.id
        layers = tab.layers

        self._updateAdjustmentsFromUI()
        active_adjustments = [
            adj for adj in self.adjustments
            if adj.get("active", True) and adj.get("name")
        ]
    
        self.debug_no_kern(f"Active adjustments: {len(active_adjustments)}")
        for adj in active_adjustments:
            self.debug_no_kern(f"  - {adj.get('name')}: {adj.get('position')} {adj.get('mode')} {adj.get('percent')}%")

        applied_with_adjustments = 0
        applied_normal = 0
        skipped_no_kern = 0
        skipped_invalid = 0
        skipped_no_kerning_needed = 0
        skipped_already_has_group_kerning = 0  # Nuevo contador
        seen = set()

        self.debug_no_kern(f"Processing {len(layers)} layers")
    
        for i in range(len(layers) - 1):
            L = layers[i]
            R = layers[i + 1]
            if not L or not R:
                continue

            Lg = L.parent.name if L.parent else None
            Rg = R.parent.name if R.parent else None
        
            # Verificar que ambos glifos existan
            if not Lg or not Rg or Lg not in font.glyphs or Rg not in font.glyphs:
                skipped_invalid += 1
                continue
        
            self.debug_no_kern(f"\n{'='*60}")
            self.debug_no_kern(f"PROCESSING PAIR {i}: {Lg} / {Rg}")
            self.debug_no_kern(f"{'='*60}")
        
            if Lg == "space" or Rg == "space":
                self.debug_no_kern("Skipping space character")
                continue

            # CORRECCIÓN: Usar _is_glyph_blocked_with_sets en lugar de verificación simple
            left_blocked = self._is_glyph_blocked_with_sets(Lg, "left", noL)
            right_blocked = self._is_glyph_blocked_with_sets(Rg, "right", noR)
        
            self.debug_no_kern(f"Left glyph '{Lg}' blocked: {left_blocked}")
            self.debug_no_kern(f"Right glyph '{Rg}' blocked: {right_blocked}")
        
            if left_blocked or right_blocked:
                self.debug_no_kern(f"⚠️ SKIPPING: Glyph blocked by NoKern")
                skipped_no_kern += 1
                continue

            key = f"{Lg}/{Rg}"
            if key in seen:
                self.debug_no_kern(f"⚠️ SKIPPING: Duplicate pair")
                continue
            seen.add(key)

            # Calcular margen actual
            self.debug_no_kern(f"Calculating current margin...")
            m = margin_for_pair(font, mid, Lg, Rg)
            if m is None or m >= 10000:
                self.debug_no_kern(f"✗ Invalid margin: {m}")
                skipped_invalid += 1
                continue
        
            self.debug_no_kern(f"Current margin: {m}")

            # Aplicar ajustes si existen
            target_margin = target
            adjustment_applied = False
        
            self.debug_no_kern(f"Checking adjustments for pair...")
            for adj_idx, adj in enumerate(active_adjustments):
                char = adj.get("name", "")
                position = adj.get("position", "Both")
                mode = adj.get("mode", "Increase")
                percent = adj.get("percent", 0.0)
            
                self.debug_no_kern(f"  Adjustment {adj_idx}: {char} ({position}, {mode}, {percent}%)")
            
                applies = False
                if position == "Both":
                    applies = (char == Lg or char == Rg)
                    self.debug_no_kern(f"    Both position - Check: {char} == {Lg} or {char} == {Rg}: {applies}")
                elif position == "Right":
                    applies = (char == Lg)
                    self.debug_no_kern(f"    Right position - Check: {char} == {Lg}: {applies}")
                elif position == "Left":
                    applies = (char == Rg)
                    self.debug_no_kern(f"    Left position - Check: {char} == {Rg}: {applies}")
            
                if applies:
                    percent_decimal = percent / 100.0
                    self.debug_no_kern(f"    Adjustment applies! Percent: {percent}% ({percent_decimal})")
                
                    if mode == "Increase":
                        target_margin = target * (1.0 - percent_decimal)
                        self.debug_no_kern(f"    Increase mode: {target} * (1 - {percent_decimal}) = {target_margin}")
                    elif mode == "Decrease":
                        target_margin = target * (1.0 + percent_decimal)
                        self.debug_no_kern(f"    Decrease mode: {target} * (1 + {percent_decimal}) = {target_margin}")
                    
                    adjustment_applied = True
                    self.debug_no_kern(f"    New target margin: {target_margin}")
                    break

            if not adjustment_applied:
                self.debug_no_kern(f"No adjustments apply, using base target: {target_margin}")

            # Calcular kerning necesario
            needed = -(m - target_margin)
            self.debug_no_kern(f"Kerning needed: -({m} - {target_margin}) = {needed}")
        
            if needed >= 0:
                self.debug_no_kern(f"✗ No kerning needed (needed >= 0)")
                skipped_no_kerning_needed += 1
                continue

            needed = int(round(needed))
            self.debug_no_kern(f"Rounded kerning value: {needed}")

            # Aplicar kerning - NUNCA crear kerning específic si hay grupos disponibles
            left_glyph_obj = font.glyphs[Lg]
            right_glyph_obj = font.glyphs[Rg]

            # **Siempre usar grupos si están disponibles**
            left_key = Lg
            right_key = Rg
        
            # Usar grupo derecho del glifo izquierdo si existe
            if left_glyph_obj and left_glyph_obj.rightKerningGroup:
                left_key = f"@MMK_L_{left_glyph_obj.rightKerningGroup}"
                self.debug_no_kern(f"Using LEFT group: {left_glyph_obj.rightKerningGroup} → {left_key}")
        
            # Usar grupo izquierdo del glifo derecho si existe
            if right_glyph_obj and right_glyph_obj.leftKerningGroup:
                right_key = f"@MMK_R_{right_glyph_obj.leftKerningGroup}"
                self.debug_no_kern(f"Using RIGHT group: {right_glyph_obj.leftKerningGroup} → {right_key}")
        
            # **VERIFICACIÓN CRÍTICA: No crear kerning específic si ambos tienen grupos**
            # Pero SI crear kerning grupo-grupo
            if (left_glyph_obj and left_glyph_obj.rightKerningGroup and 
                right_glyph_obj and right_glyph_obj.leftKerningGroup):
                # Ambos tienen grupos - esto es CORRECTO (kerning grupo-grupo)
                self.debug_no_kern(f"✅ Both have groups - will create group-group kerning")
            elif (left_glyph_obj and left_glyph_obj.rightKerningGroup and 
                  not (right_glyph_obj and right_glyph_obj.leftKerningGroup)):
                # Solo izquierdo tiene grupo - kerning grupo-glifo
                self.debug_no_kern(f"✅ Left has group, right doesn't - group-glyph kerning")
            elif (not (left_glyph_obj and left_glyph_obj.rightKerningGroup) and 
                  right_glyph_obj and right_glyph_obj.leftKerningGroup):
                # Solo derecho tiene grupo - kerning glifo-grupo
                self.debug_no_kern(f"✅ Right has group, left doesn't - glyph-group kerning")
            else:
                # Ninguno tiene grupo - kerning glifo-glifo
                self.debug_no_kern(f"⚠️ Neither has groups - specific kerning (candau obert)")
        
            # Verificar si ya existe kerning para esta combinación
            existing_kern = font.kerningForPair(mid, left_key, right_key)
            if existing_kern is not None:
                self.debug_no_kern(f"⚠️ Kerning already exists: {left_key}/{right_key} = {existing_kern}")
                skipped_already_has_group_kerning += 1
                continue
        
            # Aplicar kerning
            try:
                font.setKerningForPair(mid, left_key, right_key, needed)
                self.debug_no_kern(f"✅ KERNING APPLIED: {left_key} / {right_key} = {needed}")
            
                if adjustment_applied:
                    applied_with_adjustments += 1
                    self.debug_no_kern(f"✅ WITH ADJUSTMENT")
                else:
                    applied_normal += 1
                    self.debug_no_kern(f"✅ NORMAL KERNING")
                
            except Exception as e:
                self.debug_no_kern(f"✗ ERROR applying kerning: {e}")
    
        # Limpiar cache de miembros de grupos si se modificó kerning
        if hasattr(self, '_group_members_cache'):
            self._group_members_cache.clear()
            self.debug_no_kern(f"Cleared group members cache")
    
        self.debug_no_kern(f"\n{'='*60}")
        self.debug_no_kern("KERNING COMPLETED - SUMMARY")
        self.debug_no_kern(f"Total unique pairs considered: {len(seen)}")
        self.debug_no_kern(f"Pairs with adjustments: {applied_with_adjustments}")
        self.debug_no_kern(f"Pairs with normal kerning: {applied_normal}")
        self.debug_no_kern(f"Pairs skipped (NoKern): {skipped_no_kern}")
        self.debug_no_kern(f"Pairs skipped (invalid/missing): {skipped_invalid}")
        self.debug_no_kern(f"Pairs skipped (no kerning needed): {skipped_no_kerning_needed}")
        self.debug_no_kern(f"Pairs skipped (already has group kerning): {skipped_already_has_group_kerning}")
        self.debug_no_kern(f"Total kerned: {applied_with_adjustments + applied_normal}")
        self.debug_no_kern(f"{'='*60}")

        # Desactivar debug después de terminar
        self.DEBUG_NO_KERN = False

        self.refreshMargin(None)
    
        # También mostrar resumen en la consola normal
        self._debug("GENERAL", f"\n📊 KERNING COMPLETED")
        self._debug("GENERAL", f"   Total unique pairs considered: {len(seen)}")
        self._debug("GENERAL", f"   Pairs with adjustments: {applied_with_adjustments}")
        self._debug("GENERAL", f"   Pairs with normal kerning: {applied_normal}")
        self._debug("GENERAL", f"   Pairs skipped (NoKern): {skipped_no_kern}")
        self._debug("GENERAL", f"   Pairs skipped (invalid/missing glyphs): {skipped_invalid}")
        self._debug("GENERAL", f"   Pairs skipped (no kerning needed): {skipped_no_kerning_needed}")
        self._debug("GENERAL", f"   Pairs skipped (already has group kerning): {skipped_already_has_group_kerning}")
        self._debug("GENERAL", f"   Total kerned: {applied_with_adjustments + applied_normal}")
           
              
                 
                       

    def _is_glyph_blocked_with_sets(self, glyphName, side, noKernSet):
        """Versión mejorada que NO aplica automáticamente a variantes"""
        font = Glyphs.font
        if not font or glyphName not in font.glyphs:
            return False

        glyph = font.glyphs[glyphName]
    
        self.debug_no_kern(f"Checking glyph: {glyphName}, side: {side}")
        self.debug_no_kern(f"NoKern set: {sorted(noKernSet)}")

        # --------------------------------------------------
        # 1. GLIFO INDIVIDUAL: Coincidencia EXACTA del nombre
        # --------------------------------------------------
        if glyphName in noKernSet:
            self.debug_no_kern(f"✓ GLYPH MATCH (exact): {glyphName}")
            return True

        # --------------------------------------------------
        # 2. BASE del glifo (sin extensión) - SOLO si está explícitamente en el set
        # --------------------------------------------------
        base_name = self._get_glyph_base(glyphName)
    
        # **IMPORTANTE: NO aplicar automáticamente a variantes**
        # Si el usuario escribió "l", NO debería bloquear "l.sc" automáticamente
        # Solo bloquear "l.sc" si el usuario escribió explícitamente "l.sc"
    
        # --------------------------------------------------
        # 3. GRUPO DE KERNING del glifo - SOLO el lado correspondiente
        # --------------------------------------------------
        # CORRECCIÓN: Solo verificar el grupo del LADO ESPECIFICADO
        if side == "left":
            # Para "No Kern RightSB" (lado izquierdo del glifo)
            # Verificar el grupo DERECHO del glifo (rightKerningGroup)
            group_attr = "rightKerningGroup"
        else:
            # Para "No Kern LeftSB" (lado derecho del glifo)
            # Verificar el grupo IZQUIERDO del glifo (leftKerningGroup)
            group_attr = "leftKerningGroup"
    
        group = getattr(glyph, group_attr, None)
    
        if group:
            group_name = group.lstrip('@')
        
            # Verificar coincidencia exacta del grupo CON @
            group_key_with_at = f"@{group_name}"
            if group_key_with_at in noKernSet:
                self.debug_no_kern(f"✓ EXACT GROUP MATCH ({side}): {group_key_with_at}")
                return True
        
            # Verificar grupo sin @
            if group_name in noKernSet:
                self.debug_no_kern(f"✓ GROUP MATCH ({side}, no @): {group_name}")
                return True
    
        # --------------------------------------------------
        # 4. Verificar si el glifo es miembro de un grupo excluido
        # --------------------------------------------------
        # **CORRECCIÓN IMPORTANTE: Solo verificar miembros del LADO CORRESPONDIENTE**
        for no_kern_item in noKernSet:
            if no_kern_item.startswith('@'):
                # Es un grupo, obtener sus miembros del LADO CORRESPONDIENTE
                group_members = self.get_kerning_group_members_for_side(no_kern_item, side)
                if glyphName in group_members:
                    self.debug_no_kern(f"✓ GLYPH IS MEMBER OF EXCLUDED GROUP ({side}): {no_kern_item}")
                    return True

        self.debug_no_kern(f"✗ No match found for {glyphName} on side {side}")
        return False        
                  

                  
    def get_kerning_group_members_for_side(self, group_name_with_at, side):
        """Obtiene glifos que pertenecen a un grupo de kerning en un lado específico"""
        font = Glyphs.font
        if not font:
            return []
    
        # Cache para mejorar rendimiento
        if not hasattr(self, '_group_members_cache_side'):
            self._group_members_cache_side = {}
    
        cache_key = f"{group_name_with_at}_{side}"
        if cache_key in self._group_members_cache_side:
            return self._group_members_cache_side[cache_key]
    
        group_name = group_name_with_at.lstrip('@')
        members = set()
    
        for glyph in font.glyphs:
            # Determinar qué atributo verificar según el lado
            if side == "left":
                # Para "No Kern RightSB" - verificar rightKerningGroup
                group = glyph.rightKerningGroup
            else:
                # Para "No Kern LeftSB" - verificar leftKerningGroup
                group = glyph.leftKerningGroup
        
            if group and group.lstrip('@') == group_name:
                members.add(glyph.name)
        
            # También verificar subgrupos (ej: @h.sc.alt es subgrupo de @h.sc)
            if group:
                clean_group = group.lstrip('@')
                if clean_group.startswith(group_name + '.'):
                    members.add(glyph.name)
    
        result = list(members)
        self._group_members_cache_side[cache_key] = result
    
        return result
                  
                  
    def _is_glyph_blocked(self, glyphName, side):
        """Versión original que mantiene compatibilidad"""
        noKernLeft, noKernRight = self._get_no_kern_items()
        noKernSet = noKernLeft if side == "left" else noKernRight
    
        # **VERIFICACIÓN ESPECIAL: Para variantes, ser más estricto**
        if '.' in glyphName:
            self.debug_no_kern(f"Variant glyph detected: {glyphName}")
        
            # Para variantes, solo bloquear si:
            # 1. El nombre exacto está en el set
            # 2. O está en un grupo excluido
            # PERO NO bloquear solo porque la base está en el set
        
            if glyphName in noKernSet:
                self.debug_no_kern(f"✓ Variant exact match: {glyphName}")
                return True
        
            # Verificar grupos
            font = Glyphs.font
            if font and glyphName in font.glyphs:
                glyph = font.glyphs[glyphName]
                group_attr = "rightKerningGroup" if side == "left" else "leftKerningGroup"
                group = getattr(glyph, group_attr, None)
            
                if group:
                    group_name = group.lstrip('@')
                    group_key_with_at = f"@{group_name}"
                
                    if group_key_with_at in noKernSet:
                        self.debug_no_kern(f"✓ Variant group exact match: {group_key_with_at}")
                        return True
                
                    if group_name in noKernSet:
                        self.debug_no_kern(f"✓ Variant group match (no @): {group_name}")
                        return True
        
            # **IMPORTANTE: NO bloquear variante solo porque la base está en NoKern**
            self.debug_no_kern(f"✗ Variant {glyphName} not blocked (base exclusion doesn't apply to variants)")
            return False
    
        # Para glifos base (sin extensión), usar la lógica normal
        return self._is_glyph_blocked_with_sets(glyphName, side, noKernSet)


    def makeAdjustmentPercentCallback(self, index):
        def callback(sender):
            if 0 <= index < len(self.adjustments):
                raw = sender.get().strip().replace('%', '')

                try:
                    new_percent = int(float(raw))
                except ValueError:
                    new_percent = 0

                old_percent = int(self.adjustments[index].get('percent', 0))

                if new_percent != old_percent:
                    self.adjustments[index]['percent'] = new_percent

                sender.set(str(new_percent))

                self.refreshAdjustmentsList()
                self.refreshPreview()
        return callback




    def _clearKerningInTab(self, tab):
        font = Glyphs.font
        if not font or not tab:
            return

        masterID = font.selectedFontMaster.id
        layers = tab.layers
        removed = 0
        seen = set()

        for i in range(len(layers) - 1):
            L = layers[i]
            R = layers[i + 1]
            if not L or not R:
                continue

            left = L.parent.name
            right = R.parent.name
            if left == "space" or right == "space":
                continue

            key = (left, right)
            if key in seen:
                continue
            seen.add(key)

            left_groups = [left]
            right_groups = [right]

            gL = font.glyphs[left]
            gR = font.glyphs[right]

            if gL and gL.rightKerningGroup:
                left_groups.append(f"@MMK_L_{gL.rightKerningGroup}")

            if gR and gR.leftKerningGroup:
                right_groups.append(f"@MMK_R_{gR.leftKerningGroup}")

            for lg in left_groups:
                for rg in right_groups:
                    try:
                        if font.kerningForPair(masterID, lg, rg) is not None:
                            font.removeKerningForPair(masterID, lg, rg)
                            removed += 1
                    except:
                        pass



    def clearKerningForCurrentTab(self, sender=None):
        font = Glyphs.font
        if not font:
            return

        tab = font.currentTab
        if not tab:
            return
    
        if not tab.text:
            return

        masterID = font.selectedFontMaster.id
        removed = 0
        protected = 0

        import re
        protected_pairs = set()
    
        matches = list(re.finditer(r'#([^#]+)#', tab.text))
    
        if matches:
            for match in matches:
                content = match.group(1).strip()
                full_match = match.group(0)
            
                if len(content) < 2:
                    continue
            
                glyphs = []
                for char in content:
                    try:
                        g = font.glyphForCharacter_(ord(char))
                        if g:
                            glyphs.append(g.name)
                    except Exception:
                        pass
            
                if len(glyphs) < 2:
                    continue
            
                for i in range(len(glyphs) - 1):
                    left = glyphs[i]
                    right = glyphs[i + 1]
                    protected_pairs.add((left, right))
        else:
            layers = tab.layers
            seen = set()
        
            for i in range(len(layers) - 1):
                L = layers[i]
                R = layers[i + 1]
                if not L or not R:
                    continue

                left = L.parent.name
                right = R.parent.name
                if left == "space" or right == "space":
                    continue

                key = (left, right)
                if key in seen:
                    continue
                seen.add(key)

                left_variants = [left]
                right_variants = [right]

                gL = font.glyphs[left] if left in font.glyphs else None
                gR = font.glyphs[right] if right in font.glyphs else None

                if gL and gL.rightKerningGroup:
                    left_variants.append(f"@MMK_L_{gL.rightKerningGroup}")

                if gR and gR.leftKerningGroup:
                    right_variants.append(f"@MMK_R_{gR.leftKerningGroup}")

                for lg in left_variants:
                    for rg in right_variants:
                        try:
                            if font.kerningForPair(masterID, lg, rg) is not None:
                                font.removeKerningForPair(masterID, lg, rg)
                                removed += 1
                        except:
                            pass

            all_pairs = set()
            layers = tab.layers
        
            for i in range(len(layers) - 1):
                L = layers[i]
                R = layers[i + 1]
                if not L or not R:
                    continue
            
                left = L.parent.name
                right = R.parent.name
                if left == "space" or right == "space":
                    continue
            
                all_pairs.add((left, right))
        
            pairs_to_process = all_pairs - protected_pairs
        
            seen = set()
            for left, right in pairs_to_process:
                key = (left, right)
                if key in seen:
                    continue
                seen.add(key)
            
                left_variants = [left]
                right_variants = [right]

                gL = font.glyphs[left] if left in font.glyphs else None
                gR = font.glyphs[right] if right in font.glyphs else None

                if gL and gL.rightKerningGroup:
                    left_variants.append(f"@MMK_L_{gL.rightKerningGroup}")

                if gR and gR.leftKerningGroup:
                    right_variants.append(f"@MMK_R_{gR.leftKerningGroup}")

                for lg in left_variants:
                    for rg in right_variants:
                        try:
                            if font.kerningForPair(masterID, lg, rg) is not None:
                                font.removeKerningForPair(masterID, lg, rg)
                                removed += 1
                        except:
                            pass
        
            protected = len(protected_pairs)

        current_text = tab.text or ""
        reorganized_text = self._reorganizeTo4Columns(current_text)
    
        if reorganized_text != current_text:
            tab.text = reorganized_text
            
            # Después de modificar kerning, limpiar cache
            if master_id in self._kerningCache:
                del self._kerningCache[master_id]

        self._debug("GENERAL", f"📊 RESUMEN CLEAR KERNING")
        self._debug("GENERAL", f"   Pares protegidos (dentro de #...#): {protected}")
        self._debug("GENERAL", f"   Pares de kerning eliminados: {removed}")
        
        
    def removeHashSymbolsCallback(self, sender):
        font = Glyphs.font
        if not font or not font.currentTab:
            return

        tab = font.currentTab
        original_text = tab.text or ""

        if not original_text:
            return

        import re

        lines_before = original_text.split('\n')
        new_lines = []

        for line in lines_before:
            cleaned_line = line.replace('#', '')
            new_lines.append(cleaned_line)

        new_text = '\n'.join(new_lines)
    
        tab.text = new_text
    
        if hasattr(tab, 'layers') and tab.layers:
            layers_cleaned = 0
            for layer in tab.layers:
                if hasattr(layer, 'text') and layer.text and '#' in layer.text:
                    layer.text = layer.text.replace('#', '')
                    layers_cleaned += 1
		
		
		
		

    def _charToGlyphName(self, font, char_or_name):
        if not char_or_name:
            return None
    
        if '.' in char_or_name and char_or_name in font.glyphs:
            return char_or_name
    
        if len(char_or_name) == 1:
            try:
                g = font.glyphForCharacter_(ord(char_or_name))
                return g.name if g else None
            except:
                return None
    
        if char_or_name in font.glyphs:
            return char_or_name
    
        return None

    def kernHashWordsCallback(self, sender=None):
        font = Glyphs.font
        if not font or not font.currentTab:
            return

        try:
            baseMargin = float(self.tab1.mValue.get())
        except Exception:
            return

        tab = font.currentTab
        layers = [l for l in tab.layers if l and l.parent]
        if len(layers) < 2:
            return

        masterID = font.selectedFontMaster.id

        glyph_names = [l.parent.name for l in layers]

        def is_hash(name):
            return name.split(".")[0] == "numbersign"

        hash_positions = [i for i, n in enumerate(glyph_names) if is_hash(n)]

        if len(hash_positions) < 2:
            return

        applied = 0
        errors = 0

        for b in range(0, len(hash_positions) - 1, 2):
            start = hash_positions[b]
            end = hash_positions[b + 1]
            inner = glyph_names[start + 1 : end]

            if len(inner) < 2:
                continue

            for i in range(len(inner) - 1):
                left = inner[i]
                right = inner[i + 1]

                if left not in font.glyphs or right not in font.glyphs:
                    continue

                try:
                    if not self._pair_allowed_for_generation(left, right):
                        continue
                except Exception:
                    errors += 1
                    continue

                try:
                    m = margin_for_pair(font, masterID, left, right)
                    if m is None or m >= 10000:
                        continue
                except Exception:
                    errors += 1
                    continue

                needed = -(m - baseMargin)
                if needed >= 0:
                    continue

                k_value = int(round(needed))

                try:
                    gL = font.glyphs[left]
                    gR = font.glyphs[right]

                    left_key = left
                    right_key = right

                    if gL and getattr(gL, "rightKerningGroup", None):
                        left_key = f"@MMK_L_{gL.rightKerningGroup}"

                    if gR and getattr(gR, "leftKerningGroup", None):
                        right_key = f"@MMK_R_{gR.leftKerningGroup}"

                    font.setKerningForPair(masterID, left_key, right_key, k_value)
                    applied += 1

                except Exception:
                    errors += 1

        # Después de modificar kerning, limpiar cache
        if master_id in self._kerningCache:
            del self._kerningCache[master_id]
                    
                    
        if applied > 0:
            try:
                self.refreshMargin(None)
            except Exception:
                pass



    def _resolveGlyphName(self, token, font):
        token = token.strip()
        if not token:
            return None
    
        if token in font.glyphs:
            return token
    
        if '.' in token:
            base_name = token.split('.')[0]
            if base_name in font.glyphs:
                return base_name
    
        if len(token) == 1:
            try:
                g = font.glyphForCharacter_(ord(token))
                return g.name if g else None
            except:
                return None
    
        for glyph in font.glyphs:
            if glyph.name == token:
                return token
    
        return None



   
        








        
    def format_header_with_spaces(self, text, add_spaces=True):
        if not add_spaces:
            return text
        
        result = []
        for char in text:
            if char == ' ':
                result.append('	 ')
            else:
                result.append(char)
                result.append(' ')
        return ''.join(result).rstrip()
        

    def closeCurrentTabCallback(self, sender=None):
        font = Glyphs.font
        if font and font.currentTab:
            font.currentTab.close()


    def _setup_tab1(self):
        y = 10

        self.tab1.section1Title = TextBox((12, y, 200, 20), "Kern Engine")
        y += 25

        self.tab1.currentLabel = TextBox((12, y + 2, 60, 20), "Current")
        self.tab1.currentInput = EditText(
            (70, y, 60, 22), "H", callback=self.refreshMargin
        )
        self.tab1.currentInputRight = EditText(
            (140, y, 60, 22), "H", callback=self.refreshMargin
        )
        self.tab1.resultLabel = TextBox(
            (210, y + 2, 180, 20), "margin: — • kern: —"
        )

        y += 32

        self.tab1.noKernLeftLabel = TextBox((12, y, 130, 20), "No Kern RightSD:")
        self.tab1.noKernRightLabel = TextBox((160, y, 130, 20), "No Kern LeftSD:")

        y += 18
        self.tab1.noKernLeft = TextEditor((12, y + 5, 130, 60), "H\nl\nh.sc")
        self.tab1.noKernRight = TextEditor((160, y + 5, 130, 60), "H\nl\nh.sc")

        self.tab1.saveNoKernButton = Button(
            (300, y + 5, 75, 22),
            "Save",
            callback=self.saveNoKernGroups
        )
        self.tab1.loadNoKernButton = Button(
            (300, y + 35, 75, 22),
            "Load",
            callback=self.loadNoKernGroups
        )

        y += 75

        self.tab1.marginLabel = TextBox((12, y + 2, 60, 20), "Margin:")
        self.tab1.mValue = EditText((70, y, 50, 22), "80")
        self.tab1.kernButton = Button(
            (130, y, 140, 24),
            "Kern Tab",
            callback=self.applyCharacterAdjustmentsFromTab
        )
    
        self.tab1.kernHashWordsButton = Button(
            (280, y, 60, 24),
            "#AV#",
            callback=self.kernHashWordsCallback
        )

        self.tab1.removeHashButton = Button(
            (342, y, 40, 24),
            "🗑️#",
            callback=self.removeHashSymbolsCallback
        )

        self.tab1.groupMembersButton = Button(
            (285, y+100, 60, 24),
            "@ Tab",
            callback=self.listKerningGroupMembersInNewTab
        )

        self.tab1.groupMembersButton.getNSButton().setToolTip_(
            "List members of the kerning group\nof the glyph to the right of the cursor"
        )

        self.tab1.closeCurrentTabButtonTop = Button(
            (350, y + 100, 25, 24),
            "✕",
            callback=self.closeCurrentTabCallback
        )

        self.tab1.closeCurrentTabButtonBottom = Button(
            (350, y + 209, 25, 24),
            "✕",
            callback=self.closeCurrentTabCallback
        )

        self.tab1.groupLegend = TextBox(
            (285, y+60 + 26, 120, 14),
            "@ group → new tab",
            sizeStyle="mini"
        )
        
        y += 40

        self.tab1.separator1 = HorizontalLine((10, y - 5, -10, 1))
        y += 15
        self.tab1.separator3 = HorizontalLine((10, y + 22, -10, 1))
        y += 1

        self.tab1.section2Title = TextBox(
            (12, y + 25, 200, 20), "Pairs Generator"
        )
        y += 30

        self.tab1.hidePairsButton = Button(
            (12, y - 45, 180, 28),
            "Hide existing pairs",
            callback=self.hideExistingPairsSmart
        )
        self.tab1.removeTabKern = Button(
            (202, y - 45, 180, 28),
            "Remove tab kern",
            callback=self.removeTabKernCallback
        )

        y += 40

        self.tab1.baseLabel = TextBox(
            (12, y - 20, 130, 20), "Base glyph names:"
        )
        y += 25
        self.tab1.baseInput = EditText((12, y - 20, -12, 24), "A,")

        y += 40

        self.tab1.separator6 = HorizontalLine((10, y + 11, -10, 1))
        y += 4

        self.tab1.generateButton = Button(
            (12, y + 10, 130, 32),
            "Generate Tabs",
            callback=self.generatePairsGeneratorCallback
        )
        self.tab1.closeTabsButton = Button(
            (152, y + 10, 130, 32),
            "CLOSE TABS",
            callback=self.closeAllTabsCallback
        )

        self.tab1.navPrevButton = Button(
            (292, y + 10, 24, 32),
            "◀",
            callback=self.navigateTabsCallback
        )
        self.tab1.navNextButton = Button(
            (318, y + 10, 24, 32),
            "▶",
            callback=self.navigateTabsCallback
        )

        y += 40
        self.tab1.separator7 = HorizontalLine((10, y + 8, -10, 1))
        y += 4

        self.tab1.positionLabel = TextBox(
            (12, y - 70, 60, 20), "Position:"
        )
        self.tab1.positionPopup = PopUpButton(
            (80, y - 70, 100, 24),
            ["Left", "Right", "Both"]
        )
        self.tab1.positionPopup.set(2)
    
        self.tab1.hideKernedPairsCheck = CheckBox(
            (15, y+390 - 70, 150, 24),
            "Hide kerned pairs",
            value=True
        )
    
        self.tab1.showInfoInTabCheck = CheckBox(
            (300, y+390 - 70, 150, 24),
            "Info in Tab",
            value=False
        )
        
        self.tab1.showOnlyBossCheck = CheckBox(
            (155, y+390 - 70, 150, 24),
            "Show only @ boss",
            value=True
        )

        y += 40

        self.tab1.neighLabel = TextBox(
            (12, y - 30, 120, 20), "Neighboring sets:"
        )
        y += 25

        self.tab1.latinUpperCheck = CheckBox(
            (12, y - 30, 110, 20), "Latin Upper", value=False
        )
        self.tab1.latinLowerCheck = CheckBox(
            (130, y - 30, 110, 20), "Latin Lower", value=True
        )
        self.tab1.numCheck = CheckBox(
            (250, y - 30, 90, 20), "Numbers", value=False
        )

        y += 25

        self.tab1.puncCheck = CheckBox(
            (12, y - 30, 110, 20), "Punctuation", value=False
        )
        self.tab1.symCheck = CheckBox(
            (130, y - 30, 90, 20), "Symbols", value=False
        )
        self.tab1.myGlyphsCheck = CheckBox(
            (250, y - 30, 90, 20), "My Glyphs", value=False
        )

        y += 25

        self.tab1.cyrillicUpperCheck = CheckBox(
            (12, y - 30, 120, 20), "Cyrillic Upper", value=False
        )
        self.tab1.cyrillicLowerCheck = CheckBox(
            (130, y - 30, 120, 20), "Cyrillic Lower", value=False
        )

        y += 40

        self.tab1.exLeftLabel = TextBox(
            (12, y - 34, 220, 20), "Exclude first RightSB:"
        )
        self.tab1.exRightLabel = TextBox(
            (190, y - 34, 220, 20), "Exclude second LeftSB:"
        )

        y += 30
        self.tab1.exLeft = TextEditor((12, y+0 - 40, 170, 80), "@nokern")
        self.tab1.exRight = TextEditor((190, y+ - 40, 180, 80), "@nokern")
        
        self.tab1.saveExcludeButton = Button(
            (12, y+90 - 40, 85, 22),
            "Save",
            callback=self.saveExcludeGroups
        )
        self.tab1.loadExcludeButton = Button(
            (110, y+55 - 5, 85, 22),
            "Load",
            callback=self.loadExcludeGroups
        )

        y += 100

        self.tab1.prefixLabel = TextBox((12, y+55 - 60, 45, 20), "Prefix:")
        self.tab1.prefixInput = EditText((65, y+55 - 60, 50, 24), "HH")
        self.tab1.suffixLabel = TextBox((125, y+55 - 60, 45, 20), "Suffix:")
        self.tab1.suffixInput = EditText((175, y+55 - 60, 50, 24), "HH")

        y += 40

        self.tab1.separator2 = HorizontalLine((10, y+100 - 110, -10, 1))
        y += 40
        self.tab1.separator4 = HorizontalLine((10, y+10 - 105, -10, 1))
        y += 40

        feature_names = self.getFeatureNames()
        self.tab1.featureLabel = TextBox((200, y-340 - 135, 60, 20), "Feature:")
        self.tab1.featurePopup = PopUpButton(
            (260, y-340 - 135, 90, 24),
            feature_names
        )

        if "aalt" in feature_names:
            self.tab1.featurePopup.set(feature_names.index("aalt"))
        elif feature_names:
            self.tab1.featurePopup.set(0)


    
    def __init__(self):
        self.w = FloatingWindow((400, 800), "Kern Coach")
        self.baseglyphslist = []
        
        self._kerningCache = {}  # Cache de kerning por master
        
        # Sistema de debug centralizado
        self.DEBUG_ALL = False  # Activa todo el debug
        self.DEBUG_EXCLUSION = False
        self.DEBUG_HAS_KERNING = False  # Para debug de has_kerning
        self.DEBUG_NO_KERN = False
        self.DEBUG_HIDE = True  # Para debug específico de hideExistingPairsSmart
        self.DEBUG_TAB = False
    
        self.initializePairsGeneratorCollections()
    
        if not hasattr(self, 'adjustments'):
            self.adjustments = [
                {
                    "active": True,
                    "name": "",
                    "position": "Both",
                    "mode": "Increase",
                    "percent": 0.0,
                    "selected": False
                }
            ]
    
        self.previewMode = "virtual"
        self.characterAdjustmentsActive = True
    
        tab_titles = ["Negative values", "Add Base Glyphs", "Adjusts"]
        self.w.tabs = Tabs((0, 10, 400, 800), tab_titles)
    
        self.tab1 = self.w.tabs[0]
        self._setup_tab1()
    
        self.tab2 = self.w.tabs[1]
        self._setup_tab2()
    
        self.tab3 = self.w.tabs[2]
        self._setup_tab3()
    
        self.w.open()
        self.refreshMargin(None)
    
        try:
            import time
            time.sleep(0.2)
        
            if hasattr(self.tab2, 'listContainer'):
                sv = self.tab2.listContainer._nsObject
                if sv:
                    cv = sv.contentView()
                    cv.scrollToPoint_((0, 1000))
                    cv.scrollToPoint_((0, 0))
                    sv.reflectScrolledClipView_(cv)
        
            if hasattr(self.tab3, 'listContainer'):
                sv = self.tab3.listContainer._nsObject
                if sv:
                    cv = sv.contentView()
                    cv.scrollToPoint_((0, 1000))
                    cv.scrollToPoint_((0, 0))
                    sv.reflectScrolledClipView_(cv)
                
        except Exception:
            pass
    
    def _setup_tab2(self):
        y = 10
        self.tab2.titleLabel = TextBox((12, y, 200, 20), "Add Base Glyphs")
        y += 30

        self.tab2.headerSelect = TextBox((12, y, 30, 20), "")
        self.tab2.headerName = TextBox((50, y, 180, 20), "Glyph Name")
        self.tab2.headerCategory = TextBox((240, y, 120, 20), "Category")
        y += 25
    
        y += 8
    
        self.tab2.listContainer = self._createScrollableList(
            parent=self.tab2,
            frame=(12, y, 376, 470),
            content_width=355,
            min_height=470
        )

        y += 470 + 5

        self.tab2.addGlyphButton = Button((12, y, 160, 20), "Add Glyph", callback=self.addGlyphCallback)
        self.tab2.deleteSelectedButton = Button((12, y + 28, 160, 20), "Delete Selected Glyphs", callback=self.deleteSelectedGlyphs)
        self.tab2.selectAllButton = Button((12, y + 56, 160, 20), "Select All Glyphs", callback=self.selectAllGlyphsCallback)

        self.tab2.saveListButton = Button((220, y, 160, 20), "Save List", callback=self.saveListCallback)
        self.tab2.loadListButton = Button((220, y + 28, 160, 20), "Load List", callback=self.loadListCallback)

        self.refreshGlyphsList()


    def refreshGlyphsList(self):
        self._refreshScrollableList(
            scrollView=self.tab2.listContainer,
            buildRowCallback=self._buildTab2Row,
            items=self.baseglyphslist,
            rowHeight=26,
            minHeight=470
        )

        self.updateSelectAllButtonText()
    
        try:
            sv = self.tab2.listContainer._nsObject
            cv = sv.contentView()
            max_y = sv.documentView().frame().size.height - sv.contentView().frame().size.height
            if max_y > 0:
                cv.scrollToPoint_((0, max_y))
            cv.scrollToPoint_((0, 0))
            sv.reflectScrolledClipView_(cv)
        except:
            pass

    def _refreshScrollableList(
        self,
        scrollView,
        buildRowCallback,
        items,
        rowHeight,
        minHeight
    ):
        inner = scrollView.innerGroup

        for key in list(inner.__dict__.keys()):
            if key.startswith(("cb_", "name_", "cat_", "adj_")):
                delattr(inner, key)

        inner.dynamiccontrols = []

        ypos = 0

        for i in range(len(items)):
            buildRowCallback(i, ypos)
            ypos += rowHeight

        contentHeight = max(ypos, minHeight)
        inner._nsObject.setFrame_(((0, 0), (inner._nsObject.frame().size.width, contentHeight)))

        sv = scrollView._nsObject
        sv.setDocumentView_(inner._nsObject)

        cv = sv.contentView()
        max_y = sv.documentView().frame().size.height - sv.contentView().frame().size.height
        if max_y > 0:
            cv.scrollToPoint_((0, max_y))
        cv.scrollToPoint_((0, 0))
        sv.reflectScrolledClipView_(cv)

    def hideExistingPairsSmart(self, sender=None):
        self._debug("GENERAL", "🔥 hideExistingPairsSmart STARTED")
    
        font = Glyphs.font
        if not font or not font.currentTab:
            self._debug("ERROR", "❌ No font or tab open")
            return

        master_id = font.selectedFontMaster.id
        tab = font.currentTab

        if not tab.text:
            self._debug("ERROR", "❌ Tab is empty")
            return

        try:
            hide_gap_spaces = int(self.tab1.hideGapInput.get() if hasattr(self.tab1, 'hideGapInput') else 7)
        except:
            hide_gap_spaces = 7
        hide_gap = " " * hide_gap_spaces

        original_text = tab.text

        lines = original_text.splitlines()
        new_lines = []

        total_pairs = 0
        hidden_pairs = 0
        kept_pairs = 0

        # Obtener features activas del tab
        active_features = self._get_active_features_from_tab()
    
        self._debug("HIDE", f"\n🔍 HIDE EXISTING PAIRS DEBUG START")
        self._debug("HIDE", f"   Master ID: {master_id}")
        self._debug("HIDE", f"   Active features in tab: {active_features}")
        self._debug("HIDE", f"   Original text lines: {len(lines)}")
    
        # Activar debug temporal
        DEBUG_HAS_KERNING_ORIGINAL = getattr(self, "DEBUG_HAS_KERNING", False)
        DEBUG_HIDE_ORIGINAL = getattr(self, "DEBUG_HIDE", False)
        self.DEBUG_HAS_KERNING = True
        self.DEBUG_HIDE = True

        for line_num, line in enumerate(lines):
            raw = line.rstrip()
    
            if not raw:
                new_lines.append(line)
                continue
    
            is_header = raw.lstrip().startswith((
                "C a t e g o r y",
                "B A S E",
                "P o s i t i o n",
                "H i d e",
                "E x c l u d e",
                "###",
                "/N/O/",
                "/A/l/l/",
                "M e m b e r s",
                "Kern Coach Preview"
            ))
    
            if is_header:
                new_lines.append(line)
                continue
    
            import re
            gap_pattern = r'\s{' + str(max(3, hide_gap_spaces)) + r',}'
            blocks = re.split(gap_pattern, raw)
            blocks = [b.strip() for b in blocks if b.strip()]
    
            kept_blocks = []
    
            for block_idx, block in enumerate(blocks):
                total_pairs += 1
        
                left_name = None
                right_name = None
        
                if "/" in block:
                    parts = [p for p in block.split("/") if p]
            
                    if len(parts) >= 2:
                        for i in range(len(parts) - 1):
                            potential_left = parts[i]
                            potential_right = parts[i + 1]
                    
                            if (potential_left in font.glyphs and 
                                potential_right in font.glyphs):
                                left_name = potential_left
                                right_name = potential_right
                                break
            
                    if not left_name and len(parts) >= 4:
                        mid = len(parts) // 2
                        left_name = parts[mid - 1]
                        right_name = parts[mid]
                else:
                    tokens = block.split()
            
                    for i in range(len(tokens) - 1):
                        if (tokens[i] in font.glyphs and 
                            tokens[i + 1] in font.glyphs):
                            left_name = tokens[i]
                            right_name = tokens[i + 1]
                            break
        
                    if not left_name and len(tokens) >= 2:
                        left_name = tokens[0]
                        right_name = tokens[1]
    
                if not left_name or not right_name:
                    kept_blocks.append(block)
                    kept_pairs += 1
                    continue
        
                # **VERIFICACIÓN ESPECIAL: Detectar si son variantes**
                left_base = self._get_glyph_base(left_name)
                right_base = self._get_glyph_base(right_name)
        
                is_left_variant = '.' in left_name
                is_right_variant = '.' in right_name
        
                self._debug("HIDE", f"\n       Checking pair: {left_name} / {right_name}")
                if is_left_variant:
                    self._debug("HIDE", f"       Left is variant: {left_name} (base: {left_base})")
                if is_right_variant:
                    self._debug("HIDE", f"       Right is variant: {right_name} (base: {right_base})")
        
                # *** CAMBIO CRÍTICO: Verificar solo kerning por GRUPOS (candados cerrados) ***
                has_group_kerning = self._has_group_kerning_only(font, master_id, left_name, right_name)
        
                self._debug("HIDE", f"       Has group kerning (candado cerrado): {has_group_kerning}")
        
                # Verificar si tiene kerning específico (candado abierto) - SOLO para debug
                has_specific_kerning = self._has_specific_kerning_pair(font, master_id, left_name, right_name)
                if has_specific_kerning:
                    self._debug("HIDE", f"       ⚠️ Pair has specific kerning (candado abierto) - IGNORING for hiding")
            
                # **REGLA CRÍTICA: Si es una variante y no tiene kerning por grupos,**
                # **verificar si DEBERÍAMOS considerar el kerning de base por grupos**
        
                special_case_handled = False
        
                if not has_group_kerning and (is_left_variant or is_right_variant):
                    self._debug("HIDE", f"       Variant pair without group kerning, checking base groups...")
            
                    # Caso 1: Ambos son variantes con la MISMA extensión
                    if is_left_variant and is_right_variant:
                        left_ext = left_name.split('.')[1]
                        right_ext = right_name.split('.')[1]
                
                        if left_ext == right_ext:
                            # Ambos son .sc, .ss01, etc.
                            self._debug("HIDE", f"         Both have same extension: .{left_ext}")
                    
                            # Verificar si el kerning de base existe POR GRUPOS
                            base_has_group_kerning = self._has_group_kerning_only(font, master_id, left_base, right_base)
                            self._debug("HIDE", f"         Base pair {left_base}/{right_base} has group kerning: {base_has_group_kerning}")
                    
                            if base_has_group_kerning:
                                # **DECISIÓN: ¿Ocultar o mostrar?**
                                # En Glyphs, el kerning de base por grupos NO se aplica automáticamente a variantes
                                # a menos que uses grupos específicos. Por lo tanto, NO ocultamos.
                                self._debug("HIDE", f"         ⚠️ Base has group kerning but variants don't - KEEPING pair")
                                has_group_kerning = False  # Mantener como False
                                special_case_handled = True
            
                    # Caso 2: Solo uno es variante
                    elif is_left_variant or is_right_variant:
                        self._debug("HIDE", f"         Mixed pair (one variant, one base)")
                
                        # Verificar kerning por grupos para esta combinación mixta
                        # En Glyphs, e/Y por grupos NO implica automáticamente e.sc/Y
                        # Solo se aplica si hay grupos específicos configurados
                
                        # No hacemos nada especial aquí - ya _has_group_kerning_only lo verificó
                        special_case_handled = True
        
                # **DECISIÓN FINAL: Ocultar o mantener**
                # Solo ocultamos si tiene kerning POR GRUPOS (candado cerrado)
                # Ignoramos completamente los candados abiertos
                if has_group_kerning:
                    # Ocultar solo si encontramos kerning POR GRUPOS (candado cerrado)
                    hidden_pairs += 1
                    self._debug("HIDE", f"       ✅ HIDDEN: {left_name} / {right_name} (has group kerning 🔒)")
                else:
                    kept_blocks.append(block)
                    kept_pairs += 1
            
                    if special_case_handled:
                        self._debug("HIDE", f"       ✅ KEPT: {left_name} / {right_name} (variant without group kerning)")
                    elif has_specific_kerning:
                        self._debug("HIDE", f"       ✅ KEPT: {left_name} / {right_name} (has specific kerning 🔓 - ignoring)")
                    else:
                        self._debug("HIDE", f"       ✅ KEPT: {left_name} / {right_name} (no group kerning)")
    
            if kept_blocks:
                columns = 4
                for i in range(0, len(kept_blocks), columns):
                    chunk = kept_blocks[i:i + columns]
                    if chunk:
                        line_text = chunk[0]
                        for j in range(1, len(chunk)):
                            line_text += hide_gap + chunk[j]
                        new_lines.append(line_text)
                if len(kept_blocks) > columns:
                    new_lines.append("")

        final_text = "\n".join(new_lines)

        # Restaurar estado original del debug
        self.DEBUG_HAS_KERNING = DEBUG_HAS_KERNING_ORIGINAL
        self.DEBUG_HIDE = DEBUG_HIDE_ORIGINAL
    
        if final_text != original_text:
            tab.text = final_text
            self._debug("HIDE", f"   Text modified: {len(original_text.splitlines())} → {len(final_text.splitlines())} lines")
        else:
            self._debug("HIDE", f"   Text unchanged")
    
        # Mostrar resumen
        self._debug("HIDE", f"\n📊 HIDE EXISTING PAIRS SUMMARY")
        self._debug("HIDE", f"   Total blocks checked: {total_pairs}")
        self._debug("HIDE", f"   Blocks hidden (had GROUP kerning 🔒): {hidden_pairs}")
        self._debug("HIDE", f"   Blocks kept (no group kerning): {kept_pairs}")
    
        if active_features:
            self._debug("HIDE", f"   Active features considered: {active_features}")
    
        if hidden_pairs > 0:
            self._debug("HIDE", f"   ✅ Successfully hid {hidden_pairs} pairs with GROUP kerning (candados cerrados)")
        else:
            self._debug("HIDE", f"   ⚠️ No pairs were hidden (only GROUP kerning counts, specific kerning 🔓 is ignored)")
    
        self._debug("HIDE", f"🔍 HIDE EXISTING PAIRS DEBUG END\n")
        self._debug("GENERAL", "🔥 hideExistingPairsSmart COMPLETED")



    def _hidePairsWithExtensions(self, tab, font, master_id):
        if hasattr(tab, 'text'):
            text = tab.text or ""
        else:
            text = tab or ""
    
        if "/" in text:
            blocks = [b for b in text.split() if b]

            all_pairs = []

            for block in blocks:
                if not block.startswith("/"):
                    block_norm = "/" + block
                else:
                    block_norm = block

                parts = [p for p in block_norm.split("/") if p]
                if len(parts) < 2:
                    continue

                for i in range(len(parts) - 1):
                    left = parts[i]
                    right = parts[i + 1]
                    if left == "space" or right == "space":
                        continue
                    all_pairs.append(f"/{left}/{right}")

            if not all_pairs:
                return text

            remaining_pairs = self.filter_pairs_with_existing_kerning(all_pairs, font, master_id)

            if not remaining_pairs:
                return ""

            new_text = " ".join(remaining_pairs)
            return new_text

        words = [w for w in text.replace("\n", " ").split(" ") if w]
        all_pairs = []

        for word in words:
            if len(word) < 3:
                continue

            chars = list(word)
            for i in range(len(chars) - 1):
                left_ch = chars[i]
                right_ch = chars[i + 1]

                gL = self._resolve_name_to_glyph(font, left_ch)
                gR = self._resolve_name_to_glyph(font, right_ch)
                if not gL or not gR:
                    continue

                all_pairs.append(f"/{gL.name}/{gR.name}")

        if not all_pairs:
            return text

        remaining_pairs = self.filter_pairs_with_existing_kerning(all_pairs, font, master_id)

        if not remaining_pairs:
            return ""

        new_text = " ".join(remaining_pairs)
        return new_text

        
    def _hidePairsByLayers(self, tab, font, master_id):
        layers = [l for l in tab.layers if l and l.parent]
        if len(layers) < 2:
            return tab.text

        kept_layers = []
        i = 0
        removed_pairs = 0

        while i < len(layers) - 1:
            L = layers[i]
            R = layers[i + 1]
            left = L.parent.name
            right = R.parent.name

            if left not in font.glyphs or right not in font.glyphs:
                kept_layers.append(L)
                i += 1
                continue

            gL = font.glyphs[left]
            gR = font.glyphs[right]

            left_keys = {left}
            right_keys = {right}

            if gL.rightKerningGroup:
                left_keys.add(f"@MMK_L_{gL.rightKerningGroup}")
            if gR.leftKerningGroup:
                right_keys.add(f"@MMK_R_{gR.leftKerningGroup}")

            has_kern = False
            for lk in left_keys:
                for rk in right_keys:
                    if font.kerningForPair(master_id, lk, rk) is not None:
                        has_kern = True
                        break
                if has_kern:
                    break

            if has_kern:
                removed_pairs += 1
                i += 2
            else:
                kept_layers.append(L)
                i += 1

        if i == len(layers) - 1:
            kept_layers.append(layers[-1])

        tab.layers = kept_layers
        return tab.text


        
        
    
    def _hidePairsNoExtensions(self, text, font, master_id):
        import re

        blocks = re.split(r'(\s{3,})', text)

        new_parts = []
        hidden_blocks = 0

        for i in range(0, len(blocks), 2):
            block = blocks[i] if i < len(blocks) else ""
            sep      = blocks[i+1] if i+1 < len(blocks) else ""

            if not block.strip():
                new_parts.append(block)
                if sep:
                    new_parts.append(sep)
                continue

            glyphs = []
            for ch in block:
                if ch == "/":
                    continue
                g = font.glyphForCharacter_(ord(ch))
                glyphs.append(g.name if g else None)

            if len([g for g in glyphs if g]) < 2:
                new_parts.append(block)
                if sep:
                    new_parts.append(sep)
                continue

            has_kerned_pair = False
            for j in range(len(glyphs) - 1):
                left_name  = glyphs[j]
                right_name = glyphs[j + 1]
                if not left_name or not right_name:
                    continue

                if self.has_kerning(font, master_id, left_name, right_name):
                    has_kerned_pair = True
                    break

            if has_kerned_pair:
                hidden_blocks += 1
            else:
                new_parts.append(block)
                if sep:
                    new_parts.append(sep)

        return "".join(new_parts)
        
        
        


    
    
    
    
    def _processWithExtensions(self, tab, font, master_id):
        import re

        text = tab.text or ""

        lines = text.splitlines()
        new_lines = []
        hidden_lines = 0

        for idx, line in enumerate(lines):
            raw_line = line

            tokens = [t for t in raw_line.split(" ") if t.strip()]

            keep_tokens = []
            for token in tokens:
                parts = [p for p in token.split("/") if p]
                if len(parts) < 2:
                    keep_tokens.append(token)
                    continue

                mid = len(parts) // 2
                left_name  = parts[mid - 1]
                right_name = parts[mid]

                if left_name not in font.glyphs or right_name not in font.glyphs:
                    keep_tokens.append(token)
                    continue

                if self.has_kerning(font, master_id, left_name, right_name):
                    continue
                else:
                    keep_tokens.append(token)

            if keep_tokens:
                new_line = " ".join(keep_tokens)
                new_lines.append(new_line)
            else:
                hidden_lines += 1

        final_text = "\n".join(new_lines).strip()

        return final_text
        

    def _smartHide_with_extensions(self, tab, font, master_id):
        import re

        text = tab.text or ""

        tokens = [t for t in text.split() if t.strip()]

        kept_tokens = []
        hidden_tokens = []

        for token in tokens:
            parts = [p for p in token.split("/") if p]

            if len(parts) < 2:
                kept_tokens.append(token)
                continue

            mid = len(parts) // 2
            left_name  = parts[mid - 1]
            right_name = parts[mid]

            if left_name not in font.glyphs or right_name not in font.glyphs:
                kept_tokens.append(token)
                continue

            if self.has_kerning(font, master_id, left_name, right_name):
                hidden_tokens.append(token)
            else:
                kept_tokens.append(token)

        final_text = " ".join(kept_tokens)

        return final_text




    def smartHideCallback(self, sender=None):
        font = Glyphs.font
        if not font or not font.currentTab:
            return

        tab = font.currentTab
        master_id = font.selectedFontMaster.id

        all_glyphs = []
        ext_glyphs = []

        for layer in tab.layers:
            if not layer or not layer.parent:
                continue
            name = layer.parent.name
            all_glyphs.append(name)
            if "." in name:
                ext_glyphs.append(name)

        total_ext = len(ext_glyphs)
        has_extensions = total_ext > 0

        if has_extensions:
            tab.text = self._smartHide_with_extensions(tab, font, master_id)
        else:
            tab.text = self._processNormal(tab, font, master_id)

        
    
    def _processNormal(self, tab, font, master_id):
        import re

        text = tab.text or ""
        blocks = re.split(r'(\s{3,})', text)
        new_parts = []

        for i in range(0, len(blocks), 2):
            block = blocks[i] if i < len(blocks) else ""
            sep      = blocks[i+1] if i+1 < len(blocks) else ""

            if not block.strip():
                new_parts.append(block)
                if sep:
                    new_parts.append(sep)
                continue

            glyphs = []
            for char in block:
                if char == '/':
                    continue
                g = font.glyphForCharacter_(ord(char))
                if g:
                    glyphs.append(g.name)

            has_kerning = False
            for j in range(len(glyphs) - 1):
                left_name  = glyphs[j]
                right_name = glyphs[j + 1]
                if self.has_kerning(font, master_id, left_name, right_name):
                    has_kerning = True
                    break

            if has_kerning:
                continue

            new_parts.append(block)
            if sep:
                new_parts.append(sep)

        return "".join(new_parts).strip()

    def _resolve_name_to_glyph(self, font, name):
        if not name:
            return None

        if name in font.glyphs:
            return font.glyphs[name]

        if len(name) == 1:
            uni = ord(name)
            for g in font.glyphs:
                if g.unicode and int(g.unicode, 16) == uni:
                    return g

        return None

    def _reorganizeTo4Columns(self, text):
        if not text:
            return text
    
        lines = [line.rstrip() for line in text.split('\n') if line.strip()]
    
        if not lines:
            return text
    
        header_lines = []
        content_lines = []
    
        for line in lines:
            if (line.startswith("Category") or 
                line.startswith("BASE") or 
                line.startswith("Position") or
                line.startswith("Hide existing") or
                line.startswith("Exclude") or
                line.startswith("###") or
                "Kern Coach" in line or
                line.startswith("/N/O/") or
                line.startswith("/A/l/l/") or
                line.startswith("/A/l/r/e/a/d/y/")):
                header_lines.append(line)
            else:
                content_lines.append(line)
    
        all_tokens = []
    
        for line in content_lines:
            import re
            tokens = re.split(r'\s{3,}', line)
            tokens = [token.strip() for token in tokens if token.strip()]
            if tokens:
                all_tokens.extend(tokens)
    
        if not all_tokens:
            return text
    
        columns = 4
        reorganized_content = []
    
        for i in range(0, len(all_tokens), columns):
            chunk = all_tokens[i:i + columns]
            line = "     ".join(chunk)
            reorganized_content.append(line)
    
        final_lines = []
    
        if header_lines:
            final_lines.extend(header_lines)
            final_lines.append("")
    
        if reorganized_content:
            final_lines.extend(reorganized_content)
    
        return "\n".join(final_lines)



KernCoach()