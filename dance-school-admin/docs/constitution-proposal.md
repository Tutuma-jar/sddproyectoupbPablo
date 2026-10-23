# Propuesta de constitución — dance-school-admin

App administrativa de clientes para una escuela de danza. Maneja datos de
alumnos (muchos menores), de sus tutores, de contacto y posiblemente de salud o
lesiones, así que la protección de datos personales es un principio de primer
nivel y no un detalle de implementación.

## Objetivo

De seis a ocho principios innegociables, cortos y verificables (máximo 20
líneas), que cubran:

- simplicidad del stack,
- spec antes que código,
- separación entre lógica e interfaz,
- tests,
- persistencia,
- idioma,
- protección de datos personales (menores, contacto, salud).

## Supuestos de partida

El contexto del encargo llegó con los campos de ejemplo sin rellenar (usuarios,
qué se gestiona, restricciones). Para esta fase no hacen falta: los principios
no dependen del stack ni del alcance. Se concretarán en las preguntas de la
fase 2 (alcance, roles, ciclo de vida, pagos) y de la fase 5 (stack, despliegue,
autenticación).

## Principios propuestos

El texto está en [`constitution.md`](constitution.md). Resumen:

| # | Principio | Qué protege |
|---|-----------|-------------|
| 1 | Stack simple | Que un equipo pequeño pueda mantenerlo y desplegarlo. |
| 2 | Spec antes que código | Que solo se construya lo acordado y que todo sea rastreable. |
| 3 | Dominio sin E/S | Que las reglas de negocio se prueben sin base de datos ni interfaz. |
| 4 | Tests obligatorios | Que cada requisito tenga una prueba que lo demuestre. |
| 5 | Persistencia controlada | Que los datos no se corrompan ni se pierdan. |
| 6 | Idioma | Un solo idioma en el código; español para quien usa la app. |
| 7 | Mínimo dato, mínimo acceso | Que cada persona vea solo lo que su rol necesita. |
| 8 | Datos protegidos y trazables | Cumplimiento legal, cifrado, auditoría y borrado. |

## Cómo se verifica cada principio

| # | Principio | Verificación |
|---|-----------|--------------|
| 1 | Stack simple | El plan contiene una tabla de dependencias con su motivo; el manifiesto de dependencias del proyecto no incluye nada que no esté en esa tabla. Hay un único artefacto desplegable y una única base de datos. |
| 2 | Spec antes que código | La tabla de trazabilidad del plan asigna cada RF a un módulo y un test; cada tarea T-x cita los RF/CL que cubre; ningún test ni tarea cita un RF que no exista en la spec aprobada. |
| 3 | Dominio sin E/S | Un test automático de arquitectura falla si la capa de dominio importa módulos de interfaz, persistencia, red o reloj del sistema. Buscar llamadas a la fecha u hora actual dentro del dominio no devuelve nada. |
| 4 | Tests obligatorios | El comando de tests termina en verde; cada RF y cada CL de la spec aparece citado al menos en un test. Los datos de prueba están en fixtures ficticias del repositorio. |
| 5 | Persistencia controlada | Solo la capa de persistencia importa el driver o la librería de base de datos; cada cambio de esquema tiene su archivo de migración; existe un procedimiento escrito de restauración y un registro de la última prueba. |
| 6 | Idioma | Revisión de código: identificadores y comentarios en inglés; todos los textos al usuario están en el catálogo de mensajes M-x / E-x de la spec, en español. |
| 7 | Mínimo dato, mínimo acceso | Cada campo del modelo de datos del plan cita el RF que lo justifica. Hay tests que comprueban, para cada fila de la matriz de permisos, que un rol no autorizado recibe un rechazo del servidor. |
| 8 | Datos protegidos y trazables | Tests que comprueban: el registro de auditoría se escribe en cada alta, cambio, baja y borrado de datos personales, en cada consulta del campo de salud y en cada exportación; los logs no contienen campos personales; la purga o anonimización se ejecuta al vencer el plazo. La configuración de despliegue fuerza HTTPS y el cifrado en reposo. Las fixtures no contienen datos reales. |

## Decisiones que tienes que tomar (D-x)

D-1…D-4 las decidió el usuario, de una en una. Desde D-5 rige la regla «usa
tus recomendaciones»: Claude decide y registra el motivo.

### D-1. ¿Qué normativa de protección de datos aplica? — *resuelta*

Determina la edad a partir de la cual un menor consiente por sí mismo, el
tratamiento de los datos de salud y los derechos que la app debe soportar.

- (a) Colombia: Ley 1581 de 2012 y Decreto 1377 de 2013 (datos de menores con autorización del representante legal; salud como dato sensible).
- (b) España / UE: RGPD y LOPDGDD (menores de 14 con consentimiento de los tutores; salud como categoría especial).
- (c) Otra jurisdicción.
- **Recomendación:** la del país donde opera la escuela. No es asesoría legal: conviene validar el resultado con quien lleve la protección de datos de la escuela.
- **Decisión:** (a) Colombia, Ley 1581 de 2012 y Decreto 1377 de 2013.
- **Motivo:** la escuela opera en Colombia (decisión del usuario).
- **Consecuencias para las fases siguientes:** la spec deberá cubrir la autorización
  previa e informada del titular o, en menores, de su representante legal; el
  tratamiento de la salud como dato sensible (autorización explícita y facultativa);
  y los derechos de consulta, actualización, rectificación y supresión del titular.

### D-2. ¿Se guardan datos de salud o lesiones? — *resuelta*

- (a) No se guardan en el MVP; el profesor pregunta directamente al alumno o al tutor.
- (b) **(Recomendada)** Solo un campo breve de «observaciones de salud relevantes para la clase» (alergias, lesiones), visible únicamente para los roles que autorice la matriz y con auditoría de cada consulta.
- (c) Ficha de salud completa.
- **Motivo de la recomendación:** la seguridad en clase justifica conocer lesiones y alergias, y un solo campo restringido cumple el principio de mínimo dato. Con D-1 (Colombia) la salud es dato sensible: el campo sería opcional y exigiría autorización explícita del titular o de su representante legal.
- **Decisión:** (b) un único campo breve de observaciones de salud, opcional, restringido por rol y con auditoría de cada consulta.
- **Motivo:** el recomendado; equilibra la seguridad en clase con el mínimo dato.

### D-3. ¿Cómo se cifran los datos en reposo? — *resuelta*

- (a) **(Recomendada)** Cifrado de la base de datos y de las copias que ofrece el proveedor de hosting, sin cifrado adicional por campo.
- (b) Lo anterior más cifrado por campo de los datos de salud dentro de la aplicación.
- **Motivo de la recomendación:** (a) cubre el robo de discos y copias sin añadir código ni gestión de claves; el acceso indebido desde la app ya lo frenan los principios 7 y 8. Si en D-2 eliges (c), recomiendo (b).
- **Decisión:** (a) cifrado de la base de datos y de las copias que ofrece el proveedor de hosting, sin cifrado por campo.
- **Motivo:** el recomendado; con D-2 limitada a un campo breve, el cifrado por campo no compensa su coste. El plan (fase 5) deberá elegir un hosting que ofrezca ese cifrado.

### D-4. ¿Qué se audita? — *resuelta*

- (a) Altas, cambios, bajas y borrados de cualquier dato personal.
- (b) **(Recomendada)** Lo de (a) más las consultas de datos de salud y las exportaciones de datos.
- (c) Toda lectura y escritura de datos personales.
- **Motivo de la recomendación:** (b) registra lo que importa en caso de incidente sin llenar la auditoría con cada consulta rutinaria de la lista de alumnos.
- **Decisión:** (b) altas, cambios, bajas y borrados de datos personales, más las consultas del campo de salud y las exportaciones de datos.
- **Motivo:** el recomendado; además es coherente con D-2, que exige auditar cada consulta del campo de salud.

### D-5. ¿Con qué frecuencia se hacen copias de seguridad? — *resuelta*

- (a) **(Recomendada)** Diaria, cifrada, conservada 30 días, con prueba de restauración trimestral.
- (b) Semanal, cifrada, conservada 8 semanas, con prueba de restauración semestral.
- **Motivo de la recomendación:** los pagos y la asistencia cambian cada día; perder una semana de datos sería grave para la administración.
- **Decisión:** (a) diaria, cifrada, conservada 30 días, con prueba de restauración trimestral.
- **Motivo:** tomada por Claude con la regla «usa tus recomendaciones»; es la opción recomendada, por el motivo indicado arriba.

## Resultado

D-1…D-5 están resueltas y el usuario aprobó la fase 1 el 2026-10-23. El texto
final aprobado está en [`constitution.md`](constitution.md).
