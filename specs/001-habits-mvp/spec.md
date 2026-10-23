# Spec 001 — MVP de habits-cli

- **Estado:** aprobada
- **Fecha:** 2026-10-23

## 1. Contexto y objetivo

Mantener un hábito de estudio cuesta, sobre todo, porque no se ve el progreso.
Ver una racha de días consecutivos motiva a no romperla.

El objetivo de este MVP es que una persona pueda, desde la terminal y en pocos
segundos:

1. dar de alta los hábitos de estudio que quiere mantener,
2. anotar que hoy ha cumplido uno de ellos, y
3. ver todos sus hábitos con su racha actual y si ya los ha hecho hoy.

Es un proyecto educativo. Las reglas deben ser pocas, explícitas y fáciles de
verificar, para que pueda mantenerlo un desarrollador junior.

## 2. Usuarios

- **Estudiante (usuario principal):** usa la terminal con soltura básica,
  trabaja en un solo equipo y quiere un registro rápido, sin cuentas ni conexión.
- **Desarrollador junior (mantenedor):** necesita que cada regla esté escrita y
  se pueda comprobar con pruebas automáticas.

## 3. Historias de usuario

- **HU-1:** Como estudiante, quiero crear un hábito con un nombre para empezar a
  registrar su cumplimiento.
- **HU-2:** Como estudiante, quiero marcar un hábito como hecho hoy para que mi
  racha avance.
- **HU-3:** Como estudiante, quiero listar mis hábitos con su racha y si ya los
  hice hoy para saber qué me falta y no romper ninguna racha.

## 4. Requisitos funcionales

Los criterios de aceptación siguen la notación EARS:
*El sistema deberá…* (ubicuo), *Cuando…* (evento), *Mientras…* (estado) y
*Si…, entonces…* (comportamiento no deseado).

### RF-1 — Crear un hábito (HU-1)

- **RF-1.1** Cuando el usuario ejecute «crear» con un nombre válido, el sistema
  deberá guardar el hábito sin días marcados y confirmar la creación mostrando
  el nombre.
- **RF-1.2** El sistema deberá normalizar el nombre antes de validarlo: eliminar
  los espacios al principio y al final, y reducir a uno los espacios seguidos del
  interior. Deberá guardar el nombre normalizado respetando las mayúsculas y
  minúsculas con que se escribió.
- **RF-1.3** Si el nombre queda vacío después de normalizarlo, entonces el
  sistema deberá rechazar la creación con un error.
- **RF-1.4** Si el nombre normalizado tiene más de 50 caracteres, entonces el
  sistema deberá rechazar la creación con un error que indique el límite.
- **RF-1.5** Si ya existe un hábito con el mismo nombre sin distinguir mayúsculas
  y minúsculas, entonces el sistema deberá rechazar la creación con un error que
  indique el nombre existente.

### RF-2 — Marcar un hábito como hecho hoy (HU-2)

- **RF-2.1** El sistema deberá identificar el hábito por su nombre, normalizado
  igual que en RF-1.2 y sin distinguir mayúsculas y minúsculas.
- **RF-2.2** Cuando el usuario ejecute «hecho» con un hábito existente que no
  está marcado hoy, el sistema deberá registrar la fecha de hoy para ese hábito y
  confirmarlo mostrando el nombre y la racha resultante (por ejemplo: «Leer
  marcado como hecho hoy. Racha: 5 días»).
- **RF-2.3** Si el hábito ya estaba marcado hoy, entonces el sistema deberá
  informar de que ya estaba marcado mostrando la racha actual, no modificar los
  datos y terminar con éxito.
- **RF-2.4** Si no existe ningún hábito con ese nombre, entonces el sistema
  deberá mostrar un error que indique el nombre buscado.

### RF-3 — Listar hábitos (HU-3)

- **RF-3.1** Cuando el usuario ejecute «listar», el sistema deberá mostrar una
  línea de texto por hábito con su nombre, su racha actual (RF-4) y si está
  hecho hoy, con este formato:

  ```text
  Leer libros — racha: 5 días — hecho hoy
  Matemáticas — racha: 1 día — pendiente hoy
  Inglés — racha: 0 días — pendiente hoy
  ```

- **RF-3.2** El sistema deberá escribir «día» en singular cuando la racha sea 1 y
  «días» en cualquier otro caso.
- **RF-3.3** El sistema deberá mostrar los hábitos en el orden en que se crearon.
- **RF-3.4** Mientras no exista ningún hábito, el sistema deberá mostrar un
  mensaje que explique cómo crear el primero y terminar con éxito.

### RF-4 — Cálculo de la racha

- **RF-4.1** El sistema deberá usar como «hoy» la fecha local del equipo en el
  momento de ejecutar el comando.
- **RF-4.2** Mientras el hábito esté marcado hoy, el sistema deberá calcular la
  racha como el número de días consecutivos marcados que terminan hoy.
- **RF-4.3** Mientras el hábito no esté marcado hoy pero sí ayer, el sistema
  deberá calcular la racha como el número de días consecutivos marcados que
  terminan ayer (la racha sigue viva hasta que termine el día de hoy).
- **RF-4.4** Si el hábito no está marcado ni hoy ni ayer, entonces el sistema
  deberá mostrar una racha de 0.
- **RF-4.5** Si hay días marcados posteriores a hoy (por ejemplo, porque el
  reloj del equipo se ha atrasado), entonces el sistema deberá ignorarlos al
  calcular la racha y al decidir si está hecho hoy, y deberá conservarlos en los
  datos guardados.

### RF-5 — Errores y persistencia

- **RF-5.1** Si ocurre cualquier error, entonces el sistema deberá mostrar un
  mensaje claro en español por la salida de error, terminar con un código de
  salida distinto de 0 y no modificar los datos guardados.
- **RF-5.2** Cuando una operación termine con éxito, el sistema deberá conservar
  sus cambios para las siguientes ejecuciones.
- **RF-5.3** Mientras no existan datos guardados (primer uso), el sistema deberá
  comportarse como si no hubiera ningún hábito.
- **RF-5.4** Si los datos guardados no se pueden leer o tienen un formato
  inválido, entonces el sistema deberá mostrar un error y no deberá
  sobrescribirlos.
- **RF-5.5** Si el usuario escribe un comando desconocido u omite un argumento
  obligatorio, entonces el sistema deberá mostrar cómo se usa y terminar con un
  código de salida distinto de 0.
- **RF-5.6** El sistema deberá guardar y leer los datos siempre en un lugar fijo
  dentro de la carpeta personal del usuario, el mismo sea cual sea el directorio
  desde el que se ejecute el comando.

## 5. Requisitos no funcionales

- **RNF-1 Idioma:** todo lo que ve o escribe el usuario está en español: los
  nombres de los comandos («crear», «hecho» y «listar») y todos los mensajes,
  incluidos los de error y la ayuda.
- **RNF-2 Local y sin conexión:** funciona sin red, sin cuentas y sin servicios
  externos; los datos se guardan solo en el equipo del usuario.
- **RNF-3 Rapidez:** cada comando responde en menos de 1 segundo con 100 hábitos
  y un año de días marcados en cada uno.
- **RNF-4 Integridad:** una ejecución interrumpida no deja los datos guardados
  ilegibles.
- **RNF-5 Verificabilidad:** el cálculo de la racha se puede comprobar con
  pruebas automáticas usando fechas fijas, sin depender del día real.
- **RNF-6 Simplicidad:** la funcionalidad se limita a lo descrito en esta spec;
  cualquier ampliación necesita una spec nueva.

## 6. Casos límite

| # | Situación | Resultado esperado |
|---|-----------|--------------------|
| CL-1 | Hábito recién creado, sin marcar | Racha 0, no hecho hoy |
| CL-2 | Marcado ayer y anteayer, hoy no | Racha 2, no hecho hoy (RF-4.3) |
| CL-3 | Marcado hoy, ayer no, anteayer sí | Racha 1: el hueco rompe la racha |
| CL-4 | Marcado anteayer, ni ayer ni hoy | Racha 0 |
| CL-5 | Días consecutivos que cruzan fin de mes, fin de año o un 29 de febrero | Cuentan como consecutivos |
| CL-6 | Marcar dos veces el mismo día | Aviso, éxito, sin cambios (RF-2.3) |
| CL-7 | Crear «Leer» existiendo «leer» | Error de duplicado (RF-1.5) |
| CL-8 | Crear « Leer » (con espacios) | Se guarda como «Leer» (RF-1.2) |
| CL-9 | Nombre formado solo por espacios | Error de nombre vacío (RF-1.3) |
| CL-10 | Nombre de exactamente 50 caracteres / de 51 | Se acepta / error (RF-1.4) |
| CL-11 | «Matemáticas» frente a «MATEMÁTICAS» | Mismo hábito; «Matematicas» sin tilde es otro |
| CL-12 | Marcar «LEER» cuando existe «Leer» | Marca «Leer» (RF-2.1) |
| CL-13 | Primer uso, sin datos guardados | Listado vacío con mensaje de ayuda (RF-3.4, RF-5.3) |
| CL-14 | Datos guardados corruptos | Error y los datos no se tocan (RF-5.4) |
| CL-15 | Marcar justo antes de medianoche y otra vez justo después | Son dos días distintos; racha +1 |
| CL-16 | Crear «Leer  libros» (dos espacios) existiendo «Leer libros» | Error de duplicado (RF-1.2, RF-1.5) |
| CL-17 | Hay un día marcado posterior a hoy | No cuenta para la racha ni para «hecho hoy», pero se conserva (RF-4.5) |
| CL-18 | Racha de 1 | Se muestra «1 día», en singular (RF-3.2) |
| CL-19 | Ejecutar desde dos directorios distintos | Se ven los mismos hábitos (RF-5.6) |

## 7. Fuera de alcance

- Marcar días pasados o futuros: solo se puede marcar el día de hoy.
- Borrar o renombrar hábitos, y desmarcar un día.
- Racha récord, historial o calendario de días marcados.
- Frecuencias no diarias (por ejemplo, «3 veces por semana»): todos los hábitos
  son diarios.
- Recordatorios, notificaciones, estadísticas y exportación de datos.
- Varios usuarios, sincronización entre equipos e interfaz gráfica.
- Elegir dónde se guardan los datos.

## 8. Criterios de finalización

- Cada criterio de aceptación RF-x.y tiene al menos una prueba automática que
  lo cubre, y todas pasan.
- Cada caso límite CL-x tiene al menos una prueba automática que lo cubre.
- Los mensajes al usuario están en español y se han revisado.
- Se cumplen todos los principios de `docs/constitution.md`.
- No queda ninguna duda abierta en la sección 9.
- La spec está aprobada antes de empezar el plan.

## 9. Dudas abiertas

No queda ninguna duda abierta. Estas son las que se resolvieron:

| # | Duda | Decisión | Dónde |
|---|------|----------|-------|
| D-1 | ¿Idioma de los nombres de los comandos? | Español: «crear», «hecho», «listar» | RNF-1 |
| D-2 | ¿La confirmación al marcar muestra la racha? | Sí, también en el aviso de «ya estaba marcado» | RF-2.2, RF-2.3 |
| D-3 | ¿Se normalizan los espacios internos de los nombres? | Sí, varios espacios seguidos se reducen a uno | RF-1.2, RF-2.1 |
| D-4 | ¿Qué pasa con los días marcados posteriores a hoy? | Se ignoran en los cálculos, pero se conservan | RF-4.5 |
| D-5 | ¿Formato del listado? | Una línea de texto por hábito, sin símbolos | RF-3.1, RF-3.2 |
| D-6 | ¿El usuario elige dónde se guardan los datos? | No: lugar fijo en su carpeta personal | RF-5.6 |
