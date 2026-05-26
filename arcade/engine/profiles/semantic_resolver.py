"""Resolución semántica opción B: BTN_* -> token para iconos/plugins."""


def resolve_semantic_for_physical(profile_dict, physical_id, default_label):
	"""
	Retorna token en MAYÚSCULAS para resolver iconos (p.ej. LP, A, X).
	Si no hay semantic_binding, usa la etiqueta de layout (modo legacy).
	"""
	if not isinstance(profile_dict, dict):
		return str(default_label or "").strip().upper()
	sb = profile_dict.get("semantic_binding")
	if not isinstance(sb, dict):
		return str(default_label or "").strip().upper()
	raw = sb.get(str(physical_id).strip())
	if isinstance(raw, str) and raw.strip():
		return raw.strip().upper()
	return str(default_label or "").strip().upper()
