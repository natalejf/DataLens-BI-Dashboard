@echo off
title Dashboard Minimalista de Datos
color 0F

echo.
echo  =============================================
echo   Dashboard Minimalista de Datos
echo  =============================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python encontrado. Iniciando servidor en http://localhost:8888
    echo.
    echo Presiona Ctrl+C para detener el servidor
    echo.
    start "" "http://localhost:8888"
    python -m http.server 8888
    goto :end
)

echo Verificando Node.js / npx...
npx --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Node.js encontrado. Iniciando servidor con npx serve...
    echo.
    echo Presiona Ctrl+C para detener el servidor
    echo.
    npx serve . -l 8888
    goto :end
)

echo Verificando PHP...
php --version >nul 2>&1
if %errorlevel% equ 0 (
    echo PHP encontrado. Iniciando servidor en http://localhost:8888
    echo.
    echo Presiona Ctrl+C para detener el servidor
    echo.
    start "" "http://localhost:8888"
    php -S localhost:8888
    goto :end
)

echo.
echo ERROR: No se encontro Python, Node.js (npx) ni PHP.
echo Instala uno de ellos para ejecutar el servidor local.
echo.
echo Opciones:
echo   - Python: https://python.org
echo   - Node.js: https://nodejs.org
echo   - PHP: https://php.net
echo.
pause

:end