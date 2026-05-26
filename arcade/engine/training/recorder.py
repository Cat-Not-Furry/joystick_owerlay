# training/recorder.py
# Lógica de grabación y reproducción de secuencias de inputs para modo entrenamiento.
# Grabación por eventos: solo se guardan cambios de estado, respetando delays exactos.

import time
import copy

TRAINING_MAX_SNAPSHOTS = 30
TRAINING_MAX_SECONDS = 30.0
TRAINING_SAMPLE_INTERVAL = 0.1
TRAINING_MAX_EVENTOS = 500
TRAINING_STICK_TOLERANCE = 0.01


def create_training_state():
	return {
		"status": "idle",
		"sequence": [],
		"record_start_time": None,
		"last_sample_time": None,
		"ultimo_estado": None,
		"playback_index": 0,
		"playback_start_time": None,
	}


def _snapshot_from_input_state(input_state):
	stick = list(input_state.get("stick", [0, 0]))
	buttons = [1 if b else 0 for b in input_state.get("buttons", [])]
	return {"stick": stick, "buttons": buttons}


def _estado_igual(a, b):
	if a is None or b is None:
		return a == b
	sa, sb = a.get("stick", [0, 0]), b.get("stick", [0, 0])
	tol = TRAINING_STICK_TOLERANCE
	if abs(sa[0] - sb[0]) > tol or abs(sa[1] - sb[1]) > tol:
		return False
	ba, bb = a.get("buttons", []), b.get("buttons", [])
	if len(ba) != len(bb):
		return False
	return all(x == y for x, y in zip(ba, bb))


def start_recording(state):
	if state["status"] != "idle":
		return False
	state["status"] = "recording"
	state["sequence"] = []
	state["record_start_time"] = time.monotonic()
	state["last_sample_time"] = state["record_start_time"]
	state["ultimo_estado"] = None
	print("[INFO] Grabando: iniciada.")
	return True


def stop_recording(state):
	if state["status"] != "recording":
		return False
	n = len(state["sequence"])
	state["status"] = "idle"
	print(f"[INFO] Grabando: detenida ({n} eventos).")
	return True


def clear_sequence(state):
	had = len(state.get("sequence", []))
	state["sequence"] = []
	if state["status"] == "recording":
		state["status"] = "idle"
		state["record_start_time"] = None
		state["last_sample_time"] = None
		state["ultimo_estado"] = None
	if state["status"] == "playing":
		state["status"] = "idle"
		state["playback_index"] = 0
		state["playback_start_time"] = None
	if had > 0:
		print("[INFO] Secuencia: borrada.")
	return True


def snapshot_if_recording(state, input_state):
	if state["status"] != "recording":
		return
	now = time.monotonic()
	elapsed = now - state["record_start_time"]
	if elapsed >= TRAINING_MAX_SECONDS:
		state["status"] = "idle"
		return
	if len(state["sequence"]) >= TRAINING_MAX_EVENTOS:
		state["status"] = "idle"
		return
	estado_actual = _snapshot_from_input_state(input_state)
	if len(state["sequence"]) == 0:
		estado_actual["t"] = 0.0
		state["sequence"].append(estado_actual)
		state["ultimo_estado"] = estado_actual
		return
	if _estado_igual(estado_actual, state["ultimo_estado"]):
		return
	estado_actual["t"] = elapsed
	state["sequence"].append(estado_actual)
	state["ultimo_estado"] = estado_actual


def has_sequence(state):
	return len(state.get("sequence", [])) > 0


def get_sequence_copy(state):
	return copy.deepcopy(state.get("sequence", []))


def start_playback(state):
	if not has_sequence(state):
		return False
	state["status"] = "playing"
	state["playback_index"] = 0
	state["playback_start_time"] = time.monotonic()
	n = len(state["sequence"])
	print(f"[INFO] Reproduciendo: iniciada ({n} eventos).")
	return True


def update_playback(state, input_state):
	"""Actualiza input_state con el frame actual de la reproducción. Retorna True si sigue reproduciendo."""
	if state["status"] != "playing":
		return False
	seq = state["sequence"]
	if not seq:
		state["status"] = "idle"
		return False
	now = time.monotonic()
	elapsed = now - state["playback_start_time"]
	last_applied = -1
	for i in range(state["playback_index"], len(seq)):
		if seq[i]["t"] <= elapsed:
			snap = seq[i]
			input_state["stick"] = list(snap["stick"])
			input_state["buttons"] = [bool(b) for b in snap["buttons"]]
			last_applied = i
		else:
			break
	state["playback_index"] = last_applied + 1
	if state["playback_index"] >= len(seq):
		state["status"] = "idle"
		print("[INFO] Reproduciendo: finalizada.")
		return False
	return True


def sequence_to_dict(state):
	seq = get_sequence_copy(state)
	duracion = seq[-1]["t"] if seq else 0.0
	return {"sequence": seq, "duracion_total": duracion}


def dict_to_sequence(data):
	seq = data.get("sequence", data.get("eventos", []))
	if not isinstance(seq, list):
		return []
	result = []
	limite = max(TRAINING_MAX_SNAPSHOTS, TRAINING_MAX_EVENTOS)
	for item in seq[:limite]:
		if isinstance(item, dict) and "stick" in item and "buttons" in item:
			result.append({
				"t": item.get("t", 0.0),
				"stick": list(item["stick"]),
				"buttons": list(item["buttons"]),
			})
	return result
