# Fuentes externas verificables (índice)

Este fichero agrupa enlaces a **especificaciones, documentación oficial del stack y materiales de seguridad contrastables** usados en las guías de Joystick Overlay. Sirve como índice único; cada guía enlaza aquí y, cuando aplica, repite 1–2 enlaces directos al tema.

**Política de citas (resumen):** priorizar estándares (freedesktop, kernel.org), OWASP/ASVS como marco de lectura (no certificación del producto), documentación upstream (Pygame, SDL, python-evdev, OBS KB), SPDX y texto legal GNU para licencias. Evitar blogs y tutoriales de terceros como fuente primaria.

| Tema | Enlace | Uso en el repo |
| ---- | ------- | -------------- |
| XDG Base Directory | [basedir-spec (freedesktop.org)](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) | Contexto de rutas bajo `~/.local/share` en el contrato de datos |
| Linux input / evdev | [Input subsystem (kernel.org)](https://www.kernel.org/doc/html/latest/input/input.html) | Dispositivos `/dev/input`, eventos |
| python-evdev | [Documentación estable](https://python-evdev.readthedocs.io/en/stable/) | Bindings Python al subsistema de entrada |
| SDL2 / ventana | [SDL2 CategoryVideo (wiki)](https://wiki.libsdl.org/SDL2/CategoryVideo) | Contexto de ventana y subsistema de video (Pygame usa SDL) |
| Pygame | [Documentación](https://www.pygame.org/docs/) | API de alto nivel sobre SDL |
| Path traversal | [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal) | Relación conceptual con rutas maliciosas en archivos |
| ASVS (archivos) | [OWASP ASVS V5 File Handling](https://github.com/OWASP/ASVS/blob/master/5.0/en/0x12-V5-File-Handling.md) | Marco de verificación de aplicaciones (lectura) |
| Zip Slip (divulgación) | [Snyk: Zip Slip vulnerability](https://security.snyk.io/research/zip-slip-vulnerability) | Descripción técnica del patrón en archivos ZIP |
| GNU GPL-3.0 | [Texto de la licencia](https://www.gnu.org/licenses/gpl-3.0.html) | Licencia del proyecto |
| SPDX GPL-3.0-only | [Identificador SPDX](https://spdx.org/licenses/GPL-3.0-only) | Identificador de lista SPDX |
| OBS: ventana | [Window Capture Sources](https://obsproject.com/kb/window-capture-sources) | Captura de ventana en Linux (Xcomposite / PipeWire) |
| OBS: filtros | [Filters Guide](https://obsproject.com/kb/filters-guide) | Filtros de efecto (incl. croma / chroma key en la categoría descrita) |
| OBS: fuentes | [Sources Guide](https://obsproject.com/kb/sources-guide) | Visión general de fuentes y escenas |

Volver al [índice de documentación](../README.md).
