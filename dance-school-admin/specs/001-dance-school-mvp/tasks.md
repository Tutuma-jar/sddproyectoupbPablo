# Tareas 001 — MVP de la app administrativa de la escuela de danza

- **Estado:** borrador, pendiente de la aprobación final del usuario
- **Fecha:** 2026-10-23
- **Origen:** [spec 001, versión 3](spec.md) y [plan 001](plan.md)

## Cómo usar esta lista

- Las tareas están en **orden de dependencia**; cada una indica de cuáles
  depende. Empiezan por el dominio y sus tests; la interfaz va al final.
- Cada tarea cabe en **menos de medio día** e incluye sus tests: se escriben
  primero, se ven fallar y después se escribe el código.
- Los tests citan en su nombre o con `pytest.mark.req(...)` los RF y CL que
  cubren (plan, 8.3).
- Todos los comandos se ejecutan desde `dance-school-admin/`, con la base de
  datos local levantada (`docker compose up -d db`).
- **Al terminar cada tarea**, se ejecuta `pytest -q` y debe pasar entero
  (principio 4). Es parte del «Hecho cuando» de todas las tareas, aunque no se
  repita.
- Las referencias D-x, H-x y R-x remiten al [plan](plan.md).
- Ninguna tarea se ha implementado todavía: esta fase solo planifica.

---

## Fase 0 — Preparación

- [ ] **T-1 · Esqueleto del proyecto** — principios 1 y 4
  - Depende de: —
  - Archivos: `pyproject.toml`, `manage.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `docker-compose.yml`, paquetes vacíos `dance_school/{domain,application,infrastructure,web}/`, `tests/conftest.py`
  - Hacer: dependencias de la tabla del plan (sección 2) y ninguna más; `TIME_ZONE = "America/Bogota"`, `USE_TZ = True`, `LANGUAGE_CODE = "es-co"`; PostgreSQL 16 en Docker; sin `django.contrib.admin` (H-51).
  - Test: `python manage.py check` y `pytest -q`.
  - Hecho cuando: `manage.py check` no da errores y `pytest -q` termina sin errores de importación ni de configuración.

- [ ] **T-2 · Puertos y reloj fijo** — RF-1.1, RNF-11
  - Depende de: T-1
  - Archivos: `dance_school/application/ports.py`, `tests/conftest.py`, `tests/application/test_ports.py`
  - Hacer: protocolos `Clock`, `UnitOfWork`, `AuditLog`, `PasswordHasher`, `Totp` y repositorios (plan, sección 3); `FixedClock` y fixtures `today` (2026-10-23) y `clock`.
  - Test: `tests/application/test_ports.py` comprueba que `FixedClock` devuelve la fecha fijada y que se puede mover a otro día.
  - Hecho cuando: el test pasa y ningún archivo de `tests/` usa el reloj real.

- [ ] **T-3 · Test de arquitectura de capas** — principio 3, RNF-11
  - Depende de: T-1
  - Archivos: `tests/architecture/test_layers.py`
  - Hacer: analizar con `ast` los `import` de `domain` y `application` (prohibidos Django, psycopg, `infrastructure`, `web`) y buscar llamadas a `now(` y `today(` fuera de `infrastructure/clock.py` (R-1).
  - Test: el propio archivo, más un caso que pasa código con `import django` a la función de análisis y espera que la detecte.
  - Hecho cuando: pasa con los paquetes actuales y el caso negativo se detecta.

- [ ] **T-4 · Catálogo de mensajes** — sección 6 de la spec, RNF-1
  - Depende de: T-1
  - Archivos: `dance_school/messages.py`, `tests/architecture/test_messages.py`
  - Hacer: diccionario `MESSAGES` con los 39 M-x y los 48 E-x y `render(code, **params)`.
  - Test: `test_messages.py` lee la tabla de la sección 6 de `spec.md` y compara cada texto con el catálogo, sin diferencias.
  - Hecho cuando: los 87 textos coinciden y `render` falla si falta un parámetro.

---

## Fase 1 — Dominio (sin E/S)

- [ ] **T-5 · Normalización y validación de textos** — RF-1.2, RF-1.3, RF-1.4, RF-1.5
  - Depende de: T-4
  - Archivos: `dance_school/domain/errors.py`, `dance_school/domain/text.py`, `tests/domain/test_text.py`
  - Hacer: `DomainError(code, params)`; `normalize()` (NFC, espacios de Unicode, colapso); `validate_text(value, max_length, required)` con [E-2], [E-3] y [E-4].
  - Test: tabulador, salto de línea y U+00A0 interiores; «á» descompuesta; vacío tras normalizar → E-2; 61 caracteres en un campo de 60 → E-3; U+0007 → E-4.
  - Hecho cuando: `pytest -q tests/domain/test_text.py` pasa con esos casos.

- [ ] **T-6 · Clave de comparación de nombres** — RF-1.6; CL-5, CL-6, CL-45
  - Depende de: T-5
  - Archivos: `dance_school/domain/text.py`, `tests/domain/test_text.py`
  - Hacer: `fold()` según D-27.
  - Test: «María» = «maria» = «MARIA»; «Peña» ≠ «Pena»; «ç» = «c»; «Ruiz-López» ≠ «Ruiz López»; «maria  perez» = «María Pérez» tras normalizar.
  - Hecho cuando: los casos de CL-5, CL-6 y CL-45 pasan.

- [ ] **T-7 · Teléfono y correo** — RF-1.7, RF-1.8, RF-1.9, RF-1.16; CL-8, CL-46
  - Depende de: T-5
  - Archivos: `dance_school/domain/contact_info.py`, `tests/domain/test_contact_info.py`
  - Hacer: `parse_phone()` → 10 dígitos o [E-5]; `parse_email()` → minúsculas o [E-6].
  - Test: «+57 (300) 123-4567» → `3001234567`; 9 y 11 dígitos → E-5; «a b@x.co», «a@b.», «a@.b», «@x.co», «a@@x.co» → E-6; «Ana@Escuela.co» → «ana@escuela.co».
  - Hecho cuando: los casos pasan, incluidos los de CL-8 y CL-46.

- [ ] **T-8 · Importes y formatos** — RF-1.10, RF-1.11, RNF-1
  - Depende de: T-5
  - Archivos: `dance_school/domain/formatting.py`, `tests/domain/test_formatting.py`
  - Hacer: `validate_amount()` ([E-22]); `format_money`, `format_date`, `format_phone`, `format_month`.
  - Test: 0, 10.000.001, 1,5 y «abc» → E-22; `1250000` → «$ 1.250.000»; `date(2026, 10, 23)` → «23/10/2026»; `3001234567` → «300 123 4567»; octubre de 2026 → «octubre de 2026».
  - Hecho cuando: los casos pasan.

- [ ] **T-9 · Edad, minoría de edad y fechas** — RF-1.12, RF-1.13, RF-1.14, RF-4.3; CL-1, CL-2, CL-3, CL-4
  - Depende de: T-5
  - Archivos: `dance_school/domain/people.py`, `tests/domain/test_people.py`
  - Hacer: `age_on(birth, today)`, `is_minor()`, `validate_birth_date()` ([E-7]) y `validate_not_future()` ([E-41]).
  - Test: cumple 18 hoy → adulto (CL-1); mañana → menor (CL-2); nacido el 29/02 y hoy 28/02 de año no bisiesto → aún no los cumple (CL-3); nacido hoy → E-7 (CL-4); 100 años → válido, 101 → E-7; firma mañana → E-41.
  - Hecho cuando: los casos pasan.

- [ ] **T-10 · Matriz de permisos** — RF-3.1, sección 5 de la spec
  - Depende de: T-4
  - Archivos: `dance_school/domain/permissions.py`, `tests/domain/test_permissions.py`
  - Hacer: `Role`, `Action` (una por fila de la matriz), `PERMISSIONS` y `can(role, action)`.
  - Test: tabla literal con las 22 filas de la matriz × 3 roles, comparada con `can()`.
  - Hecho cuando: las 66 combinaciones coinciden con la spec.

- [ ] **T-11 · Reglas de cuentas** — RF-2.4, RF-2.10, RF-2.11, RF-2.14, RF-2.19, RF-2.20; CL-34, CL-42
  - Depende de: T-10
  - Archivos: `dance_school/domain/accounts.py`, `tests/domain/test_accounts.py`
  - Hacer: `register_failed_attempt()`, `is_locked()`, `reset_attempts()`; `validate_password()` ([E-45]); comprobaciones de última cuenta de Dirección ([E-29]) y de profesor con grupos ([E-30]).
  - Test: quinto fallo bloquea 15 minutos aunque luego la contraseña sea correcta (CL-42); acceso correcto y fin del bloqueo reinician el contador; desactivar a la última Dirección → E-29 y a un profesor con grupos → E-30 (CL-34); contraseña de 11 caracteres → E-45.
  - Hecho cuando: los casos pasan.

- [ ] **T-12 · Alta de alumnos (reglas)** — RF-4.2, RF-4.5, RF-4.6, RF-4.7, RF-4.8; CL-43
  - Depende de: T-6, T-7, T-9
  - Archivos: `dance_school/domain/students.py`, `tests/domain/test_students.py`
  - Hacer: `validate_new_student(data, today)`.
  - Test: faltan nombre o autorización → E-2/E-11; menor sin contactos → E-9; adulto sin teléfono → E-2; responsable por defecto del adulto = él mismo; responsable que no es contacto → E-39; adulto que paga su padre → válido (CL-43).
  - Hecho cuando: los casos pasan.

- [ ] **T-13 · Contactos y vínculos (reglas)** — RF-5.2, RF-5.3, RF-5.4, RF-5.5, RF-5.9, RF-5.10, RF-5.11; CL-10, CL-11, CL-12
  - Depende de: T-12
  - Archivos: `dance_school/domain/contacts.py`, `tests/domain/test_contacts.py`
  - Hacer: validación de contacto y relación; tipo de contacto según la edad; máximo 2; reglas de desvinculación; predicado `is_orphan()`.
  - Test: tercer contacto → E-10 (CL-10); quitar al único tutor de un menor → E-9 (CL-11); quitar al responsable de pago → E-40 (CL-12); un contacto con un solo hermano anonimizado y otro activo no es huérfano.
  - Hecho cuando: los casos pasan.

- [ ] **T-14 · Autorizaciones y salud (reglas)** — RF-6.1, RF-6.3, RF-6.4, RF-6.5, RF-6.7, RF-6.9, RF-6.11; CL-9, CL-15, CL-55
  - Depende de: T-13
  - Archivos: `dance_school/domain/consent.py`, `tests/domain/test_consent.py`
  - Hacer: `Consent` con copia del otorgante; `current_consent()`; `validate_consent()`; `is_renewal_pending(student, today)`; `can_store_health()`.
  - Test: menor autorizado por quien no es su contacto → E-12; adulto autorizado por un contacto → E-12; salud sin autorización de salud o revocada → E-13 (CL-15); 18 años con autorización del tutor → pendiente (CL-9); renovación sin teléfono → E-2; 13 años sin opinión → E-47 y 8 años → válido (CL-55).
  - Hecho cuando: los casos pasan.

- [ ] **T-15 · Edición, baja y reactivación (reglas)** — RF-7.7, RF-7.8, RF-7.9, RF-7.10, RF-8.2, RF-8.3, RF-8.4, RF-8.5, RF-8.6, RF-8.7, RF-8.8, RF-8.9; CL-16, CL-17, CL-52
  - Depende de: T-14
  - Archivos: `dance_school/domain/students.py`, `tests/domain/test_students.py`
  - Hacer: `validate_changes()` solo sobre lo modificado; `plan_leave()` (estado, fecha, matrículas a cerrar, salud a borrar; la deuda no cambia); `validate_reactivation()`.
  - Test: editar a un recién mayor de edad sin teléfono y con autorización del tutor → permitido; salud de un alumno de baja → E-14; editar anonimizado → E-37; baja con 3 matrículas → las 3 se cierran hoy y se borra la salud (CL-16); reactivar sin autorización → E-11; reactivar a un adulto que se fue siendo menor exige que autorice él mismo (CL-52); reactivado sin matrículas ni salud (CL-17).
  - Hecho cuando: los casos pasan.

- [ ] **T-16 · Grupos (reglas)** — RF-9.2, RF-9.3, RF-9.4, RF-9.5, RF-9.6, RF-9.7, RF-9.9, RF-9.11, RF-9.15; CL-32, CL-33, CL-44, CL-54
  - Depende de: T-6, T-8, T-10
  - Archivos: `dance_school/domain/groups.py`, `tests/domain/test_groups.py`
  - Hacer: `validate_group()`, `validate_capacity_change()`, `validate_archive()`.
  - Test: 0 y 8 franjas → E-34; fin igual a inicio → E-19; cupo 0 y 101 → E-42; profesor Recepción → E-43 y Dirección → válido (CL-44); cupo menor que matrículas → E-20 (CL-32); archivar con matrículas → E-21 (CL-33); lunes 17:00–18:00 y 17:30–18:30 → E-46 (CL-54).
  - Hecho cuando: los casos pasan.

- [ ] **T-17 · Matrículas (reglas)** — RF-10.3, RF-10.4, RF-10.5, RF-10.6, RF-10.8, RF-10.10; CL-21, CL-22
  - Depende de: T-15, T-16
  - Archivos: `dance_school/domain/enrollments.py`, `tests/domain/test_enrollments.py`
  - Hacer: `is_active_on(enrollment, day)`, `free_places()`, `validate_enrollment()`, `should_void_fee_on_end()`.
  - Test: activa el día de alta, inactiva el día de baja (CL-21); ya matriculado → E-15; sin plazas → E-16; archivado → E-17; de baja → E-14; finalizada el día del alta con cuota sin pagos → anular (CL-22), con pagos → no.
  - Hecho cuando: los casos pasan.

- [ ] **T-18 · Cuotas mensuales (reglas)** — RF-11.1, RF-11.2, RF-11.3, RF-11.5, RF-11.6, RF-11.8; CL-18, CL-19, CL-20, CL-23, CL-48
  - Depende de: T-17
  - Archivos: `dance_school/domain/billing.py`, `tests/domain/test_billing.py`
  - Hacer: `fees_due_for_month()`, `fee_on_enrollment()`, `fee_key()` (alumno, grupo, mes; las anuladas no cuentan, RF-11.1), `concept()`, `issued_on()`, `due_date()`.
  - Test: alta el 15 → cuota emitida el 15 con vencimiento el 25 (CL-18); alta el 16 → sin cuota ese mes (CL-19); segunda generación sin nada nuevo (CL-20); mes anterior → rechazado (CL-23); rematrícula el 10 tras baja el 5 → sin segunda cuota (CL-48); concepto con «septiembre de 2026» y grupo de 60 caracteres cabe en 100.
  - Hecho cuando: los casos pasan.

- [ ] **T-19 · Saldo, estado y anulación de cargos** — RF-11.9, RF-11.10, RF-11.12, RF-11.13; CL-26, CL-28
  - Depende de: T-18
  - Archivos: `dance_school/domain/billing.py`, `tests/domain/test_billing.py`
  - Hacer: `balance()` (ignora aplicaciones de pagos anulados), `status()`, `validate_void_charge()`.
  - Test: vence hoy → pendiente; mañana → vencido (CL-28); saldo 0 → pagado; anular con pagos → E-26 (CL-26); anular dos veces → E-38.
  - Hecho cuando: los casos pasan.

- [ ] **T-20 · Pagos (reglas)** — RF-12.2, RF-12.3, RF-12.4, RF-12.5, RF-12.6, RF-12.7; CL-24, CL-25, CL-27, CL-29, CL-47
  - Depende de: T-19
  - Archivos: `dance_school/domain/payments.py`, `tests/domain/test_payments.py`
  - Hacer: `validate_payment()`, `allocate()`, `reverse()`.
  - Test: sin deuda → E-23; $ 150.000 con deuda de $ 120.000 → E-24 (CL-24); $ 50.000 sobre dos cargos de $ 80.000 → saldos 30.000 y 80.000 (CL-25); desempate por creación; anular un pago repartido en dos cargos devuelve ambos saldos (CL-27); fecha de hace 32 días → E-25 (CL-29); la fecha del pago no cambia el orden (CL-47).
  - Hecho cuando: los casos pasan.

- [ ] **T-21 · Deuda y morosidad** — RF-13.2, RF-13.3, RF-13.5
  - Depende de: T-19
  - Archivos: `dance_school/domain/delinquency.py`, `tests/domain/test_delinquency.py`
  - Hacer: `debt_summary()` (pendiente y vencida), `is_delinquent()`, `days_overdue()`.
  - Test: los anulados no suman; un alumno de baja con deuda vencida es moroso; días de atraso desde el vencimiento más antiguo.
  - Hecho cuando: los casos pasan.

- [ ] **T-22 · Plazos de conservación** — RF-16.2, RF-16.5, RF-16.6, RF-16.7, RF-16.8; CL-37, CL-38
  - Depende de: T-9, T-21
  - Archivos: `dance_school/domain/retention.py`, `tests/domain/test_retention.py`
  - Hacer: `retention_actions(students, accounts, today)` y predicados de cada plazo.
  - Test: 2 años exactos → anonimizar (CL-38); baja el 29/02 → plazo el 01/03; 2 años con deuda → conservar (CL-37); 10 años anonimizado → eliminar; cuenta desactivada hace 5 años → anonimizar; auditoría de más de 5 años → eliminar.
  - Hecho cuando: los casos pasan.

- [ ] **T-23 · Anonimización (transformación)** — RF-16.3, RF-16.9
  - Depende de: T-22
  - Archivos: `dance_school/domain/retention.py`, `tests/domain/test_retention.py`
  - Hacer: `anonymize(student, alias_number)` y `scrub_financials(charges, payments)`.
  - Test: nombre → «Alumno anonimizado 7»; fecha, teléfono, correo, salud, autorizaciones, solicitudes y vínculos vacíos; concepto manual → «Cargo manual»; referencias y motivos borrados; conceptos de cuotas intactos.
  - Hecho cuando: los casos pasan.

- [ ] **T-24 · Catálogo de acciones auditables** — RF-17.1
  - Depende de: T-10
  - Archivos: `dance_school/domain/audit.py`, `tests/domain/test_audit.py`
  - Hacer: `AuditAction` con una entrada por evento de RF-17.1 y su tipo de entidad.
  - Test: el catálogo contiene todos los eventos enumerados en RF-17.1 (lista literal en el test).
  - Hecho cuando: el test pasa.

---

## Fase 2 — Persistencia

- [ ] **T-25 · Modelos de cuentas y personas** — RF-4.4; sección 7 de la spec
  - Depende de: T-2, T-6
  - Archivos: `dance_school/infrastructure/models.py`, `dance_school/infrastructure/migrations/0001_people.py`, `tests/application/test_models_people.py`
  - Hacer: `account`, `student`, `contact`, `student_contact` y `consent` con las columnas y restricciones del plan (4.1–4.4).
  - Test: el índice parcial rechaza dos alumnos no anonimizados con la misma clave y fecha y admite el duplicado de un anonimizado; `CHECK` de `status`/`left_on` y de correo en minúsculas.
  - Hecho cuando: `python manage.py makemigrations --check` no detecta cambios y los tests pasan.

- [ ] **T-26 · Modelos de grupos y matrículas** — RF-9.3, RF-10.3
  - Depende de: T-25
  - Archivos: `models.py`, `migrations/0002_groups.py`, `tests/application/test_models_groups.py`
  - Hacer: `dance_group`, `time_slot` y `enrollment` (plan, 4.5–4.6).
  - Test: dos grupos sin archivar con el mismo nombre → rechazo de la base de datos; dos matrículas abiertas del mismo alumno y grupo → rechazo; `CHECK` de cupo y franjas.
  - Hecho cuando: los tests pasan.

- [ ] **T-27 · Modelos económicos, solicitudes y auditoría** — RF-11.1, RF-15.11, RF-17.2
  - Depende de: T-26
  - Archivos: `models.py`, `migrations/0003_billing_audit.py`, `tests/application/test_models_billing.py`
  - Hacer: `charge`, `payment`, `payment_allocation`, `data_request` y `audit_entry` (plan, 4.7–4.9).
  - Test: dos cuotas activas del mismo alumno, grupo y mes → rechazo, pero se admite si una está anulada; `CHECK` de solicitud con un solo titular y respuesta posterior a la recepción.
  - Hecho cuando: los tests pasan.

- [ ] **T-28 · Roles de base de datos de la auditoría** — RF-17.4; H-58
  - Depende de: T-27
  - Archivos: `migrations/0004_db_roles.py`, `tests/architecture/test_audit_grants.py`
  - Hacer: roles `app_rw` y `app_maint` con los permisos del plan (7.1).
  - Test: con la conexión de `app_rw`, `UPDATE` y `DELETE` sobre `audit_entry` fallan; con `app_maint`, `DELETE` funciona.
  - Hecho cuando: el test pasa.

- [ ] **T-29 · Repositorios, unidad de trabajo y bloqueo optimista** — RF-1.15; CL-41
  - Depende de: T-27
  - Archivos: `dance_school/infrastructure/repositories.py`, `dance_school/infrastructure/unit_of_work.py`, `tests/application/test_repositories.py`
  - Hacer: implementaciones de los puertos; `UPDATE … WHERE version = ?` (D-28); `lock_group()` y `lock_student()` (D-29).
  - Test: dos ediciones con la misma versión → la segunda recibe E-35 (CL-41); una excepción dentro de la unidad de trabajo deshace todo.
  - Hecho cuando: los tests pasan.

- [ ] **T-30 · Auditoría transaccional** — RF-17.2, RF-17.5, RNF-9; CL-40
  - Depende de: T-24, T-29
  - Archivos: `dance_school/infrastructure/repositories.py` (`AuditLog`), `tests/application/test_audit_log.py`
  - Hacer: escritura de entradas sin valores personales, en la misma transacción.
  - Test: la entrada solo tiene fecha y hora, actor, acción, tipo e id; si la escritura falla durante un pago, no queda ni el pago ni la entrada (CL-40).
  - Hecho cuando: los tests pasan.

- [ ] **T-31 · Reloj de Bogotá** — RF-1.1; R-2
  - Depende de: T-2
  - Archivos: `dance_school/infrastructure/clock.py`, `tests/application/test_clock.py`
  - Hacer: `BogotaClock` con `zoneinfo`.
  - Test: con un instante UTC de las 04:30 del 24/10, «hoy» es 23/10 en Bogotá; a las 05:00 UTC ya es 24/10.
  - Hecho cuando: los tests pasan.

- [ ] **T-32 · TOTP** — RF-2.22, RF-2.23; R-3
  - Depende de: T-2
  - Archivos: `dance_school/infrastructure/totp.py`, `tests/application/test_totp.py`
  - Hacer: generación de secreto, `verify(secret, code, now, last_step)` con ventana ±1 (D-33).
  - Test: vectores de la RFC 6238 (SHA-1); código fuera de la ventana → falso; mismo paso reutilizado → falso.
  - Hecho cuando: los tests pasan.

---

## Fase 3 — Casos de uso (aplicación)

- [ ] **T-33 · Comprobación de permisos y alcance del profesor** — RF-3.2, RF-3.3, RF-3.4; CL-35
  - Depende de: T-10, T-29
  - Archivos: `dance_school/application/authorization.py`, `tests/application/test_authorization.py`
  - Hacer: `authorize(actor, action)` y `teacher_scope(actor)` (plan, sección 6).
  - Test: rol no autorizado → E-1 sin consultar repositorios (doble que falla si se le llama); profesor que pide un alumno de otro grupo → E-1 (CL-35).
  - Hecho cuando: los tests pasan.

- [ ] **T-34 · Alta de cuentas y activación** — RF-2.7, RF-2.8, RF-2.16, RF-2.17, RF-2.18, RF-2.19; CL-46, CL-56
  - Depende de: T-11, T-30, T-33
  - Archivos: `dance_school/application/accounts.py`, `tests/application/test_accounts.py`
  - Hacer: `create_account()` con código de activación (D-33); `activate()`.
  - Test: [M-22] con el código; correo repetido con otras mayúsculas → E-33 (CL-46); código usado o de más de 72 horas → E-44 (CL-56); contraseña corta → E-45; activar invalida el código; todo queda auditado.
  - Hecho cuando: los tests pasan.

- [ ] **T-35 · Inicio de sesión, bloqueo y segundo factor** — RF-2.2, RF-2.3, RF-2.4, RF-2.20, RF-2.22, RF-2.23, RF-2.24; CL-42
  - Depende de: T-32, T-34
  - Archivos: `dance_school/infrastructure/auth_backend.py`, `dance_school/application/accounts.py`, `tests/application/test_login.py`
  - Hacer: acceso por correo; bloqueo; segundo factor obligatorio para Dirección y configuración en el primer acceso.
  - Test: credenciales erróneas o cuenta desactivada → E-31; quinto fallo → E-32 durante 15 minutos aunque la contraseña sea correcta (CL-42); Dirección sin segundo factor configurado debe configurarlo; código TOTP erróneo → E-31 y cuenta como fallo.
  - Hecho cuando: los tests pasan.

- [ ] **T-36 · Gestión de cuentas** — RF-2.9, RF-2.10, RF-2.11, RF-2.12, RF-2.13, RF-2.15, RF-2.21, RF-2.25; CL-34
  - Depende de: T-35
  - Archivos: `dance_school/application/accounts.py`, `tests/application/test_accounts_admin.py`
  - Hacer: desactivar, reactivar, cambiar rol, restablecer, desbloquear y cerrar sesiones (incrementa `session_epoch`, D-32).
  - Test: [M-23], [M-32], [M-33], [M-37], [M-39]; E-29 y E-30 (CL-34); el cambio de rol se aplica en la siguiente operación; restablecer invalida contraseña y segundo factor.
  - Hecho cuando: los tests pasan.

- [ ] **T-37 · Alta de alumnos** — RF-4.1, RF-4.4, RF-6.2; CL-5, CL-7
  - Depende de: T-12, T-14, T-30, T-33
  - Archivos: `dance_school/application/students.py`, `tests/application/test_register_student.py`
  - Hacer: `register_student()` con contactos, autorización y auditoría.
  - Test: [M-1]; «maria  perez» con la misma fecha que «María Pérez» → E-8 (CL-5); mismo nombre que un anonimizado → permitido (CL-7); sin autorización → E-11.
  - Hecho cuando: los tests pasan.

- [ ] **T-38 · Contactos** — RF-5.1, RF-5.6, RF-5.7, RF-5.8, RF-5.11; CL-13, CL-14, CL-49
  - Depende de: T-13, T-37
  - Archivos: `dance_school/application/contacts.py`, `tests/application/test_contacts.py`
  - Hacer: crear, buscar (nombre, apellidos, teléfono), vincular, editar, desvincular y borrar huérfanos; bloqueo del alumno al vincular.
  - Test: teléfono repetido → [M-18] y se puede crear igual (CL-14); un cambio se ve en los dos hermanos; desvincular del último alumno borra el contacto; con un hermano anonimizado y otro activo se conserva (CL-13); un alumno y un contacto con el mismo nombre quedan como registros independientes (CL-49).
  - Hecho cuando: los tests pasan.

- [ ] **T-39 · Autorizaciones** — RF-6.6, RF-6.8, RF-6.10; CL-9
  - Depende de: T-14, T-37
  - Archivos: `dance_school/application/consent.py`, `tests/application/test_consent.py`
  - Hacer: registrar, renovar y revocar la salud; exponer la marca de pendiente de renovar.
  - Test: autorización sin salud borra las observaciones; revocar → [M-27] y salud borrada; al cumplir 18 años la ficha lleva la marca y [M-17] y nada se bloquea (CL-9).
  - Hecho cuando: los tests pasan.

- [ ] **T-40 · Búsqueda y ficha** — RF-7.1, RF-7.2, RF-7.3, RF-7.4, RF-16.10
  - Depende de: T-37
  - Archivos: `dance_school/application/students.py`, `tests/application/test_search.py`
  - Hacer: `search_students()` y `get_student_file()`.
  - Test: «maria» encuentra a «María»; orden por apellidos y nombre; filtro por estado; sin resultados → [M-24]; la ficha indica si hay salud sin su contenido; los anonimizados no aparecen.
  - Hecho cuando: los tests pasan.

- [ ] **T-41 · Edición y observaciones de salud** — RF-7.5, RF-7.6, RF-7.11; CL-41, CL-53
  - Depende de: T-15, T-40
  - Archivos: `dance_school/application/students.py`, `tests/application/test_edit_student.py`
  - Hacer: `update_student()` con versión; `reveal_health_notes()` (solo Dirección, auditado) y `replace_health_notes()`.
  - Test: [M-2]; edición concurrente → E-35 (CL-41); Dirección ve la salud y queda auditada; Recepción la sustituye sin recibir el texto anterior (CL-53) y no puede verla (E-1).
  - Hecho cuando: los tests pasan.

- [ ] **T-42 · Baja y reactivación** — RF-8.1, RF-8.2, RF-8.3, RF-8.4, RF-8.5, RF-8.6, RF-8.7, RF-8.8, RF-8.9, RNF-9; CL-16, CL-17, CL-52
  - Depende de: T-15, T-39, T-41
  - Archivos: `dance_school/application/students.py`, `tests/application/test_leave.py`
  - Hacer: `prepare_leave()` (datos de [M-3]), `confirm_leave()` y `reactivate()` en una transacción.
  - Test: [M-3] con el número de matrículas; [M-4]; matrículas cerradas, salud borrada y sigue moroso (CL-16); fallo forzado a mitad → nada cambia (RNF-9); reactivar → [M-5] sin matrículas ni salud (CL-17); adulto que se fue siendo menor (CL-52).
  - Hecho cuando: los tests pasan.

- [ ] **T-43 · Grupos** — RF-9.1, RF-9.8, RF-9.10, RF-9.12, RF-9.13, RF-9.14; CL-30, CL-33
  - Depende de: T-16, T-33
  - Archivos: `dance_school/application/groups.py`, `tests/application/test_groups.py`
  - Hacer: crear, editar, archivar, desarchivar y listar con plazas libres.
  - Test: [M-25], [M-26], [M-34]; cambiar la cuota no altera las generadas (CL-30); archivar con matrículas → E-21 (CL-33); desarchivar con nombre ocupado → E-18.
  - Hecho cuando: los tests pasan.

- [ ] **T-44 · Matrículas** — RF-10.1, RF-10.2, RF-10.7, RF-10.9, RF-10.10, RF-11.3; CL-22, CL-31, CL-57
  - Depende de: T-17, T-18, T-42, T-43
  - Archivos: `dance_school/application/enrollments.py`, `tests/application/test_enrollments.py`
  - Hacer: `enroll()` con bloqueo del grupo y cuota del mes si procede; `end_enrollment()` con anulación automática como «sistema».
  - Test: [M-6]; moroso → confirmación [M-7]; [M-8]; dos hilos por la última plaza → una matrícula y un E-16 (CL-31); alta y baja el mismo día → cuota anulada con el motivo fijo y actor «sistema», aunque finalice Recepción (CL-22); al volver a matricularlo en ese grupo el mismo mes se genera una cuota nueva (CL-57).
  - Hecho cuando: los tests pasan.

- [ ] **T-45 · Generación de cuotas del mes** — RF-11.2, RF-11.4, RF-11.5; CL-20, CL-21, CL-51
  - Depende de: T-44
  - Archivos: `dance_school/application/billing.py`, `tests/application/test_generate_fees.py`
  - Hacer: `generate_month_fees()` con `INSERT … ON CONFLICT DO NOTHING RETURNING` (D-30).
  - Test: [M-9] con el número creado; segunda vez → [M-10] (CL-20); matrícula cerrada el día 1 → sin cuota (CL-21); dos hilos a la vez → cada cuota una vez y la suma de los [M-9] igual al total (CL-51).
  - Hecho cuando: los tests pasan.

- [ ] **T-46 · Cargos manuales y anulación** — RF-11.7, RF-11.11, RF-11.12, RF-11.13; CL-26
  - Depende de: T-19, T-45
  - Archivos: `dance_school/application/billing.py`, `tests/application/test_charges.py`
  - Hacer: `create_manual_charge()` y `void_charge()`.
  - Test: [M-12]; alumno anonimizado → E-37; [M-13] y el cargo deja de contar; con pagos → E-26 (CL-26); ya anulado → E-38.
  - Hecho cuando: los tests pasan.

- [ ] **T-47 · Pagos** — RF-12.1, RF-12.6, RF-12.7, RNF-9; CL-27, CL-47, CL-50
  - Depende de: T-20, T-46
  - Archivos: `dance_school/application/payments.py`, `tests/application/test_payments.py`
  - Hacer: `register_payment()` y `void_payment()`.
  - Test: [M-14] con la deuda restante; [M-15]; anulación repartida (CL-27); fecha anterior a la emisión → se aplica igual (CL-47); dos hermanos con la misma referencia (CL-50); fallo forzado al guardar las aplicaciones → nada cambia (RNF-9).
  - Hecho cuando: los tests pasan.

- [ ] **T-48 · Estado de cuenta y morosos** — RF-13.1, RF-13.4, RF-13.6
  - Depende de: T-21, T-47
  - Archivos: `dance_school/application/statements.py`, `tests/application/test_statements.py`
  - Hacer: `account_statement()` y `delinquents()`.
  - Test: cargos con estado y saldo, pagos con anulados marcados y totales; listado con responsable y teléfono, ordenado por días de atraso; sin morosos → [M-16].
  - Hecho cuando: los tests pasan.

- [ ] **T-49 · Vista del profesor** — RF-14.1, RF-14.2, RF-14.3, RF-14.4, RF-14.5, RF-14.6; CL-36, CL-44
  - Depende de: T-33, T-41, T-44
  - Archivos: `dance_school/application/teaching.py`, `tests/application/test_teaching.py`
  - Hacer: grupos del profesor, alumnos con contactos, señal de salud y revelado auditado.
  - Test: solo sus grupos sin archivar; sin grupos → [M-29]; la lista señala a quien tiene salud sin el contenido y al pedirla se audita (CL-36); una cuenta de Dirección profesora ve sus grupos en el inicio (CL-44).
  - Hecho cuando: los tests pasan.

- [ ] **T-50 · Exportación de fichas** — RF-15.1, RF-15.2
  - Depende de: T-38, T-48
  - Archivos: `dance_school/application/rights.py`, `tests/application/test_export.py`
  - Hacer: `export_student()` y `export_contact()` devuelven la estructura con secciones fijas; auditado.
  - Test: cada dato guardado del alumno (o del contacto) aparece en su sección con su etiqueta; [M-21]; la exportación queda en la auditoría.
  - Hecho cuando: los tests pasan.

- [ ] **T-51 · Supresión a petición** — RF-15.3, RF-15.4, RF-15.5, RF-15.6, RF-15.7, RF-15.8, RF-15.9; CL-39
  - Depende de: T-23, T-42, T-50
  - Archivos: `dance_school/application/rights.py`, `tests/application/test_erasure.py`
  - Hacer: suprimir alumno (anonimización inmediata) y contacto.
  - Test: [M-19] y [M-20]; alumno activo → E-28, con deuda → E-27 (CL-39); contacto único tutor → E-9; contacto responsable → E-40; [M-31].
  - Hecho cuando: los tests pasan.

- [ ] **T-52 · Solicitudes de titulares** — RF-15.10, RF-15.11
  - Depende de: T-51
  - Archivos: `dance_school/application/rights.py`, `tests/application/test_requests.py`
  - Hacer: registrar y responder solicitudes.
  - Test: se guardan tipo, titular y fechas; respuesta anterior a la recepción → E-48; fecha futura → E-41; auditado.
  - Hecho cuando: los tests pasan.

- [ ] **T-53 · Revisión diaria** — RF-16.1, RF-16.2, RF-16.3, RF-16.4, RF-16.5, RF-16.6, RF-16.7, RF-16.8, RF-16.9; CL-13, CL-37, CL-38
  - Depende de: T-22, T-23, T-28, T-52
  - Archivos: `dance_school/application/retention.py`, `dance_school/infrastructure/management/commands/daily_review.py`, `tests/application/test_daily_review.py`
  - Hacer: aplicar `retention_actions()` como «sistema» con el rol de mantenimiento (D-37).
  - Test: con `FixedClock` en el día exacto del plazo se anonimiza (CL-38); con deuda no (CL-37); contactos huérfanos borrados y el del hermano activo conservado (CL-13); ejecutarla dos veces seguidas no cambia nada; tras saltarse días recupera lo pendiente.
  - Hecho cuando: los tests pasan y `python manage.py daily_review` termina sin errores sobre la base de datos de desarrollo.

- [ ] **T-54 · Cobertura y consulta de la auditoría** — RF-17.1, RF-17.3
  - Depende de: T-53
  - Archivos: `dance_school/application/audit_queries.py`, `tests/application/test_audit_coverage.py`
  - Hacer: consulta filtrada por alumno, cuenta o fechas.
  - Test: cada acción de `AuditAction` se produce al menos una vez ejecutando su servicio; filtros y orden de más reciente a más antigua.
  - Hecho cuando: los tests pasan.

- [ ] **T-55 · Inicio** — RF-18.1, RF-18.2, RF-18.3, RF-18.4, RF-18.5
  - Depende de: T-39, T-45, T-48, T-52, T-53
  - Archivos: `dance_school/application/home.py`, `tests/application/test_home.py`
  - Hacer: avisos del inicio según el rol.
  - Test: [M-11] si falta alguna cuota del mes; lista de pendientes de renovar; morosos y deuda vencida total; [M-30] solo a Dirección; [M-36] con días transcurridos solo a Dirección.
  - Hecho cuando: los tests pasan.

---

## Fase 4 — Interfaz web

- [ ] **T-56 · Base de la interfaz y seguridad HTTP** — RF-1.17, RF-3.2, RNF-1, RNF-5, RNF-13
  - Depende de: T-4, T-55
  - Archivos: `dance_school/web/templates/base.html`, `dance_school/web/static/css/app.css`, `dance_school/web/middleware.py`, `config/settings.py`, `tests/web/test_base.py`
  - Hacer: plantilla base con mensajes del catálogo, CSS móvil primero, aviso [M-35] en campos de texto libre, página 403 con [E-1], cabeceras de D-36.
  - Test: respuestas autenticadas con `Cache-Control: no-store`; HTTPS forzado y cookies seguras con la configuración de producción; un campo «concepto» lleva [M-35]; un 403 no contiene datos.
  - Hecho cuando: los tests pasan.

- [ ] **T-57 · Pantallas de acceso y sesión** — RF-2.1, RF-2.5, RF-2.6, RF-2.17, RF-2.24
  - Depende de: T-36, T-56
  - Archivos: `web/views/auth.py`, `web/templates/auth/`, `web/middleware.py`, `tests/web/test_auth_views.py`
  - Hacer: inicio de sesión, activación, configuración y verificación del segundo factor, cierre por inactividad y por `session_epoch`.
  - Test: sin sesión solo se ve el inicio de sesión; tras 30 minutos sin actividad → [M-28]; una sesión de una cuenta desactivada deja de valer en la siguiente petición.
  - Hecho cuando: los tests pasan.

- [ ] **T-58 · Pantallas de cuentas** — RF-2.7 a RF-2.25 (por HTTP)
  - Depende de: T-57
  - Archivos: `web/views/accounts.py`, `web/templates/accounts/`, `tests/web/test_accounts_views.py`
  - Hacer: listado y acciones de Dirección sobre cuentas.
  - Test: cada acción muestra su mensaje; el código de activación solo aparece en la respuesta de creación o restablecimiento.
  - Hecho cuando: los tests pasan.

- [ ] **T-59 · Búsqueda y ficha de alumnos** — RF-7.1, RF-7.2, RF-7.3, RF-7.4, RF-7.5
  - Depende de: T-56
  - Archivos: `web/views/students.py`, `web/templates/students/`, `tests/web/test_student_views.py`
  - Hacer: búsqueda por `POST` con redirección (D-35), ficha y botón «Ver observaciones de salud» solo para Dirección.
  - Test: el texto buscado nunca aparece en ninguna URL; la ficha no contiene el texto de salud; Dirección lo ve tras pulsar el botón.
  - Hecho cuando: los tests pasan.

- [ ] **T-60 · Alta y edición de alumnos, contactos y autorizaciones** — RF-4.1, RF-5.6, RF-6.10, RF-7.6, RF-7.11
  - Depende de: T-59
  - Archivos: `web/views/students.py`, `web/views/contacts.py`, `web/forms.py`, `web/templates/students/`, `tests/web/test_student_forms.py`
  - Hacer: formularios con versión oculta, flujo de [M-18], registro y revocación de autorizaciones, sustitución de salud para Recepción.
  - Test: alta completa de un menor con dos tutores; errores de campo con su E-x junto al campo; [M-18] ofrece vincular el existente; Recepción no recibe el texto de salud en el formulario.
  - Hecho cuando: los tests pasan.

- [ ] **T-61 · Baja, reactivación y supresión** — RF-8.1, RF-8.6, RF-15.3, RF-15.7
  - Depende de: T-60
  - Archivos: `web/views/students.py`, `web/views/rights.py`, `web/templates/`, `tests/web/test_leave_views.py`
  - Hacer: confirmaciones [M-3] y [M-19] y pantallas de reactivación.
  - Test: la baja solo se aplica tras confirmar; la supresión exige confirmar y muestra [M-20].
  - Hecho cuando: los tests pasan.

- [ ] **T-62 · Grupos y matrículas** — RF-9.1, RF-9.14, RF-10.1, RF-10.2, RF-10.7
  - Depende de: T-56
  - Archivos: `web/views/groups.py`, `web/views/enrollments.py`, `web/templates/groups/`, `tests/web/test_group_views.py`
  - Hacer: formulario de grupo con franjas, listado con plazas libres, matricular con confirmación [M-7] y finalizar.
  - Test: crear un grupo con dos franjas; matricular a un moroso exige confirmar; finalizar muestra [M-8].
  - Hecho cuando: los tests pasan.

- [ ] **T-63 · Cuotas, cargos, pagos y morosos** — RF-11.2, RF-11.7, RF-11.11, RF-12.1, RF-12.6, RF-13.1, RF-13.4
  - Depende de: T-62
  - Archivos: `web/views/billing.py`, `web/templates/billing/`, `tests/web/test_billing_views.py`
  - Hacer: generar cuotas, cargo manual, anulaciones con motivo, registrar pago, estado de cuenta y listado de morosos.
  - Test: importes y fechas con el formato de RNF-1; los botones de anular solo aparecen a Dirección; [M-14] muestra la deuda restante.
  - Hecho cuando: los tests pasan.

- [ ] **T-64 · Vista del profesor** — RF-14.1, RF-14.3, RF-14.4, RF-14.5
  - Depende de: T-56
  - Archivos: `web/views/teaching.py`, `web/templates/teaching/`, `tests/web/test_teaching_views.py`
  - Hacer: pantallas pensadas para 360 px.
  - Test: el profesor ve solo sus grupos; el teléfono es un enlace de llamada; la salud se pide alumno por alumno.
  - Hecho cuando: los tests pasan.

- [ ] **T-65 · Exportación, solicitudes, auditoría e inicio** — RF-15.1, RF-15.2, RF-15.10, RF-17.3, RF-18.1, RF-18.5
  - Depende de: T-61, T-63
  - Archivos: `web/views/rights.py`, `web/views/audit.py`, `web/views/home.py`, `web/templates/`, `web/static/css/print.css`, `tests/web/test_rights_home_views.py`
  - Hacer: página de exportación con estilos de impresión (D-34), registro de solicitudes, consulta de auditoría e inicio por rol.
  - Test: la exportación lleva las secciones fijas y [M-21]; el inicio de Recepción no muestra [M-30] ni [M-36].
  - Hecho cuando: los tests pasan.

- [ ] **T-66 · Permisos por HTTP** — RF-3.1, RF-3.2, RF-3.3; CL-35
  - Depende de: T-58, T-65
  - Archivos: `tests/web/test_permissions_http.py`
  - Hacer: test parametrizado: cada fila de la matriz × cada rol contra su URL, incluidas las peticiones directas a acciones que la interfaz no ofrece.
  - Test: «Sí» → 200 o redirección; «No» → 403 con [E-1] y sin datos; profesor contra la ficha de un alumno ajeno → 403 (CL-35).
  - Hecho cuando: las 66 combinaciones se comportan como la matriz (criterio de finalización 2).

---

## Fase 5 — Verificación y despliegue

- [ ] **T-67 · Trazabilidad estricta** — principios 2 y 4; criterio de finalización 1
  - Depende de: T-66
  - Archivos: `tests/architecture/test_traceability.py`
  - Hacer: leer la spec, extraer todos los RF-x.y y CL-x y buscarlos en los nombres y marcas de los tests.
  - Test: el propio archivo.
  - Hecho cuando: ningún RF ni CL queda sin test.

- [ ] **T-68 · Registros sin datos personales** — RNF-6
  - Depende de: T-66
  - Archivos: `tests/application/test_logs_privacy.py`
  - Hacer: recorrer alta, edición, pago, baja, error forzado y búsqueda capturando todos los registros.
  - Test: ningún nombre, teléfono, correo, fecha de nacimiento ni texto de salud de las factorías aparece en los registros.
  - Hecho cuando: el test pasa.

- [ ] **T-69 · Pantallas y accesibilidad** — RNF-4, RNF-12
  - Depende de: T-66
  - Archivos: `tests/ui/test_layout.py`, `tests/ui/test_accessibility.py`, `tests/fixtures/axe.min.js`
  - Hacer: Playwright a 1280 px (Dirección y Recepción) y 360 px (profesor); recorrido con teclado de los formularios; axe-core.
  - Test: `pytest -q -m ui`.
  - Hecho cuando: sin desplazamiento horizontal a 360 px en las pantallas del profesor, formularios completables con teclado y cero errores de nivel A.

- [ ] **T-70 · Carga y rapidez** — RNF-2, RNF-3; R-5
  - Depende de: T-66
  - Archivos: `tests/perf/load.py`, `docs/verification/performance.md`
  - Hacer: generar el volumen de RNF-2 con datos ficticios y lanzar 10 hilos con la mezcla de RNF-3 contra el entorno de pruebas.
  - Test: `python tests/perf/load.py` registra los percentiles.
  - Hecho cuando: p95 < 1 s, máximo < 3 s y generar cuotas < 10 s, registrados con fecha.

- [ ] **T-71 · Imagen y despliegue** — RNF-5, RNF-8; D-23, R-7, R-8
  - Depende de: T-67, T-68
  - Archivos: `Dockerfile`, `docs/deploy.md`
  - Hacer: imagen con gunicorn; Cloud Run (mínimo 1 y máximo 2 instancias); Cloud SQL con copias diarias, 30 días de retención y cifrado en reposo; Secret Manager; job de migraciones con `app_owner`; alertas de presupuesto. Requiere resolver antes el aviso A-2 (región).
  - Test: despliegue en un entorno de prueba con datos ficticios; `curl -I` muestra HTTPS y HSTS.
  - Hecho cuando: la app responde por HTTPS en el entorno de prueba y la configuración de copias muestra 30 días.

- [ ] **T-72 · Revisión diaria programada y monitorización** — RF-16.1, RNF-10; R-6
  - Depende de: T-71
  - Archivos: `docs/deploy.md`
  - Hacer: Cloud Run Job `daily_review` a las 02:00 de Bogotá con `app_maint`; alerta si falla; comprobación de disponibilidad cada 5 minutos.
  - Test: ejecución manual del job en el entorno de prueba y alerta de prueba recibida.
  - Hecho cuando: el job queda programado, ha corrido una vez sin errores y la comprobación de disponibilidad está activa.

- [ ] **T-73 · Restauración y revisiones registradas** — RNF-7, RNF-8, RNF-13
  - Depende de: T-72
  - Archivos: `docs/verification/restore.md`, `docs/verification/reviews.md`
  - Hacer: restaurar una copia en una instancia aparte, ejecutar la revisión de plazos y medir la duración; revisar fixtures (RNF-7) y la caché en teléfono y ordenador (RNF-13).
  - Test: procedimiento seguido paso a paso.
  - Hecho cuando: la restauración tarda menos de 4 horas y queda registrada con fecha; las revisiones de RNF-7 y RNF-13 quedan registradas sin incidencias.

---

## Cobertura

| Elemento | Tareas |
|----------|--------|
| RF-1 | T-2, T-5–T-9, T-29, T-31, T-56 |
| RF-2 | T-11, T-32, T-34–T-36, T-57, T-58 |
| RF-3 | T-10, T-33, T-56, T-66 |
| RF-4 | T-9, T-12, T-37, T-60 |
| RF-5 | T-13, T-38, T-60 |
| RF-6 | T-14, T-37, T-39, T-60 |
| RF-7 | T-15, T-40, T-41, T-59, T-60 |
| RF-8 | T-15, T-42, T-61 |
| RF-9 | T-16, T-43, T-62 |
| RF-10 | T-17, T-44, T-62 |
| RF-11 | T-18, T-19, T-44–T-46, T-63 |
| RF-12 | T-20, T-47, T-63 |
| RF-13 | T-21, T-48, T-63 |
| RF-14 | T-49, T-64 |
| RF-15 | T-50–T-52, T-61, T-65 |
| RF-16 | T-22, T-23, T-40, T-53, T-72 |
| RF-17 | T-24, T-27, T-28, T-30, T-54, T-65 |
| RF-18 | T-55, T-65 |
| RNF-1…RNF-13 | T-4, T-8 (1); T-70 (2, 3); T-69 (4, 12); T-56, T-71 (5); T-68 (6); T-73 (7, 13); T-71, T-73 (8); T-30, T-42, T-47 (9); T-72 (10); T-2, T-3 (11) |

Los 57 casos límite están asignados en las cabeceras de las tareas; la
comprobación automática es T-67.
