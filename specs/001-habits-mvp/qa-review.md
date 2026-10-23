# Revisión de QA — Spec 001 (MVP de habits-cli)

- **Documento revisado:** spec 001, versión 1 (aprobada el 2026-10-23)
- **Referencia:** constitución del proyecto
- **Fecha de la revisión:** 2026-10-23
- **Alcance:** solo detección. Las resoluciones están en la sección 5.

Los números de requisito (RF-x.y, RNF-x, CL-x) de las secciones 1 a 4 se refieren
a la **versión 1** de la spec.

## 1. Ambigüedades restantes

1. **RF-1.2 / RF-2.1:** no se define qué cuenta como «espacio»: ¿solo el espacio normal, o también tabuladores, saltos de línea y el espacio de no separación (U+00A0)?
2. **RF-1.4:** no se define cómo se cuentan los «50 caracteres». Una «á» puede ocupar uno o dos puntos de código Unicode, y un emoji compuesto, varios.
3. **RF-1.5 / RF-2.1:** no se define la comparación sin mayúsculas para casos especiales («ß» frente a «SS»). Tampoco si una «á» compuesta y una descompuesta dan el mismo nombre; CL-11 solo cubre el caso simple.
4. **RF-1.5:** no dice que la comparación de duplicados se haga sobre el nombre normalizado; solo se deduce de CL-16.
5. **RF-1.1, RF-1.5, RF-2.2, RF-2.4:** no dice qué forma del nombre aparece en los mensajes: la que escribió el usuario («LEER») o la guardada («Leer»).
6. **RF-2.2:** el texto de la confirmación es solo «por ejemplo», mientras que RF-3.1 fija el formato. RF-1.1, RF-2.3, RF-2.4, RF-3.4 y los errores no tienen texto definido, así que las pruebas no pueden comprobar los mensajes.
7. **RF-3.2:** la regla «día» / «días» está en la sección del listado. No queda claro si también se aplica a las confirmaciones de RF-2.2 y RF-2.3.
8. **RF-2.3:** no dice si el aviso «ya estaba marcado» sale por la salida estándar o por la de error.
9. **RF-5.1 / RF-5.5:** «código de salida distinto de 0» no fija ningún valor. No se sabe si es el mismo para todos los errores o cambia según el tipo.
10. **RF-5.5:** no define qué pasa con argumentos de sobra. Con `crear Leer libros` sin comillas, ¿se crea «Leer libros», se crea «Leer» o es un error? ¿Y con `listar algo`?
11. **RF-5.5:** no dice qué pasa si se ejecuta el programa sin ningún comando, ni si los comandos distinguen mayúsculas (`CREAR`).
12. **RF-5.1:** «cualquier error» no está acotado. No se sabe si incluye fallos al escribir: disco lleno, falta de permisos o carpeta de solo lectura.
13. **RF-5.4:** «formato inválido» no está definido. ¿Cuentan los datos sintácticamente válidos con fechas imposibles, hábitos duplicados o nombres de más de 50 caracteres editados a mano?
14. **RF-5.x:** no define qué error tiene prioridad cuando hay varios a la vez, por ejemplo datos corruptos y además un nombre inválido.
15. **RNF-3:** «menos de 1 segundo» no dice en qué equipo ni si incluye el arranque del programa, así que no se puede medir de forma reproducible.
16. **RNF-4:** no dice en qué estado deben quedar los datos tras una interrupción: el anterior, el nuevo o cualquiera de los dos.
17. **Sección 8:** exige una prueba para cada RF y CL, pero no dice si los RNF (rapidez, integridad) se tienen que verificar ni cómo.
18. **RF-1.2, RF-2.2, RF-5.1:** varios criterios juntan varias obligaciones en uno (normalizar + guardar, registrar + confirmar, mensaje + código + no modificar). Cuando una prueba falla, cuesta saber qué parte se ha incumplido.

## 2. Contradicciones entre requisitos

19. **RF-3.1 frente a D-5:** D-5 se decidió «sin símbolos especiales que algunas terminales no muestran», pero el formato usa la raya «—», que es justo un carácter de ese tipo.
20. **RNF-1 frente a RF-5.5:** RNF-1 habla de «la ayuda», pero ningún RF define cómo pedirla; solo se muestra cómo se usa el programa cuando hay un error.
21. **RF-1.3 / RF-2.4 frente a RF-5.5:** `crear ""` encaja a la vez en «nombre vacío» (RF-1.3) y en «falta un argumento» (RF-5.5). Lo mismo ocurre con `hecho ""` entre RF-2.4 y RF-5.5, y cada caso exige un mensaje distinto.
22. **RF-5.6 y «Fuera de alcance» frente a la sección 8:** la ubicación de los datos es fija y no se puede cambiar. Por eso, las pruebas de RF-5.x, CL-13, CL-14 y CL-19 tendrían que leer y escribir en la carpeta personal real del usuario.
23. **RNF-5 frente a la sección 8:** RNF-5 solo garantiza que la racha se puede probar con fechas fijas. Pero la sección 8 exige probar también RF-2.2 («registrar la fecha de hoy») y CL-15 (medianoche), que dependen del reloj real.
24. **RNF-2 frente a RF-5.6:** RNF-2 dice que los datos se guardan «solo en el equipo», pero en Windows la carpeta personal puede estar sincronizada con OneDrive.
25. **Uso de EARS:** RF-2.3 está escrito como comportamiento no deseado («Si…, entonces…») aunque es un caso normal que termina con éxito. Además, RF-4.2 y RF-4.3 «calculan» la racha, mientras que RF-4.4 «muestra» 0.

## 3. Casos límite no cubiertos

26. Un nombre que coincide con un comando o parece una opción: `crear listar`, `crear -h`, `crear --ayuda`.
27. Un nombre que contiene « — » o un salto de línea, lo que rompería el formato «una línea por hábito» de RF-3.1.
28. Un nombre de más de 50 caracteres que, tras normalizar los espacios, queda en 50 o menos. RF-1.4 lo permite, pero ningún CL lo prueba.
29. Un archivo de datos vacío (0 bytes) frente a un archivo que no existe: no se sabe si es «primer uso» (RF-5.3) o «formato inválido» (RF-5.4).
30. La carpeta personal no existe o no tiene permiso de escritura, o el disco se llena al guardar.
31. Dos ejecuciones a la vez (dos terminales marcando al mismo tiempo): una puede perder los cambios de la otra.
32. Una sola ejecución que empieza antes de medianoche y termina después. CL-15 solo cubre dos ejecuciones separadas.
33. Cambio de hora (horario de verano) o cambio de zona horaria al viajar: se puede saltar un día o repetir la misma fecha real.
34. Un día marcado con el reloj adelantado que más tarde deja de ser futuro: cuando llegue esa fecha, aparecerá «hecho hoy» sin que el usuario lo haya marcado ese día (RF-4.5).
35. Una terminal que no usa UTF-8, algo habitual en Windows: puede fallar la salida de tildes, «ñ» y «—», y también la entrada de nombres con tildes. Tampoco se cubren rachas de más de un año ni más de 100 hábitos, que quedan fuera de lo que mide RNF-3.

## 4. Conflictos con la constitución

36. **Principios 5 y 6, y una regla de redacción:**
    - **Principio 5:** exige actualizar la spec antes de cambiar el formato de los datos, pero la spec no describe ese formato. No hay nada que actualizar ni contra qué comprobar un cambio. Además, RNF-4 (integridad ante interrupciones) puede chocar con la regla de un único archivo de datos, y la spec no aclara si se permiten archivos temporales.
    - **Principio 6:** dice que los identificadores van en inglés, pero RNF-1 pone los comandos en español (`crear`, `hecho`, `listar`). No queda claro si un nombre de comando es un identificador o un texto para el usuario.
    - **Regla de redacción:** la sección 8 cita la constitución por su nombre de archivo, lo que incumple la regla acordada para la spec: «nada de nombres de archivos».

No se han encontrado conflictos con los principios 1, 2 y 3.

## 5. Resoluciones

Todas las decisiones siguen las recomendaciones de la revisión y están aplicadas
en la **versión 2** de la spec. La columna «Dónde» usa la numeración de la
versión 2.

| # | Decisión | Dónde (v2) |
|---|----------|------------|
| 1 | Cualquier espacio en blanco de Unicode (tabulador, salto de línea, espacio de no separación…) cuenta como espacio. | RF-1.1, CL-20 |
| 2 | Primero se pasa el nombre a la forma Unicode compuesta; luego se cuentan caracteres Unicode. Un emoji compuesto puede contar como varios. | RF-1.1, RF-1.4, CL-21 |
| 3 | Comparación sin mayúsculas con las reglas completas de Unicode («ß» = «SS»), sobre la forma compuesta. Las tildes distinguen. | RF-1.3, CL-21, CL-22 |
| 4 | La igualdad de nombres se define una sola vez, sobre el nombre normalizado, y la usan `crear` y `hecho`. | RF-1.3 |
| 5 | Los mensajes muestran el nombre guardado; E-6 muestra el nombre normalizado que escribió el usuario. | RF-2.2, RF-2.3, RF-3.2, RF-3.5 |
| 6 | Nueva sección «Mensajes» con el texto exacto de cada mensaje (M-1 a M-5, E-1 a E-9). | Sección 5 |
| 7 | La regla «día» / «días» se aplica a todos los mensajes con racha. | RF-5.7, CL-18 |
| 8 | Los mensajes de éxito (incluido «ya estaba marcado») van por la salida estándar; los errores, por la de error. | RF-7.1, RF-7.2 |
| 9 | Código 0 en éxito, 2 en errores de uso y 1 en el resto. | RF-7.1, RF-7.3, RF-7.4 |
| 10 | `crear` y `hecho` exigen exactamente un argumento; `listar` y `ayuda`, ninguno. Los argumentos de sobra son error de uso. | RF-6.2, RF-6.5, CL-27, CL-31 |
| 11 | Sin comando o con un comando desconocido (incluido en mayúsculas) es error de uso. | RF-6.1, RF-6.5, CL-30 |
| 12 | Los fallos al guardar son un error propio (E-9) y dejan intactos los datos anteriores. | RF-8.6, CL-35 |
| 13 | Se enumera qué datos no son válidos, incluido el archivo vacío. | RF-8.5, CL-32, CL-33 |
| 14 | Orden fijo de comprobación: uso, nombre, lectura de datos, existencia, escritura. Solo se muestra el primer error. | RF-7.6, CL-34 |
| 15 | Se mide de principio a fin, con arranque incluido, en el equipo de desarrollo y con 100 hábitos × 365 días. | RNF-3 |
| 16 | Tras una interrupción, los datos quedan enteros en el estado anterior o en el nuevo. | RNF-4 |
| 17 | La sección de criterios de finalización dice cómo se verifica cada RNF. | Sección 10 |
| 18 | Los criterios compuestos se dividen: crear (RF-2.1/RF-2.2), marcar (RF-3.1/RF-3.2) y errores (RF-7.2 a RF-7.5). | RF-2, RF-3, RF-7 |
| 19 | El listado usa « \| » en lugar de la raya, y todos los mensajes usan solo puntuación ASCII. | RF-4.1, sección 5 |
| 20 | Nuevo comando `ayuda` y nueva historia HU-4. | RF-6.1, RF-6.4, CL-41 |
| 21 | Un argumento vacío cuenta como presente: `crear ""` y `hecho ""` dan E-1; solo la falta de argumento es error de uso. | RF-6.3, RF-3.4, CL-28, CL-29 |
| 22 | Las pruebas pueden usar otra ubicación de datos; no es una función para el usuario. | RNF-5, sección 9 |
| 23 | Las pruebas pueden fijar «hoy» en cualquier comando, no solo en el cálculo de la racha. | RNF-5 |
| 24 | RNF-2 garantiza que el programa no envía datos; la sincronización de la carpeta personal queda fuera de su control. | RNF-2 |
| 25 | Uso de EARS corregido: «Si…, entonces…» solo para errores; marcar dos veces pasa a «Cuando…» y la racha 0 se «calcula». | RF-3.3, RF-5.5 |
| 26 | `crear listar` crea el hábito «listar»; un nombre que empieza por «-» se rechaza (E-4). | RF-1.7, CL-23, CL-24 |
| 27 | Los saltos de línea se convierten en espacios; el resto de caracteres de control se rechaza (E-3). « \| » en un nombre se acepta. | RF-1.1, RF-1.6, CL-25, CL-40 |
| 28 | Nuevo caso límite. | CL-26 |
| 29 | Un archivo de datos vacío no es válido (E-8); solo la ausencia de datos es primer uso. | RF-8.3, RF-8.5, CL-32 |
| 30 | La carpeta de datos se crea si falta; si no se puede escribir, E-9. | RF-8.4, RF-8.6, CL-35 |
| 31 | No se coordinan ejecuciones simultáneas: se puede perder un cambio, pero nunca corromper los datos. | RNF-7, sección 9 |
| 32 | «Hoy» se lee una sola vez al empezar cada ejecución. | RF-5.1, CL-36 |
| 33 | Se trabaja con fechas de calendario (el cambio de hora no afecta); el cambio de zona horaria queda fuera de alcance. | RF-5.2, CL-37, sección 9 |
| 34 | Se acepta: un día marcado con el reloj adelantado cuenta cuando llega a ser hoy. | RF-5.6, CL-38 |
| 35 | Nuevo RNF de terminal para tildes y «ñ» en Windows; con más datos que en RNF-3 solo se garantiza que el resultado sea correcto. | RNF-3, RNF-6, CL-39 |
| 36 | Nueva sección «Datos que se guardan»; el formato exacto va en el plan y cambiarlo exige actualizar antes ambos. Se permiten archivos temporales al guardar. Los comandos se tratan como texto para el usuario, no como identificadores. Se quita el nombre de archivo de la constitución. | Sección 6, RNF-1, RNF-4, sección 10 |

La constitución no se ha modificado: las tres resoluciones del hallazgo 36 son
interpretaciones compatibles con ella.
