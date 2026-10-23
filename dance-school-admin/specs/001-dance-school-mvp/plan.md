# Plan 001 — MVP de la app administrativa de la escuela de danza

- **Estado:** aprobado (2026-10-23)
- **Fecha:** 2026-10-23
- **Origen:** [spec 001, versión 3](spec.md) y [constitución](../../docs/constitution.md)

El usuario pidió hacer las fases 5 y 6 sin detenerse a pedir aprobación; rige
la regla «usa tus recomendaciones». Este plan ya incorpora su autorrevisión
(sección 12). Los avisos que requieren una decisión del usuario están en la
sección 13.

## 1. Decisiones de la fase 5 (D-21…D-25)

### D-21. ¿Qué tipo de aplicación y qué stack?

- (a) **(Recomendada)** Aplicación web monolítica con páginas generadas en el servidor: Python 3.12 y Django 5.2 LTS, sin framework de JavaScript.
- (b) API en Python (FastAPI) y una aplicación de página única en React.
- (c) Next.js (TypeScript) para todo.
- **Decisión:** (a).
- **Motivo:** un solo lenguaje y un solo artefacto desplegable (principio 1); Django ya trae sesiones, hash de contraseñas, protección CSRF, migraciones y plantillas, así que evita varias dependencias; Python es el lenguaje que el equipo ya usa en `habits-cli`. Django 5.2 tiene soporte hasta abril de 2028.

### D-22. ¿Qué base de datos?

- (a) **(Recomendada)** PostgreSQL 16 gestionado por el proveedor.
- (b) SQLite en el mismo servidor.
- **Decisión:** (a).
- **Motivo:** 10 personas a la vez (RNF-2) y la última plaza disputada (CL-31) necesitan bloqueos de fila fiables; el servicio gestionado da cifrado en reposo (D-3) y copias con 30 días de retención (D-5) sin código propio.

### D-23. ¿Dónde se despliega?

- (a) **(Recomendada)** Google Cloud: Cloud Run (contenedor) + Cloud SQL para PostgreSQL + Cloud Scheduler + Secret Manager, en una región de un país con nivel adecuado de protección según la SIC.
- (b) Un servidor virtual propio con PostgreSQL instalado.
- (c) Un PaaS sencillo (Render, Railway) con PostgreSQL incluido.
- **Decisión:** (a).
- **Motivo:** HTTPS gestionado, cifrado en reposo por defecto y copias automáticas con retención configurable (30 días) cubren D-3 y D-5 sin administración de servidores; Cloud Run Jobs ejecuta la revisión diaria (RF-16.1). (b) exige administrar sistema operativo, copias y certificados; (c) no permite en todos los planes 30 días de copias. La región y la transferencia internacional de datos (Ley 1581, art. 26) deben validarse con quien lleve la protección de datos (sección 13, A-2).

### D-24. ¿Cómo se autentica el personal?

- (a) **(Recomendada)** Autenticación propia de Django (sesiones en servidor, contraseñas con PBKDF2) y segundo factor TOTP (RFC 6238) implementado con la biblioteca estándar, introduciendo la clave a mano en la app autenticadora.
- (b) Paquetes externos de segundo factor (django-otp, django-two-factor-auth).
- (c) Proveedor de identidad externo (Auth0, Google).
- **Decisión:** (a).
- **Motivo:** TOTP son unas 30 líneas con `hmac` y `hashlib`, comprobables con los vectores de la RFC; evita dependencias (principio 1) y no envía datos del personal a terceros. Sin código QR para no añadir una librería.

### D-25. ¿Con qué se escriben los tests?

- (a) **(Recomendada)** pytest + pytest-django para unidad e integración, y Playwright solo para RNF-4 y RNF-12.
- (b) El ejecutor de tests de Django (unittest), sin dependencias.
- **Decisión:** (a).
- **Motivo:** pytest es lo que el equipo ya usa en `habits-cli` y sus fixtures fijan la fecha con poco código (RNF-11); la spec exige probar las pantallas en dos anchos y con teclado (RNF-4, RNF-12), lo que requiere un navegador automatizado. Todas son dependencias de desarrollo.

## 2. Stack y dependencias

| Dependencia | Versión | Uso | Motivo (principio 1) |
|-------------|---------|-----|----------------------|
| Python | 3.12+ | Lenguaje único | D-21 |
| Django | 5.2 LTS | Web, ORM, migraciones, sesiones, hash, CSRF, plantillas | D-21 |
| psycopg | 3.x | Driver de PostgreSQL | Obligatorio para usar PostgreSQL desde Django |
| gunicorn | 23.x | Servidor WSGI de producción | Django no incluye un servidor apto para producción |
| whitenoise | 6.x | Servir el CSS desde la propia app | Evita un servidor web o un CDN aparte |
| pytest, pytest-django | 8.x, 4.x | Tests (solo desarrollo) | D-25 |
| playwright | 1.x | RNF-4 y RNF-12 (solo desarrollo) | D-25 |
| axe-core | 4.x, archivo JS copiado en `tests/` | Revisión automática de accesibilidad (solo desarrollo) | RNF-12 |

Fuera de Python: PostgreSQL 16, Docker (imagen de despliegue y base de datos
local), Cloud Run, Cloud SQL, Cloud Scheduler, Secret Manager y Cloud
Monitoring (comprobación de disponibilidad, RNF-10). No se usan servicios de
terceros de seguimiento de errores ni de analítica (sección 12, H-53).

## 3. Arquitectura por capas

```text
            web (Django: vistas, formularios, plantillas, middleware)
                         │ llama a
                         ▼
            application (casos de uso, transacciones, auditoría)
               │ usa                         │ define puertos
               ▼                             ▼
            domain (reglas puras)     ports: Clock, UnitOfWork, repositorios,
                                             AuditLog, PasswordHasher
                                             ▲ implementa
            infrastructure (Django ORM, PostgreSQL, reloj, TOTP, comandos)
```

| Capa | Contiene | Puede importar | No puede importar |
|------|----------|----------------|-------------------|
| `domain` | Entidades (dataclasses), validaciones, reglas de edad, cuotas, aplicación de pagos, morosidad, conservación, matriz de permisos, formatos | Biblioteca estándar (sin `datetime.now`, `date.today`, E/S) | Django, psycopg, `application`, `infrastructure`, `web` |
| `application` | Un servicio por caso de uso; comprueba permisos, lee «hoy» una vez del `Clock`, llama al dominio, persiste y audita dentro de una `UnitOfWork` | `domain`, `ports`, biblioteca estándar | Django, psycopg, `infrastructure`, `web` |
| `infrastructure` | Modelos y migraciones, repositorios, `UnitOfWork` con `transaction.atomic`, reloj de Bogotá, TOTP, comando de revisión diaria | Todo lo anterior y Django | `web` |
| `web` | URLs, vistas, formularios, plantillas, CSS, middleware de sesión y caché | `application`, `messages`, Django | `infrastructure` (salvo el arranque en `config/`) |

`messages.py` (catálogo M-x / E-x) no depende de nada y lo usan `application`
y `web`. Los servicios devuelven resultados o lanzan `DomainError(code, params)`
con el identificador del mensaje; solo `web` convierte el código en texto.

Flujo de una operación (por ejemplo, registrar un pago):

1. La vista valida el formulario y llama a `PaymentService.register(actor, data)`.
2. El servicio lee `today = clock.today()` una sola vez (RF-1.1) y comprueba el permiso (RF-3.3).
3. Dentro de `with uow:` carga los cargos del alumno, llama a `domain.payments.allocate(...)`, guarda el pago, las aplicaciones y la entrada de auditoría.
4. Si algo falla, `uow` deshace todo (RNF-9, RF-17.5) y la vista muestra [E-36].

## 4. Modelo de datos

PostgreSQL 16. Todas las tablas tienen `id bigint` generado. Los nombres de
tabla se fijan con `db_table` para no depender del nombre de la app. «FK» es
clave foránea; «R» es `ON DELETE RESTRICT` salvo que se indique otra cosa.
Los textos ya llegan normalizados (RF-1.2) desde el dominio.

### 4.1 `account` (modelo de usuario propio sobre `AbstractBaseUser`)

| Columna | Tipo | Restricciones | Requisito |
|---------|------|---------------|-----------|
| `name` | varchar(60) | not null | RF-2.7 |
| `email` | varchar(254) | not null, único, `CHECK (email = lower(email))` | RF-1.16, RF-2.8 |
| `password` | varchar(128) | hash de Django; vacío hasta activar | RF-2.17, RNF-5 |
| `role` | varchar(12) | `CHECK (role IN ('direction','reception','teacher'))` | RF-2.14 |
| `is_active` | boolean | not null | RF-2.9 |
| `deactivated_at` | timestamptz | null | RF-16.8 |
| `failed_attempts` | smallint | not null default 0 | RF-2.4, RF-2.20 |
| `locked_until` | timestamptz | null | RF-2.4 |
| `activation_code_hash` | varchar(128) | null | RF-2.16 |
| `activation_expires_at` | timestamptz | null | RF-2.16, RF-2.18 |
| `totp_secret` | varchar(32) | null (base32) | RF-2.22 |
| `totp_last_step` | bigint | null (evita reutilizar un código) | RF-2.23 |
| `session_epoch` | integer | not null default 0 | RF-2.9, RF-2.25 |
| `anonymized` | boolean | not null default false | RF-16.8 |
| `version` | integer | not null default 0 | RF-1.15 |

### 4.2 `student`

| Columna | Tipo | Restricciones | Requisito |
|---------|------|---------------|-----------|
| `first_name`, `last_name` | varchar(60) | null solo si `anonymized` | RF-4.2 |
| `name_key` | varchar(121) | clave de comparación (RF-1.6); null si anonimizado | RF-4.4 |
| `birth_date` | date | null solo si `anonymized` | RF-1.12 |
| `phone` | char(10) | null | RF-4.8 |
| `email` | varchar(254) | null, en minúsculas | RF-1.16 |
| `health_notes` | varchar(500) | null | RF-6.5 |
| `status` | varchar(8) | `CHECK (status IN ('active','inactive'))` | RF-8.2 |
| `left_on` | date | `CHECK ((status = 'inactive') = (left_on IS NOT NULL))` | RF-8.2, RF-16.2 |
| `payer_contact_id` | FK `contact` R, null | null significa «el propio alumno» | RF-4.6, RF-4.7 |
| `anonymized` | boolean | not null default false | RF-16.3 |
| `alias_number` | integer | único, null; secuencia propia | RF-16.3 |
| `version` | integer | not null default 0 | RF-1.15 |

Índice único parcial `(name_key, birth_date) WHERE NOT anonymized` (RF-4.4) y
`CHECK (anonymized OR (first_name IS NOT NULL AND last_name IS NOT NULL AND birth_date IS NOT NULL))`.

### 4.3 `contact` y `student_contact`

| Tabla | Columna | Tipo | Restricciones | Requisito |
|-------|---------|------|---------------|-----------|
| `contact` | `first_name`, `last_name` | varchar(60) | not null | RF-5.2 |
| `contact` | `name_key` | varchar(121) | not null, índice | RF-5.7 |
| `contact` | `phone` | char(10) | not null, índice | RF-5.6, RF-5.7 |
| `contact` | `email` | varchar(254) | null | RF-5.2 |
| `contact` | `version` | integer | not null default 0 | RF-1.15 |
| `student_contact` | `student_id` | FK `student` CASCADE | not null | RF-5.1 |
| `student_contact` | `contact_id` | FK `contact` R | not null | RF-5.1 |
| `student_contact` | `relationship` | varchar(30) | not null | RF-5.2 |

Único `(student_id, contact_id)`. El máximo de 2 contactos (RF-5.5) lo
comprueba el dominio con la fila del alumno bloqueada (`SELECT … FOR UPDATE`).

### 4.4 `consent` (autorización de tratamiento)

| Columna | Tipo | Restricciones | Requisito |
|---------|------|---------------|-----------|
| `student_id` | FK `student` CASCADE | not null | RF-6.1 |
| `signed_on` | date | not null | RF-6.1, RF-1.14 |
| `grantor_name` | varchar(121) | not null (copia del nombre) | RF-6.1, H-21 |
| `grantor_relationship` | varchar(30) | not null («alumno» si lo otorga él mismo) | RF-6.1 |
| `granted_by_student` | boolean | not null | RF-6.3, RF-6.7 |
| `includes_health` | boolean | not null | RF-6.5 |
| `health_revoked_on` | date | null | RF-6.10 |
| `minor_opinion_considered` | boolean | null; `true` exigido por el dominio en menores de 12 años o más | RF-6.11 |
| `recorded_at` | timestamptz | not null | RF-6.4 |

La autorización vigente es la de `recorded_at` más reciente (RF-6.4). La tabla
se llama `consent` porque `authorization` es palabra reservada de PostgreSQL.

### 4.5 `dance_group` y `time_slot`

| Tabla | Columna | Tipo | Restricciones | Requisito |
|-------|---------|------|---------------|-----------|
| `dance_group` | `name` | varchar(60) | not null | RF-9.2 |
| `dance_group` | `name_key` | varchar(60) | índice único parcial `WHERE NOT archived` | RF-9.3, RF-9.13 |
| `dance_group` | `style` | varchar(40) | not null | RF-9.2 |
| `dance_group` | `teacher_id` | FK `account` R | not null | RF-9.2, RF-9.7 |
| `dance_group` | `capacity` | smallint | `CHECK (capacity BETWEEN 1 AND 100)` | RF-9.6 |
| `dance_group` | `monthly_fee` | integer | `CHECK (monthly_fee BETWEEN 1 AND 10000000)` | RF-1.11 |
| `dance_group` | `archived` | boolean | not null default false | RF-9.10 |
| `dance_group` | `version` | integer | not null default 0 | RF-1.15 |
| `time_slot` | `group_id` | FK `dance_group` CASCADE | not null | RF-9.2 |
| `time_slot` | `weekday` | smallint | `CHECK (weekday BETWEEN 0 AND 6)` (0 = lunes) | RF-9.2 |
| `time_slot` | `starts_at`, `ends_at` | time | `CHECK (ends_at > starts_at)` | RF-9.5 |

El solape de franjas (RF-9.15) y su número (RF-9.4) los valida el dominio.

### 4.6 `enrollment`

| Columna | Tipo | Restricciones | Requisito |
|---------|------|---------------|-----------|
| `student_id` | FK `student` R | not null | RF-10.1 |
| `group_id` | FK `dance_group` R | not null | RF-10.1 |
| `started_on` | date | not null | RF-10.1 |
| `ended_on` | date | null, `CHECK (ended_on >= started_on)` | RF-10.7 |

Como la baja siempre se fecha hoy y no hay fechas futuras, «activa hoy»
equivale a `ended_on IS NULL` (RF-10.8). Índice único parcial
`(student_id, group_id) WHERE ended_on IS NULL` (RF-10.3).

### 4.7 `charge`, `payment` y `payment_allocation`

| Tabla | Columna | Tipo | Restricciones | Requisito |
|-------|---------|------|---------------|-----------|
| `charge` | `student_id` | FK `student` R | not null | RF-11.7 |
| `charge` | `kind` | varchar(12) | `CHECK (kind IN ('monthly_fee','manual'))` | RF-11.6 |
| `charge` | `enrollment_id` | FK `enrollment` SET NULL | null | RF-10.10 |
| `charge` | `group_id` | FK `dance_group` R | not null si `monthly_fee` | RF-11.1 |
| `charge` | `period` | date (día 1 del mes) | not null si `monthly_fee` | RF-11.1 |
| `charge` | `concept` | varchar(100) | not null | RF-11.6, RF-16.9 |
| `charge` | `amount` | integer | `CHECK (amount BETWEEN 1 AND 10000000)` | RF-1.11 |
| `charge` | `issued_on` | date | not null | RF-11.6, RF-11.8 |
| `charge` | `created_at` | timestamptz | not null (desempate de RF-12.2) | RF-12.2 |
| `charge` | `voided_at` | timestamptz | null | RF-11.11 |
| `charge` | `voided_by_id` | FK `account` R | null (null con `voided_at` = «sistema») | RF-10.10, RF-11.11 |
| `charge` | `void_reason` | varchar(200) | null | RF-11.11, RF-16.9 |
| `payment` | `student_id` | FK `student` R | not null | RF-12.1 |
| `payment` | `amount` | integer | `CHECK (amount BETWEEN 1 AND 10000000)` | RF-12.1 |
| `payment` | `paid_on` | date | not null | RF-12.5, RF-12.7 |
| `payment` | `method` | varchar(8) | `CHECK (method IN ('cash','transfer','card','other'))` | RF-12.1 |
| `payment` | `reference` | varchar(50) | null | RF-12.1, RF-16.9 |
| `payment` | `recorded_at`, `recorded_by_id` | timestamptz, FK `account` R | not null | RF-12.7, RF-17.1 |
| `payment` | `voided_at`, `voided_by_id`, `void_reason` | como en `charge` | null | RF-12.6 |
| `payment_allocation` | `payment_id` | FK `payment` CASCADE | not null | RF-12.2 |
| `payment_allocation` | `charge_id` | FK `charge` R | not null | RF-12.2 |
| `payment_allocation` | `amount` | integer | `CHECK (amount > 0)` | RF-12.2 |

Índice único parcial `charge (student_id, group_id, period) WHERE kind = 'monthly_fee' AND voided_at IS NULL`
(RF-11.1, CL-48, CL-51). Una aplicación de un pago anulado no cuenta en el saldo
(RF-11.9); no se borra para conservar el histórico.

### 4.8 `data_request` (solicitudes de titulares)

| Columna | Tipo | Restricciones | Requisito |
|---------|------|---------------|-----------|
| `student_id` | FK `student` CASCADE | null | RF-15.10 |
| `contact_id` | FK `contact` CASCADE | null; `CHECK ((student_id IS NULL) <> (contact_id IS NULL))` | RF-15.10 |
| `kind` | varchar(14) | `CHECK (kind IN ('access','rectification','erasure','revocation'))` | RF-15.10 |
| `received_on` | date | not null | RF-15.10, RF-1.14 |
| `answered_on` | date | null, `CHECK (answered_on >= received_on)` | RF-15.11 |

### 4.9 `audit_entry`

| Columna | Tipo | Restricciones | Requisito |
|---------|------|---------------|-----------|
| `occurred_at` | timestamptz | not null, índice | RF-17.2, RF-17.3 |
| `actor_id` | FK `account` R | null = «sistema», índice | RF-17.2 |
| `action` | varchar(40) | not null (catálogo cerrado en `domain/audit.py`) | RF-17.1 |
| `entity_type` | varchar(20) | not null | RF-17.2 |
| `entity_id` | bigint | not null; índice `(entity_type, entity_id)` | RF-17.3 |

Sin columnas de valores (RF-17.2). Permisos de base de datos (sección 7.1):
el rol de la app solo puede `INSERT` y `SELECT`; el rol de mantenimiento,
además, `DELETE` (RF-16.7, RF-17.4).

### 4.10 Tablas de Django

`django_session` (sesiones en base de datos; solo guardan el id de la cuenta,
su `session_epoch` y la hora de la última actividad), `django_migrations` y
`django_content_type` (requerida por `django.contrib.auth`). No se instala
`django.contrib.admin` (sección 12, H-51).

## 5. Estructura de carpetas

```text
dance-school-admin/
├── AGENTS.md
├── pyproject.toml            # dependencias y configuración de pytest
├── manage.py
├── Dockerfile
├── docker-compose.yml        # PostgreSQL local para desarrollo y tests
├── config/                   # settings.py, urls.py, wsgi.py
├── dance_school/
│   ├── messages.py           # catálogo M-x / E-x (sección 6 de la spec)
│   ├── domain/
│   │   ├── errors.py         # DomainError(code, params)
│   │   ├── text.py           # normalización y clave de comparación (RF-1.2–RF-1.6)
│   │   ├── contact_info.py   # teléfono y correo (RF-1.7–RF-1.9, RF-1.16)
│   │   ├── formatting.py     # importes, fechas, teléfonos, meses (RNF-1)
│   │   ├── people.py         # edad y minoría de edad (RF-1.12, RF-1.13)
│   │   ├── accounts.py       # roles, bloqueo por intentos (RF-2.4, RF-2.20)
│   │   ├── permissions.py    # matriz de permisos (sección 5 de la spec)
│   │   ├── students.py       # alta, edición, baja, reactivación (RF-4, RF-7, RF-8)
│   │   ├── contacts.py       # contactos y vínculos (RF-5)
│   │   ├── consent.py        # autorizaciones y salud (RF-6)
│   │   ├── groups.py         # grupos y franjas (RF-9)
│   │   ├── enrollments.py    # matrículas (RF-10)
│   │   ├── billing.py        # cuotas, cargos, saldo y estado (RF-11)
│   │   ├── payments.py       # validación y aplicación de pagos (RF-12)
│   │   ├── delinquency.py    # deuda y morosidad (RF-13)
│   │   ├── retention.py      # plazos y anonimización (RF-16)
│   │   └── audit.py          # catálogo de acciones auditables (RF-17.1)
│   ├── application/
│   │   ├── ports.py          # Clock, UnitOfWork, repositorios, AuditLog, PasswordHasher, Totp
│   │   ├── authorization.py  # comprobación de permisos y alcance del profesor (RF-3)
│   │   ├── accounts.py  students.py  contacts.py  consent.py  groups.py
│   │   ├── enrollments.py  billing.py  payments.py  statements.py
│   │   ├── teaching.py  rights.py  retention.py  audit_queries.py  home.py
│   ├── infrastructure/
│   │   ├── models.py  migrations/  repositories.py  unit_of_work.py
│   │   ├── clock.py          # BogotaClock (zoneinfo America/Bogota)
│   │   ├── totp.py           # RFC 6238 con hmac/hashlib
│   │   ├── auth_backend.py   # acceso por correo, bloqueo, segundo factor
│   │   └── management/commands/daily_review.py
│   └── web/
│       ├── urls.py  forms.py  middleware.py  views/  templates/  static/css/
└── tests/
    ├── conftest.py           # FixedClock, today, factorías, cuentas por rol
    ├── fixtures/             # datos ficticios y axe.min.js
    ├── domain/  application/  web/  ui/  perf/
    └── architecture/         # capas, trazabilidad, catálogo de mensajes
```

## 6. Cómo se implementan los permisos

1. **Matriz única:** `domain/permissions.py` define `Action` (una por fila de la matriz de la spec) y `PERMISSIONS: dict[Action, frozenset[Role]]`. Es la única fuente de verdad.
2. **Comprobación en cada servicio (RF-3.3):** todo método público de `application` empieza con `authorize(actor, Action.X)`; si falla, lanza `DomainError("E-1")` antes de leer ningún dato (RF-3.2). Las vistas no deciden permisos: solo ocultan los botones que el rol no puede usar, consultando la misma matriz.
3. **Alcance del profesor (RF-3.4):** `authorization.teacher_scope(actor)` devuelve los ids de sus grupos no archivados; los servicios de RF-14 filtran por esos ids y, si se pide un alumno o grupo fuera del alcance, responden [E-1] (CL-35).
4. **Observaciones de salud:** solo `students.reveal_health_notes()` devuelve su texto, y escribe la entrada de auditoría en la misma transacción (RF-7.5, RF-14.5, RF-17.1). Las fichas y listas nunca lo incluyen; Recepción solo tiene `replace_health_notes()` (RF-7.11).
5. **Acciones del «sistema»:** la anulación de RF-10.10 y la revisión diaria se ejecutan con `actor=SYSTEM`, que no pasa por la matriz y se audita con `actor_id = NULL`.
6. **Respuesta HTTP:** [E-1] se muestra con estado 403 y una página sin datos.
7. **Pruebas:** un test parametrizado recorre cada fila de la matriz × cada rol, a nivel de servicio y por HTTP, y comprueba «permitido» o [E-1] sin datos (sección 11 de la spec, criterio 2).

## 7. Decisiones técnicas de implementación (D-26…D-37)

| Id | Decisión | Motivo | Requisitos |
|----|----------|--------|------------|
| D-26 | «Hoy» y «ahora» vienen de un puerto `Clock`; `BogotaClock` usa `zoneinfo("America/Bogota")`; el servicio lo lee una vez al empezar. `TIME_ZONE = "America/Bogota"`, `USE_TZ = True`. | El dominio no toca el reloj (principio 3) y los tests fijan la fecha (RNF-11). | RF-1.1 |
| D-27 | Clave de comparación: NFC → `casefold` → NFD → quitar marcas combinantes salvo la tilde de la «ñ» → NFC. | Cumple RF-1.6 sin dependencias. | RF-1.6 |
| D-28 | Bloqueo optimista: columna `version`; el formulario la reenvía y el `UPDATE … WHERE version = ?` que no afecta a ninguna fila produce [E-35]. | Detecta ediciones simultáneas sin bloquear la pantalla. | RF-1.15, CL-41 |
| D-29 | Plazas y contactos: `SELECT … FOR UPDATE` de la fila del grupo (o del alumno) antes de contar e insertar. | Solo una matrícula gana la última plaza. | RF-10.9, RF-5.5, CL-31 |
| D-30 | Cuotas: `INSERT … ON CONFLICT DO NOTHING RETURNING id` sobre el índice único parcial; [M-9] cuenta las filas devueltas. | Evita duplicados y da la cifra exacta de cada operación. | RF-11.1, RF-11.2, CL-51 |
| D-31 | Toda operación con auditoría corre en una sola `transaction.atomic`; un fallo al auditar la deshace entera. | Integridad. | RF-17.5, RNF-9, CL-40 |
| D-32 | Sesiones en base de datos; middleware que guarda la última actividad, cierra la sesión a los 30 minutos y compara el `session_epoch` de la sesión con el de la cuenta (desactivar, restablecer o cerrar sesiones lo incrementa). | Cierra todas las sesiones de una cuenta sin recorrer la tabla. | RF-2.5, RF-2.6, RF-2.9, RF-2.25 |
| D-33 | Código de activación de 12 caracteres sin ambigüedades (`secrets`, alfabeto sin 0/O ni 1/I), guardado con hash; TOTP SHA-1, 30 s, 6 dígitos, ventana ±1 y sin reutilizar el último paso. | Se puede dictar en persona; TOTP compatible con las apps comunes. | RF-2.16–RF-2.24 |
| D-34 | Exportación como página HTML con hoja de estilos de impresión; el navegador la imprime o guarda en PDF. | Sin librería de PDF. | RF-15.1, RF-15.2 |
| D-35 | Búsquedas por `POST` con redirección; el texto buscado se guarda en la sesión, nunca en la URL. | Los registros de peticiones del proveedor guardan las URL completas. | RNF-6, H-52 |
| D-36 | Respuestas autenticadas con `Cache-Control: no-store`; sin almacenamiento local ni service workers; HTTPS forzado, HSTS, cookies `Secure`, `HttpOnly` y `SameSite=Lax`. | Nada queda en el dispositivo. | RNF-5, RNF-13 |
| D-37 | Revisión diaria como Cloud Run Job a las 02:00 (hora de Bogotá), con el rol de base de datos de mantenimiento; cada paso se basa en estados, así que repetirla no cambia nada. | Recupera los días perdidos. | RF-16.1–RF-16.8 |

### 7.1 Roles de base de datos

- `app_owner`: dueño del esquema; solo lo usan las migraciones (Cloud Run Job previo a cada despliegue).
- `app_rw`: lo usa la app; todos los permisos sobre las tablas de negocio, pero en `audit_entry` solo `INSERT` y `SELECT`.
- `app_maint`: lo usa la revisión diaria; como `app_rw` más `DELETE` en `audit_entry`.

Las tres credenciales viven en Secret Manager. Una migración crea los permisos y
un test comprueba que `app_rw` no puede modificar ni borrar `audit_entry`.

## 8. Estrategia de tests

### 8.1 Tipos

| Tipo | Qué prueba | Base de datos | Carpeta |
|------|------------|---------------|---------|
| Unidad de dominio | Reglas puras: normalización, edad, cuotas, aplicación de pagos, morosidad, conservación, permisos | No | `tests/domain/` |
| Integración | Servicios de `application` con repositorios reales, transacciones, auditoría, concurrencia | PostgreSQL de prueba | `tests/application/` |
| HTTP | Vistas: formularios, mensajes, códigos de estado, permisos por URL, cabeceras | PostgreSQL de prueba | `tests/web/` |
| Interfaz | Anchos de 360 y 1280 px, teclado y accesibilidad (RNF-4, RNF-12) | PostgreSQL de prueba | `tests/ui/` (marca `ui`) |
| Arquitectura | Capas, catálogo de mensajes, trazabilidad, permisos de base de datos | Según el test | `tests/architecture/` |
| Rendimiento | Carga de RNF-2/RNF-3 (script manual con medición registrada) | Base de datos de rendimiento | `tests/perf/` (marca `perf`) |

`pytest -q` ejecuta todo salvo `ui` y `perf`; `pytest -q -m ui` y el script de
`perf` se ejecutan antes de cada versión.

### 8.2 Fecha fija y datos de prueba

- `FixedClock(today=date(2026, 10, 23), now=...)` se inyecta en los servicios; la fixture `today` y la fixture `clock` permiten moverla en cada test (por ejemplo, al día 15 o 16 para CL-18 y CL-19).
- Ningún test llama al reloj real; el test de arquitectura busca `now(` y `today(` fuera de `infrastructure/clock.py`.
- Factorías escritas a mano en `tests/fixtures/factories.py` con nombres claramente ficticios (por ejemplo, «Alumna Prueba Uno»); teléfonos `300 000 00xx`; correos `@example.invalid`. Nunca datos reales (RNF-7).
- Cada test de integración usa una transacción que se deshace; los de concurrencia (CL-31, CL-51) usan `transaction=True` y dos hilos.

### 8.3 Reglas de nombres y trazabilidad

- Cada test cita en su nombre o en `pytest.mark.req("RF-x.y", "CL-x")` los requisitos que cubre.
- `tests/architecture/test_traceability.py` lee la spec, extrae todos los RF y CL y falla si alguno no aparece en ningún test (principios 2 y 4).
- `tests/architecture/test_messages.py` compara el catálogo `messages.py` con la tabla de la sección 6 de la spec, texto por texto (criterio de finalización 3).

### 8.4 Requisitos no funcionales

| RNF | Cómo se prueba |
|-----|----------------|
| RNF-1 | Unidad: `formatting.py`; arquitectura: catálogo de mensajes |
| RNF-2, RNF-3 | `tests/perf/`: genera el volumen de RNF-2 con factorías y lanza 10 hilos con la mezcla de RNF-3; registra percentiles en `docs/verification/` |
| RNF-4, RNF-12 | Playwright en 360 y 1280 px (sin desplazamiento horizontal), recorrido con teclado y axe-core sin errores de nivel A |
| RNF-5 | HTTP: redirección a HTTPS, cabeceras, cookies; unidad: longitud de contraseña; revisión de la configuración de despliegue |
| RNF-6 | Integración: recorre los flujos principales capturando los registros y busca los valores de las factorías |
| RNF-7 | Revisión registrada de fixtures y del procedimiento de copias |
| RNF-8 | Prueba trimestral de restauración registrada (fecha, duración, revisión de plazos ejecutada) |
| RNF-9 | Integración: fallo forzado a mitad de pago, baja y operación auditada; nada cambia |
| RNF-10 | Comprobación de Cloud Monitoring cada 5 minutos; informe del primer mes |
| RNF-11 | Arquitectura: ningún uso del reloj real; cada grupo de RF tiene tests con `FixedClock` |
| RNF-13 | HTTP: `Cache-Control: no-store`; revisión registrada en teléfono y ordenador |

## 9. Trazabilidad RF → módulo → tipo de test

| RF | Dominio | Aplicación / infraestructura / web | Tipo de test |
|----|---------|------------------------------------|--------------|
| RF-1 | `text.py`, `contact_info.py`, `formatting.py`, `people.py` | `repositories.py` (versión, RF-1.15), formularios (RF-1.17) | Unidad; integración (RF-1.15); HTTP (RF-1.17) |
| RF-2 | `accounts.py` | `accounts.py`, `auth_backend.py`, `totp.py`, `middleware.py` | Unidad (bloqueo, vectores RFC 6238); integración; HTTP |
| RF-3 | `permissions.py` | `authorization.py` | Unidad (matriz); integración y HTTP parametrizados |
| RF-4 | `students.py` | `students.py` | Unidad; integración (duplicados con índice) |
| RF-5 | `contacts.py` | `contacts.py` | Unidad; integración (borrado de huérfanos, bloqueo) |
| RF-6 | `consent.py` | `consent.py` | Unidad; integración |
| RF-7 | `students.py` | `students.py`, vistas de ficha | Integración; HTTP (salud oculta, búsqueda por POST) |
| RF-8 | `students.py` | `students.py` | Unidad; integración (atomicidad) |
| RF-9 | `groups.py` | `groups.py` | Unidad; integración |
| RF-10 | `enrollments.py` | `enrollments.py` | Unidad; integración (concurrencia CL-31) |
| RF-11 | `billing.py` | `billing.py` | Unidad (fechas, días 15/16); integración (CL-51) |
| RF-12 | `payments.py` | `payments.py` | Unidad (aplicación); integración (anulación) |
| RF-13 | `delinquency.py` | `statements.py` | Unidad; integración; HTTP |
| RF-14 | `permissions.py` | `teaching.py`, vistas del profesor | Integración; HTTP; interfaz (360 px) |
| RF-15 | `retention.py` (anonimización) | `rights.py`, plantilla de exportación | Integración; HTTP |
| RF-16 | `retention.py` | `retention.py`, `daily_review.py` | Unidad (plazos, 29/02); integración |
| RF-17 | `audit.py` | `audit_queries.py`, `unit_of_work.py`, roles de BD | Integración (incluye permisos de BD) |
| RF-18 | — | `home.py`, vista de inicio | Integración; HTTP |

## 10. Comprobación contra la constitución

| # | Principio | Cómo lo cumple el plan | Resultado |
|---|-----------|------------------------|-----------|
| 1 | Stack simple | Un lenguaje, un monolito Django, una base de datos; cada dependencia está en la tabla de la sección 2 con su motivo | Cumple |
| 2 | Spec antes que código | Trazabilidad RF → módulo → test (sección 9) y test que exige que cada RF y CL aparezca en un test | Cumple |
| 3 | Dominio sin E/S | `domain` y `application` sin Django ni reloj; test de arquitectura sobre los `import` y las llamadas a `now`/`today` | Cumple |
| 4 | Tests obligatorios | Cada RF y CL con test; `pytest -q` antes de cada commit; fecha fija y datos ficticios | Cumple |
| 5 | Persistencia controlada | Solo `infrastructure` importa Django ORM y psycopg; migraciones versionadas; sin `django.contrib.admin`; copias de Cloud SQL diarias, cifradas, 30 días, con restauración trimestral | Cumple |
| 6 | Idioma | Identificadores, archivos y comentarios en inglés; textos solo en `messages.py` y plantillas, en español | Cumple |
| 7 | Mínimo dato, mínimo acceso | Cada columna cita su RF (sección 4); permisos en cada servicio; salud solo por `reveal_health_notes` | Cumple |
| 8 | Datos protegidos y trazables | HTTPS y HSTS, PBKDF2, cifrado en reposo de Cloud SQL, auditoría inmutable para la app, registros sin datos personales, búsquedas sin datos en la URL, revisión diaria de plazos | Cumple, con el aviso A-2 (región) |

## 11. Riesgos técnicos

| Id | Riesgo | Mitigación |
|----|--------|------------|
| R-1 | El ORM de Django se cuela en el dominio y se pierde la separación de capas | Test de arquitectura que falla con cualquier `import django` en `domain` o `application` |
| R-2 | Errores de zona horaria (UTC frente a Bogotá) al calcular «hoy», vencimientos o plazos | Un único `Clock`; tests en los bordes del día (23:59 y 00:00 de Bogotá) |
| R-3 | Implementación propia de TOTP incorrecta | Vectores de prueba de la RFC 6238; prueba manual con dos apps autenticadoras |
| R-4 | La única cuenta de Dirección pierde su segundo factor y nadie puede restablecerla | Recomendar al menos dos cuentas de Dirección; comando de emergencia `reset_direction_access` ejecutable solo con acceso a la infraestructura y auditado como «sistema» |
| R-5 | El arranque en frío de Cloud Run incumple RNF-3 | Una instancia mínima siempre activa |
| R-6 | La revisión diaria no se ejecuta durante días | Al basarse en estados, la siguiente recupera lo pendiente (RF-16.1); alerta de Cloud Monitoring si el job falla |
| R-7 | Migraciones aplicadas con instancias antiguas en marcha | Migraciones compatibles hacia atrás y ejecutadas como job antes de cambiar el tráfico |
| R-8 | Coste por encima de lo previsto | Instancias acotadas (mínimo 1, máximo 2), la base de datos más pequeña que cumpla RNF-3 y alertas de presupuesto |
| R-9 | Las pruebas de interfaz (Playwright) son lentas o frágiles | Se ejecutan aparte (`-m ui`) antes de cada versión, no en cada commit |

## 12. Autorrevisión del plan

Revisión hecha con el mismo formato que la fase 3. Numeración H-x global (la
revisión de la spec llegó a H-42). Todas las resoluciones ya están aplicadas en
las secciones anteriores.

### 12.1 Hallazgos

**(1) Ambigüedades**

- **H-43 — Cuotas anuladas y RF-11.1:** el plan necesita saber si una cuota anulada cuenta para «como máximo una cuota por alumno, grupo y mes». La spec no lo dice.
- **H-44 — Hora de la revisión diaria:** «una vez al día» no fija la hora; si se ejecuta cerca de medianoche puede tomar el «hoy» equivocado.
- **H-45 — «Activa hoy» en base de datos:** traducir RF-10.8 a SQL exige saber si puede haber fechas de baja futuras.

**(2) Contradicciones**

- **H-46 — RNF-4 y RNF-12 frente al principio 1:** la spec exige pruebas automáticas de pantallas y teclado, lo que obliga a añadir un navegador automatizado como dependencia.

**(3) Casos límite no cubiertos**

- **H-47 — Única cuenta de Dirección sin segundo factor:** si pierde el teléfono, nadie puede restablecer su acceso (RF-2.13 lo hace otra cuenta de Dirección).
- **H-48 — Arranque en frío:** con cero instancias, la primera petición del día puede tardar varios segundos y romper RNF-3.
- **H-49 — Despliegue con migraciones:** una migración puede romper las instancias que siguen sirviendo la versión anterior.
- **H-50 — La revisión diaria falla sin que nadie se entere:** RF-16.1 recupera lo pendiente, pero nadie sabría que falla.

**(4) Conflictos con la constitución**

- **H-51 — Principio 5 frente a `django.contrib.admin`:** el panel de administración de Django modificaría la base de datos sin pasar por los servicios, los permisos ni la auditoría.
- **H-52 — Principio 8 frente a los registros del proveedor:** una búsqueda por `GET` (`?q=María`) deja el nombre en los registros de peticiones de Cloud Run, que la app no controla.
- **H-53 — Principio 8 frente al seguimiento de errores:** un servicio externo de errores recibiría trazas con datos personales.

**(5) Privacidad y seguridad**

- **H-54 — Secreto TOTP sin cifrar:** el secreto del segundo factor no se puede guardar con hash como una contraseña.
- **H-55 — Región y transferencia internacional:** alojar los datos fuera de Colombia es una transferencia internacional (Ley 1581, art. 26).
- **H-56 — Copias en caché del navegador:** las fichas podrían quedar en la caché del teléfono del profesor.

**(6) No comprobables**

- **H-57 — RNF-12 «revisión automática»:** no dice con qué herramienta.
- **H-58 — Permisos de base de datos de la auditoría:** RF-17.4 se cumple en la app, pero sin una prueba no se sabe si el rol de base de datos lo impide.

### 12.2 Resoluciones

| Hallazgo | Decisión | Dónde está en el plan |
|----------|----------|------------------------|
| H-43 | Las anuladas no cuentan (índice único con `voided_at IS NULL`), para que RF-10.10 no impida generar la cuota correcta. Confirmado por el usuario y recogido en RF-11.1 (spec v3) y CL-57. | 4.7, aviso A-1 |
| H-44 | La revisión se ejecuta a las 02:00 de Bogotá y toma «hoy» del `Clock`. | D-37 |
| H-45 | La baja siempre se fecha hoy y no hay fechas futuras, así que «activa hoy» es `ended_on IS NULL`. | 4.6 |
| H-46 | Playwright y axe-core solo como dependencias de desarrollo, justificadas en la tabla de dependencias. | 2, D-25 |
| H-47 | Al menos dos cuentas de Dirección y comando de emergencia auditado. | R-4 |
| H-48 | Una instancia mínima siempre activa. | R-5 |
| H-49 | Migraciones compatibles hacia atrás, ejecutadas como job antes de cambiar el tráfico. | R-7, 7.1 |
| H-50 | Alerta de Cloud Monitoring si el job falla. | R-6 |
| H-51 | No se instala `django.contrib.admin`. | 4.10, 10 |
| H-52 | Búsquedas por `POST` y texto guardado en la sesión. | D-35 |
| H-53 | Sin servicios externos de errores ni analítica; los errores van a los registros propios, sin datos personales. | 2 |
| H-54 | Riesgo aceptado: el secreto se protege con el cifrado en reposo de la base de datos y con su acceso restringido; quien lo robara ya tendría acceso a todos los datos. Cifrarlo exigiría una librería criptográfica extra. | 4.1 |
| H-55 | Elegir una región en un país con nivel adecuado según la SIC y validarlo con protección de datos. | D-23, aviso A-2 |
| H-56 | `Cache-Control: no-store` en todas las respuestas autenticadas. | D-36 |
| H-57 | axe-core ejecutado con Playwright; el criterio es cero errores de nivel A. | 2, 8.4 |
| H-58 | Una migración crea los roles y un test comprueba que `app_rw` no puede modificar ni borrar `audit_entry`. | 7.1 |

### 12.3 Principios sin conflictos

Tras las resoluciones, ningún principio queda en conflicto. Antes de ellas, los
principios **1** (H-46), **5** (H-51) y **8** (H-52, H-53) tenían conflictos;
los principios **2, 3, 4, 6 y 7** no tenían ninguno.

## 13. Avisos para el usuario

Por la regla 6, estos puntos no se deciden aquí porque tocan una fase aprobada o
una cuestión legal:

- **A-1 — Interpretación de RF-11.1 (H-43): resuelto.** El usuario confirmó que una cuota anulada no cuenta como «la cuota de ese grupo y mes»; la spec lo recoge en su versión 3 (RF-11.1 y CL-57).
- **A-2 — Región de los datos (H-55):** el despliegue en Google Cloud implica una transferencia internacional de datos. Hay que confirmar con quien lleve la protección de datos de la escuela qué región es aceptable antes de desplegar.
