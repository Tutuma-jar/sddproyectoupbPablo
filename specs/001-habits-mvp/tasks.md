# Tareas 001 — MVP de habits-cli

- **Estado:** borrador
- **Fecha:** 2026-10-23
- **Origen:** spec 001 (versión 2) y plan 001

## Cómo usar esta lista

- Las tareas están en **orden de dependencia**: cada una solo necesita las
  anteriores que indica «Depende de».
- Cada tarea cabe en **20-30 minutos** e incluye sus pruebas. Se escriben
  primero las pruebas, se ven fallar y después se escribe el código.
- Las pruebas citan en su nombre o en su `id` el RF o CL que cubren (plan, 8.4),
  así que los filtros `-k` de «Hecho cuando» las encuentran.
- Al cerrar cualquier tarea, `python -m pytest -q` debe pasar entero (principio 4).
- `T-x` remite a las decisiones técnicas del plan (sección 6).

---

## Fase 0 — Preparación

- [ ] **TA-01 · Esqueleto del proyecto y pytest** — RF: ninguno (principio 4, T-18)
  - Depende de: —
  - Hacer: instalar pytest; crear `pyproject.toml` solo con
    `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `pythonpath = ["."]`);
    crear `habits/__init__.py` vacío y la carpeta `tests/`.
  - Hecho cuando: `python -m pytest -q` termina con «no tests ran» (código 5)
    sin errores de importación ni de configuración.

- [ ] **TA-02 · Fixtures base de las pruebas** — RF-7.5, RNF-5
  - Depende de: TA-01
  - Hacer: en `tests/conftest.py`, las fixtures `today` (2026-10-23),
    `data_file` (`tmp_path/home/.habits/habits.json`, con `home` creada y
    `.habits` sin crear), `write_raw` y `assert_unchanged` (plan, 8.2).
  - Hecho cuando: una prueba de humo en `tests/test_conftest.py` usa las cuatro
    fixtures, y `assert_unchanged` falla si se modifica el archivo dentro de
    su bloque.

---

## Fase 1 — Núcleo puro (`habits/core.py`)

- [ ] **TA-03 · Tipos y constantes del núcleo** — RF-1.1, RF-1.8
  - Depende de: TA-01
  - Hacer: `WHITESPACE` (los 25 caracteres de `White_Space`, T-9),
    `MAX_NAME_LENGTH = 50`, `ErrorCode` (`E-1` … `E-9`), `Habit` (dataclass
    congelada con `frozenset[date]`), `HabitError(code, name)` y `MarkResult`.
  - Hecho cuando: `python -m pytest -q -k whitespace` pasa y comprueba que
    `WHITESPACE` tiene 25 caracteres, incluye U+0009, U+000A, U+00A0 y U+3000, y
    **no** incluye U+001C–U+001F.

- [ ] **TA-04 · `normalize_name`** — RF-1.1, RF-1.2
  - Depende de: TA-03
  - Hacer: NFC, recorte y colapso de espacios con `WHITESPACE` (plan, 4.1).
  - Hecho cuando: `python -m pytest -q -k normalize_name` pasa con los casos
    CL-8 («  Leer  » -> «Leer»), CL-20 (tabulador, salto de línea y U+00A0 en el
    interior), CL-21 («á» descompuesta -> compuesta), «Leer  libros» -> «Leer
    libros» y «LeEr» conserva sus mayúsculas.

- [ ] **TA-05 · `name_key`** — RF-1.3
  - Depende de: TA-04
  - Hacer: `NFC(casefold(name))` (T-10).
  - Hecho cuando: `python -m pytest -q -k name_key` pasa con: «Leer» = «leer»;
    CL-11 («Matemáticas» = «MATEMÁTICAS», ≠ «Matematicas»); CL-22 («Straße» =
    «STRASSE» = «strasse»).

- [ ] **TA-06 · `check_name` y `validate_new_name`** — RF-1.4, RF-1.5, RF-1.6, RF-1.7, RF-1.8, RF-7.6
  - Depende de: TA-04
  - Hacer: las cuatro reglas en el orden E-1, E-3, E-4, E-2; `Cc` como control
    (T-11); `validate_new_name = normalize_name + check_name`.
  - Hecho cuando: `python -m pytest -q -k "check_name or validate_new_name"`
    pasa con: CL-9 (solo espacios -> E-1), CL-10 (50 se acepta, 51 -> E-2),
    CL-21 («á» descompuesta cuenta 1), CL-24 (`-h`, `--ayuda` -> E-4), CL-25
    (U+0007 -> E-3), U+001C -> E-3, CL-26 (más de 50 antes de normalizar, 50 o
    menos después -> se acepta), un emoji compuesto con U+200D se acepta, y el
    orden: control + > 50 -> E-3; «-» + > 50 -> E-4.

- [ ] **TA-07 · `validate_lookup_name`** — RF-3.4, RF-3.5
  - Depende de: TA-04
  - Hacer: normalizar y aplicar solo la regla de vacío.
  - Hecho cuando: `python -m pytest -q -k validate_lookup_name` pasa con: `""` y
    `"   "` -> E-1; `"-x"`, un nombre de 51 caracteres y uno con U+0007
    se devuelven normalizados **sin** error.

- [ ] **TA-08 · `find_habit` y `add_habit`** — RF-1.2, RF-1.3, RF-2.1, RF-2.3
  - Depende de: TA-05, TA-06
  - Hacer: búsqueda por `name_key`; `add_habit` añade al final sin fechas, no
    muta la lista recibida y lanza E-5 con el nombre **guardado**.
  - Hecho cuando: `python -m pytest -q -k "find_habit or add_habit"` pasa con:
    el nuevo hábito queda último y con `done_dates` vacío; la lista original no
    cambia; CL-7 (crear «Leer» con «leer» -> E-5 con `name == "leer"`); CL-16;
    CL-22.

- [ ] **TA-09 · `compute_streak`** — RF-5.2, RF-5.3, RF-5.4, RF-5.5
  - Depende de: TA-03
  - Hacer: el algoritmo de la sección 4.2 del plan, con la protección de
    `date.min`.
  - Hecho cuando: `python -m pytest -q -k compute_streak` pasa con CL-1 (sin
    fechas -> 0), CL-2 (ayer y anteayer -> 2), CL-3 (hoy y anteayer -> 1), CL-4
    (solo anteayer -> 0), CL-5 (31-dic -> 1-ene, 28-feb -> 29-feb -> 1-mar de
    2028), CL-37 (fechas alrededor del cambio de hora de 2026), CL-39 (400 días
    -> 400) y una racha que llega hasta `date.min` sin excepción.

- [ ] **TA-10 · `is_done_today` y fechas futuras** — RF-5.6
  - Depende de: TA-09
  - Hacer: `is_done_today` con igualdad exacta.
  - Hecho cuando: `python -m pytest -q -k "is_done_today or future"` pasa con:
    CL-17 (con mañana marcado, `is_done_today` es falso y la racha no cambia) y
    CL-38 (la fecha que era futura cuenta cuando `today` la alcanza).

- [ ] **TA-11 · `mark_done`** — RF-3.1, RF-3.3, RF-3.5
  - Depende de: TA-08, TA-09
  - Hacer: devuelve `MarkResult`; si ya estaba marcado, `already_done=True` y la
    misma lista; si no existe, E-6 con el nombre recibido.
  - Hecho cuando: `python -m pytest -q -k mark_done` pasa con: marcar añade
    `today` y calcula la racha resultante; marcar dos veces da
    `already_done=True` sin cambiar fechas (CL-6); `"LEER"` encuentra «Leer» y
    `result.habit.name == "Leer"` (CL-12); un nombre inexistente da E-6 con
    `name` tal como se pasó; la lista original no se muta.

- [ ] **TA-12 · `has_duplicate_names`** — RF-8.5
  - Depende de: TA-05
  - Hecho cuando: `python -m pytest -q -k has_duplicate_names` pasa con: lista
    vacía -> falso; «Leer» y «leer» -> verdadero; «Straße» y «STRASSE» ->
    verdadero; «Matemáticas» y «Matematicas» -> falso.

---

## Fase 2 — Textos (`habits/messages.py`)

- [ ] **TA-13 · `days_label` y `list_line`** — RF-4.1, RF-5.7
  - Depende de: TA-01
  - Hecho cuando: `python -m pytest -q -k "days_label or list_line"` pasa con:
    0, 2 y 400 -> «días»; 1 -> «día» (CL-18); las tres líneas literales del
    ejemplo de RF-4.1; un nombre con « | » se muestra tal cual (CL-40).

- [ ] **TA-14 · Mensajes de éxito y ayuda** — RF-2.2, RF-3.2, RF-3.3, RF-4.3, RF-6.4
  - Depende de: TA-13
  - Hacer: `habit_created`, `marked_done`, `already_done`, `NO_HABITS`, `HELP`.
  - Hecho cuando: `python -m pytest -q -k "test_m_"` pasa comparando M-1 a M-5
    con el texto literal de la spec, incluidas «1 día» y «5 días» en M-2 y M-3.

- [ ] **TA-15 · Mensajes de error** — RF-7.2, RF-2.3, RF-3.5, RF-6.5
  - Depende de: TA-14, TA-03
  - Hacer: `error_text(code, name=None)` para E-1 a E-9; E-7 = texto + línea
    en blanco + `HELP`.
  - Hecho cuando: `python -m pytest -q -k "test_e_"` pasa comparando los nueve
    textos literales de la spec (E-5 y E-6 con un nombre de ejemplo) y un test
    comprueba que ningún texto de `messages.py` contiene comillas angulares,
    rayas (—) ni comillas tipográficas.

---

## Fase 3 — Persistencia (`habits/storage.py`)

- [ ] **TA-16 · Ubicación y errores de persistencia** — RF-8.2
  - Depende de: TA-01
  - Hacer: constantes `DATA_DIR_NAME`, `DATA_FILE_NAME`, `FORMAT_VERSION`;
    `DataReadError`, `DataWriteError`; `default_data_file()` (devuelve `None` si
    `Path.home()` falla).
  - Hecho cuando: `python -m pytest -q -k default_data_file` pasa con
    `Path.home` sustituido: devuelve `<home>/.habits/habits.json`, el mismo
    resultado tras `monkeypatch.chdir` a dos carpetas distintas, y `None` si
    `Path.home` lanza `RuntimeError`.

- [ ] **TA-17 · `save_habits`: camino feliz** — RF-8.1, RF-8.4, RF-5.6
  - Depende de: TA-16, TA-03
  - Hacer: serializar según la sección 3.2 del plan (UTF-8, `ensure_ascii=False`,
    `indent=2`, fechas ordenadas); `mkdir(exist_ok=True)` sin `parents`;
    temporal + `fsync` + `os.replace` (T-13).
  - Hecho cuando: `python -m pytest -q -k "save_habits and not error"` pasa con:
    guardar los tres hábitos del ejemplo del plan produce **byte a byte** el
    JSON del ejemplo; se crea `.habits`; tras guardar, la carpeta contiene solo
    `habits.json`; una fecha futura se escribe.

- [ ] **TA-18 · `load_habits`: datos válidos y primer uso** — RF-8.1, RF-8.3, RF-5.6, RF-4.2
  - Depende de: TA-17
  - Hecho cuando: `python -m pytest -q -k "load_habits and valid"` pasa con:
    archivo inexistente -> `[]`; `path=None` -> `[]`; ida y vuelta
    `save` -> `load` devuelve los mismos hábitos en el mismo orden, con la fecha
    futura conservada; fechas desordenadas en el archivo se aceptan.

- [ ] **TA-19 · `load_habits`: estructura no válida** — RF-8.5
  - Depende de: TA-18
  - Hacer: 0 bytes, UTF-8 estricto, JSON con claves repetidas
    (`object_pairs_hook`), claves exactas, `type(version) is int and version == 1`,
    errores de E/S distintos de `FileNotFoundError`.
  - Hecho cuando: `python -m pytest -q -k "load_habits and invalid_structure"`
    pasa con una tabla parametrizada en la que cada caso lanza `DataReadError`:
    CL-32 (0 bytes), bytes no UTF-8, JSON roto (CL-14), raíz que no es objeto,
    clave de más, clave de menos, clave repetida, `version` 2, `version` `true`,
    `habits` que no es lista, hábito con clave de más, `data_file` que es una
    carpeta.

- [ ] **TA-20 · `load_habits`: contenido no válido** — RF-8.5
  - Depende de: TA-19, TA-06, TA-12
  - Hacer: fechas con la expresión regular ASCII + `fromisoformat` (T-7); sin
    fechas repetidas; nombres ya normalizados y válidos (T-12); sin hábitos
    iguales.
  - Hecho cuando: `python -m pytest -q -k "load_habits and invalid_content"`
    pasa con una tabla en la que cada caso lanza `DataReadError`: CL-33
    (`2026-02-30`, fecha repetida, «Leer» y «leer»), `20261023`, fecha con
    dígitos no ASCII, fecha que no es cadena, nombre `"  Leer"`, nombre vacío,
    nombre de 51 caracteres, nombre que empieza por «-», nombre con U+0007.

- [ ] **TA-21 · `save_habits`: fallos e interrupciones** — RF-8.6, RF-7.5, RNF-4, RNF-7
  - Depende de: TA-18
  - Hacer: convertir `OSError` y `UnicodeError` en `DataWriteError`; borrar el
    temporal propio ante cualquier excepción y relanzarla; limpiar al guardar
    los `habits-*.tmp` sobrantes; `path=None` -> `DataWriteError`.
  - Hecho cuando: `python -m pytest -q -k "save_habits and error"` pasa con:
    CL-35 (`mkstemp` y `os.fsync` lanzan `OSError` -> `DataWriteError`, bytes
    anteriores intactos); carpeta personal inexistente -> `DataWriteError` y no
    se crea; `os.replace` lanza `KeyboardInterrupt` -> se propaga, archivo
    intacto, sin `.tmp` (RNF-4); un `.tmp` sobrante desaparece tras guardar;
    dos `load` + dos `save` seguidos dejan un archivo válido con el segundo
    cambio (RNF-7).

---

## Fase 4 — Interfaz (`habits/cli.py` y `habits/__main__.py`)

- [ ] **TA-22 · `parse` y tabla de comandos** — RF-6.1, RF-6.2, RF-6.3, RF-6.5
  - Depende de: TA-01
  - Hacer: `COMMANDS`, `UsageError`, `parse(argv)` (T-1).
  - Hecho cuando: `python -m pytest -q -k parse` pasa con: los cuatro comandos
    válidos con su aridad; `""` y `"   "` cuentan como argumento (RF-6.3);
    `UsageError` para CL-27 (`crear Leer libros`), CL-28 (`crear` solo), CL-30
    (sin comando, `borrar`, `CREAR`) y CL-31 (`listar algo`, `ayuda algo`);
    CL-23 (`crear listar`) devuelve `("crear", "listar")`.

- [ ] **TA-23 · `main`, `ayuda` y errores de uso** — RF-5.1, RF-6.4, RF-6.5, RF-7.1, RF-7.2, RF-7.3
  - Depende de: TA-22, TA-15, TA-16, TA-02
  - Hacer: `read_local_date`; `main(argv, *, today, data_file)` con la
    traducción de excepciones a mensajes y códigos (plan, 4.3); comando
    `ayuda`; añadir la fixture `run` a `conftest.py`.
  - Hecho cuando: `python -m pytest -q -k "cli and (ayuda or usage)"` pasa con:
    CL-41 (`ayuda` -> M-5 en stdout, stderr vacío, código 0); CL-27, CL-28,
    CL-30 y CL-31 -> E-7 completo en stderr, stdout vacío, código 2.

- [ ] **TA-24 · Comando `crear`** — RF-1.2, RF-2.1, RF-2.2, RF-2.3, RF-1.5–1.8, RF-7.4, RF-7.5, RF-8.1, RF-8.4
  - Depende de: TA-23, TA-08, TA-21
  - Hecho cuando: `python -m pytest -q -k "cli and crear"` pasa con: M-1 y
    código 0, y el archivo creado con `.habits`; CL-7 y CL-16 (E-5 con el
    nombre guardado); CL-23 (crea «listar»); CL-24 (E-4); CL-28 (`crear ""` ->
    E-1, código 1); un caso por E-2 y E-3; `crear "  LeEr  "` guarda «LeEr»; y
    todas las de error usan `assert_unchanged`.

- [ ] **TA-25 · Comando `listar`** — RF-4.1, RF-4.2, RF-4.3, RF-5.3–5.5, RF-8.3
  - Depende de: TA-24, TA-10
  - Hecho cuando: `python -m pytest -q -k "cli and listar"` pasa con: CL-13
    (sin archivo -> M-4, código 0, y no se crea ningún archivo); el archivo
    del ejemplo del plan produce las tres líneas literales de RF-4.1; crear B,
    A, C lista B, A, C; CL-40.

- [ ] **TA-26 · Comando `hecho`** — RF-3.1, RF-3.2, RF-3.3, RF-3.4, RF-3.5, RF-5.7
  - Depende de: TA-24, TA-11, TA-07
  - Hecho cuando: `python -m pytest -q -k "cli and hecho"` pasa con: M-2 con
    «1 día» (CL-18) y la fecha guardada; CL-6 (segunda vez -> M-3, código 0,
    `assert_unchanged`); CL-12 (`hecho LEER` -> mensaje con «Leer»); CL-15
    (`today` = D y luego D+1 -> racha 2); CL-29 (`hecho ""` -> E-1, código 1);
    `hecho "-x"` y `hecho` con 51 caracteres -> E-6 con el nombre normalizado.

- [ ] **TA-27 · Datos corruptos, fallos al guardar y orden de errores** — RF-7.4, RF-7.5, RF-7.6, RF-8.5, RF-8.6
  - Depende de: TA-25, TA-26, TA-20
  - Hecho cuando: `python -m pytest -q -k "cli and (corrupt or write_error or error_order)"`
    pasa con: CL-14 (`listar`, `crear` y `hecho` con datos corruptos -> E-8,
    código 1, archivo intacto); CL-35 (`crear` y `hecho` con fallo de escritura
    -> E-9, código 1, intacto); CL-34 (corruptos + `crear ""` -> E-1);
    corruptos + duplicado -> E-8; duplicado + fallo de escritura -> E-5;
    corruptos + `hecho` inexistente -> E-8.

- [ ] **TA-28 · Una lectura del reloj y ubicación por defecto** — RF-5.1, RF-8.2
  - Depende de: TA-26
  - Hecho cuando: `python -m pytest -q -k "cli and (clock or location)"` pasa
    con: CL-36 (`read_local_date` sustituido devuelve D y luego D+1; se llama
    una sola vez y se guarda D); CL-19 (sin pasar `data_file`, con `Path.home`
    sustituido, `crear` desde una carpeta y `listar` desde otra muestran el
    mismo hábito).

- [ ] **TA-29 · `__main__.py` y pruebas de humo** — RF-6.4, RF-7.3, RF-8.2, RNF-6
  - Depende de: TA-28
  - Hacer: `__main__.py` con `reconfigure(errors="replace")` en stdout y
    stderr (T-14) y `raise SystemExit(cli.main(sys.argv[1:]))`.
  - Hecho cuando: `python -m pytest -q tests/test_e2e.py` pasa ejecutando
    `python -m habits` con `subprocess`, `HOME` y `USERPROFILE` apuntando a
    `tmp_path` y `PYTHONIOENCODING=utf-8`: `ayuda` -> M-5 y 0 (CL-41);
    `CREAR` -> E-7 y 2 (CL-30); `crear "Inglés"` y luego `listar` desde otra
    carpeta -> «Inglés | racha: 0 días | pendiente hoy» (CL-19).

---

## Fase 5 — Constitución y cierre

- [ ] **TA-30 · Pruebas de la constitución** — principios 1, 3, 4 y 5; RNF-2
  - Depende de: TA-29
  - Hacer: `tests/test_architecture.py` con `ast` (plan, 8.6).
  - Hecho cuando: `python -m pytest -q tests/test_architecture.py` pasa, y
    falla si se añade temporalmente `import json` o `print()` en `core.py`, o
    una función pública en `core.py` sin probar.

- [ ] **TA-31 · Comprobar la trazabilidad de las pruebas** — todos los RF; §10 de la spec
  - Depende de: TA-30
  - Hacer: buscar cada RF-x.y y cada CL-x de la spec en `tests/` (por nombre
    de prueba o `id`); añadir las pruebas que falten.
  - Hecho cuando: un `grep` de los 43 RF y los 41 CL de la spec sobre `tests/`
    no deja ninguno sin aparecer, y cada M-x y E-x aparece con su texto literal
    en `test_messages.py` y en `test_cli.py`.

- [ ] **TA-32 · Medición de rapidez** — RNF-3
  - Depende de: TA-29
  - Hacer: `tools/make_perf_data.py`, que genera 100 hábitos × 365 días en una
    carpeta personal indicada; medir `listar`, `crear` y `hecho` con
    `Measure-Command`, apuntando `USERPROFILE` a esa carpeta.
  - Hecho cuando: los tres tiempos son menores de 1 s y están anotados (equipo,
    versión de Python y tiempos) en la descripción del PR.

- [ ] **TA-33 · Revisión manual en terminales** — RNF-1, RNF-6
  - Depende de: TA-29
  - Hecho cuando: en PowerShell, en el símbolo del sistema y en una terminal
    UTF-8, `crear "Inglés"`, `crear "Año"`, `hecho "INGLÉS"`, `listar` y `ayuda`
    muestran bien tildes y «ñ», y el resultado de cada terminal está anotado en
    el PR (incluida la limitación de `crear ""` en PowerShell 5.1, plan, 7).

- [ ] **TA-34 · Cierre** — §10 de la spec
  - Depende de: TA-31, TA-32, TA-33
  - Hecho cuando: `python -m pytest -q` pasa entero; la revisión de código
    confirma RNF-2 y RNF-8 (sin red y sin funciones fuera de la spec); y todas
    las casillas de esta lista están marcadas.

---

## Cobertura de requisitos

| RF | Tareas |
|----|--------|
| RF-1.1 | TA-03, TA-04 |
| RF-1.2 | TA-04, TA-08, TA-24 |
| RF-1.3 | TA-05, TA-08 |
| RF-1.4 | TA-06 |
| RF-1.5 | TA-06, TA-24 |
| RF-1.6 | TA-06, TA-24 |
| RF-1.7 | TA-06, TA-24 |
| RF-1.8 | TA-03, TA-06, TA-24 |
| RF-2.1 | TA-08, TA-24 |
| RF-2.2 | TA-14, TA-24 |
| RF-2.3 | TA-08, TA-15, TA-24 |
| RF-3.1 | TA-11, TA-26 |
| RF-3.2 | TA-14, TA-26 |
| RF-3.3 | TA-11, TA-14, TA-26 |
| RF-3.4 | TA-07, TA-26 |
| RF-3.5 | TA-07, TA-11, TA-15, TA-26 |
| RF-4.1 | TA-13, TA-25 |
| RF-4.2 | TA-18, TA-25 |
| RF-4.3 | TA-14, TA-25 |
| RF-5.1 | TA-23, TA-28 |
| RF-5.2 | TA-09 |
| RF-5.3 | TA-09, TA-25 |
| RF-5.4 | TA-09, TA-25 |
| RF-5.5 | TA-09, TA-25 |
| RF-5.6 | TA-10, TA-17, TA-18 |
| RF-5.7 | TA-13, TA-26 |
| RF-6.1 | TA-22 |
| RF-6.2 | TA-22 |
| RF-6.3 | TA-22 |
| RF-6.4 | TA-14, TA-23, TA-29 |
| RF-6.5 | TA-15, TA-22, TA-23 |
| RF-7.1 | TA-23 |
| RF-7.2 | TA-15, TA-23 |
| RF-7.3 | TA-23, TA-29 |
| RF-7.4 | TA-24, TA-27 |
| RF-7.5 | TA-02, TA-21, TA-24, TA-27 |
| RF-7.6 | TA-06, TA-27 |
| RF-8.1 | TA-17, TA-18, TA-24 |
| RF-8.2 | TA-16, TA-28, TA-29 |
| RF-8.3 | TA-18, TA-25 |
| RF-8.4 | TA-17, TA-24 |
| RF-8.5 | TA-12, TA-19, TA-20, TA-27 |
| RF-8.6 | TA-21, TA-27 |

| RNF | Tareas |
|-----|--------|
| RNF-1 | TA-33 |
| RNF-2 | TA-30, TA-34 |
| RNF-3 | TA-32 |
| RNF-4 | TA-21 |
| RNF-5 | TA-02, TA-23 |
| RNF-6 | TA-29, TA-33 |
| RNF-7 | TA-21 |
| RNF-8 | TA-34 |
