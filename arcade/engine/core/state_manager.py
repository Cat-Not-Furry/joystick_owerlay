# state_manager.py - Estados explícitos y gestor (ventana única pygame)

# Señal de terminación del bucle principal
STOP = object()


class BootState:
	"""Arranque: cargar perfiles y ajustes iniciales."""


class MainMenuState:
	"""Menú principal (Iniciar / Configurar / Salir)."""


class ModalState:
	"""Diálogo modal en la misma ventana (p. ej. confirmar salida)."""


class ProfileConfigState:
	"""Configuración de perfiles (incluye subflujos como import/export)."""


class HudLayoutEditorState:
	"""
	Editor de posiciones HUD (render/hud_layout_editor.py).
	Se ejecuta como sub-bucle dentro de ProfileConfigState, no como estado raíz del gestor.
	"""


class HudSetupState:
	"""Selección de formato, modo de entrada y mapeo antes del HUD."""


class HudRunState:
	"""Bucle de dibujo y lectura de entradas del overlay."""


class StateManager:
	"""Mantiene la clase de estado actual (identidad del estado lógico)."""

	def __init__(self, initial_state):
		self.current = initial_state

	def set_state(self, state_cls):
		self.current = state_cls
