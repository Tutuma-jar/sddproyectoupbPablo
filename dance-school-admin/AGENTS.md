# AGENTS.md — dance-school-admin

## Proyecto
App administrativa de clientes para una escuela de danza, construida con
desarrollo guiado por especificaciones (SDD). Todas las rutas de este archivo
son relativas a la carpeta `dance-school-admin/`.

## Fases
1. Constitución — `docs/constitution.md`
2. Spec del MVP — `specs/001-<nombre>/spec.md`
3. Revisión de QA — `specs/001-<nombre>/qa-review.md`
4. Resolución de hallazgos — nueva versión de la spec
5. Plan técnico — `specs/001-<nombre>/plan.md`
6. Tareas — `specs/001-<nombre>/tasks.md`

No se escribe código de la aplicación hasta la fase 6. Cada fase se detiene
hasta que el usuario escribe «Apruebo la fase N».

## Reglas
- Lee `docs/constitution.md` y la spec activa en `specs/` antes de tocar nada.
- Preguntas de una en una, con 2-4 opciones y la recomendación marcada.
- Con «usa tus recomendaciones», decide y registra cada decisión con su motivo.
  El usuario activó esta regla en la fase 1 (desde D-5) para todo lo que siga;
  las aprobaciones de fase («Apruebo la fase N») siguen siendo suyas.
- Todo se documenta en Markdown; en el chat, solo resúmenes.
- Numeración rastreable: RF-x.y, RNF-x, CL-x, M-x / E-x, D-x, H-x, T-x.
- Commit al aprobar cada fase, en una rama de trabajo (nunca en `main`).
- Si algo contradice una fase aprobada, se avisa al usuario en vez de decidirlo.
- Código e identificadores en inglés; interfaz y documentación en español.

## Estado
- Fases 1-6 aprobadas el 2026-10-23: constitución, spec 001 (versión 3), revisión
  de QA, plan y tareas (`specs/001-dance-school-mvp/`).
- La implementación empieza por T-1 y sigue el orden de `tasks.md`; al terminar
  cada tarea se ejecuta `pytest -q`.
- Pendiente antes de T-71 (despliegue): aviso A-2 del plan, la región de los
  datos, que debe validar quien lleve la protección de datos de la escuela.
