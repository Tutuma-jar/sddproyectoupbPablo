# Constitución — dance-school-admin

> Estado: **aprobada** (fase 1, 2026-10-23). Decisiones D-1…D-5 en [`constitution-proposal.md`](constitution-proposal.md).

1. **Stack simple**: un solo lenguaje para dominio y servidor, una sola aplicación desplegable y una sola base de datos. Cada dependencia externa aparece en el plan con su motivo; si no está justificada, no entra.
2. **Spec antes que código**: ningún comportamiento se implementa sin un RF aprobado en `specs/`. Si spec y código no coinciden, se corrige el código; si la spec está mal, se cambia primero la spec con su revisión.
3. **Dominio sin E/S**: las reglas de negocio (matrículas, cuotas, morosidad, permisos, edades) viven en una capa de dominio que no importa interfaz, base de datos, red ni reloj; la fecha actual se le pasa como parámetro.
4. **Tests obligatorios**: cada RF tiene al menos un test automático y cada CL su caso. La suite completa pasa antes de cada commit y de cada despliegue, con fecha fija y datos ficticios.
5. **Persistencia controlada**: una única base de datos, a la que solo accede la capa de persistencia; cada cambio de esquema es una migración versionada; copia de seguridad cifrada diaria, conservada 30 días, con prueba de restauración trimestral (D-5).
6. **Idioma**: código, identificadores, nombres de archivo y comentarios en inglés; textos de la interfaz y documentación en español.
7. **Mínimo dato, mínimo acceso**: solo se guarda el dato personal que un RF justifica. Todo acceso se deniega por defecto y el servidor comprueba el rol en cada operación según la matriz de permisos de la spec. Los datos de menores y el único campo de observaciones de salud (opcional, D-2) solo los ven los roles que la matriz autoriza.
8. **Datos personales protegidos y trazables**: cumplimiento de la Ley 1581 de 2012 y el Decreto 1377 de 2013 de Colombia (D-1); tráfico siempre cifrado, contraseñas con hash y base de datos y copias cifradas en reposo por el hosting (D-3); registro de auditoría de altas, cambios, bajas y borrados de datos personales, de las consultas del campo de salud y de las exportaciones (D-4); logs sin datos personales; ningún dato real fuera de producción; al vencer el plazo de conservación fijado en la spec, los datos se borran o anonimizan.

Cómo se verifica cada principio y las decisiones que faltan: [`constitution-proposal.md`](constitution-proposal.md).
