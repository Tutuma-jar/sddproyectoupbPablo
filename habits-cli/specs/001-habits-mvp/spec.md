# Spec 001 — MVP de habits-cli

- **Estado:** versión 2, aprobada
- **Fecha:** 2026-10-23

### Historial

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1 | 2026-10-23 | Primera versión, aprobada. |
| 2 | 2026-10-23 | Resuelve los 36 hallazgos de la revisión de QA (en esta misma carpeta). Se renumeran los requisitos. Aprobada. |

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
- **HU-4:** Como estudiante, quiero consultar la ayuda para recordar qué
  comandos hay y cómo se usan.

## 4. Requisitos funcionales

Los criterios de aceptación siguen la notación EARS:
*El sistema deberá…* (ubicuo), *Cuando…* (evento), *Mientras…* (estado) y
*Si…, entonces…* (comportamiento no deseado, siempre un error).

Los textos entre corchetes (M-x, E-x) son los mensajes exactos de la sección 5.

### RF-1 — Nombres de hábito

- **RF-1.1** El sistema deberá normalizar todo nombre que reciba, en este orden:
  1. pasarlo a la forma Unicode compuesta (una «á» escrita con dos códigos
     pasa a ser un solo carácter);
  2. eliminar los espacios en blanco del principio y del final;
  3. sustituir cada secuencia de espacios en blanco del interior por un único
     espacio normal.

  Se considera espacio en blanco cualquier carácter de espacio de Unicode,
  incluidos el tabulador, el salto de línea y el espacio de no separación.
- **RF-1.2** El sistema deberá guardar el nombre normalizado respetando las
  mayúsculas y minúsculas con que se escribió.
- **RF-1.3** El sistema deberá considerar iguales dos nombres cuando sus formas
  normalizadas coincidan sin distinguir mayúsculas y minúsculas, según las
  reglas completas de Unicode («ß», «SS» y «ss» son iguales). Las tildes sí
  distinguen: «Matemáticas» y «Matematicas» son nombres distintos.
- **RF-1.4** El sistema deberá contar la longitud de un nombre en caracteres
  Unicode después de normalizarlo. Un emoji compuesto puede contar como
  varios caracteres.
- **RF-1.5** Si el nombre normalizado está vacío, entonces el sistema deberá
  rechazarlo con [E-1].
- **RF-1.6** Si el nombre normalizado contiene caracteres de control, entonces
  el sistema deberá rechazarlo con [E-3].
- **RF-1.7** Si el nombre normalizado empieza por «-», entonces el sistema
  deberá rechazarlo con [E-4].
- **RF-1.8** Si el nombre normalizado tiene más de 50 caracteres, entonces el
  sistema deberá rechazarlo con [E-2].

### RF-2 — Crear un hábito (HU-1)

- **RF-2.1** Cuando el usuario ejecute `crear` con un nombre que cumple RF-1 y
  no es igual (RF-1.3) a ningún hábito existente, el sistema deberá guardar el
  hábito sin días marcados y en la última posición del orden de creación.
- **RF-2.2** Cuando el sistema guarde un hábito nuevo, deberá mostrar [M-1] con
  el nombre guardado.
- **RF-2.3** Si el nombre es igual (RF-1.3) al de un hábito existente, entonces
  el sistema deberá rechazar la creación con [E-5], mostrando el nombre del
  hábito existente tal como está guardado.

### RF-3 — Marcar un hábito como hecho hoy (HU-2)

- **RF-3.1** Cuando el usuario ejecute `hecho` con un nombre igual (RF-1.3) al
  de un hábito existente que no está marcado hoy, el sistema deberá registrar la
  fecha de hoy para ese hábito.
- **RF-3.2** Cuando el sistema registre la fecha de hoy, deberá mostrar [M-2]
  con el nombre guardado y la racha resultante.
- **RF-3.3** Cuando el usuario ejecute `hecho` con un hábito que ya está marcado
  hoy, el sistema deberá mostrar [M-3] con el nombre guardado y la racha actual,
  sin modificar los datos.
- **RF-3.4** Si el nombre normalizado está vacío, entonces el sistema deberá
  rechazarlo con [E-1].
- **RF-3.5** Si el nombre no es igual (RF-1.3) a ningún hábito existente,
  entonces el sistema deberá mostrar [E-6] con el nombre normalizado tal como lo
  escribió el usuario. Las demás reglas de RF-1 no se comprueban en `hecho`.

### RF-4 — Listar hábitos (HU-3)

- **RF-4.1** Cuando el usuario ejecute `listar` y exista al menos un hábito, el
  sistema deberá mostrar una línea por hábito con este formato:

  ```text
  <nombre> | racha: <N> <día|días> | <hecho hoy|pendiente hoy>
  ```

  Por ejemplo:

  ```text
  Leer libros | racha: 5 días | hecho hoy
  Matemáticas | racha: 1 día | pendiente hoy
  Inglés | racha: 0 días | pendiente hoy
  ```

- **RF-4.2** El sistema deberá mostrar los hábitos en el orden en que se crearon.
- **RF-4.3** Mientras no exista ningún hábito, el sistema deberá mostrar [M-4]
  al ejecutar `listar`.

### RF-5 — Cálculo de la racha

- **RF-5.1** El sistema deberá leer la fecha local del equipo una sola vez, al
  empezar cada ejecución, y usarla como «hoy» durante toda esa ejecución.
- **RF-5.2** El sistema deberá trabajar con fechas de calendario, sin hora: un
  cambio de hora (horario de verano) no afecta a qué días son consecutivos.
- **RF-5.3** Mientras el hábito esté marcado hoy, el sistema deberá calcular la
  racha como el número de días consecutivos marcados que terminan hoy.
- **RF-5.4** Mientras el hábito no esté marcado hoy pero sí ayer, el sistema
  deberá calcular la racha como el número de días consecutivos marcados que
  terminan ayer (la racha sigue viva hasta que termine el día de hoy).
- **RF-5.5** Mientras el hábito no esté marcado ni hoy ni ayer, el sistema
  deberá calcular una racha de 0.
- **RF-5.6** El sistema deberá ignorar los días marcados posteriores a hoy al
  calcular la racha y al decidir si el hábito está hecho hoy, y deberá
  conservarlos en los datos guardados.
- **RF-5.7** El sistema deberá escribir «día» cuando la racha sea 1 y «días» en
  cualquier otro caso, en todos los mensajes que muestren una racha.

### RF-6 — Comandos, ayuda y uso (HU-4)

- **RF-6.1** El sistema deberá aceptar exactamente cuatro comandos, escritos en
  minúsculas: `crear`, `hecho`, `listar` y `ayuda`.
- **RF-6.2** El sistema deberá exigir exactamente un argumento (el nombre) en
  `crear` y `hecho`, y ninguno en `listar` y `ayuda`. Un nombre con espacios se
  escribe entre comillas.
- **RF-6.3** El sistema deberá tratar como presente un argumento vacío o formado
  solo por espacios; su validación corresponde a RF-1.5 y RF-3.4.
- **RF-6.4** Cuando el usuario ejecute `ayuda`, el sistema deberá mostrar [M-5].
- **RF-6.5** Si el usuario no indica ningún comando, indica uno desconocido
  (incluido uno escrito con mayúsculas, como `CREAR`) o pasa más o menos
  argumentos de los que exige RF-6.2, entonces el sistema deberá mostrar [E-7].

### RF-7 — Salida y errores

- **RF-7.1** El sistema deberá mostrar los mensajes de éxito (M-x) por la salida
  estándar y terminar con código de salida 0.
- **RF-7.2** Si ocurre un error, entonces el sistema deberá mostrar su mensaje
  (E-x) por la salida de error.
- **RF-7.3** Si ocurre un error de uso [E-7], entonces el sistema deberá
  terminar con código de salida 2.
- **RF-7.4** Si ocurre cualquier otro error (E-1 a E-6, E-8 y E-9), entonces el
  sistema deberá terminar con código de salida 1.
- **RF-7.5** Si ocurre un error, entonces el sistema no deberá modificar los
  datos guardados.
- **RF-7.6** Si se dan varios errores a la vez, entonces el sistema deberá
  mostrar solo el primero, en este orden de comprobación:
  1. uso del comando (RF-6.5);
  2. validez del nombre (RF-1.5 a RF-1.8 en `crear`; RF-3.4 en `hecho`), en el
     orden en que aparecen;
  3. lectura de los datos guardados (RF-8.5);
  4. existencia del hábito (RF-2.3, RF-3.5);
  5. escritura de los datos (RF-8.6).

### RF-8 — Persistencia

- **RF-8.1** Cuando una operación termine con éxito, el sistema deberá conservar
  sus cambios para las siguientes ejecuciones.
- **RF-8.2** El sistema deberá guardar y leer los datos siempre en un lugar fijo
  dentro de la carpeta personal del usuario, el mismo sea cual sea el directorio
  desde el que se ejecute el comando.
- **RF-8.3** Mientras no existan datos guardados (primer uso), el sistema deberá
  comportarse como si no hubiera ningún hábito.
- **RF-8.4** Cuando el sistema guarde el primer cambio y no exista la carpeta
  donde van los datos (dentro de la carpeta personal), deberá crearla.
- **RF-8.5** Si los datos guardados no se pueden leer o no son válidos, entonces
  el sistema deberá mostrar [E-8] y no deberá sobrescribirlos. No son válidos:
  - un archivo de datos vacío (0 bytes);
  - un contenido que no tiene la estructura descrita en la sección 6;
  - una fecha imposible o repetida dentro de un mismo hábito;
  - dos hábitos iguales según RF-1.3;
  - un nombre que no cumple RF-1.
- **RF-8.6** Si los datos no se pueden guardar (por ejemplo, por falta de
  permisos, disco lleno o carpeta personal inexistente), entonces el sistema
  deberá mostrar [E-9] y dejar intactos los datos anteriores.

## 5. Mensajes

Todos los mensajes usan solo signos de puntuación ASCII (comillas `"`, no «» ni
—). `{nombre}` y `{N}` se sustituyen por sus valores; `{día|días}` sigue RF-5.7.

| Id | Cuándo | Texto exacto |
|----|--------|--------------|
| M-1 | Hábito creado (RF-2.2) | `Hábito creado: {nombre}` |
| M-2 | Marcado hoy (RF-3.2) | `{nombre} marcado como hecho hoy. Racha: {N} {día\|días}` |
| M-3 | Ya estaba marcado (RF-3.3) | `{nombre} ya estaba marcado hoy. Racha: {N} {día\|días}` |
| M-4 | Listado vacío (RF-4.3) | `Aún no tienes hábitos. Crea el primero con: crear "<nombre>"` |
| M-5 | Ayuda (RF-6.4) | El bloque de ayuda de abajo |
| E-1 | Nombre vacío | `Error: el nombre no puede estar vacío.` |
| E-2 | Nombre largo | `Error: el nombre no puede tener más de 50 caracteres.` |
| E-3 | Caracteres de control | `Error: el nombre contiene caracteres no permitidos.` |
| E-4 | Empieza por «-» | `Error: el nombre no puede empezar por "-".` |
| E-5 | Duplicado | `Error: ya existe un hábito llamado "{nombre}".` |
| E-6 | No existe | `Error: no existe ningún hábito llamado "{nombre}".` |
| E-7 | Error de uso | `Error: comando no válido.` seguido de una línea en blanco y el bloque de ayuda |
| E-8 | Datos ilegibles o no válidos | `Error: no se pueden leer los datos guardados. No se ha modificado nada.` |
| E-9 | No se puede guardar | `Error: no se han podido guardar los cambios.` |

Bloque de ayuda (M-5 y final de E-7):

```text
Uso:
  crear "<nombre>"   Crea un hábito nuevo
  hecho "<nombre>"   Marca un hábito como hecho hoy
  listar             Muestra tus hábitos y sus rachas
  ayuda              Muestra esta ayuda
```

## 6. Datos que se guardan

Por cada hábito, el sistema guarda solo:

- su nombre normalizado, con las mayúsculas y minúsculas con que se escribió;
- su posición en el orden de creación;
- las fechas de calendario (sin hora) en que se marcó como hecho.

Nada más: la racha y «hecho hoy» se calculan siempre a partir de las fechas.
El formato exacto del archivo lo fija el plan de esta misma especificación.
Cualquier cambio en qué se guarda o en su formato exige actualizar antes esta
sección y el plan (principio 5 de la constitución).

## 7. Requisitos no funcionales

- **RNF-1 Idioma:** todo lo que el usuario ve o escribe está en español: los
  nombres de los comandos y todos los mensajes, incluidos los de error y la
  ayuda. Los nombres de los comandos son texto para el usuario, no
  identificadores del código (principio 6 de la constitución).
- **RNF-2 Local y sin conexión:** el programa funciona sin red, sin cuentas y sin
  servicios externos, y no envía datos fuera del equipo. Si la carpeta personal
  está sincronizada por otro servicio (por ejemplo, OneDrive), eso queda fuera
  del control del programa.
- **RNF-3 Rapidez:** cada comando termina en menos de 1 segundo, contando desde
  que se lanza hasta que acaba (incluido el arranque), con 100 hábitos y 365
  días marcados en cada uno, medido en el equipo de desarrollo del proyecto. Con
  más datos no se garantiza el tiempo, pero sí que los resultados sean correctos.
- **RNF-4 Integridad:** si una ejecución se interrumpe, los datos guardados
  quedan enteros en su estado anterior o enteros en el nuevo; nunca a medias ni
  ilegibles. Mientras se guarda se pueden usar archivos temporales, siempre que
  al terminar solo quede un archivo de datos (principio 5 de la constitución).
- **RNF-5 Verificabilidad:** las pruebas automáticas deben poder fijar la fecha
  de «hoy» y usar una ubicación de datos distinta de la real, en cualquier
  comando. Esto es una ayuda para las pruebas, no una función para el usuario.
- **RNF-6 Terminal:** las tildes y la «ñ» se muestran y se pueden escribir
  correctamente en las terminales predeterminadas de Windows (PowerShell y
  símbolo del sistema) y en cualquier terminal UTF-8.
- **RNF-7 Ejecuciones simultáneas:** si se ejecutan dos comandos a la vez, se
  puede perder el cambio de uno de ellos, pero los datos nunca quedan ilegibles
  (RNF-4).
- **RNF-8 Simplicidad:** la funcionalidad se limita a lo descrito en esta spec;
  cualquier ampliación necesita una spec nueva.

## 8. Casos límite

| # | Situación | Resultado esperado |
|---|-----------|--------------------|
| CL-1 | Hábito recién creado, sin marcar | Racha 0, pendiente hoy (RF-5.5) |
| CL-2 | Marcado ayer y anteayer, hoy no | Racha 2, pendiente hoy (RF-5.4) |
| CL-3 | Marcado hoy, ayer no, anteayer sí | Racha 1: el hueco rompe la racha (RF-5.3) |
| CL-4 | Marcado anteayer, ni ayer ni hoy | Racha 0 (RF-5.5) |
| CL-5 | Días consecutivos que cruzan fin de mes, fin de año o un 29 de febrero | Cuentan como consecutivos (RF-5.2) |
| CL-6 | Marcar dos veces el mismo día | [M-3], código 0, sin cambios (RF-3.3) |
| CL-7 | Crear «Leer» existiendo «leer» | [E-5] con «leer» (RF-1.3, RF-2.3) |
| CL-8 | Crear «  Leer  » | Se guarda como «Leer» (RF-1.1) |
| CL-9 | Nombre formado solo por espacios | [E-1] (RF-1.5) |
| CL-10 | Nombre de exactamente 50 caracteres / de 51 | Se acepta / [E-2] (RF-1.8) |
| CL-11 | «Matemáticas» frente a «MATEMÁTICAS» | Mismo hábito; «Matematicas» sin tilde es otro (RF-1.3) |
| CL-12 | `hecho LEER` cuando existe «Leer» | Marca «Leer» y el mensaje muestra «Leer» (RF-1.3, RF-3.2) |
| CL-13 | Primer uso, sin datos guardados | `listar` muestra [M-4] (RF-4.3, RF-8.3) |
| CL-14 | Datos guardados corruptos | [E-8], código 1, datos intactos (RF-8.5) |
| CL-15 | Marcar justo antes de medianoche y otra vez justo después | Son dos días distintos; la racha sube 1 (RF-5.1) |
| CL-16 | Crear «Leer  libros» (dos espacios) existiendo «Leer libros» | [E-5] (RF-1.1, RF-1.3) |
| CL-17 | Hay un día marcado posterior a hoy | No cuenta para la racha ni para «hecho hoy», pero se conserva (RF-5.6) |
| CL-18 | Racha de 1 | «1 día» en `listar` y en [M-2] (RF-5.7) |
| CL-19 | Ejecutar desde dos directorios distintos | Se ven los mismos hábitos (RF-8.2) |
| CL-20 | Nombre con tabulador, salto de línea o espacio de no separación en el interior | Se sustituye por un espacio normal (RF-1.1) |
| CL-21 | «á» compuesta frente a «á» descompuesta | Mismo hábito; cuenta como 1 carácter (RF-1.1, RF-1.4) |
| CL-22 | Crear «STRASSE» existiendo «Straße» | [E-5] (RF-1.3) |
| CL-23 | `crear listar` | Crea un hábito llamado «listar» (RF-6.2) |
| CL-24 | `crear -h` o `crear --ayuda` | [E-4] (RF-1.7) |
| CL-25 | Nombre con un carácter de control (por ejemplo, el de campana) | [E-3] (RF-1.6) |
| CL-26 | Nombre de más de 50 caracteres que, normalizado, tiene 50 o menos | Se acepta (RF-1.8) |
| CL-27 | `crear Leer libros` sin comillas (dos argumentos) | [E-7], código 2 (RF-6.5) |
| CL-28 | `crear` sin argumento / `crear ""` | [E-7] y código 2 / [E-1] y código 1 (RF-6.3, RF-6.5) |
| CL-29 | `hecho ""` | [E-1], código 1 (RF-3.4) |
| CL-30 | Sin comando, comando desconocido o `CREAR` | [E-7], código 2 (RF-6.5) |
| CL-31 | `listar algo` o `ayuda algo` | [E-7], código 2 (RF-6.5) |
| CL-32 | Archivo de datos vacío (0 bytes) | [E-8], sin sobrescribirlo (RF-8.5) |
| CL-33 | Datos con una fecha imposible, una fecha repetida o dos hábitos iguales | [E-8] (RF-8.5) |
| CL-34 | Datos corruptos y `crear ""` | [E-1]: el nombre se comprueba antes que los datos (RF-7.6) |
| CL-35 | Sin permiso de escritura o disco lleno al guardar | [E-9], código 1, datos anteriores intactos (RF-8.6) |
| CL-36 | Una ejecución empieza a las 23:59:59 y termina después de medianoche | Usa la fecha del inicio (RF-5.1) |
| CL-37 | Días marcados alrededor de un cambio de hora | Siguen siendo consecutivos (RF-5.2) |
| CL-38 | Un día marcado con el reloj adelantado llega a ser «hoy» | Cuenta como «hecho hoy»: el usuario lo marcó (RF-5.6) |
| CL-39 | Racha de 400 días seguidos | Racha 400 (RF-5.3) |
| CL-40 | Nombre que contiene « \| » | Se acepta; el listado puede parecer ambiguo, pero los datos son correctos (RF-4.1) |
| CL-41 | `ayuda` | [M-5], código 0 (RF-6.4) |

## 9. Fuera de alcance

- Marcar días pasados o futuros: solo se puede marcar el día de hoy.
- Borrar o renombrar hábitos, y desmarcar un día.
- Racha récord, historial o calendario de días marcados.
- Frecuencias no diarias (por ejemplo, «3 veces por semana»): todos los hábitos
  son diarios.
- Recordatorios, notificaciones, estadísticas y exportación de datos.
- Varios usuarios, sincronización entre equipos e interfaz gráfica.
- Que el usuario elija dónde se guardan los datos (para las pruebas, ver RNF-5).
- Coordinar ejecuciones simultáneas (ver RNF-7).
- Ajustar la racha al cambiar de zona horaria: se usa siempre la fecha local, y
  viajar puede hacer que un día se salte o se repita.

## 10. Criterios de finalización

- Cada criterio de aceptación RF-x.y tiene al menos una prueba automática que
  lo cubre, y todas pasan.
- Cada caso límite CL-x tiene al menos una prueba automática que lo cubre.
- Cada mensaje M-x y E-x se comprueba con su texto exacto en alguna prueba.
- Los requisitos no funcionales se verifican así:
  - RNF-1 y RNF-6: revisión manual en PowerShell, en el símbolo del sistema y en
    una terminal UTF-8;
  - RNF-3: medición manual en el equipo de desarrollo, anotando el resultado;
  - RNF-4 y RNF-7: prueba automática que simula un fallo durante el guardado;
  - RNF-5: lo demuestran las propias pruebas automáticas;
  - RNF-2 y RNF-8: revisión de código.
- Se cumplen todos los principios de la constitución del proyecto.
- No queda ninguna duda abierta en la sección 11.
- La spec está aprobada antes de empezar el plan.

## 11. Dudas abiertas

No queda ninguna duda abierta. Estas son las que se resolvieron en la versión 1
(con la numeración de la versión 2):

| # | Duda | Decisión | Dónde |
|---|------|----------|-------|
| D-1 | ¿Idioma de los nombres de los comandos? | Español: `crear`, `hecho`, `listar` (y `ayuda`) | RF-6.1, RNF-1 |
| D-2 | ¿La confirmación al marcar muestra la racha? | Sí, también en el aviso de «ya estaba marcado» | RF-3.2, RF-3.3 |
| D-3 | ¿Se normalizan los espacios internos de los nombres? | Sí, varios espacios seguidos se reducen a uno | RF-1.1 |
| D-4 | ¿Qué pasa con los días marcados posteriores a hoy? | Se ignoran en los cálculos, pero se conservan | RF-5.6 |
| D-5 | ¿Formato del listado? | Una línea de texto por hábito, sin símbolos especiales | RF-4.1 |
| D-6 | ¿El usuario elige dónde se guardan los datos? | No: lugar fijo en su carpeta personal | RF-8.2 |

Los 36 hallazgos de la revisión de QA y su resolución están en el documento de
revisión de esta misma carpeta.
