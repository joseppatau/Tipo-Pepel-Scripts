# MenuTitle: Decompose Components in All Masters
# -*- coding: utf-8 -*-
# Description: Descompon els components seleccionats a tots els mestres del glif actual.
# Author: Gemini & Josep Patau

from GlyphsApp import *
from vanilla import *

class DecomposeInAllMasters(object):
	def __init__(self):
		# Paràmetres de la finestra
		self.w = FloatingWindow((250, 100), "Descompon Global")
		
		self.w.info = TextBox((15, 12, -15, 30), "Descompon els components seleccionats a TOTS els mestres.", sizeStyle='small')
		
		self.w.runButton = Button((15, 45, -15, 20), "Descompondre Selecció", callback=self.decomposeAction)
		
		self.w.open()

	def decomposeAction(self, sender):
		font = Glyphs.font
		if font is None:
			return

		# Obtenir la capa activa i el glif
		currentLayer = font.selectedLayers[0]
		currentGlyph = currentLayer.parent
		
		# Identificar quins components estan seleccionats actualment
		selectedComponentNames = []
		for selection in currentLayer.selection:
			if isinstance(selection, GSComponent):
				selectedComponentNames.append(selection.name)
		
		if not selectedComponentNames:
			print("Avís: No hi ha cap component seleccionat.")
			return

		# Obrim un grup per poder fer "Undo" d'un sol cop
		font.disableUpdateInterface()
		try:
			# Iterar per cada mestre (capa) del glif
			for layer in currentGlyph.layers:
				# Només processem capes que siguin de mestres (no talls o backups)
				if layer.isMasterLayer or layer.isSpecialLayer:
					
					# Recorrem els components de la capa de darrere cap endavant per seguretat al eliminar/descompondre
					for i in range(len(layer.components)-1, -1, -1):
						component = layer.components[i]
						
						# Si el component coincideix amb un dels seleccionats a la capa activa
						if component.name in selectedComponentNames:
							layer.decomposeComponent_(component)
							
			print(f"S'han descompost: {', '.join(selectedComponentNames)} a tots els mestres de /{currentGlyph.name}")
		
		except Exception as e:
			print(f"Error: {e}")
		
		finally:
			font.enableUpdateInterface()

# Executar l'script
DecomposeInAllMasters()