@echo off
setlocal EnableDelayedExpansion

:: Setze die Konsolenfarbe auf grünen Text auf schwarzem Hintergrund
color 0A

:: Ueberpruefen auf Administratorrechte
:-------------------------------------
REM  --> Ueberpruefen der Berechtigungen
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> Wenn Fehlerflag gesetzt ist, haben wir keine Adminrechte.
if '%errorlevel%' NEQ '0' (
    echo Fordere administrative Berechtigungen an...
    goto UACPrompt
) else ( goto GotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:GotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------

echo =========================================================
echo            Batch-Skript zur Installation
echo =========================================================
echo.

:: Schritt 1: Anzeige des aktuellen Verzeichnisses
echo ---------------------------------------------------------
echo [Schritt 1] Arbeitsverzeichnis: %CD%
echo ---------------------------------------------------------
echo.

:: Schritt 2: Ueberpruefen auf MSSTDFMT.DLL
echo ---------------------------------------------------------
echo [Schritt 2] Ueberpruefe auf MSSTDFMT.DLL...
echo ---------------------------------------------------------
if exist "MSSTDFMT.DLL" (
    echo MSSTDFMT.DLL im aktuellen Verzeichnis gefunden.
    echo Registriere MSSTDFMT.DLL...
    regsvr32.exe /s MSSTDFMT.DLL
    if !errorlevel!==0 (
        echo MSSTDFMT.DLL erfolgreich registriert.
    ) else (
        echo Registrierung von MSSTDFMT.DLL fehlgeschlagen.
        echo Fehlercode: !errorlevel!
    )
) else (
    echo MSSTDFMT.DLL im aktuellen Verzeichnis nicht gefunden.
)
echo.

:: Schritt 3: Erstelle Verzeichnis C:\KIGA, falls noch nicht vorhanden
echo ---------------------------------------------------------
echo [Schritt 3] Erstelle Verzeichnis C:\KIGA...
echo ---------------------------------------------------------
if not exist "C:\KIGA" (
    mkdir "C:\KIGA"
    if !errorlevel!==0 (
        echo Verzeichnis C:\KIGA erfolgreich erstellt.
    ) else (
        echo Erstellung von C:\KIGA fehlgeschlagen.
        echo Fehlercode: !errorlevel!
    )
) else (
    echo Verzeichnis C:\KIGA ist bereits vorhanden.
)
echo.

:: Schritt 4: Ueberpruefen auf Kasse.ini
echo ---------------------------------------------------------
echo [Schritt 4] Kopiere Kasse.ini nach C:\KIGA...
echo ---------------------------------------------------------
if exist "Kasse.ini" (
    echo Kasse.ini im aktuellen Verzeichnis gefunden.
    copy /Y "Kasse.ini" "C:\KIGA\Kasse.ini"
    if !errorlevel!==0 (
        echo Kasse.ini erfolgreich nach C:\KIGA kopiert.
    ) else (
        echo Kopieren von Kasse.ini nach C:\KIGA fehlgeschlagen.
        echo Fehlercode: !errorlevel!
    )
) else (
    echo Kasse.ini im aktuellen Verzeichnis nicht gefunden.
)
echo.

:: Schritt 5: Ueberpruefen auf Flohmarkt.exe
echo ---------------------------------------------------------
echo [Schritt 5] Kopiere Flohmarkt.exe nach C:\KIGA...
echo ---------------------------------------------------------
if exist "Flohmarkt.exe" (
    echo Flohmarkt.exe im aktuellen Verzeichnis gefunden.
    copy /Y "Flohmarkt.exe" "C:\KIGA\Flohmarkt.exe"
    if !errorlevel!==0 (
        echo Flohmarkt.exe erfolgreich nach C:\KIGA kopiert.
    ) else (
        echo Kopieren von Flohmarkt.exe nach C:\KIGA fehlgeschlagen.
        echo Fehlercode: !errorlevel!
    )
    echo.

    :: Schritt 6: Erstelle Verknuepfung auf dem Desktop
    echo ---------------------------------------------------------
    echo [Schritt 6] Erstelle Verknuepfung auf dem Desktop...
    echo ---------------------------------------------------------
    set "shortcut=!temp!\CreateShortcut.vbs"
    >"!shortcut!" echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    >>"!shortcut!" echo sLinkFile = oWS.SpecialFolders^("Desktop"^) ^& "\Flohmarkt.lnk"
    >>"!shortcut!" echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    >>"!shortcut!" echo oLink.TargetPath = "C:\KIGA\Flohmarkt.exe"
    >>"!shortcut!" echo oLink.WorkingDirectory = "C:\KIGA"
    >>"!shortcut!" echo oLink.WindowStyle = 1
    >>"!shortcut!" echo oLink.IconLocation = "C:\KIGA\Flohmarkt.exe, 0"
    >>"!shortcut!" echo oLink.Description = "Flohmarkt Anwendung"
    >>"!shortcut!" echo oLink.Save
    cscript /nologo "!shortcut!"
    del "!shortcut!"
    echo Verknuepfung auf dem Desktop erstellt.
    echo.

    :: Schritt 7: Erstelle Eintrag im Startmenue
    echo ---------------------------------------------------------
    echo [Schritt 7] Erstelle Eintrag im Startmenue...
    echo ---------------------------------------------------------
    set "StartMenuPath=!APPDATA!\Microsoft\Windows\Start Menu\Programs"
    if exist "!StartMenuPath!" (
        copy /Y "%USERPROFILE%\Desktop\Flohmarkt.lnk" "!StartMenuPath!\Flohmarkt.lnk"
        if !errorlevel!==0 (
            echo Eintrag im Startmenue erfolgreich erstellt.
        ) else (
            echo Erstellen des Eintrags im Startmenue fehlgeschlagen.
            echo Fehlercode: !errorlevel!
        )
    ) else (
        echo Startmenue-Pfad nicht gefunden.
    )
) else (
    echo Flohmarkt.exe im aktuellen Verzeichnis nicht gefunden.
)
echo.

echo =========================================================
echo            Skriptausfuehrung abgeschlossen.
echo =========================================================
pause
