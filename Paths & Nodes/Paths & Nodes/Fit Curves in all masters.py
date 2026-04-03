# MenuTitle: Fit Curves in all masters
# -*- coding: utf-8 -*-
# Description: Interactive tool to adjust off‑curve smoothness in real time, preserving orthogonal relationships across all masters
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2

from vanilla import FloatingWindow, TextBox, Slider, CheckBox, HorizontalLine
import GlyphsApp
import math

class FitCurveLiveSync:
	def __init__(self):
		self.w = FloatingWindow((340, 160), "Fit Curve LIVE Sync (Fixed)")
		
		# --- SLIDER SMOOTH ---
		self.w.t1 = TextBox((10, 15, 80, 17), "Smooth %", sizeStyle='small')
		self.w.sliderAbs = Slider((100, 15, -55, 17), value=61, minValue=0, maxValue=100, callback=self.ui_callback)
		self.w.valAbs = TextBox((-50, 15, 45, 17), "61", sizeStyle='small')
		
		# --- SLIDER DELTA ---
		self.w.t2 = TextBox((10, 45, 80, 17), "Delta %", sizeStyle='small')
		self.w.sliderRel = Slider((100, 45, -55, 17), value=0, minValue=-50, maxValue=50, callback=self.ui_callback)
		self.w.valRel = TextBox((-50, 45, 45, 17), "0", sizeStyle='small')

		self.w.line = HorizontalLine((10, 80, -10, 1))

		# --- CHECKBOX SYNC ---
		self.w.syncAll = CheckBox((10, 95, -10, 20), "Sync all Masters (Safe Orthogonal)", value=True, sizeStyle='small')
		
		# MEMÒRIA D'ORTOGONALITAT
		# Estructura: {path_idx: {node_idx: {'axis': 'x' o 'y', 'owner_x': float, 'owner_y': float}}}
		self.orthogonal_memory = {}
		self.active_layer_id = None
		self.active_glyph_name = None
		
		# Umbral de tolerància ortogonal (margen de seguretat en unitats)
		self.orthogonal_tolerance = 2.0 
		
		self.w.open()

	def find_oncurve(self, path, idx, forward):
		n = len(path.nodes)
		step = 1 if forward else -1
		for j in range(1, 4):
			node = path.nodes[(idx + (j * step)) % n]
			if node.type != "offcurve": return node
		return None

	def store_orthogonal_references(self, layer, sync_active):
		"""
		Buscara els nodes seleccionats en la capa activa i guardara si s'han de moure en X o Y, 
		assegurant l'estabilitat en els altres masters.
		"""
		# Reset de memòria si canviem de capa o glif per seguretat
		if not sync_active:
			self.orthogonal_memory = {}
			return

		print("\nDEBUG: Actualitzant memòria d'ortogonalitat...")
		self.orthogonal_memory = {}

		# Guardem l'índex del camí i del node seleccionat
		for p_idx, path in enumerate(layer.paths):
			# Utilitzem una còpia per a la iteració estable
			for n_idx, node in enumerate(list(path.nodes)):
				if node.type == "offcurve" and node.selected:
					
					# Identificar owner (ancora) i target
					if path.nodes[n_idx-1].type != "offcurve":
						owner = path.nodes[n_idx-1]
						target_node = self.find_oncurve(path, n_idx, True)
					else:
						owner = path.nodes[(n_idx+1) % len(path.nodes)]
						target_node = self.find_oncurve(path, n_idx, False)
					
					if owner and target_node:
						
						# Validació ortogonal estricta en el master principal
						is_horizontal = abs(node.y - owner.y) < self.orthogonal_tolerance
						is_vertical = abs(node.x - owner.x) < self.orthogonal_tolerance
						
						if is_horizontal:
							self.orthogonal_memory[(p_idx, n_idx)] = 'x'
							print(f"  -> Path[{p_idx}] Node[{n_idx}] detectat com a HORITZONTAL")
						elif is_vertical:
							self.orthogonal_memory[(p_idx, n_idx)] = 'y'
							print(f"  -> Path[{p_idx}] Node[{n_idx}] detectat com a VERTICAL")

		print(f"DEBUG: Memòria actualitzada. {len(self.orthogonal_memory)} nodes ortogonals guardats.")

	def apply_logic_to_layer(self, layer, ratio):
		"""
		Aplica la lògica a una capa, respectant la memòria d'ortogonalitat.
		"""
		l_id = layer.layerId
		for (p_idx, n_idx), axis in self.orthogonal_memory.items():
			try:
				path = layer.paths[p_idx]
				node = path.nodes[n_idx]
				
				# Determinar owner (A) i target (B) en aquesta capa específica
				# (no podem reutilitzar l'owner de la capa activa, ja que les coordenades varien)
				if path.nodes[n_idx-1].type != "offcurve":
					owner = path.nodes[n_idx-1]
					target_node = self.find_oncurve(path, n_idx, True)
				else:
					owner = path.nodes[(n_idx+1) % len(path.nodes)]
					target_node = self.find_oncurve(path, n_idx, False)
				
				if owner and target_node:
					dx_seg = target_node.x - owner.x
					dy_seg = target_node.y - owner.y
					
					# Apliquem només sobre l'eix guardat en la memòria, 
					# ignorant la posició actual del handle.
					if axis == 'x': # Horitzontal
						node.x = owner.x + (dx_seg * ratio)
					elif axis == 'y': # Vertical
						node.y = owner.y + (dy_seg * ratio)
			except:
				pass

	def ui_callback(self, sender):
		font = Glyphs.font
		if not font: return
		
		# Actualitzar labels UI
		s_abs = int(self.w.sliderAbs.get())
		s_rel = int(self.w.sliderRel.get())
		self.w.valAbs.set(f"{s_abs}%")
		self.w.valRel.set(f"{s_rel}%")
		
		# Càlcul ràtio
		final_ratio = (s_abs / 100.0) * (1.0 + (s_rel / 100.0))
		
		font.disableUpdateInterface()
		
		sync_active = self.w.syncAll.get()
		
		for active_layer in font.selectedLayers:
			# Seguretat: Actualitzar memòria només quan és necessari (canvi de selecció o inici de moviment)
			# (En Glyphs, moure un slider sol enviar molts callbacks per segon, 
			#  però no hi ha un esdeveniment 'mousDown' de Vanilla, 
			#  per tant, mirem si hi ha una selecció vàlida i si la memòria ja existeix.)
			current_selection_valid = len([n for n in active_layer.selection if type(n) == GSNode and n.selected]) > 0
			
			if current_selection_valid and not self.orthogonal_memory:
				self.store_orthogonal_references(active_layer, sync_active)
			
			# Si la memòria encara està buida (cap node vàlid trobat), sortim
			if not self.orthogonal_memory:
				continue
				
			# 1. Aplicar a la capa actual (Live)
			self.apply_logic_to_layer(active_layer, final_ratio)
			
			# 2. Si el checkbox està actiu, aplicar a la resta
			if sync_active:
				glyph = active_layer.parent
				for layer in glyph.layers:
					# No tornem a processar la capa activa
					if layer.layerId == active_layer.layerId:
						continue
						
					if layer.isMasterLayer or layer.isSpecialLayer:
						self.apply_logic_to_layer(layer, final_ratio)
		
		font.enableUpdateInterface()
		Glyphs.redraw()
		
	def ui_callback_checkbox(self, sender):
		# Buidem la memòria quan es canvia el checkbox per forçar una actualització
		self.orthogonal_memory = {}

FitCurveLiveSync()