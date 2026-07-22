# MenuTitle: Proportion Space & Tension (Angle Preservation)
# Josep Patau Bellart / ChatGPT refactor
# Multi-segment edition + handle angle preservation.

from GlyphsApp import Glyphs, GSNode, OFFCURVE
from vanilla import FloatingWindow, RadioGroup, EditText, TextBox, Button, Slider, CheckBox
import math


EPSILON = 0.0001
NEUTRAL_TENSION = 0.6


class ProportionSpace(object):
	def __init__(self):
		self.reset_cache()
		self.w = FloatingWindow((300, 290), "Proportion Space")

		y = 15
		self.w.title = TextBox((10, y, -10, 20), "Proportion space", alignment="center")

		y += 30
		self.w.kingLabel = TextBox((15, y, 50, 20), "King:")
		self.w.kingAxis = RadioGroup((70, y, 160, 20), ["width", "height"], isVertical=False)
		self.w.kingAxis.set(0)

		y += 35
		self.w.relationLabel = TextBox((15, y, 60, 20), "Relation")
		self.w.relationValue = EditText((85, y, 60, 22), "100")
		self.w.percentLabel = TextBox((150, y, 20, 20), "%")

		y += 40
		self.w.tensionLabel = TextBox((15, y, 65, 20), "Smooth")
		self.w.tensionSlider = Slider((85, y, -65, 20), value=60, minValue=0, maxValue=100, callback=self.ui_callback)
		self.w.tensionValue = TextBox((-55, y, 40, 20), "60")

		y += 45
		self.w.debugCheck = CheckBox((15, y, -15, 20), "Debug to Macro Window", value=False)

		y += 30
		self.w.applyBtn = Button((15, y, -15, 30), "Apply", callback=self.apply_logic)

		self.w.open()

	def ui_callback(self, sender):
		self.w.tensionValue.set(str(int(self.w.tensionSlider.get())))

	def reset_cache(self):
		self.cache = {
			"segment_data": [],
			"handle_vectors": {},
			"node_targets": {},
			"managed_handle_ids": set(),
		}

	def selected_oncurve_nodes(self, layer):
		return [n for n in layer.selection if isinstance(n, GSNode) and n.type != OFFCURVE]

	def next_oncurve(self, node):
		n = node.nextNode
		while n and n != node:
			if n.type != OFFCURVE:
				return n
			n = n.nextNode
		return None

	def nodes_between(self, start_node, end_node):
		nodes = []
		n = start_node.nextNode
		while n and n != end_node and n != start_node:
			nodes.append(n)
			n = n.nextNode
		return nodes

	def selected_segments(self, selected_nodes):
		selected_ids = set([id(n) for n in selected_nodes])
		segments = []
		seen = set()

		for start_node in selected_nodes:
			end_node = self.next_oncurve(start_node)
			if end_node and id(end_node) in selected_ids:
				key = (id(start_node.parent), start_node.index, end_node.index)
				if key not in seen:
					seen.add(key)
					segments.append((start_node, end_node))

		return segments

	def has_segment_handles(self, start_node, end_node):
		return bool(self.segment_handles(start_node, end_node))

	def debug_enabled(self):
		return bool(self.w.debugCheck.get())

	def debug(self, message):
		if self.debug_enabled():
			print("[ProportionSpace] %s" % message)

	def node_label(self, node):
		if not node:
			return "None"
		path_index = "?"
		try:
			path_index = node.parent.parent.paths.index(node.parent)
		except Exception:
			pass
		return "path %s node %s (%s, %.2f, %.2f)" % (
			path_index,
			node.index,
			node.type,
			node.x,
			node.y,
		)

	def segment_handles(self, start_node, end_node):
		between = [n for n in self.nodes_between(start_node, end_node) if n.type == OFFCURVE]
		handles = []

		if len(between) == 1:
			handles.append((between[0], start_node, end_node))
		elif len(between) >= 2:
			handles.append((between[0], start_node, end_node))
			handles.append((between[-1], end_node, start_node))

		return handles

	def adjacent_handles(self, node):
		handles = []
		if node.prevNode and node.prevNode.type == OFFCURVE:
			handles.append(node.prevNode)
		if node.nextNode and node.nextNode.type == OFFCURVE:
			handles.append(node.nextNode)
		return handles

	def endpoint_handle_for_segment(self, start_node, end_node, node):
		between = [n for n in self.nodes_between(start_node, end_node) if n.type == OFFCURVE]
		if not between:
			return None
		if node == start_node:
			return between[0]
		if node == end_node:
			return between[-1]
		return None

	def handle_score_for_segment(self, start_node, end_node, node, is_width_king):
		handle = self.endpoint_handle_for_segment(start_node, end_node, node)
		if not handle:
			return -1

		dx = handle.x - node.x
		dy = handle.y - node.y

		if is_width_king:
			return abs(dx) - abs(dy)
		return abs(dy) - abs(dx)

	def choose_king_and_subject(self, start_node, end_node, is_width_king):
		start_score = self.handle_score_for_segment(start_node, end_node, start_node, is_width_king)
		end_score = self.handle_score_for_segment(start_node, end_node, end_node, is_width_king)

		self.debug(
			"choose segment: %s -> %s | start_score=%.2f end_score=%.2f axis=%s"
			% (
				self.node_label(start_node),
				self.node_label(end_node),
				start_score,
				end_score,
				"width" if is_width_king else "height",
			)
		)

		if end_score > start_score:
			self.debug("  king=%s | subject=%s" % (self.node_label(end_node), self.node_label(start_node)))
			return end_node, start_node
		self.debug("  king=%s | subject=%s" % (self.node_label(start_node), self.node_label(end_node)))
		return start_node, end_node

	def node_key(self, node):
		return id(node)

	def snapshot_node_positions(self, nodes):
		return dict([(self.node_key(n), (n.x, n.y)) for n in nodes])

	def snapshot_handle_vectors(self, nodes):
		data = {}
		for node in nodes:
			for handle in self.adjacent_handles(node):
				data[self.node_key(handle)] = {
					"handle": handle,
					"owner": node,
					"dx": handle.x - node.x,
					"dy": handle.y - node.y,
					"length": math.hypot(handle.x - node.x, handle.y - node.y),
				}
		return data

	def move_subject_target(self, king, subject, ratio, is_width_king):
		if is_width_king:
			dx_total = abs(king.x - subject.x)
			target_dy = dx_total * ratio
			sign = 1 if subject.y >= king.y else -1
			return (subject.x, king.y + (target_dy * sign))

		dy_total = abs(king.y - subject.y)
		target_dx = dy_total * ratio
		sign = 1 if subject.x >= king.x else -1
		return (king.x + (target_dx * sign), subject.y)

	def apply_node_targets(self, node_targets):
		for node_id, target_data in node_targets.items():
			node = target_data["node"]
			points = target_data["points"]
			old_x, old_y = node.x, node.y
			node.x = sum([p[0] for p in points]) / float(len(points))
			node.y = sum([p[1] for p in points]) / float(len(points))
			self.debug(
				"move %s from (%.2f, %.2f) to (%.2f, %.2f) using %i target(s): %s"
				% (
					self.node_label(node),
					old_x,
					old_y,
					node.x,
					node.y,
					len(points),
					["(%.2f, %.2f)" % (p[0], p[1]) for p in points],
				)
			)

	def restore_unmanaged_handles(self, handle_vectors, managed_handle_ids):
		for handle_id, data in handle_vectors.items():
			if handle_id in managed_handle_ids:
				continue
			handle = data["handle"]
			owner = data["owner"]
			handle.x = owner.x + data["dx"]
			handle.y = owner.y + data["dy"]

	def tension_handle(self, handle, owner, opposite, original_dx, original_dy, smooth_val, is_width_king):
		if abs(smooth_val - NEUTRAL_TENSION) < EPSILON:
			handle.x = owner.x + original_dx
			handle.y = owner.y + original_dy
			return

		original_length = math.hypot(original_dx, original_dy)
		if original_length < EPSILON:
			handle.x = owner.x + original_dx
			handle.y = owner.y + original_dy
			return

		segment_length = math.hypot(opposite.x - owner.x, opposite.y - owner.y)
		target_length = segment_length * smooth_val
		scale = target_length / original_length
		handle.x = owner.x + (original_dx * scale)
		handle.y = owner.y + (original_dy * scale)

	def apply_logic(self, sender):
		self.reset_cache()
		font = Glyphs.font
		if not font or not font.selectedLayers:
			return

		layer = font.selectedLayers[0]
		selected_nodes = self.selected_oncurve_nodes(layer)
		segments = self.selected_segments(selected_nodes)

		self.debug("selected on-curve nodes: %i" % len(selected_nodes))
		for node in selected_nodes:
			self.debug("  selected %s" % self.node_label(node))
		self.debug("selected segments: %i" % len(segments))
		for start_node, end_node in segments:
			self.debug("  segment %s -> %s" % (self.node_label(start_node), self.node_label(end_node)))

		if not segments:
			return

		try:
			ratio = float(self.w.relationValue.get()) / 100.0
			smooth_val = self.w.tensionSlider.get() / 100.0
		except Exception:
			return

		is_width_king = self.w.kingAxis.get() == 0
		all_segment_nodes = []

		for start_node, end_node in segments:
			if not self.has_segment_handles(start_node, end_node):
				self.debug(
					"skip line/no-handle segment: %s -> %s"
					% (self.node_label(start_node), self.node_label(end_node))
				)
				continue
			king, subject = self.choose_king_and_subject(start_node, end_node, is_width_king)
			handles = self.segment_handles(start_node, end_node)
			self.cache["segment_data"].append({
				"start": start_node,
				"end": end_node,
				"king": king,
				"subject": subject,
				"handles": handles,
			})
			all_segment_nodes.extend([start_node, end_node])

		self.cache["handle_vectors"] = self.snapshot_handle_vectors(all_segment_nodes)

		font.disableUpdateInterface()
		try:
			for data in self.cache["segment_data"]:
				king = data["king"]
				subject = data["subject"]
				target = self.move_subject_target(king, subject, ratio, is_width_king)
				self.debug(
					"target from king %s to subject %s ratio=%.4f target=(%.2f, %.2f)"
					% (self.node_label(king), self.node_label(subject), ratio, target[0], target[1])
				)
				subject_id = self.node_key(subject)
				if subject_id not in self.cache["node_targets"]:
					self.cache["node_targets"][subject_id] = {"node": subject, "points": []}
				self.cache["node_targets"][subject_id]["points"].append(target)

			self.apply_node_targets(self.cache["node_targets"])

			for data in self.cache["segment_data"]:
				for handle, owner, opposite in data["handles"]:
					handle_id = self.node_key(handle)
					self.cache["managed_handle_ids"].add(handle_id)
					vector = self.cache["handle_vectors"].get(handle_id)
					if not vector:
						continue
					self.tension_handle(
						handle,
						owner,
						opposite,
						vector["dx"],
						vector["dy"],
						smooth_val,
						is_width_king
					)

			self.restore_unmanaged_handles(self.cache["handle_vectors"], self.cache["managed_handle_ids"])
		finally:
			font.enableUpdateInterface()
			self.reset_cache()

		Glyphs.redraw()


ProportionSpace()
