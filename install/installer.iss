; LEGACY — sustituido por install/windows/setup_wizard.py + joystick-overlay-setup.exe
; Mantener solo como referencia histórica hasta cierre de validación VM.
; HUD Owerlay installer (Windows)

#define MyAppName "HUD Owerlay"
#define MyAppVersion "1.0.0"
#define MyAppExeName "hud_owerlay.exe"
#define MyAppPublisher "HUD Owerlay"
#define MyAppId "{{A1B2C3D4-E5F6-47AA-8899-001122334455}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={pf}\hud_owerlay
DefaultGroupName={#MyAppName}
OutputBaseFilename=hud_owerlay_installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
DisableDirPage=no
DisableProgramGroupPage=no
SetupIconFile=install\hud_overlay.ico

[Files]
Source: "dist\hud_owerlay\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Dirs]
Name: "{userappdata}\hud_owerlay"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "install\hud_overlay.ico"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "install\hud_overlay.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
	userChoice: Integer;
	roamingPath: String;
begin
	if CurUninstallStep = usUninstall then
	begin
		roamingPath := ExpandConstant('{userappdata}\hud_owerlay');
		userChoice := MsgBox(
			'Deseas eliminar tambien los datos de usuario?'#13#10#13#10 +
			'Esto eliminara perfiles, configuracion y logs.'#13#10#13#10 +
			'Esta accion NO se puede deshacer.',
			mbConfirmation, MB_YESNO);

		if userChoice = IDYES then
		begin
			if DirExists(roamingPath) then
				DelTree(roamingPath, True, True, True);
		end;
	end;
end;
