@echo off
setlocal
title GhostPet Windows Beta - Install
echo.
echo     GhostPet - Windows Tester Installer
echo     ===================================
echo.
set "TARGET=%LOCALAPPDATA%\GhostPet"
if not exist "%~dp0GhostPet.exe" (
  echo ERROR: Extract the entire tester ZIP before running Install-Windows.cmd.
  pause
  exit /b 1
)
if not exist "%~dp0GhostPetUpdater.exe" (
  echo ERROR: GhostPetUpdater.exe is missing. Extract the entire ZIP.
  pause
  exit /b 1
)
if not exist "%TARGET%" mkdir "%TARGET%"
if errorlevel 1 goto :failed
copy /Y "%~dp0GhostPet.exe" "%TARGET%\GhostPet.exe" >nul
if errorlevel 1 goto :failed
copy /Y "%~dp0GhostPetUpdater.exe" "%TARGET%\GhostPetUpdater.exe" >nul
if errorlevel 1 goto :failed
copy /Y "%~dp0VERSION" "%TARGET%\VERSION" >nul
if errorlevel 1 goto :failed
if exist "%~dp0README-Windows.txt" copy /Y "%~dp0README-Windows.txt" "%TARGET%\README-Windows.txt" >nul
echo Creating Desktop and Start Menu shortcuts...
powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; $w=New-Object -ComObject WScript.Shell; $p=Join-Path $env:LOCALAPPDATA 'GhostPet'; $desktop=[Environment]::GetFolderPath('Desktop'); $menu=Join-Path ([Environment]::GetFolderPath('Programs')) 'GhostPet.lnk'; foreach($shortcutPath in @((Join-Path $desktop 'GhostPet.lnk'),$menu)) { $sc=$w.CreateShortcut($shortcutPath); $sc.TargetPath=Join-Path $p 'GhostPet.exe'; $sc.WorkingDirectory=$p; $sc.Description='Your tiny desktop companions'; $sc.Save() }"
if errorlevel 1 echo Shortcuts could not be created; you can still launch from "%TARGET%".
echo.
echo Installed for this Windows account.
echo Save data will be stored at "%LOCALAPPDATA%\GhostPet\state.json".
echo This is an unsigned tester build and Windows SmartScreen may warn.
echo.
start "" "%TARGET%\GhostPet.exe"
exit /b 0
:failed
echo.
echo Install could not copy the files. Close any running GhostPet windows,
echo then try again. No pet saves have been deleted.
pause
exit /b 1
