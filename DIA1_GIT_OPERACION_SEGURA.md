# Dia 1 - Operacion Git segura

Este documento define las reglas para evitar perdida de trazabilidad y sobrescrituras.

## Estado inicial corregido

- Git local fue reinicializado para recuperar control de versiones en `C:/TOTAL LIVING`.
- La carpeta de respaldos ya no debe mezclarse con codigo activo.

## Reglas obligatorias desde hoy

1. No usar `robocopy /MIR` sobre el root del proyecto activo.
2. No copiar codigo manualmente entre worktrees para "sincronizar".
3. Todo cambio entra por flujo Git:
   - `git status`
   - `git add ...`
   - `git commit -m "..."`
4. Antes de editar, validar rama y estado:
   - `git branch --show-current`
   - `git status --short`
5. Respaldos y dumps siempre fuera del repo o dentro de `backups/` (ignorado por Git).

## Flujo diario recomendado

1. Abrir terminal en `C:/TOTAL LIVING`.
2. Verificar estado:
   - `git status --short`
3. Ejecutar servidor/desarrollo normal.
4. Al terminar bloque de trabajo:
   - `git add`
   - `git commit`
5. Registrar cualquier incidencia en este archivo o en un changelog.

## Alertas de riesgo (no repetir)

- Si `git status` marca "not a git repository", detener trabajo y corregir primero Git.
- Si hay procesos de copia masiva entre carpetas del proyecto, detenerlos antes de continuar.
