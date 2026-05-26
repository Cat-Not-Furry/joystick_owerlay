import threading
import time


def _normalize_stick(input_state):
	stick = input_state.get("stick", [0, 0]) if isinstance(input_state, dict) else [0, 0]
	if not isinstance(stick, list) or len(stick) != 2:
		return [0.0, 0.0]
	return [float(stick[0]), float(stick[1])]


def _normalize_buttons(input_state):
	buttons = input_state.get("buttons", []) if isinstance(input_state, dict) else []
	if not isinstance(buttons, list):
		return []
	return [bool(value) for value in buttons]


def _stick_to_direction(stick, threshold=0.3):
	x = stick[0]
	y = stick[1]
	h = ""
	v = ""
	if x <= -threshold:
		h = "left"
	elif x >= threshold:
		h = "right"
	if y <= -threshold:
		v = "up"
	elif y >= threshold:
		v = "down"
	if h and v:
		return f"{v}-{h}"
	if h:
		return h
	if v:
		return v
	return "neutral"


class InputHistory:
	"""Historial estructurado v1 con buffer circular en memoria."""

	def __init__(self, max_events=1000):
		self.schema_version = 1
		self.max_events = max(100, int(max_events))
		self.events = []
		self._last_direction = "neutral"
		self._last_buttons = []
		self._lock = threading.Lock()

	def _push_event(self, event):
		self.events.append(event)
		if len(self.events) > self.max_events:
			self.events = self.events[-self.max_events :]

	def record_snapshot(self, input_state, source="unknown", player_id="p1"):
		stick = _normalize_stick(input_state)
		buttons = _normalize_buttons(input_state)
		now = time.time()
		changes = []
		direction = _stick_to_direction(stick)

		with self._lock:
			if direction != self._last_direction:
				event = {
					"schema_version": self.schema_version,
					"time": now,
					"player_id": player_id,
					"source": source,
					"kind": "direction_change",
					"value": direction,
					"stick": stick,
				}
				self._push_event(event)
				changes.append(event)
				self._last_direction = direction

			if len(self._last_buttons) != len(buttons):
				self._last_buttons = [False] * len(buttons)

			for index, value in enumerate(buttons):
				if value == self._last_buttons[index]:
					continue
				event = {
					"schema_version": self.schema_version,
					"time": now,
					"player_id": player_id,
					"source": source,
					"kind": "button_change",
					"value": value,
					"button_index": index,
				}
				self._push_event(event)
				changes.append(event)
				self._last_buttons[index] = value
		return changes

	def append(self, event):
		if not isinstance(event, dict):
			return
		with self._lock:
			self._push_event(event)

	def to_dict(self):
		with self._lock:
			return {
				"schema_version": self.schema_version,
				"max_events": self.max_events,
				"events": list(self.events),
			}


_history = InputHistory()


def get_input_history():
	return _history
