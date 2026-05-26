import threading
import time


class ExtensionsRuntime:
	"""Registro mínimo de hooks para extensiones en modo standby."""

	def __init__(self):
		self._hooks = {}
		self._enabled = True
		self._lock = threading.Lock()

	def set_enabled(self, enabled):
		self._enabled = bool(enabled)

	def is_enabled(self):
		return self._enabled

	def clear_hooks(self):
		with self._lock:
			self._hooks = {}

	def register_hook(self, event_name, hook_fn):
		if not isinstance(event_name, str) or not event_name:
			return False
		if not callable(hook_fn):
			return False
		with self._lock:
			if event_name not in self._hooks:
				self._hooks[event_name] = []
			self._hooks[event_name].append(hook_fn)
		return True

	def emit_hook(self, event_name, payload=None):
		if not self._enabled:
			return 0
		with self._lock:
			hooks = list(self._hooks.get(event_name, []))
		if not hooks:
			return 0
		data = {
			"timestamp": time.time(),
			"event_name": event_name,
			"payload": payload if isinstance(payload, dict) else {},
		}
		executed = 0
		for hook_fn in hooks:
			try:
				hook_fn(data)
				executed += 1
			except Exception as error:
				print(f"[WARN] Hook '{event_name}' falló: {error}")
		return executed


_runtime = ExtensionsRuntime()


def set_extensions_enabled(enabled):
	_runtime.set_enabled(enabled)


def is_extensions_enabled():
	return _runtime.is_enabled()


def clear_hooks():
	_runtime.clear_hooks()


def register_hook(event_name, hook_fn):
	return _runtime.register_hook(event_name, hook_fn)


def emit_hook(event_name, payload=None):
	return _runtime.emit_hook(event_name, payload)


class _ExtensionsFacade:
	def emit(self, event_name, payload=None):
		return emit_hook(event_name, payload)

	def register_hook(self, event_name, hook_fn):
		return register_hook(event_name, hook_fn)


_facade = _ExtensionsFacade()


def get_extensions_runtime():
	return _facade
