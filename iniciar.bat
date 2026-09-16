@echo off
title DataLens BI - Streamlit Dashboard
color 0A

echo.
echo =============================================
echo   DataLens BI Dashboard (Streamlit + Plotly)
echo =============================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en el sistema.
    echo Por favor instala Python 3.9+ para ejecutar este dashboard.
    pause
    exit /b 1
)

echo Python encontrado. Verificando dependencias (Streamlit, Pandas, Plotly)...
python -c "import streamlit, pandas, plotly, openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando librerias necesarias des de requirements.txt...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Hubo un problema instalando los paquetes.
        pause
        exit /b 1
    )
)

echo.
echo Iniciando DataLens BI Dashboard en Streamlit...
echo Abrimiento el navegador en http://localhost:8501
echo.
echo Presiona Ctrl+C en esta ventana para detener el servidor.
echo.

start "" "http://localhost:8501"
python -m streamlit run app.py

:end