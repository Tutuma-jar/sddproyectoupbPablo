# Plan 001 — MVP de habits-cli

- **Estado:** borrador, pendiente de aprobación
- **Fecha:** 2026-10-23
- **Spec de referencia:** spec 001, versión 2 (aprobada)
- **Referencia:** constitución del proyecto

Este plan describe **cómo** se construye lo que la spec pide. No añade
comportamiento: si algo de aquí contradice la spec, manda la spec y se corrige
el plan. Si durante la implementación aparece una duda que la spec no resuelve,
se actualiza primero la spec (principio 2).

Cada parte indica entre corchetes los requisitos que cubre, por ejemplo
`[RF-1.1]`. La sección 9 reúne la trazabilidad completa.

---

## 1. Cumplimiento de la constitución

| # | Principio | Cómo lo cumple el plan |
|---|-----------|------------------------|
| 1 | Stack mínimo | Solo biblioteca estándar: `unicodedata`, `re`, `json`, `os`, `tempfile`, `pathlib`, `datetime`, `dataclasses`, `enum`, `sys`. pytest solo en `tests/`. Sin `argparse` (decisión T-1). |
| 2 | Spec primero | Todo el comportamiento sale de la spec v2; la sección 9 enlaza cada RF con su diseño y sus pruebas. |
| 3 | Núcleo puro | `core.py` no importa `os`, `sys`, `pathlib`, `json` ni `io`, y no llama a `print`, `input` ni `open`. Recibe «hoy» como parámetro. `cli.py` solo traduce argumentos, encadena llamadas y muestra resultados. |
| 4 | Tests obligatorios | Cada función pública de `core.py` tiene pruebas en `tests/test_core.py`; un test de arquitectura lo comprueba (sección 8.6). |
| 5 | Persistencia JSON local | Un único archivo `habits.json`; solo `storage.py` importa `json` y toca archivos. El formato exacto se fija en la sección 3.2. |
| 6 | Idioma | Identificadores, nombres de archivo, claves JSON y comentarios en inglés. Todo texto para el usuario vive en `messages.py`, en español. Los nombres de los comandos (`crear`, `hecho`…) son texto para el usuario (RNF-1). |

---

## 2. Estructura de módulos

```text
habits/
  __init__.py      vacío
  __main__.py      punto de entrada de `python -m habits`
  cli.py           argumentos -> llamadas -> mensajes y código de salida
  core.py          reglas puras: nombres, hábitos, racha
  messages.py      todos los textos en español (M-x, E-x, ayuda)
  storage.py       lectura y escritura del archivo JSON
tests/
  conftest.py      fixtures comunes (fecha fija, archivo de datos temporal)
  test_core.py
  test_messages.py
  test_storage.py
  test_cli.py
  test_e2e.py      unas pocas ejecuciones reales con subprocess
  test_architecture.py
pyproject.toml     solo configuración de pytest (sin dependencias)
```

Dependencias permitidas (una flecha significa «importa»):

```text
__main__ ──> cli ──> core
              │ ───> storage ──> core
              └────> messages
```

`core` no importa ningún otro módulo del proyecto. `messages` no importa nada
del proyecto: recibe valores ya calculados.

### 2.1 `core.py` — reglas puras

| Elemento público | Responsabilidad | Cubre |
|------------------|-----------------|-------|
| `WHITESPACE: str` | Los 25 caracteres con la propiedad Unicode `White_Space` (sección 4.1). | RF-1.1 |
| `MAX_NAME_LENGTH = 50` | Longitud máxima de un nombre. | RF-1.8 |
| `ErrorCode` (Enum) | Identificadores `E-1` … `E-9`, compartidos por todos los módulos. | RF-7 |
| `Habit` (dataclass congelada) | `name: str`, `done_dates: frozenset[date]`. | §6 de la spec |
| `HabitError(Exception)` | Error de regla de negocio; lleva `code: ErrorCode` y `name: str \| None`. | RF-1.5–1.8, RF-2.3, RF-3.4, RF-3.5 |
| `MarkResult` (dataclass) | `habits`, `habit`, `already_done: bool`, `streak: int`. | RF-3.1–3.3 |
| `normalize_name(raw) -> str` | NFC, recorte y colapso de espacios. | RF-1.1, RF-1.2 |
| `name_key(name) -> str` | Clave de comparación sin mayúsculas. | RF-1.3 |
| `check_name(name) -> None` | Valida un nombre ya normalizado, en el orden de RF-1.5 a RF-1.8. | RF-1.4–1.8 |
| `validate_new_name(raw) -> str` | `normalize_name` + `check_name` (para `crear`). | RF-1, RF-7.6 paso 2 |
| `validate_lookup_name(raw) -> str` | `normalize_name` + solo la regla de vacío (para `hecho`). | RF-3.4, RF-3.5 |
| `find_habit(habits, name) -> Habit \| None` | Busca por `name_key`. | RF-1.3 |
| `add_habit(habits, name) -> list[Habit]` | Añade al final, sin fechas; `E-5` si ya existe. | RF-2.1, RF-2.3 |
| `mark_done(habits, name, today) -> MarkResult` | Marca hoy o detecta que ya estaba; `E-6` si no existe. | RF-3.1, RF-3.3, RF-3.5 |
| `is_done_today(habit, today) -> bool` | `today in habit.done_dates`. | RF-4.1, RF-5.6 |
| `compute_streak(done_dates, today) -> int` | Algoritmo de la sección 4.2. | RF-5.2–5.6 |
| `has_duplicate_names(names) -> bool` | Usado al validar los datos leídos. | RF-8.5 |

Las funciones que «modifican» devuelven una lista nueva; nunca mutan la
recibida. Así un error a mitad de camino no deja datos a medias en memoria.

### 2.2 `messages.py` — textos para el usuario

| Elemento | Texto | Cubre |
|----------|-------|-------|
| `HELP` | Bloque de ayuda exacto de la spec | RF-6.4, M-5 |
| `NO_HABITS` | M-4 | RF-4.3 |
| `days_label(n) -> str` | `"día"` si `n == 1`, si no `"días"` | RF-5.7 |
| `habit_created(name)` | M-1 | RF-2.2 |
| `marked_done(name, streak)` | M-2 | RF-3.2 |
| `already_done(name, streak)` | M-3 | RF-3.3 |
| `list_line(name, streak, done_today)` | `<nombre> \| racha: <N> <día\|días> \| <hecho hoy\|pendiente hoy>` | RF-4.1 |
| `error_text(code, name=None)` | E-1 a E-9; E-7 = `"Error: comando no válido."` + línea en blanco + `HELP` | RF-7.2, §5 |

Solo puntuación ASCII en los textos (comillas `"`), como exige la sección 5 de
la spec.

### 2.3 `storage.py` — persistencia

| Elemento público | Responsabilidad | Cubre |
|------------------|-----------------|-------|
| `DATA_DIR_NAME = ".habits"`, `DATA_FILE_NAME = "habits.json"`, `FORMAT_VERSION = 1` | Ubicación y versión del formato. | RF-8.2 |
| `default_data_file() -> Path \| None` | `Path.home() / ".habits" / "habits.json"`; `None` si no se puede determinar la carpeta personal. | RF-8.2 |
| `DataReadError`, `DataWriteError` | Errores que `cli` traduce a E-8 y E-9. | RF-8.5, RF-8.6 |
| `load_habits(path) -> list[Habit]` | Lee y valida (sección 3.3). Archivo inexistente -> `[]`. | RF-8.3, RF-8.5 |
| `save_habits(path, habits) -> None` | Escritura atómica (sección 3.4). | RF-8.1, RF-8.4, RF-8.6, RNF-4 |

### 2.4 `cli.py` — capa de interfaz

| Elemento | Responsabilidad | Cubre |
|----------|-----------------|-------|
| `COMMANDS = {"crear": 1, "hecho": 1, "listar": 0, "ayuda": 0}` | Comando -> número exacto de argumentos. | RF-6.1, RF-6.2 |
| `read_local_date() -> date` | Única lectura del reloj (`date.today()`). Se sustituye en las pruebas. | RF-5.1 |
| `main(argv=None, *, today=None, data_file=None) -> int` | Orquesta un comando y devuelve el código de salida. Los dos parámetros con nombre existen solo para las pruebas (RNF-5). | RF-6, RF-7 |

`cli.py` no contiene reglas: no normaliza, no compara nombres ni calcula
rachas. Solo encadena llamadas en el orden de RF-7.6 y elige el mensaje.

### 2.5 `__main__.py`

```text
reconfigurar stdout y stderr con errors="replace"     # RNF-6, ver T-14
raise SystemExit(cli.main(sys.argv[1:]))
```

---

## 3. Modelo de datos

### 3.1 En memoria `[§6 de la spec]`

```text
Habit
  name:       str               # nombre normalizado, mayúsculas como se escribió  [RF-1.2]
  done_dates: frozenset[date]   # fechas de calendario, sin hora                    [RF-5.2]

list[Habit]                     # el índice en la lista es el orden de creación   [RF-2.1, RF-4.2]
```

La racha y «hecho hoy» no se guardan: se calculan siempre a partir de
`done_dates` y de «hoy».

### 3.2 Formato del archivo `[RF-8.1, RF-8.2, §6 de la spec]`

- **Ubicación:** `<carpeta personal>/.habits/habits.json` (`Path.home()`).
- **Codificación:** UTF-8 sin BOM, fin de línea `\n`.
- **Estructura:** un objeto con exactamente dos claves:
  - `version`: entero, siempre `1`;
  - `habits`: lista de hábitos **en orden de creación**. Cada hábito es un
    objeto con exactamente dos claves:
    - `name`: cadena, nombre normalizado tal como se guardó;
    - `done_dates`: lista de cadenas `AAAA-MM-DD`, sin repetir. Al escribir se
      ordenan de menor a mayor; al leer se acepta cualquier orden.
- **Escritura:** `json.dumps(..., ensure_ascii=False, indent=2)` más un salto de
  línea final.

`version` no es un dato de ningún hábito, sino del formato del archivo: permite
detectar en el futuro un archivo de otro formato (principio 5). La posición en
el orden de creación es la posición en la lista `habits`.

**Ejemplo** (con «hoy» = 2026-10-23, produce exactamente el listado de ejemplo
de RF-4.1):

```json
{
  "version": 1,
  "habits": [
    {
      "name": "Leer libros",
      "done_dates": [
        "2026-10-19",
        "2026-10-20",
        "2026-10-21",
        "2026-10-22",
        "2026-10-23"
      ]
    },
    {
      "name": "Matemáticas",
      "done_dates": [
        "2026-10-22"
      ]
    },
    {
      "name": "Inglés",
      "done_dates": []
    }
  ]
}
```

```text
Leer libros | racha: 5 días | hecho hoy        <- marcado hoy y 4 días antes (RF-5.3)
Matemáticas | racha: 1 día | pendiente hoy     <- marcado solo ayer (RF-5.4, RF-5.7)
Inglés | racha: 0 días | pendiente hoy         <- sin marcas (RF-5.5)
```

### 3.3 Lectura y validación `[RF-8.3, RF-8.5]`

```text
function load_habits(path):
    if path is None: return []                      # carpeta personal indeterminable = sin datos
    try: raw = leer todos los bytes de path
    except FileNotFoundError: return []             # primer uso                        [RF-8.3]
    except OSError: raise DataReadError             # permisos, es una carpeta, etc.

    if len(raw) == 0: raise DataReadError           # archivo vacío                     [CL-32]
    text = decodificar raw como UTF-8 estricto      # fallo -> DataReadError
    data = json.loads(text, object_pairs_hook=rechazar_claves_repetidas)
                                                    # JSON inválido -> DataReadError

    exigir: data es dict con claves exactamente {"version", "habits"}
    exigir: type(data["version"]) is int y data["version"] == 1    # True no vale como 1
    exigir: data["habits"] es list
    para cada h en data["habits"]:
        exigir: h es dict con claves exactamente {"name", "done_dates"}
        exigir: h["name"] es str
                y normalize_name(h["name"]) == h["name"]           # ya normalizado
                y check_name(h["name"]) no lanza error             # cumple RF-1
        exigir: h["done_dates"] es list de str
        para cada s: exigir s encaja con ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ (ASCII)
                     y date.fromisoformat(s) no falla              # fecha imposible -> error
        exigir: sin fechas repetidas dentro del hábito
    exigir: not has_duplicate_names(nombres)                       # iguales según RF-1.3
    cualquier "exigir" que falle -> raise DataReadError
    return [Habit(name, frozenset(fechas)) ...]                    # en el orden del archivo
```

Las fechas posteriores a «hoy» se aceptan y se conservan tal cual `[RF-5.6]`.
`load_habits` nunca escribe: un archivo inválido no se toca `[RF-8.5]`.

### 3.4 Escritura atómica `[RF-8.1, RF-8.4, RF-8.6, RNF-4, RNF-7]`

```text
function save_habits(path, habits):
    if path is None: raise DataWriteError           # carpeta personal indeterminable    [RF-8.6]
    text = serializar(habits) según 3.2
    try:
        path.parent.mkdir(exist_ok=True)            # crea .habits, NO la carpeta personal  [RF-8.4]
        borrar, sin fallar, los "habits-*.tmp" que hayan quedado en path.parent
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix="habits-", suffix=".tmp")
        try:
            escribir text en fd (UTF-8), flush, os.fsync
            os.replace(tmp, path)                   # sustitución atómica en el mismo volumen
        except BaseException:
            borrar tmp si existe (ignorando errores)
            relanzar
    except (OSError, UnicodeError):
        raise DataWriteError                        # permisos, disco lleno, sin carpeta personal
```

- Si el proceso se interrumpe antes de `os.replace`, `habits.json` sigue con su
  contenido anterior; después, con el nuevo. Nunca a medias `[RNF-4]`.
- `mkdir` sin `parents=True`: si la carpeta personal no existe, falla y se
  muestra E-9, como pide RF-8.6.
- Un temporal solo puede sobrevivir a un corte abrupto (corte de luz, `kill -9`).
  Nunca se lee, y el siguiente guardado lo borra, así que al terminar queda un
  único archivo de datos `[RNF-4, principio 5]`.

---

## 4. Algoritmos

### 4.1 Nombres `[RF-1.1 a RF-1.8, RF-3.4, RF-3.5]`

```text
WHITESPACE = los 25 caracteres con la propiedad Unicode White_Space:
    U+0009–U+000D, U+0020, U+0085, U+00A0, U+1680, U+2000–U+200A,
    U+2028, U+2029, U+202F, U+205F, U+3000

function normalize_name(raw):                                     [RF-1.1]
    s = unicodedata.normalize("NFC", raw)                         # 1. forma compuesta
    s = quitar de ambos extremos los caracteres de WHITESPACE     # 2. recorte
    s = sustituir cada secuencia de 1+ caracteres de WHITESPACE por " "   # 3. colapso
    return s                                                      # mayúsculas intactas [RF-1.2]

function name_key(name):                                          [RF-1.3]
    return unicodedata.normalize("NFC", name.casefold())
    # casefold = plegado completo de Unicode: "Straße" y "STRASSE" -> "strasse"
    # las tildes se conservan: "matemáticas" != "matematicas"

function check_name(name):            # name ya normalizado; el orden es el de RF-7.6 paso 2
    if name == "":                                    raise HabitError(E-1)   [RF-1.5]
    if algún c en name tiene categoría Unicode "Cc":  raise HabitError(E-3)   [RF-1.6]
    if name empieza por "-" (U+002D):                 raise HabitError(E-4)   [RF-1.7]
    if len(name) > 50:                                raise HabitError(E-2)   [RF-1.4, RF-1.8]
    # len() cuenta puntos de código después de NFC: una «á» = 1, un emoji compuesto puede ser > 1

function validate_new_name(raw):        # crear
    name = normalize_name(raw); check_name(name); return name

function validate_lookup_name(raw):     # hecho: solo la regla de vacío            [RF-3.4, RF-3.5]
    name = normalize_name(raw)
    if name == "": raise HabitError(E-1)
    return name
```

Como tabulador, salto de línea, U+0085, U+2028 y U+2029 son espacios en blanco,
se convierten en espacio normal antes de buscar caracteres de control. Por eso
un nombre guardado nunca contiene un salto de línea, y cada hábito ocupa
exactamente una línea en `listar` `[RF-4.1]`.

### 4.2 Cálculo de la racha `[RF-5.2 a RF-5.6]`

```text
function compute_streak(done_dates: frozenset[date], today: date) -> int:
    if today in done_dates:                         # RF-5.3
        day = today
    else if today - 1 día in done_dates:            # RF-5.4: la racha sigue viva hoy
        day = today - 1 día
    else:                                           # RF-5.5
        return 0

    streak = 0
    while day in done_dates:
        streak = streak + 1
        if day == date.min: break                   # evita desbordar con fechas extremas
        day = day - 1 día
    return streak
```

- Se trabaja con `datetime.date` y `timedelta(days=1)`: no hay horas, así que un
  cambio de hora no afecta `[RF-5.2, CL-37]`. Fin de mes, de año y 29 de febrero
  los resuelve `date` `[CL-5]`.
- El recorrido empieza en «hoy» o «ayer» y solo va hacia atrás, así que las
  fechas futuras nunca cuentan `[RF-5.6, CL-17]`. `is_done_today` compara con
  igualdad exacta, así que una fecha futura tampoco cuenta como «hecho hoy»,
  hasta el día en que deja de ser futura `[CL-38]`.
- Coste: O(longitud de la racha), con búsquedas O(1) en el conjunto `[RNF-3]`.

### 4.3 Flujo de cada comando `[RF-2, RF-3, RF-4, RF-6, RF-7]`

```text
function main(argv, today=None, data_file=None):
    today = today if today is not None else read_local_date()   # una sola vez, lo primero [RF-5.1]
    try:
        command, arg = parse(argv)                  # paso 1 de RF-7.6 -> UsageError
        if data_file is None: data_file = storage.default_data_file()
        return run(command, arg, today, data_file)
    except UsageError:   stderr(error_text(E-7));             return 2   [RF-6.5, RF-7.3]
    except HabitError e: stderr(error_text(e.code, e.name));  return 1   [RF-7.4]
    except DataReadError:  stderr(error_text(E-8));           return 1   [RF-8.5]
    except DataWriteError: stderr(error_text(E-9));           return 1   [RF-8.6]

function parse(argv):                                          [RF-6.1, RF-6.2, RF-6.3, RF-6.5]
    if argv vacío: raise UsageError
    command = argv[0]; args = argv[1:]
    if command not in COMMANDS: raise UsageError   # distingue mayúsculas: "CREAR" falla
    if len(args) != COMMANDS[command]: raise UsageError
    return command, (args[0] if args else None)    # "" o "   " cuentan como argumento presente

crear(arg):                                                    [RF-2]
    name   = validate_new_name(arg)                # paso 2: E-1, E-3, E-4, E-2
    habits = storage.load_habits(data_file)        # paso 3: E-8
    habits = add_habit(habits, name)               # paso 4: E-5 con el nombre guardado
    storage.save_habits(data_file, habits)         # paso 5: E-9
    stdout(habit_created(name)); return 0          # M-1

hecho(arg):                                                    [RF-3]
    name   = validate_lookup_name(arg)             # paso 2: E-1
    habits = storage.load_habits(data_file)        # paso 3: E-8
    r      = mark_done(habits, name, today)        # paso 4: E-6 con el nombre normalizado
    if r.already_done:
        stdout(already_done(r.habit.name, r.streak)); return 0     # M-3, sin escribir
    storage.save_habits(data_file, r.habits)       # paso 5: E-9
    stdout(marked_done(r.habit.name, r.streak)); return 0          # M-2

listar():                                                      [RF-4]
    habits = storage.load_habits(data_file)        # E-8
    if habits vacío: stdout(NO_HABITS); return 0                   # M-4
    para cada h en habits (orden de la lista):
        stdout(list_line(h.name, compute_streak(h.done_dates, today), is_done_today(h, today)))
    return 0

ayuda():                                                       [RF-6.4]
    stdout(HELP); return 0                         # no lee los datos
```

Todas las comprobaciones que pueden fallar ocurren **antes** de
`save_habits`, y `save_habits` es atómico. Por eso ningún error modifica los
datos guardados `[RF-7.5]`. Solo se muestra el primer error porque cada paso
lanza una excepción que corta el flujo `[RF-7.6]`.

---

## 5. Contrato de la CLI `[RF-6, RF-7]`

**Invocación:** `python -m habits <comando> [argumento]`. Un nombre con
espacios va entre comillas. No hay opciones (`-h`, `--ayuda`…): todo lo que va
detrás del comando es el nombre.

| Invocación | Situación | Salida estándar | Salida de error | Código |
|------------|-----------|-----------------|-----------------|--------|
| `crear "<nombre>"` | Nombre válido y nuevo | M-1 | — | 0 |
| | Vacío / control / empieza por «-» / > 50 | — | E-1 / E-3 / E-4 / E-2 | 1 |
| | Datos ilegibles o no válidos | — | E-8 | 1 |
| | Ya existe (RF-1.3) | — | E-5 con el nombre guardado | 1 |
| | No se puede guardar | — | E-9 | 1 |
| `hecho "<nombre>"` | Existe y no está marcado hoy | M-2 | — | 0 |
| | Existe y ya está marcado hoy | M-3 | — | 0 |
| | Nombre vacío | — | E-1 | 1 |
| | Datos ilegibles o no válidos | — | E-8 | 1 |
| | No existe | — | E-6 con el nombre normalizado | 1 |
| | No se puede guardar | — | E-9 | 1 |
| `listar` | Hay hábitos | Una línea por hábito (RF-4.1) | — | 0 |
| | No hay hábitos | M-4 | — | 0 |
| | Datos ilegibles o no válidos | — | E-8 | 1 |
| `ayuda` | Siempre | M-5 | — | 0 |
| Sin comando, comando desconocido, `CREAR`, nº de argumentos incorrecto | | — | E-7 (incluye la ayuda) | 2 |

Reglas comunes:

- Cada mensaje termina con un salto de línea. E-7 es
  `Error: comando no válido.`, una línea vacía y el bloque de ayuda, todo por
  la salida de error.
- Ante cualquier error, la salida estándar queda vacía, y viceversa.
- Los textos son exactamente los de la sección 5 de la spec, con
  `{día|días}` según RF-5.7.
- Un fallo inesperado (un bug) no se captura: Python muestra la traza y termina
  con código 1. Los datos siguen intactos por la escritura atómica.

---

## 6. Decisiones técnicas

| # | Decisión | Justificación | Alternativa descartada | Cubre |
|---|----------|---------------|------------------------|-------|
| T-1 | Análisis manual de argumentos con la tabla `COMMANDS`. | `argparse` trata `-h` como opción (CL-24 exige E-4), escribe sus propios mensajes y no permite reproducir E-7 al pie de la letra. Con 4 comandos, el análisis manual ocupa pocas líneas. | `argparse` con mensajes personalizados. | RF-6, CL-24, CL-27 |
| T-2 | Textos en un módulo propio, `messages.py`. | Todo el español en un único archivo: el principio 6 se revisa de un vistazo y los textos exactos se prueban sin ejecutar comandos. | Textos repartidos por `cli.py`. | §5 de la spec, principio 6 |
| T-3 | La orquestación vive en `cli.py`, sin capa de servicios. | Son 4 comandos de 3 a 5 llamadas cada uno; una capa más añade un módulo sin reglas propias (RNF-8). Las reglas siguen en `core`. | Módulo `app.py` con casos de uso. | RF-7.6, principio 3 |
| T-4 | Errores como excepciones (`HabitError`, `DataReadError`, `DataWriteError`, `UsageError`). | La primera excepción corta el flujo: «solo el primer error» sale gratis y el orden queda escrito en el propio código. | Devolver códigos de error en cada función. | RF-7.6 |
| T-5 | Archivo = objeto `{"version", "habits"}` con `habits` como lista. | La lista conserva el orden de creación sin campo extra; `version` permite reconocer el formato. | Objeto indexado por nombre: pierde el orden y obliga a decidir qué variante de mayúsculas es la clave. | RF-2.1, RF-4.2, principio 5 |
| T-6 | Orden de creación = posición en la lista. | Un único origen de verdad; no hay posiciones repetidas ni huecos que validar. | Campo `position` en cada hábito. | RF-2.1, RF-4.2 |
| T-7 | Fechas como texto ISO `AAAA-MM-DD`, validado con expresión regular ASCII + `date.fromisoformat`. | Legible, ordenable y sin hora. La expresión regular evita que `fromisoformat` acepte otras formas (`20261023`) o dígitos no ASCII. | Números (`toordinal`) o marcas de tiempo: ilegibles y, las segundas, con hora y zona. | RF-5.2, RF-8.5 |
| T-8 | Fechas en memoria como `frozenset[date]`. | Comprobar «¿está marcado este día?» es O(1) y el conjunto no admite repetidos. | Lista ordenada recorrida con índices. | RF-5.3–5.6, RNF-3 |
| T-9 | Espacios en blanco = conjunto explícito `WHITESPACE` (propiedad Unicode `White_Space`). | `str.isspace()` y `str.split()` consideran espacio U+001C–U+001F, que son caracteres de control: se convertirían en espacios en lugar de dar E-3. | `str.strip()` / `" ".join(s.split())`. | RF-1.1, RF-1.6 |
| T-10 | Comparación con `NFC(casefold(nombre))`. | `casefold` aplica el plegado completo de Unicode («ß» = «ss») y respeta las tildes. | `lower()`: «ß».lower() es «ß», así que «Straße» y «STRASSE» serían distintos. | RF-1.3, CL-22 |
| T-11 | Caracteres de control = categoría Unicode `Cc`. | Es la definición estándar. Los caracteres de formato (`Cf`, p. ej. el unidor de ancho cero) se permiten porque forman los emojis compuestos que RF-1.4 contempla. | Rechazar también `Cf`. | RF-1.6, RF-1.4 |
| T-12 | Los nombres leídos del archivo deben estar ya normalizados; si no, E-8. | El programa siempre guarda nombres normalizados: uno que no lo está es una edición manual. Normalizarlo en silencio cambiaría los datos sin avisar y podría crear duplicados. | Normalizar al leer. | RF-8.5 |
| T-13 | Escritura atómica: temporal en la misma carpeta + `fsync` + `os.replace`. | El archivo queda entero en el estado anterior o en el nuevo, también si dos ejecuciones guardan a la vez. | Escribir directamente sobre `habits.json` (puede quedar a medias) o mantener una copia `.bak` (deja dos archivos de datos). | RNF-4, RNF-7, RF-7.5, RF-8.6 |
| T-14 | Codificación: archivo siempre en UTF-8 explícito; `stdout`/`stderr` con `errors="replace"`. | En Windows la codificación por defecto de los archivos no es UTF-8. En la consola, Python 3.12 ya escribe Unicode; si la salida se redirige a un archivo con una página de códigos antigua, un carácter imposible se sustituye por «?» en vez de romper el programa. | Forzar UTF-8 en toda la salida: en consumidores con página de códigos antigua se verían caracteres extraños en las tildes. | RNF-6 |
| T-15 | Ubicación `~/.habits/habits.json` con `Path.home()`. | Fija, dentro de la carpeta personal e independiente del directorio actual; misma ruta en Windows y en sistemas Unix. | Carpetas propias de cada sistema (`%APPDATA%`, XDG): más código y más casos que probar. | RF-8.2, CL-19 |
| T-16 | Las pruebas inyectan «hoy» y la ruta del archivo como parámetros de `main()`. | No crea una vía oculta para que el usuario elija dónde se guardan los datos (fuera de alcance, §9). | Variables de entorno `HABITS_TODAY` / `HABITS_DATA_FILE`. | RNF-5, RF-5.1, RF-8.2 |
| T-17 | Sin bloqueo de archivo entre ejecuciones simultáneas. | La spec acepta perder un cambio (RNF-7); la escritura atómica basta para que el archivo siga legible. | Archivo de bloqueo: código extra y bloqueos huérfanos tras un fallo. | RNF-7 |
| T-18 | `pyproject.toml` solo con `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `pythonpath = ["."]`). | `pytest -q` funciona desde la raíz sin instalar el paquete. | Instalar el paquete en modo editable: un paso más para el mantenedor. | Principio 4 |

---

## 7. Riesgos y limitaciones conocidas

- **Argumento vacío en Windows PowerShell 5.1:** esa versión elimina los
  argumentos `""` al llamar a un programa externo, así que `crear ""` llega como
  `crear` sin argumento y produce E-7 en vez de E-1. Es un fallo de PowerShell,
  no del programa (PowerShell 7.3+ y el símbolo del sistema lo pasan bien). Las
  pruebas de RF-6.3 llaman a `main()` directamente.
- **Bytes no UTF-8 en los argumentos (solo Unix con locale no UTF-8):** Python
  los representa como sustitutos sueltos; al guardar fallaría la codificación y
  se muestra E-9 sin tocar los datos (T-14). Fuera de RNF-6, que solo exige
  terminales UTF-8 y las predeterminadas de Windows.
- **`os.replace` en Windows** puede fallar si otro proceso tiene abierto
  `habits.json` (un antivirus, otra ejecución). Se muestra E-9 y los datos
  quedan intactos.
- **Carpeta personal sincronizada (OneDrive):** fuera del control del programa
  (RNF-2).

---

## 8. Estrategia de tests

### 8.1 Pirámide y archivos

| Archivo | Nivel | Qué prueba | Técnica |
|---------|-------|------------|---------|
| `test_core.py` | Unidad | Cada función pública de `core` | Funciones puras, `pytest.mark.parametrize`, fechas fijas |
| `test_messages.py` | Unidad | Texto exacto de M-1 a M-5 y E-1 a E-9, `days_label`, `list_line` | Comparación de cadenas literales copiadas de la spec |
| `test_storage.py` | Integración | Formato, validación, escritura atómica, errores de E/S | `tmp_path`, `monkeypatch` de `os.replace`, `tempfile.mkstemp` y `Path.home` |
| `test_cli.py` | Aceptación | Cada comando de principio a fin: salida, salida de error, código, datos | `main(argv, today=..., data_file=...)` + `capsys` |
| `test_e2e.py` | Humo | El programa real arranca con `python -m habits` | `subprocess` con `HOME` y `USERPROFILE` apuntando a `tmp_path` |
| `test_architecture.py` | Constitución | Principios 1, 3, 4 y 5 y RNF-2 | Análisis de los fuentes con `ast` |

### 8.2 Fixtures (`conftest.py`)

- `today`: `date(2026, 10, 23)`, para que las pruebas no dependan del reloj.
- `data_file`: `tmp_path / "home" / ".habits" / "habits.json"`, con
  `tmp_path / "home"` creada y `.habits` sin crear (para probar RF-8.4).
- `run(*argv, today=...)`: llama a `main(list(argv), today=..., data_file=...)`
  y devuelve `(código, stdout, stderr)` usando `capsys`.
- `write_raw(contenido)`: escribe bytes arbitrarios en `data_file` para preparar
  datos corruptos.
- `assert_unchanged`: guarda los bytes de `data_file` (o su ausencia) antes del
  comando y comprueba que no han cambiado después. Se usa en **todas** las
  pruebas de error `[RF-7.5]`.

### 8.3 Técnicas para los casos difíciles

| Caso | Cómo se prueba |
|------|----------------|
| Medianoche entre dos ejecuciones `[CL-15]` | Dos llamadas a `run`, con `today` = D y D+1. |
| Una ejecución que cruza la medianoche `[CL-36, RF-5.1]` | Sin pasar `today`; `monkeypatch` de `cli.read_local_date` con una función que devuelve D la primera vez y D+1 después. Se comprueba que se llamó una sola vez y que se guardó D. |
| Interrupción durante el guardado `[RNF-4]` | `monkeypatch` de `os.replace` para que lance `KeyboardInterrupt`: el archivo conserva sus bytes anteriores y no queda ningún `habits-*.tmp`. |
| Disco lleno / sin permisos `[CL-35, RF-8.6]` | `monkeypatch` de `os.fsync` o `tempfile.mkstemp` para que lance `OSError` (`chmod` no protege carpetas en Windows, así que no se usa). Resultado: E-9, código 1, datos intactos. |
| Carpeta personal inexistente `[RF-8.6]` | `data_file` dentro de una carpeta «home» que no existe: E-9 y no se crea la carpeta personal. |
| Ejecuciones simultáneas `[RNF-7]` | Dos `load_habits` seguidos de dos `save_habits`: el archivo final es válido y contiene el cambio del segundo. |
| Mismo hábito desde dos directorios `[CL-19, RF-8.2]` | `monkeypatch` de `Path.home` y `monkeypatch.chdir` a dos carpetas distintas, sin pasar `data_file`. |
| Orden de errores `[RF-7.6, CL-34]` | Combinaciones: datos corruptos + `crear ""` -> E-1; datos corruptos + nombre duplicado -> E-8; duplicado + fallo al guardar -> E-5; nombre con control y > 50 -> E-3; «-» y > 50 -> E-4. |
| `hecho` no aplica el resto de RF-1 `[RF-3.5]` | `hecho "-x"` y `hecho` con 51 caracteres -> E-6, no E-4 ni E-2. |
| Datos no válidos `[RF-8.5, CL-14, CL-32, CL-33]` | Tabla parametrizada: 0 bytes, no UTF-8, JSON roto, claves de más o de menos, claves repetidas, `version` 2 o `true`, fecha `2026-02-30`, fecha `20261023`, fecha repetida, dos hábitos iguales según RF-1.3, nombre sin normalizar, nombre de 51 caracteres. Cada caso: `listar` da E-8, y `crear "Nuevo"` da E-8 sin sobrescribir el archivo. |

### 8.4 Reglas de escritura de las pruebas

- El nombre de cada prueba o su `id` de `parametrize` cita el requisito o caso
  que cubre (`test_rf_5_4_streak_alive_until_end_of_today`, `id="CL-22"`), para
  poder comprobar la sección 10 de la spec con una búsqueda.
- Los textos esperados se escriben literales en la prueba, copiados de la
  spec; no se construyen con las funciones de `messages.py`.
- Ninguna prueba lee el reloj real ni la carpeta personal real.

### 8.5 Requisitos no funcionales

| RNF | Verificación (según §10 de la spec) |
|-----|--------------------------------------|
| RNF-1, RNF-6 | Revisión manual en PowerShell, símbolo del sistema y una terminal UTF-8: `crear "Inglés"`, `crear "Año"`, `listar`, `ayuda`. |
| RNF-2 | Revisión de código + `test_architecture.py` comprueba que no se importan `socket`, `urllib`, `http` ni `ssl`. |
| RNF-3 | Medición manual: un script auxiliar genera 100 hábitos × 365 días en una carpeta personal temporal y se mide `listar`, `crear` y `hecho` con `Measure-Command` (cambiando `USERPROFILE`). El resultado se anota en este plan o en el PR. |
| RNF-4, RNF-7 | Pruebas automáticas de la sección 8.3. |
| RNF-5 | Lo demuestran las propias pruebas: ninguna usa el reloj ni la carpeta personal reales. |
| RNF-8 | Revisión de código contra la spec. |

### 8.6 Pruebas de la constitución (`test_architecture.py`)

- **Principio 1 / RNF-2:** todos los `import` de `habits/` están en
  `sys.stdlib_module_names` o son del propio paquete, y ninguno es de red.
- **Principio 3:** `core.py` no llama a `print`, `input` ni `open`, y no importa
  `os`, `sys`, `io`, `pathlib` ni `json`.
- **Principio 4:** cada función pública definida en `core.py` aparece en
  `tests/test_core.py`.
- **Principio 5:** solo `storage.py` importa `json`.

---

## 9. Trazabilidad

### 9.1 Requisitos funcionales

| RF | Diseño | Pruebas |
|----|--------|---------|
| RF-1.1 | `normalize_name`, `WHITESPACE` (4.1, T-9) | core: CL-8, CL-16, CL-20, CL-21 |
| RF-1.2 | `normalize_name` no cambia mayúsculas; `add_habit` guarda el nombre normalizado | core; cli: `crear "  LeEr  "` y luego `listar` muestra `LeEr` |
| RF-1.3 | `name_key` (T-10), `find_habit`, `add_habit` | core: CL-7, CL-11, CL-22; cli: CL-12 |
| RF-1.4 | `check_name` con `len` tras NFC | core: CL-10, CL-21, CL-26, emoji compuesto |
| RF-1.5 | `check_name` -> E-1 | core: CL-9; cli: CL-28 |
| RF-1.6 | `check_name` -> E-3 (T-11) | core: CL-25, U+001C; cli: E-3 |
| RF-1.7 | `check_name` -> E-4 | core; cli: CL-24 |
| RF-1.8 | `check_name` -> E-2 | core: CL-10, CL-26 |
| RF-2.1 | `add_habit` (al final, sin fechas); flujo `crear` (4.3) | core; cli: creación + `listar` |
| RF-2.2 | `messages.habit_created` | messages; cli |
| RF-2.3 | `add_habit` -> E-5 con el nombre guardado | core; cli: CL-7, CL-16, CL-22 |
| RF-3.1 | `mark_done` añade `today` | core; cli: el archivo contiene la fecha |
| RF-3.2 | `messages.marked_done` + `compute_streak` | cli: CL-12, CL-18 |
| RF-3.3 | `mark_done.already_done`; `hecho` no guarda | cli: CL-6 + `assert_unchanged` |
| RF-3.4 | `validate_lookup_name` -> E-1 | core; cli: CL-29 |
| RF-3.5 | `mark_done` -> E-6; `validate_lookup_name` no aplica el resto de RF-1 | core; cli: `hecho "-x"`, 51 caracteres |
| RF-4.1 | `messages.list_line`, flujo `listar` | messages; cli: ejemplo de la spec (3.2), CL-40 |
| RF-4.2 | Orden de la lista (T-6) | cli: crear B, A, C -> se listan B, A, C |
| RF-4.3 | `messages.NO_HABITS` | cli: CL-13 |
| RF-5.1 | `read_local_date` una vez al inicio de `main` | cli: CL-15, CL-36 |
| RF-5.2 | `date` + `timedelta` (4.2) | core: CL-5, CL-37 |
| RF-5.3 | `compute_streak`, rama «hoy» | core: CL-3, CL-39 |
| RF-5.4 | `compute_streak`, rama «ayer» | core: CL-2 |
| RF-5.5 | `compute_streak`, rama 0 | core: CL-1, CL-4 |
| RF-5.6 | Recorrido hacia atrás; `is_done_today`; `load`/`save` conservan fechas futuras | core: CL-17, CL-38; storage: ida y vuelta con fecha futura |
| RF-5.7 | `messages.days_label` | messages: 0, 1, 2, 400; cli: CL-18 |
| RF-6.1 | `COMMANDS` (T-1) | cli: CL-30 |
| RF-6.2 | `COMMANDS` (aridad) | cli: CL-23, CL-27, CL-31 |
| RF-6.3 | `parse` cuenta `""` como argumento | cli: CL-28, CL-29 |
| RF-6.4 | `messages.HELP` | messages; cli: CL-41; e2e |
| RF-6.5 | `parse` -> `UsageError` -> E-7 | cli: CL-27, CL-28, CL-30, CL-31; e2e |
| RF-7.1 | `main`: mensajes de éxito a stdout, código 0 | cli: todas las pruebas de éxito comprueban stdout, stderr vacío y 0 |
| RF-7.2 | `main`: errores a stderr | cli: todas las pruebas de error comprueban stderr y stdout vacío |
| RF-7.3 | `UsageError` -> 2 | cli; e2e |
| RF-7.4 | Resto de errores -> 1 | cli: un caso por E-1 a E-6, E-8, E-9 |
| RF-7.5 | Validar antes de guardar + escritura atómica (4.3, 3.4) | cli: `assert_unchanged` en todas las pruebas de error |
| RF-7.6 | Orden de llamadas en cada flujo + excepciones (T-4) | cli: CL-34 y combinaciones de 8.3 |
| RF-8.1 | `save_habits`, `load_habits` | storage: ida y vuelta; cli: ejecuciones sucesivas |
| RF-8.2 | `default_data_file` (T-15) | storage; cli: CL-19; e2e |
| RF-8.3 | `load_habits`: archivo inexistente -> `[]` | storage; cli: CL-13 |
| RF-8.4 | `mkdir(exist_ok=True)` sin `parents` | storage: crea `.habits`, no crea la carpeta personal |
| RF-8.5 | Validación de 3.3 (T-7, T-12) | storage y cli: CL-14, CL-32, CL-33 y tabla de 8.3 |
| RF-8.6 | `save_habits` -> `DataWriteError` -> E-9 | storage y cli: CL-35, carpeta personal inexistente |

### 9.2 Casos límite

| Archivo de pruebas | Casos |
|--------------------|-------|
| `test_core.py` | CL-1, CL-2, CL-3, CL-4, CL-5, CL-8, CL-9, CL-10, CL-11, CL-16, CL-17, CL-20, CL-21, CL-22, CL-25, CL-26, CL-37, CL-38, CL-39 |
| `test_cli.py` | CL-6, CL-7, CL-12, CL-13, CL-14, CL-15, CL-18, CL-19, CL-23, CL-24, CL-27, CL-28, CL-29, CL-30, CL-31, CL-34, CL-35, CL-36, CL-40, CL-41 |
| `test_storage.py` | CL-14, CL-17 (se conserva), CL-32, CL-33, CL-35 |
| `test_e2e.py` | CL-19, CL-30, CL-41 |

Los 41 casos límite tienen al menos una prueba.

### 9.3 Mensajes

M-1 a M-5 y E-1 a E-9 se comprueban con su texto literal en
`test_messages.py`, y cada uno aparece además en al menos una prueba de
`test_cli.py` junto con su salida y su código de salida.
