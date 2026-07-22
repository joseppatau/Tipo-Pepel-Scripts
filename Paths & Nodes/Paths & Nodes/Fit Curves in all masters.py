# MenuTitle: Fit Curves in all masters
# -*- coding: utf-8 -*-

from vanilla import FloatingWindow, TextBox, Slider, CheckBox, HorizontalLine
import GlyphsApp
from GlyphsApp import GSNode
import math

class FitCurveLiveSync:
	def __init__(self):
		self.w = FloatingWindow((340, 160), "Fit Curve LIVE Sync (Fixed)")
		
		self.w.t1 = TextBox((10, 15, 80, 17), "Smooth %", sizeStyle='small')
		self.w.sliderAbs = Slider((100, 15, -55, 17), value=61, minValue=0, maxValue=100, callback=self.ui_callback)
		self.w.valAbs = TextBox((-50, 15, 45, 17), "61", sizeStyle='small')
		
		self.w.t2 = TextBox((10, 45, 80, 17), "Delta %", sizeStyle='small')
		self.w.sliderRel = Slider((100, 45, -55, 17), value=0, minValue=-50, maxValue=50, callback=self.ui_callback)
		self.w.valRel = TextBox((-50, 45, 45, 17), "0", sizeStyle='small')

		self.w.line = HorizontalLine((10, 80, -10, 1))

		self.w.syncAll = CheckBox((10, 95, -10, 20), "Sync all Masters (Safe Orthogonal)", value=True, sizeStyle='small')
		
		self.orthogonal_memory = {}
		self.orthogonal_tolerance = 2.0 
		
		self.w.open()

	# ---------------------------------------------------------

	def find_oncurve(self, path, idx, forward):
		n = len(path.nodes)
		step = 1 if forward else -1
		for j in range(1, 4):
			node = path.nodes[(idx + (j * step)) % n]
			if node.type != "offcurve":
				return node
		return None

	# ---------------------------------------------------------

	def store_orthogonal_references(self, layer, sync_active):

		if not sync_active:
			self.orthogonal_memory = {}
			return

		self.orthogonal_memory = {}

		for p_idx, path in enumerate(layer.paths):
			for n_idx, node in enumerate(list(path.nodes)):
				if node.type == "offcurve" and node.selected:
					
					if path.nodes[n_idx-1].type != "offcurve":
						owner = path.nodes[n_idx-1]
						target_node = self.find_oncurve(path, n_idx, True)
					else:
						owner = path.nodes[(n_idx+1) % len(path.nodes)]
						target_node = self.find_oncurve(path, n_idx, False)
					
					if owner and target_node:
						is_horizontal = abs(node.y - owner.y) < self.orthogonal_tolerance
						is_vertical = abs(node.x - owner.x) < self.orthogonal_tolerance
						
						if is_horizontal:
							self.orthogonal_memory[(p_idx, n_idx)] = 'x'
						elif is_vertical:
							self.orthogonal_memory[(p_idx, n_idx)] = 'y'

	# ---------------------------------------------------------

	def apply_logic_to_layer(self, layer, ratio):

		for (p_idx, n_idx), axis in self.orthogonal_memory.items():
			try:
				# ✅ FIX 1: validar índexs
				if p_idx >= len(layer.paths):
					continue

				path = layer.paths[p_idx]

				if n_idx >= len(path.nodes):
					continue

				node = path.nodes[n_idx]
				
				if path.nodes[n_idx-1].type != "offcurve":
					owner = path.nodes[n_idx-1]
					target_node = self.find_oncurve(path, n_idx, True)
				else:
					owner = path.nodes[(n_idx+1) % len(path.nodes)]
					target_node = self.find_oncurve(path, n_idx, False)
				
				if owner and target_node:
					dx_seg = target_node.x - owner.x
					dy_seg = target_node.y - owner.y
					
					if axis == 'x':
						node.x = owner.x + (dx_seg * ratio)
					elif axis == 'y':
						node.y = owner.y + (dy_seg * ratio)

			except Exception as e:
				print(f"Error en path[{p_idx}] node[{n_idx}]: {e}")

	# ---------------------------------------------------------

	def ui_callback(self, sender):
		font = Glyphs.font
		if not font:
			return
		
		s_abs = int(self.w.sliderAbs.get())
		s_rel = int(self.w.sliderRel.get())
		self.w.valAbs.set(f"{s_abs}%")
		self.w.valRel.set(f"{s_rel}%")
		
		final_ratio = (s_abs / 100.0) * (1.0 + (s_rel / 100.0))
		
		font.disableUpdateInterface()
		
		sync_active = self.w.syncAll.get()
		
		for active_layer in font.selectedLayers:

			current_selection_valid = len([
				n for n in active_layer.selection 
				if isinstance(n, GSNode) and n.selected
			]) > 0
			
			# ✅ FIX 2: recalcular sempre (evita errors)
			if current_selection_valid:
				self.store_orthogonal_references(active_layer, sync_active)
			
			if not self.orthogonal_memory:
				continue
				
			self.apply_logic_to_layer(active_layer, final_ratio)
			
			if sync_active:
				glyph = active_layer.parent
				for layer in glyph.layers:
					if layer.layerId == active_layer.layerId:
						continue
						
					if layer.isMasterLayer or layer.isSpecialLayer:
						self.apply_logic_to_layer(layer, final_ratio)
		
		font.enableUpdateInterface()
		Glyphs.redraw()


FitCurveLiveSync()