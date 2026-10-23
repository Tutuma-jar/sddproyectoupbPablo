# Constitución — habits-cli

1. **Stack mínimo**: solo Python 3.12+ y su biblioteca estándar. La única dependencia externa es pytest, y solo para los tests.
2. **Spec primero**: ningún cambio de comportamiento entra sin una spec aprobada en `specs/`. Si el código y la spec no coinciden, se corrige el código.
3. **Núcleo puro**: `habits/core.py` no hace E/S (nada de `print`, `input` ni archivos). `habits/cli.py` solo lee los argumentos y muestra los resultados.
4. **Tests obligatorios**: cada función pública del núcleo tiene tests en `tests/`. `pytest -q` debe pasar antes de cada commit.
5. **Persistencia JSON local**: los datos van en un único archivo JSON, que solo `habits/storage.py` lee y escribe. Antes de cambiar su formato hay que actualizar la spec.
6. **Idioma**: identificadores, nombres de archivo y comentarios en inglés; los mensajes al usuario, en español.

La propuesta, las decisiones y cómo verificar cada principio están en [`constitution-proposal.md`](constitution-proposal.md).
