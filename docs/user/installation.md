# Instalación (Windows)

## Requisitos

- Windows 10 o superior (64 bits recomendado)
- Python 3.9+ solo para **desarrollo**; el usuario final usa el instalador empaquetado

## Usuario final (recomendado)

1. Ejecute **`joystick-overlay-setup.exe`** como administrador si elige modo *Instalado*.
2. Elija:
   - **Instalado:** programa en `C:\Program Files\Joystick Owerlay\`, datos en `%LOCALAPPDATA%\joystick_owerlay\user\`
   - **Portable:** carpeta libre con `user\` junto al ejecutable
3. Si detecta una instalación **`hud_owerlay`** anterior, puede importar perfiles (opcional).
4. Tras instalar: accesos en el menú Inicio — **Joystick Owerlay**, **Configuración**, **Torneo**.

### ZIP portable (USB / torneo)

Descomprima el ZIP y ejecute `joystick-overlay.exe`. Para accesos directos sin reinstalar, ejecute **`setup.exe --register-only`** en esa carpeta.

### Desinstalar

Ejecute **`joystick-overlay-uninstall.exe`** en la carpeta de instalación (se copia durante la instalación).

## Desarrollo

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

CLI unificada:

```bat
python cli.py run
python cli.py config
python cli.py tournament
python cli.py doctor
python cli.py --version
```

## Actualización

Desde **Configurar perfiles → Actualizar overlay** (ZIP de release), o:

```bat
python cli.py --update --zip ruta\release.zip
```

No se sobrescribe `user/`. Log: `user\update.log`.

## Inno Setup (legado)

El archivo `install\installer.iss` está **obsoleto**; usar el instalador Python documentado en [constructor.md](../../constructor.md).
