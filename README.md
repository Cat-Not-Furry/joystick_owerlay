# Joystick Owerlay (Windows)

Overlay arcade para joystick o teclado (Pygame), orientado a streamers y entrenamiento.

## Inicio rápido (desarrollo)

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

CLI:

```bat
python cli.py run
python cli.py config
python cli.py tournament
python cli.py doctor
python cli.py --version
```

## Estructura

```
arcade/
  assets/          # icon packs, binding_templates, fonts
  engine/          # config, core, profiles, render, maps, utils, training
configs/           # migraciones, esquemas, defaults
docs/              # usuario, desarrollador, seguridad
install/windows/   # setup_wizard, uninstall, install_ops
main.py, cli.py, configure.py, tournament.py, doctor.py
user/              # datos locales (desarrollo)
```

## Instalación usuario final

Ver [docs/user/installation.md](docs/user/installation.md) y [constructor.md](constructor.md) (build + `joystick-overlay-setup.exe`).

## Datos y paridad

- Contrato Windows: [docs/developer/data_contract_windows_v1.md](docs/developer/data_contract_windows_v1.md)
- Paridad con Linux: [docs/archive/bitacora.md](docs/archive/bitacora.md)
- Seguridad ZIP: [docs/security/security_model.md](docs/security/security_model.md)

## Licencia

GPL-3.0 — ver [LICENSE](LICENSE).
