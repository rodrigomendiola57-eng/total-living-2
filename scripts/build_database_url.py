"""Genera DATABASE_URL con contraseña codificada para Render/RDS."""
from __future__ import annotations

import sys
from urllib.parse import quote


def main() -> int:
    if len(sys.argv) < 2:
        print('Uso: python scripts/build_database_url.py TU_CONTRASEÑA_RDS')
        print('Ejemplo de salida: postgresql://total_living:...host.../postgres')
        return 1

    password = sys.argv[1]
    encoded = quote(password, safe='')
    url = (
        'postgresql://total_living:'
        f'{encoded}@total-living-staging.c4ji4emmcvf3.us-east-1.rds.amazonaws.com:5432/postgres'
    )
    print(url)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
