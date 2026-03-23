; AcademicAnchor Installer Script
; Target: Windows x64
; Author: U.Š
; Date: 2026
; ---------------------------------------------

[Setup]
; Basic info
AppName=AcademicAnchor
AppVersion=1.0
DefaultDirName={pf}\AcademicAnchor
DefaultGroupName=AcademicAnchor
UninstallDisplayIcon={app}\AcademicAnchor.exe
OutputBaseFilename=AcademicAnchor_Installer_x64
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

; Silent options (optional)
; SilentInstall=yes
; SilentUninstall=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Main executable
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

; Icon / assets
Source: "assets\ico.ico"; DestDir: "{app}"; Flags: ignoreversion

; Optional: database file (empty will be created on first run)
;Source: "academic_anchor.db"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AcademicAnchor"; Filename: "{app}\main.exe"
Name: "{commondesktop}\AcademicAnchor"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\main.exe"; Description: "Launch AcademicAnchor"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*.*"