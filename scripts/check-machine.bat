@echo off
rem caveman - Windows machine check (read-only).
rem
rem Checks whether this PC is ready for caveman and whether caveman is
rem already installed for Claude Code. Changes nothing on disk.
rem
rem Usage: double-click, or run  scripts\check-machine.bat  from cmd.
rem Exit code = number of required checks that failed (0 = ready).

setlocal EnableExtensions
set "FAIL=0"
set "WARN=0"

echo.
echo === caveman machine check ===
echo.

rem --- Windows ---------------------------------------------------------------
for /f "tokens=*" %%v in ('ver') do echo [INFO] %%v
echo [INFO] Arch: %PROCESSOR_ARCHITECTURE%
echo.
echo --- Required ---

rem --- Node.js >= 18 (installer needs it) -----------------------------------
where node >nul 2>&1
if errorlevel 1 (
  echo [FAIL] Node.js not found. Install: winget install OpenJS.NodeJS.LTS
  set /a FAIL+=1
  goto :after_node
)
set "NODE_VER="
set "NODE_MAJOR="
for /f "tokens=*" %%v in ('node -p "process.versions.node" 2^>nul') do set "NODE_VER=%%v"
for /f "tokens=1 delims=." %%m in ("%NODE_VER%") do set "NODE_MAJOR=%%m"
if not defined NODE_MAJOR (
  echo [FAIL] Node.js found but did not report a version.
  set /a FAIL+=1
  goto :after_node
)
if %NODE_MAJOR% LSS 18 (
  echo [FAIL] Node.js %NODE_VER% too old. Need 18 or newer: https://nodejs.org
  set /a FAIL+=1
) else (
  echo [ OK ] Node.js %NODE_VER%
)
:after_node

where npx >nul 2>&1
if errorlevel 1 (
  echo [FAIL] npx not found. Reinstall Node.js - npx ships with it.
  set /a FAIL+=1
) else (
  echo [ OK ] npx
)

echo.
echo --- Optional ---

where git >nul 2>&1
if errorlevel 1 (
  echo [WARN] git not found. Only needed to clone the repo. winget install Git.Git
  set /a WARN+=1
) else (
  for /f "tokens=3" %%v in ('git --version') do echo [ OK ] git %%v
)

rem Python 3.10+ is only needed for /caveman-compress.
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY (
  echo [WARN] Python not found. Needed only for /caveman-compress ^(3.10+^).
  set /a WARN+=1
  goto :after_py
)
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if errorlevel 1 (
  echo [WARN] Python older than 3.10 or broken. /caveman-compress needs 3.10+.
  set /a WARN+=1
) else (
  for /f "tokens=2" %%v in ('%PY% --version 2^>^&1') do echo [ OK ] Python %%v
)
:after_py

where pwsh >nul 2>&1
if errorlevel 1 (
  where powershell >nul 2>&1
  if errorlevel 1 (
    echo [WARN] PowerShell not found. Statusline badge uses it on Windows.
    set /a WARN+=1
  ) else (
    echo [ OK ] Windows PowerShell
  )
) else (
  echo [ OK ] PowerShell 7 ^(pwsh^)
)

echo.
echo --- AI agents found ---
set "AGENTS=0"
call :probe claude   "Claude Code"
call :probe codex    "Codex"
call :probe gemini   "Gemini CLI"
call :probe opencode "opencode"
call :probe cursor   "Cursor"
call :probe code     "VS Code"
if "%AGENTS%"=="0" echo [WARN] No known agent on PATH. caveman needs one to be useful.

rem --- Claude Code caveman install state -------------------------------------
echo.
echo --- caveman in Claude Code ---
if defined CLAUDE_CONFIG_DIR (
  set "CFG=%CLAUDE_CONFIG_DIR%"
) else (
  set "CFG=%USERPROFILE%\.claude"
)
echo [INFO] Config dir: %CFG%
if not exist "%CFG%\" (
  echo [INFO] Config dir missing - Claude Code never ran, or caveman not installed.
  goto :summary
)

set "HOOKS_OK=1"
for %%f in (caveman-config.js caveman-parse.js caveman-activate.js caveman-mode-tracker.js caveman-statusline.ps1) do (
  if not exist "%CFG%\hooks\%%f" set "HOOKS_OK=0"
)
if "%HOOKS_OK%"=="1" (
  echo [ OK ] Standalone hooks present in %CFG%\hooks
) else (
  echo [INFO] Standalone hooks not ^(fully^) present - fine if you use the plugin.
)

if exist "%CFG%\settings.json" (
  findstr /i /c:"caveman" "%CFG%\settings.json" >nul 2>&1
  if errorlevel 1 (
    echo [INFO] settings.json has no caveman entries.
  ) else (
    echo [ OK ] settings.json mentions caveman ^(hooks/statusline wired^)
  )
) else (
  echo [INFO] No settings.json yet.
)

if exist "%CFG%\plugins\" (
  dir /s /b /ad "%CFG%\plugins\*caveman*" >nul 2>&1
  if errorlevel 1 (
    echo [INFO] caveman plugin not found under %CFG%\plugins
  ) else (
    echo [ OK ] caveman plugin found under %CFG%\plugins
  )
)

if exist "%CFG%\.caveman-active" (
  set /p "MODE=" < "%CFG%\.caveman-active"
  call echo [INFO] Last active mode: %%MODE%%
)

:summary
echo.
echo === Result: %FAIL% failed, %WARN% warnings ===
if not "%FAIL%"=="0" (
  echo Fix the FAIL lines above, then run this again.
) else (
  echo Machine ready. Install: npx -y github:JuliusBrussee/caveman
)
echo.
rem Keep window open when double-clicked from Explorer.
echo %CMDCMDLINE% | findstr /i /c:"/c" >nul 2>&1 && pause
endlocal & exit /b %FAIL%

:probe
where %1 >nul 2>&1
if not errorlevel 1 (
  echo [ OK ] %~2
  set /a AGENTS+=1
)
exit /b 0
