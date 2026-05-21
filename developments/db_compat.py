"""Comprobaciones de esquema para no romper el panel ni el público si falta migrar."""


def floorplan_table_ready() -> bool:
    try:
        from django.db import connection

        return 'developments_developmentunitmodelfloorplan' in connection.introspection.table_names()
    except Exception:
        return False
