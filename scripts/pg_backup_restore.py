#!/usr/bin/env python3
"""
Backup y restore físico de PostgreSQL con pg_dump / pg_restore (formato custom -Fc).

Requiere herramientas cliente en PATH: pg_dump, pg_restore (PostgreSQL.org).

  DATABASE_URL — URI postgresql://usuario:clave@host:5432/base

Ejemplos (PowerShell, desde la raíz del proyecto):

  $env:DATABASE_URL = "postgresql://user:pass@localhost:5432/total_living"
  python scripts/pg_backup_restore.py backup --output backups/simulacro.dump

  # Solo simulacro / staging: pg_restore puede eliminar objetos (--clean).
  python scripts/pg_backup_restore.py restore --input backups/simulacro.dump --confirm

Alternativa solo datos (sin pg_dump): ver ESTADO_Y_PLAN.md (dumpdata).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _require_pg_tool(name: str) -> None:
    if not shutil.which(name):
        sys.stderr.write(
            f"No se encontró '{name}' en PATH. Instala el cliente PostgreSQL "
            "o usa respaldo lógico con Django (dumpdata).\n"
        )
        sys.exit(2)


def _database_url() -> str:
    url = (os.environ.get('DATABASE_URL') or '').strip()
    if not url:
        sys.stderr.write('Define la variable de entorno DATABASE_URL.\n')
        sys.exit(2)
    return url


def cmd_backup(args: argparse.Namespace) -> None:
    _require_pg_tool('pg_dump')
    url = _database_url()
    if args.output:
        out = Path(args.output).resolve()
    else:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        out = Path('backups') / f'total_living_{stamp}.dump'
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['pg_dump', url, '-Fc', '-f', str(out)], check=True)
    print(f'Backup guardado en: {out}')


def cmd_restore(args: argparse.Namespace) -> None:
    if not args.confirm:
        sys.stderr.write(
            'Restore usa --clean / --if-exists y puede borrar objetos en la base '
            'apuntada por DATABASE_URL. Re-ejecuta con --confirm tras validar el entorno.\n'
        )
        sys.exit(3)
    _require_pg_tool('pg_restore')
    url = _database_url()
    inp = Path(args.input).resolve()
    if not inp.is_file():
        sys.stderr.write(f'No existe el archivo: {inp}\n')
        sys.exit(2)
    rc = subprocess.run(
        [
            'pg_restore',
            '--clean',
            '--if-exists',
            '--no-owner',
            '--dbname',
            url,
            str(inp),
        ]
    ).returncode
    if rc != 0:
        sys.stderr.write(
            f'pg_restore terminó con código {rc}. Revisa mensajes anteriores '
            '(orden de extensiones, permisos o objetos ya existentes).\n'
        )
        sys.exit(rc)
    print('Restore completado.')


def main() -> None:
    parser = argparse.ArgumentParser(description='Backup/restore PostgreSQL (pg_dump/pg_restore)')
    sub = parser.add_subparsers(dest='command', required=True)

    p_bak = sub.add_parser('backup', help='Volcado con pg_dump -Fc')
    p_bak.add_argument(
        '--output',
        '-o',
        help='Ruta del archivo .dump (por defecto backups/total_living_<UTC>.dump)',
    )
    p_bak.set_defaults(func=cmd_backup)

    p_res = sub.add_parser('restore', help='Restaurar con pg_restore (destructivo con --clean)')
    p_res.add_argument('--input', '-i', required=True, help='Archivo .dump generado por pg_dump -Fc')
    p_res.add_argument(
        '--confirm',
        action='store_true',
        help='Confirmar que DATABASE_URL apunta al entorno correcto (staging/simulacro)',
    )
    p_res.set_defaults(func=cmd_restore)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
