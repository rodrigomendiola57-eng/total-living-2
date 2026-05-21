"""
Preflight local sin Docker para Total Living.

Valida rápidamente entorno, settings, migraciones y checks antes de arrancar.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], label: str) -> bool:
    print(f"[CHECK] {label}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"[FAIL] {label}")
        return False
    print(f"[OK] {label}")
    return True


def main() -> int:
    print("=== PREFLIGHT LOCAL (SIN DOCKER) ===")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Root:   {ROOT}")

    if sys.version_info < (3, 11):
        print("[FAIL] Python 3.11+ es requerido.")
        return 1

    if not (ROOT / "manage.py").exists():
        print("[FAIL] No existe manage.py en el root del proyecto.")
        return 1

    env_candidates = [ROOT / ".env.development", ROOT / ".env", ROOT / ".env.example"]
    if not any(p.exists() for p in env_candidates):
        print("[FAIL] No se encontro .env.development, .env ni .env.example.")
        return 1
    print("[OK] Variables de entorno base encontradas.")

    checks = [
        ([sys.executable, "-m", "django", "--version"], "Django instalado"),
        ([sys.executable, "manage.py", "check"], "Django system check"),
        ([sys.executable, "manage.py", "migrate", "--check"], "Migraciones aplicadas"),
    ]

    all_ok = True
    for cmd, label in checks:
        all_ok = run(cmd, label) and all_ok

    if not all_ok:
        print("\n[RESULT] Preflight incompleto. Corrige errores antes de continuar.")
        return 1

    print("\n[RESULT] Preflight correcto. Entorno listo para trabajar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
