@echo off
REM Simulacro de backup PostgreSQL: requiere DATABASE_URL y pg_dump en PATH.
REM Uso: copia .env.production a .env temporal o exporta DATABASE_URL antes de ejecutar.

cd /d "%~dp0.."

python scripts\pg_backup_restore.py backup

if errorlevel 1 exit /b 1
echo.
echo Listo. Revisa la carpeta backups\ para el archivo .dump generado.
