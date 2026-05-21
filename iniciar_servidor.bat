@echo off
setlocal
REM Arranque local estandar (sin Docker) con preflight
echo ========================================
echo   TOTAL LIVING - ARRANQUE LOCAL
echo ========================================
echo.

cd /d "C:\TOTAL LIVING"

if not exist "manage.py" (
    echo [ERROR] No se encontro manage.py en C:\TOTAL LIVING
    exit /b 1
)

echo [1/2] Ejecutando preflight...
python "scripts\preflight_no_docker.py"
if errorlevel 1 (
    echo.
    echo [ERROR] Preflight fallo. Corrige lo reportado y vuelve a intentar.
    exit /b 1
)

echo.
echo [2/2] Iniciando servidor en http://127.0.0.1:8090
echo Presiona Ctrl+C para detener.
python manage.py runserver 8090

endlocal
