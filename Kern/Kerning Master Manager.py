# MenuTitle: Kerning Master Manager
# -*- coding: utf-8 -*-
# Description: Manage kerning per master: delete, backup, restore, and clean small-value pairs.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: Apache2
from vanilla import *
import json, os

def nameForID(font, ID):
	try:
		if ID[0] == "@":
			return ID
		else:
			return font.glyphForId_(ID).name
	except:
		return None

class KerningMasterUtilities:
	def __init__(self):
		self.w = Window((340, 420), "Kerning Master Utilities")

		self.w.titleLabel = TextBox((15, 15, -15, 20), "Select master:")
		self.w.masterPopup = PopUpButton((15, 40, -15, 20), self.getMasterNames())

		self.w.sep1 = HorizontalLine((15, 75, -15, 1))
		self.w.deleteButton = Button((15, 90, -15, 20), "🗑️ Delete kerning of selected master", callback=self.deleteKerning)
		self.w.backupCheck = CheckBox((15, 120, -15, 20), "Create JSON backup before deleting", value=True)
		self.w.restoreButton = Button((15, 150, -15, 20), "♻️ Restore kerning from JSON backup", callback=self.restoreCallback)

		self.w.sep2 = HorizontalLine((15, 185, -15, 1))
		self.w.smallValLabel = TextBox((15, 200, -15, 20), "Delete small-value pairs in active master:")
		self.w.threshold = EditText((15, 225, 60, 22), "10")
		self.w.negativeOnly = CheckBox((90, 225, -15, 20), "Only negative", value=True)
		self.w.deleteSmallButton = Button((15, 255, -15, 20), "🧹 Delete small values", callback=self.deleteSmallKerning)

		self.w.closeButton = Button((15, 360, -15, 20), "Close", callback=lambda s: self.w.close())
		self.w.open()

	def getMasterNames(self):
		font = Glyphs.font
		if not font:
			return ["No font open"]
		return [f"{i+1}: {m.name}" for i, m in enumerate(font.masters)]

	def getSelectedMaster(self):
		font = Glyphs.font
		if not font:
			return None
		idx = self.w.masterPopup.get()
		return font.masters[idx]

	# ---------- DELETE ALL ----------
	def deleteKerning(self, sender):
		font = Glyphs.font
		if not font:
			Message("Error", "Please open a font first.", OKButton="OK")
			return

		master = self.getSelectedMaster()
		if not master:
			Message("Error", "No master selected.", OKButton="OK")
			return

		if self.w.backupCheck.get():
			self.backupKerning(master)

		count = 0
		kdict = font.kerning.get(master.id, {})
		for leftKey in list(kdict.keys()):
			count += len(kdict[leftKey])
			kdict[leftKey].clear()
		print(f"🗑️ Deleted {count} pairs in {master.name}")
		Message("Done", f"🗑️ Deleted {count} kerning pairs in '{master.name}'.", OKButton="OK")

	# ---------- BACKUP ----------
	def backupKerning(self, master):
		font = Glyphs.font
		if not font:
			return
		from GlyphsApp import GetSaveFile
		masterName = master.name.replace(" ", "_")
		filePath = GetSaveFile(message="Save JSON Backup As", ProposedFileName=f"{masterName}_kerning_backup.json")
		if not filePath:
			return
		try:
			with open(filePath, "w", encoding="utf-8") as f:
				json.dump(font.kerning.get(master.id, {}), f, indent=2)
			print(f"💾 Backup saved: {filePath}")
		except Exception as e:
			Message("Error", f"Could not save backup: {e}", OKButton="OK")

	# ---------- RESTORE ----------
	def restoreCallback(self, sender):
		from GlyphsApp import GetOpenFile
		filePath = GetOpenFile(message="Select kerning JSON backup")
		if not filePath:
			return
		self.restoreKerning(filePath)

	def restoreKerning(self, filePath):
		font = Glyphs.font
		if not font:
			Message("Error", "Open a font first.", OKButton="OK")
			return
		master = self.getSelectedMaster()
		if not master:
			Message("Error", "No master selected.", OKButton="OK")
			return
		with open(filePath, "r", encoding="utf-8") as f:
			data = json.load(f)

		count = 0
		for left, rightDict in data.items():
			for right, value in rightDict.items():
				try:
					font.setKerningForPair(master.id, left, right, value)
					count += 1
				except Exception as e:
					print(f"❌ {left}-{right}: {e}")
		print(f"✅ Imported {count} pairs into {master.name}")
		Message("Done", f"✅ Imported {count} pairs into '{master.name}'.", OKButton="OK")

	# ---------- DELETE SMALL VALUES ----------
	def deleteSmallKerning(self, sender):
		font = Glyphs.font
		if not font:
			Message("Error", "Open a font first.", OKButton="OK")
			return
		master = font.selectedFontMaster
		masterID = master.id
		kernDict = font.kerning[masterID]
		try:
			threshold = abs(float(self.w.threshold.get()))
		except:
			Message("Error", "Threshold must be numeric.", OKButton="OK")
			return
		negativeOnly = self.w.negativeOnly.get()

		toDelete = []
		for leftID in kernDict.keys():
			for rightID in kernDict[leftID].keys():
				val = kernDict[leftID][rightID]
				if (negativeOnly and 0 > val > -threshold) or (not negativeOnly and abs(val) <= threshold):
					leftName = nameForID(font, leftID)
					rightName = nameForID(font, rightID)
					if leftName and rightName:
						toDelete.append((leftName, rightName))

		for left, right in toDelete:
			font.removeKerningForPair(masterID, left, right)

		print(f"🧹 Deleted {len(toDelete)} small-value pairs ≤ {threshold} in '{master.name}'.")
		Message("Done", f"🧹 Deleted {len(toDelete)} small-value pairs ≤ {threshold} in '{master.name}'.", OKButton="OK")


KerningMasterUtilities()
