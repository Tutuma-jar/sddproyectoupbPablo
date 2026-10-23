# Propuesta de constitución — habits-cli

Proyecto educativo: CLI en Python para registrar hábitos de estudio y calcular
rachas de días consecutivos. Debe poder mantenerlo un desarrollador junior.

## Objetivo

Seis principios innegociables, cortos y verificables (máximo 15 líneas), que cubren:

- simplicidad del stack,
- relación entre spec y código,
- separación entre lógica e interfaz,
- política de tests,
- persistencia de datos,
- idioma del código y los mensajes.

## Principios propuestos

1. **Stack mínimo**: solo Python 3.12+ y su biblioteca estándar. La única dependencia externa es pytest, y solo para los tests.
2. **Spec primero**: ningún cambio de comportamiento entra sin una spec aprobada en `specs/`. Si el código y la spec no coinciden, se corrige el código.
3. **Núcleo puro**: `habits/core.py` no hace E/S (nada de `print`, `input` ni archivos). `habits/cli.py` solo lee los argumentos y muestra los resultados.
4. **Tests obligatorios**: cada función pública del núcleo tiene tests en `tests/`. `pytest -q` debe pasar antes de cada commit.
5. **Persistencia JSON local**: los datos van en un único archivo JSON, que solo `habits/storage.py` lee y escribe. Antes de cambiar su formato hay que actualizar la spec.
6. **Idioma**: identificadores, nombres de archivo y comentarios en inglés; los mensajes al usuario, en español.

## Cómo se verifica cada principio

| # | Principio | Verificación |
|---|-----------|--------------|
| 1 | Stack mínimo | Los imports de `habits/` solo usan la biblioteca estándar; no hay más dependencias que pytest. |
| 2 | Spec primero | Cada PR que cambia comportamiento enlaza su spec en `specs/`. |
| 3 | Núcleo puro | `grep -nE "print\(|input\(|open\(" habits/core.py` no devuelve nada. |
| 4 | Tests obligatorios | `pytest -q` pasa; cada función pública de `core.py` aparece en `tests/`. |
| 5 | Persistencia JSON | `grep -rn "import json" habits/` solo encuentra `storage.py`. |
| 6 | Idioma | Revisión de código: nombres y comentarios en inglés, textos al usuario en español. |

## Decisiones tomadas

### Principio 2: ¿qué manda si spec y código no coinciden?

- **Opciones:** (a) se corrige siempre el código; (b) se corrige uno de los dos y se documenta.
- **Decisión:** (a) se corrige el código.
- **Motivo:** una regla sin excepciones es más fácil de aplicar para un junior. Si la spec
  está mal, se cambia primero la spec (con su revisión) y después el código, así que la
  regla sigue cumpliéndose.

### Principio 6: ¿en qué idioma van los comentarios?

- **Opciones:** (a) comentarios en inglés; (b) comentarios en español.
- **Decisión:** (a) comentarios en inglés.
- **Motivo:** así todo el código está en un único idioma, igual que los identificadores.
  El español queda solo para lo que ve el usuario, lo que hace la regla fácil de revisar.

## Resultado

El texto final aprobado está en [`constitution.md`](constitution.md).
