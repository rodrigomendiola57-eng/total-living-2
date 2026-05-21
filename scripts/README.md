# Scripts de mantenimiento

Aquí están los utilitarios que antes estaban en la raíz del proyecto (`fix_*.py`, `verificar_*.py`, poblar datos, etc.).

**Importante:** ejecútalos **desde la raíz del repositorio** (`C:\TOTAL LIVING` o la ruta equivalente en Linux/macOS), para que las rutas relativas (por ejemplo `.env`, `db.sqlite3`) y los imports de Django sigan funcionando:

```bash
cd /ruta/al/proyecto
python scripts/setup_env.py
python scripts/verificar_db.py
```

El archivo `manage.py` **permanece en la raíz**; no lo muevas.
