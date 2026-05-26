@echo off
setlocal
echo Joystick Owerlay — build del instalador
echo.
echo 1) Construya primero dist\joystick-overlay\ con PyInstaller (ver constructor.md)
echo 2) Empaquete release.zip con arcade\, configs\, entrypoints y install\
echo 3) Ejecute:
echo    pyinstaller install\windows\setup_wizard.py --name joystick-overlay-setup --onefile --noconsole
echo    joystick-overlay-setup.exe --zip release.zip
echo.
echo Inno Setup (installer.iss) esta obsoleto.
endlocal
