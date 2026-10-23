# Spec 001 — MVP de la app administrativa de clientes de la escuela de danza

- **Estado:** versión 3, aprobada
- **Fecha:** 2026-10-23

### Historial

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1 | 2026-10-23 | Primera versión. Recoge las aclaraciones D-6…D-15 y resuelve las dudas abiertas D-16…D-20 (ver [`clarifications.md`](clarifications.md)). Aprobada. |
| 2 | 2026-10-23 | Resuelve los 42 hallazgos de la revisión de QA (ver «Resoluciones» en [`qa-review.md`](qa-review.md)). Añade RF-1.16, RF-1.17, RF-2.16–RF-2.25, RF-6.11, RF-7.10, RF-7.11, RF-9.15, RF-12.7, RF-14.6, RF-15.10, RF-15.11, RF-16.8–RF-16.10, RF-18.5, RNF-13, CL-45–CL-56, M-35–M-39 y E-44–E-48. Aprobada. |
| 3 | 2026-10-23 | Aclara en RF-11.1 que las cuotas anuladas no cuentan (aviso A-1 del [plan](plan.md), confirmado por el usuario) y añade CL-57. Aprobada. |

## 1. Contexto y objetivo

La escuela lleva hoy la administración de sus alumnos en hojas sueltas: es
difícil saber quién está matriculado en cada grupo, quién debe cuotas y a quién
llamar si un alumno se lesiona en clase. Además maneja datos de menores, de
contacto y de salud, que la Ley 1581 de 2012 obliga a tratar con autorización,
acceso restringido y un plazo de conservación (D-1).

El objetivo de este MVP es que el personal de la escuela pueda:

1. registrar a los alumnos, sus tutores o contactos y la autorización de
   tratamiento de sus datos;
2. organizar los grupos y las matrículas respetando el cupo;
3. generar las cuotas, registrar los pagos y saber en todo momento quién es
   moroso;
4. dar a cada profesor los contactos y las observaciones de salud de sus
   alumnos, y nada más;
5. cumplir los derechos de los titulares y borrar los datos al vencer su plazo.

## 2. Usuarios y roles

Solo usa la app el personal de la escuela, cada persona con su propia cuenta y
un único rol (D-7). Los alumnos y las familias no tienen acceso.

- **Dirección:** responsable de la escuela. Hace todo lo que hace Recepción y,
  además, gestiona las cuentas y los grupos, anula cargos y pagos, atiende los
  derechos de los titulares y consulta la auditoría.
- **Recepción:** atiende a las familias. Da de alta y edita alumnos y contactos,
  matricula, genera cuotas, crea cargos y registra pagos.
- **Profesor:** da clase en uno o varios grupos. Solo ve sus grupos y, de sus
  alumnos, lo necesario para la clase: nombre, edad, contactos y observaciones
  de salud. No ve datos económicos.

Términos que usa esta spec:

- **Alumno:** persona que asiste a clase. Es **menor** si tiene menos de 18
  años cumplidos.
- **Contacto:** persona vinculada a uno o varios alumnos. Para un menor, sus
  contactos son sus **tutores** (representantes legales); para un adulto, son
  sus **contactos de emergencia** (D-9).
- **Responsable de pago:** persona a quien se reclama la deuda de un alumno.
- **Grupo:** clase semanal con profesor, horario, cupo y cuota mensual.
- **Matrícula:** pertenencia de un alumno a un grupo entre dos fechas.
- **Cargo:** importe que debe un alumno: una **cuota mensual** o un **cargo
  manual**.
- **Pago:** dinero recibido de un alumno, que se aplica a sus cargos.
- **Titular:** persona a la que se refieren unos datos (alumno o contacto).

## 3. Historias de usuario

- **HU-1:** Como persona del personal, quiero entrar con mi propia cuenta para
  ver solo lo que mi rol necesita.
- **HU-2:** Como Recepción, quiero dar de alta a un alumno con sus datos para
  poder matricularlo.
- **HU-3:** Como Recepción, quiero registrar a cada tutor o contacto una sola
  vez y vincularlo a varios alumnos para no duplicar los datos de una familia.
- **HU-4:** Como Dirección, quiero que conste la autorización de tratamiento de
  datos de cada alumno para cumplir la Ley 1581.
- **HU-5:** Como Recepción, quiero buscar alumnos y corregir su ficha para tener
  los datos al día.
- **HU-6:** Como Recepción, quiero dar de baja y reactivar alumnos sin perder su
  histórico.
- **HU-7:** Como Dirección, quiero definir los grupos con su profesor, horario,
  cupo y cuota para organizar la oferta de clases.
- **HU-8:** Como Recepción, quiero matricular alumnos en grupos respetando el
  cupo.
- **HU-9:** Como Recepción, quiero generar las cuotas del mes y crear cargos
  para saber qué debe cada alumno.
- **HU-10:** Como Recepción, quiero registrar pagos, también parciales, para
  mantener la deuda al día.
- **HU-11:** Como Recepción, quiero ver el estado de cuenta de un alumno y el
  listado de morosos para gestionar los cobros.
- **HU-12:** Como Profesor, quiero ver mis grupos con los contactos y las
  observaciones de salud de mis alumnos para dar clase con seguridad.
- **HU-13:** Como Dirección, quiero atender las solicitudes de consulta y
  supresión de los titulares para cumplir la Ley 1581.
- **HU-14:** Como Dirección, quiero que los datos se anonimicen al vencer su
  plazo de conservación sin tener que acordarme.
- **HU-15:** Como Dirección, quiero una auditoría de los cambios y de las
  consultas sensibles para poder investigar un incidente.
- **HU-16:** Como Recepción, quiero ver en el inicio lo que tengo pendiente.

## 4. Requisitos funcionales

Los criterios de aceptación siguen la notación EARS:
*El sistema deberá…* (ubicuo), *Cuando…* (evento), *Mientras…* (estado) y
*Si…, entonces…* (comportamiento no deseado, siempre un error).

Los textos entre corchetes (M-x, E-x) son los mensajes exactos de la sección 6.
Las longitudes máximas de los campos están en la sección 7.

### RF-1 — Reglas generales de datos

- **RF-1.1** El sistema deberá tomar como «hoy» la fecha del calendario de
  Colombia (hora de Bogotá), leída una sola vez al empezar cada operación.
- **RF-1.2** El sistema deberá normalizar todo texto que reciba: llevarlo a la
  forma Unicode compuesta (una «á» escrita con dos códigos pasa a ser un solo
  carácter), eliminar los espacios en blanco del principio y del final y
  sustituir cada secuencia de espacios en blanco interiores por un único
  espacio. Es espacio en blanco cualquier carácter de espacio de Unicode,
  incluidos el tabulador, el salto de línea y el espacio de no separación.
- **RF-1.3** Si un campo obligatorio queda vacío tras normalizarlo, entonces el
  sistema deberá rechazarlo con [E-2].
- **RF-1.4** Si un texto supera la longitud máxima de su campo, entonces el
  sistema deberá rechazarlo con [E-3].
- **RF-1.5** Si un texto contiene caracteres de control, entonces el sistema
  deberá rechazarlo con [E-4].
- **RF-1.6** El sistema deberá comparar los nombres sin distinguir mayúsculas,
  minúsculas ni signos diacríticos (tildes, diéresis, «ç»…), salvo la «ñ», que
  sí se distingue de la «n»; guiones y apóstrofos sí cuentan («Maria» es igual
  a «María»; «Pena» es distinto de «Peña»; «Ruiz-López» es distinto de «Ruiz
  López»).
- **RF-1.7** El sistema deberá aceptar un teléfono cuando, tras quitar espacios,
  guiones, paréntesis y un prefijo «+57» opcional, queden exactamente 10
  dígitos, y guardarlo como esos 10 dígitos.
- **RF-1.8** Si un teléfono no cumple RF-1.7, entonces el sistema deberá
  rechazarlo con [E-5].
- **RF-1.9** Si un correo electrónico contiene espacios, no tiene exactamente
  una «@», tiene vacía la parte izquierda o su parte derecha no está formada
  por al menos dos partes no vacías separadas por puntos, entonces el sistema
  deberá rechazarlo con [E-6].
- **RF-1.10** El sistema deberá manejar los importes en pesos colombianos
  enteros, sin decimales.
- **RF-1.11** Si un importe no es un número entero entre 1 y 10.000.000,
  entonces el sistema deberá rechazarlo con [E-22].
- **RF-1.12** El sistema deberá calcular la edad en años cumplidos a fecha de
  hoy; quien nació un 29 de febrero cumple años el 1 de marzo en los años no
  bisiestos.
- **RF-1.13** El sistema deberá considerar menor de edad a quien tenga menos de
  18 años cumplidos.
- **RF-1.14** Si una fecha que no admite el futuro (firma de una autorización,
  recepción o respuesta de una solicitud) es posterior a hoy, entonces el
  sistema deberá rechazarla con [E-41].
- **RF-1.15** Si al guardar unos datos otra persona los ha modificado desde que
  se cargaron, entonces el sistema deberá rechazar el cambio con [E-35] sin
  guardar nada.
- **RF-1.16** El sistema deberá guardar y comparar los correos electrónicos en
  minúsculas.
- **RF-1.17** El sistema deberá mostrar [M-35] junto a cada campo de texto
  libre que no sea un nombre ni las observaciones de salud: concepto, motivo,
  referencia y relación.

### RF-2 — Acceso y cuentas del personal (HU-1)

- **RF-2.1** Mientras una persona no haya iniciado sesión, el sistema deberá
  mostrarle solo la pantalla de inicio de sesión.
- **RF-2.2** Cuando una persona con cuenta activa introduzca su correo y su
  contraseña correctos, el sistema deberá iniciar su sesión con el rol de su
  cuenta.
- **RF-2.3** Si el correo o la contraseña no son correctos, o la cuenta está
  desactivada, entonces el sistema deberá rechazar el acceso con [E-31], sin
  indicar qué dato falla.
- **RF-2.4** Si se producen 5 intentos de acceso fallidos seguidos en una
  cuenta, entonces el sistema deberá rechazar con [E-32] todo intento de acceso
  a esa cuenta durante los 15 minutos siguientes, aunque la contraseña sea
  correcta.
- **RF-2.5** Cuando una sesión cumpla 30 minutos sin actividad, el sistema
  deberá cerrarla. Es actividad cualquier operación que la persona pide al
  sistema (abrir una pantalla, buscar, guardar); las actualizaciones
  automáticas de una pantalla no cuentan.
- **RF-2.6** Cuando una persona intente usar una sesión cerrada por
  inactividad, el sistema deberá mostrarle [M-28] junto a la pantalla de inicio
  de sesión.
- **RF-2.7** Cuando Dirección cree una cuenta con nombre, correo y rol válidos,
  el sistema deberá guardarla activa, mostrando [M-22].
- **RF-2.8** Si el correo de la cuenta coincide, sin distinguir mayúsculas, con
  el de otra cuenta, entonces el sistema deberá rechazarla con [E-33].
- **RF-2.9** Cuando Dirección desactive una cuenta, el sistema deberá cerrar sus
  sesiones abiertas e impedir nuevos accesos, mostrando [M-23].
- **RF-2.10** Si la cuenta que se intenta desactivar, o a la que se intenta
  quitar el rol Dirección, es la última cuenta activa con rol Dirección,
  entonces el sistema deberá rechazar el cambio con [E-29].
- **RF-2.11** Si la cuenta que se intenta desactivar, o pasar a rol Recepción,
  es profesor de algún grupo no archivado, entonces el sistema deberá rechazar
  el cambio con [E-30].
- **RF-2.12** Cuando Dirección reactive una cuenta desactivada, el sistema
  deberá permitir de nuevo su acceso, mostrando [M-32].
- **RF-2.13** Cuando Dirección restablezca el acceso de una cuenta, el sistema
  deberá invalidar su contraseña y su segundo factor y generar un nuevo código
  de activación (RF-2.16), mostrando [M-33].
- **RF-2.14** El sistema deberá asignar a cada cuenta exactamente un rol:
  Dirección, Recepción o Profesor.
- **RF-2.15** Cuando Dirección cambie el rol de una cuenta, el sistema deberá
  aplicar el nuevo rol desde la siguiente operación de esa cuenta.
- **RF-2.16** Cuando Dirección cree una cuenta, el sistema deberá generar para
  ella un código de activación de un solo uso, válido durante 72 horas, que
  solo se muestra a Dirección en [M-22] para que lo entregue en persona.
- **RF-2.17** Cuando una persona introduzca un código de activación válido y
  una contraseña nueva de al menos 12 caracteres, el sistema deberá guardar la
  contraseña e invalidar el código, mostrando [M-38].
- **RF-2.18** Si el código de activación no existe, ya se usó o ha caducado,
  entonces el sistema deberá rechazarlo con [E-44].
- **RF-2.19** Si la contraseña nueva tiene menos de 12 caracteres, entonces el
  sistema deberá rechazarla con [E-45].
- **RF-2.20** El sistema deberá reiniciar el contador de intentos fallidos de
  una cuenta tras un acceso correcto y al terminar un bloqueo; los intentos
  con un correo que no pertenece a ninguna cuenta no bloquean nada.
- **RF-2.21** Cuando Dirección desbloquee una cuenta bloqueada por RF-2.4, el
  sistema deberá permitir su acceso de inmediato y reiniciar su contador,
  mostrando [M-37].
- **RF-2.22** Mientras una cuenta tenga rol Dirección, el sistema deberá
  exigirle un segundo factor de autenticación, además de la contraseña, en
  cada inicio de sesión.
- **RF-2.23** Si el segundo factor no es correcto, entonces el sistema deberá
  rechazar el acceso con [E-31] y contarlo como intento fallido (RF-2.4).
- **RF-2.24** Cuando una cuenta con rol Dirección inicie sesión sin tener
  configurado el segundo factor, el sistema deberá exigirle configurarlo antes
  de permitirle cualquier otra operación.
- **RF-2.25** Cuando Dirección cierre las sesiones de una cuenta, el sistema
  deberá cerrar todas sus sesiones abiertas, mostrando [M-39].

### RF-3 — Permisos

- **RF-3.1** El sistema deberá permitir cada acción solo a los roles que la
  autorizan en la matriz de permisos (sección 5).
- **RF-3.2** Si una cuenta intenta una acción que su rol no permite, entonces el
  sistema deberá rechazarla con [E-1], sin mostrar ni modificar ningún dato.
- **RF-3.3** El sistema deberá comprobar el permiso en cada operación, aunque la
  interfaz no ofrezca esa acción al rol.
- **RF-3.4** Mientras una cuenta con rol Profesor tenga la sesión iniciada, el
  sistema deberá limitar lo que le muestra a los grupos no archivados de los que
  es profesor y a los alumnos con matrícula activa en ellos.

### RF-4 — Alta de alumnos (HU-2)

- **RF-4.1** Cuando Recepción o Dirección den de alta un alumno con datos
  válidos, el sistema deberá guardarlo como activo, mostrando [M-1].
- **RF-4.2** El sistema deberá exigir en el alta de todo alumno nombre,
  apellidos, fecha de nacimiento, responsable de pago y una autorización de
  tratamiento (RF-6). El correo y las observaciones de salud son opcionales.
- **RF-4.3** Si la fecha de nacimiento es posterior a hoy o da una edad menor de
  2 años o mayor de 100, entonces el sistema deberá rechazarla con [E-7].
- **RF-4.4** Si al dar de alta o editar un alumno existe otro alumno no
  anonimizado con el mismo nombre, los mismos apellidos (RF-1.6) y la misma
  fecha de nacimiento, entonces el sistema deberá rechazar el cambio con
  [E-8].
- **RF-4.5** Si el alumno es menor y no tiene ningún contacto, entonces el
  sistema deberá rechazar el alta con [E-9].
- **RF-4.6** El sistema deberá proponer como responsable de pago de un adulto al
  propio alumno, que puede cambiarse por uno de sus contactos.
- **RF-4.7** Si el responsable de pago no es uno de los contactos del alumno ni,
  siendo adulto, el propio alumno, entonces el sistema deberá rechazarlo con
  [E-39].
- **RF-4.8** Mientras el alumno que se da de alta sea adulto, el sistema deberá
  exigir su teléfono propio; el de un menor es opcional. Los contactos de un
  menor los exige RF-4.5.

### RF-5 — Contactos y tutores (HU-3)

- **RF-5.1** El sistema deberá guardar cada contacto una sola vez y permitir
  vincularlo a varios alumnos.
- **RF-5.2** El sistema deberá exigir de cada contacto nombre, apellidos y
  teléfono, y de cada vínculo su relación con el alumno (por ejemplo, «madre»);
  el correo del contacto es opcional.
- **RF-5.3** Mientras un alumno sea menor, el sistema deberá tratar a sus
  contactos como sus tutores.
- **RF-5.4** Mientras un alumno sea adulto, el sistema deberá tratar a sus
  contactos como contactos de emergencia.
- **RF-5.5** Si se intenta vincular un tercer contacto a un alumno, entonces el
  sistema deberá rechazarlo con [E-10].
- **RF-5.6** Cuando se cree un contacto con un teléfono que ya tiene otro
  contacto, el sistema deberá mostrar [M-18] y permitir vincular el contacto
  existente o crear el nuevo de todos modos.
- **RF-5.7** Cuando Recepción o Dirección busquen un contacto para vincularlo,
  el sistema deberá encontrarlo por nombre, apellidos (RF-1.6) o teléfono.
- **RF-5.8** Cuando se modifiquen los datos de un contacto, el sistema deberá
  mostrar los datos nuevos en todos los alumnos vinculados.
- **RF-5.9** Si al desvincular un contacto un alumno menor queda sin contactos,
  entonces el sistema deberá rechazar el cambio con [E-9].
- **RF-5.10** Si el contacto que se intenta desvincular es el responsable de
  pago del alumno, entonces el sistema deberá rechazar el cambio con [E-40].
- **RF-5.11** Cuando un contacto se quede sin vínculos con alumnos no
  anonimizados, el sistema deberá borrar sus datos.

### RF-6 — Autorización de tratamiento y datos de salud (HU-4)

- **RF-6.1** El sistema deberá registrar cada autorización con su fecha de
  firma, el nombre completo y la relación de quien la otorga tal como constan
  al registrarla, si incluye los datos de salud y, en menores de 12 años o
  más, la confirmación de que se tuvo en cuenta su opinión (D-14).
- **RF-6.2** Si se intenta dar de alta un alumno sin autorización, entonces el
  sistema deberá rechazar el alta con [E-11].
- **RF-6.3** Si la autorización de un menor no la otorga uno de sus contactos, o
  la de un adulto no la otorga el propio alumno, entonces el sistema deberá
  rechazarla con [E-12].
- **RF-6.4** El sistema deberá considerar vigente la última autorización
  registrada de cada alumno.
- **RF-6.5** Si se intentan guardar observaciones de salud sin que la
  autorización vigente incluya los datos de salud, o con esa inclusión
  revocada, entonces el sistema deberá rechazarlas con [E-13].
- **RF-6.6** Cuando se registre una autorización que no incluye los datos de
  salud, el sistema deberá borrar las observaciones de salud del alumno.
- **RF-6.7** Mientras un alumno activo sea adulto y su autorización vigente la
  haya otorgado uno de sus contactos, el sistema deberá considerar esa
  autorización pendiente de renovar (D-16).
- **RF-6.8** Mientras la autorización de un alumno esté pendiente de renovar, el
  sistema deberá mostrar [M-17] en su ficha.
- **RF-6.9** Si al registrar la autorización renovada el alumno no tiene
  teléfono propio, entonces el sistema deberá rechazarla con [E-2].
- **RF-6.10** Cuando Recepción o Dirección registren que se revoca la
  autorización de los datos de salud, el sistema deberá marcar como revocada
  la inclusión de la salud en la autorización vigente y borrar las
  observaciones de salud, mostrando [M-27]. Para volver a guardarlas hace
  falta una autorización nueva que incluya la salud.
- **RF-6.11** Si al registrar la autorización de un menor de 12 años o más no
  se confirma que se tuvo en cuenta su opinión, entonces el sistema deberá
  rechazarla con [E-47].

### RF-7 — Búsqueda, ficha y edición (HU-5)

- **RF-7.1** Cuando Recepción o Dirección busquen alumnos por un texto, el
  sistema deberá mostrar los alumnos cuyo nombre o apellidos contengan ese
  texto (RF-1.6), ordenados por apellidos y nombre.
- **RF-7.2** El sistema deberá mostrar por defecto solo los alumnos activos, con
  la opción de ver los de baja o todos.
- **RF-7.3** Mientras una búsqueda no tenga resultados, el sistema deberá
  mostrar [M-24].
- **RF-7.4** Cuando Recepción o Dirección abran la ficha de un alumno, el
  sistema deberá mostrar sus datos personales, edad, estado, contactos con su
  relación y teléfono, responsable de pago, autorización vigente, matrículas
  activas e históricas y su deuda pendiente y vencida, indicando solo si tiene
  observaciones de salud, sin su contenido.
- **RF-7.5** Cuando Dirección pida ver las observaciones de salud de un
  alumno, el sistema deberá mostrárselas.
- **RF-7.6** Cuando Recepción o Dirección guarden cambios válidos en la ficha de
  un alumno activo o de baja, el sistema deberá guardarlos, mostrando [M-2].
- **RF-7.7** El sistema deberá aplicar al guardar cambios las validaciones del
  alta (RF-4 y RF-5) a los datos modificados; las de la autorización (RF-6.3 y
  RF-6.11) solo se aplican al registrar una autorización nueva.
- **RF-7.8** Si se intentan guardar observaciones de salud de un alumno de baja,
  entonces el sistema deberá rechazarlas con [E-14].
- **RF-7.9** Si se intenta editar o reactivar un alumno anonimizado, entonces el
  sistema deberá rechazarlo con [E-37].
- **RF-7.10** Mientras la autorización de un alumno esté pendiente de renovar,
  el sistema deberá permitir guardar cambios en su ficha sin exigir su
  teléfono propio (RF-4.8).
- **RF-7.11** Cuando Recepción guarde las observaciones de salud de un alumno,
  el sistema deberá sustituir el texto completo sin mostrarle el texto
  anterior.

### RF-8 — Baja y reactivación (HU-6)

- **RF-8.1** Cuando Recepción o Dirección pidan dar de baja a un alumno activo,
  el sistema deberá pedir confirmación con [M-3].
- **RF-8.2** Cuando se confirme la baja, el sistema deberá marcar al alumno como
  de baja con fecha de hoy, mostrando [M-4].
- **RF-8.3** Cuando se confirme la baja, el sistema deberá finalizar todas sus
  matrículas activas con fecha de hoy (RF-10.7).
- **RF-8.4** Cuando se confirme la baja, el sistema deberá borrar sus
  observaciones de salud.
- **RF-8.5** El sistema deberá conservar los cargos, los pagos y la deuda de un
  alumno de baja, que siguen contando para la morosidad (RF-13.3).
- **RF-8.6** Cuando Recepción o Dirección reactiven a un alumno de baja
  registrando una nueva autorización (RF-6), el sistema deberá marcarlo como
  activo y borrar su fecha de baja, mostrando [M-5].
- **RF-8.7** Si se intenta reactivar a un alumno sin registrar una nueva
  autorización, entonces el sistema deberá rechazarlo con [E-11].
- **RF-8.8** El sistema deberá aplicar al reactivar las validaciones del alta
  (RF-4).
- **RF-8.9** El sistema deberá reactivar al alumno sin matrículas ni
  observaciones de salud; se crean de nuevo cuando hagan falta.

### RF-9 — Grupos (HU-7)

- **RF-9.1** Cuando Dirección cree un grupo con datos válidos, el sistema deberá
  guardarlo, mostrando [M-25].
- **RF-9.2** El sistema deberá exigir de cada grupo: nombre, estilo, profesor
  (una cuenta activa con rol Profesor o Dirección), horario de 1 a 7 franjas
  (día de la semana, hora de inicio y hora de fin), cupo y cuota mensual.
- **RF-9.3** Si el nombre coincide (RF-1.6) con el de otro grupo no archivado,
  entonces el sistema deberá rechazarlo con [E-18].
- **RF-9.4** Si el horario no tiene entre 1 y 7 franjas, entonces el sistema
  deberá rechazarlo con [E-34].
- **RF-9.5** Si en una franja la hora de fin no es posterior a la de inicio,
  entonces el sistema deberá rechazarla con [E-19].
- **RF-9.6** Si el cupo no es un número entero entre 1 y 100, entonces el
  sistema deberá rechazarlo con [E-42].
- **RF-9.7** Si el profesor elegido no es una cuenta activa con rol Profesor o
  Dirección, entonces el sistema deberá rechazarlo con [E-43].
- **RF-9.8** Cuando Dirección cambie la cuota de un grupo, el sistema deberá
  aplicarla solo a las cuotas que se generen después; las ya generadas no
  cambian.
- **RF-9.9** Si se intenta reducir el cupo por debajo del número de matrículas
  activas del grupo, entonces el sistema deberá rechazarlo con [E-20].
- **RF-9.10** Cuando Dirección archive un grupo sin matrículas activas, el
  sistema deberá dejar de ofrecerlo para matricular y conservar su histórico,
  mostrando [M-26].
- **RF-9.11** Si el grupo que se intenta archivar tiene matrículas activas,
  entonces el sistema deberá rechazarlo con [E-21].
- **RF-9.12** Cuando Dirección desarchive un grupo, el sistema deberá volver a
  ofrecerlo para matricular, mostrando [M-34].
- **RF-9.13** Si al desarchivar un grupo su nombre coincide con el de otro grupo
  no archivado, entonces el sistema deberá rechazarlo con [E-18].
- **RF-9.14** Cuando Recepción o Dirección consulten la lista de grupos, el
  sistema deberá mostrar de cada grupo no archivado su nombre, estilo,
  profesor, horario, plazas libres (cupo menos matrículas activas) y cuota.
- **RF-9.15** Si dos franjas de un grupo del mismo día de la semana se
  solapan, entonces el sistema deberá rechazarlas con [E-46].

### RF-10 — Matrículas (HU-8)

- **RF-10.1** Cuando Recepción o Dirección matriculen a un alumno activo en un
  grupo no archivado con plazas libres, el sistema deberá crear la matrícula con
  fecha de alta de hoy, mostrando [M-6].
- **RF-10.2** Cuando el alumno que se va a matricular tenga deuda vencida, el
  sistema deberá pedir confirmación con [M-7] antes de crear la matrícula.
- **RF-10.3** Si el alumno ya tiene una matrícula activa en ese grupo, entonces
  el sistema deberá rechazarla con [E-15].
- **RF-10.4** Si el grupo no tiene plazas libres, entonces el sistema deberá
  rechazar la matrícula con [E-16].
- **RF-10.5** Si el grupo está archivado, entonces el sistema deberá rechazar la
  matrícula con [E-17].
- **RF-10.6** Si el alumno está de baja, entonces el sistema deberá rechazar la
  matrícula con [E-14].
- **RF-10.7** Cuando Recepción o Dirección finalicen una matrícula activa, el
  sistema deberá guardar hoy como su fecha de baja, mostrando [M-8].
- **RF-10.8** El sistema deberá considerar activa una matrícula en un día dado
  cuando su fecha de alta sea igual o anterior a ese día y no tenga fecha de
  baja o esta sea posterior a ese día. «Matrícula activa», sin más, significa
  activa hoy.
- **RF-10.9** Si dos matrículas simultáneas compiten por la última plaza de un
  grupo, entonces el sistema deberá crear solo la primera que se guarde y
  rechazar la otra con [E-16].
- **RF-10.10** Cuando se finalice, el mismo día de su alta, una matrícula cuya
  cuota generada al crearla no tiene pagos aplicados, el sistema deberá anular
  esa cuota en nombre del «sistema», con el motivo «Matrícula finalizada el
  día de su alta», sea cual sea el rol de quien finaliza la matrícula.

### RF-11 — Cuotas mensuales y cargos (HU-9)

- **RF-11.1** El sistema deberá generar como máximo una cuota mensual por
  alumno, grupo y mes, aunque el alumno tenga varias matrículas en ese grupo
  dentro del mismo mes. Las cuotas anuladas no cuentan: en este requisito, en
  RF-11.2 y en RF-11.3, «tener la cuota de ese grupo y mes» significa tener una
  no anulada (aviso A-1 del plan).
- **RF-11.2** Cuando Recepción o Dirección generen las cuotas del mes en
  curso, el sistema deberá crear una cuota para cada matrícula activa el día 1
  de ese mes cuyo alumno no tenga ya la cuota de ese grupo y mes, mostrando
  [M-9] con el número de cuotas que ha creado esa operación.
- **RF-11.3** Cuando se cree una matrícula entre el día 1 y el 15 de un mes y
  el alumno no tenga ya la cuota de ese grupo y mes, el sistema deberá
  generarla en ese momento (D-17). Una matrícula creada el día 16 o después no
  paga ese mes: su primera cuota es la del mes siguiente (RF-11.2).
- **RF-11.4** Cuando se generen las cuotas del mes en curso y no quede ninguna
  por crear, el sistema deberá mostrar [M-10] sin crear ninguna.
- **RF-11.5** El sistema deberá permitir generar solo las cuotas del mes en
  curso; para meses anteriores se usan cargos manuales.
- **RF-11.6** El sistema deberá dar a cada cuota mensual el concepto
  «Cuota {mes} - {grupo}», el importe de la cuota del grupo en el momento de
  generarla y, como fecha de emisión, la más tardía entre el día 1 del mes y la
  fecha de alta de la matrícula.
- **RF-11.7** Cuando Recepción o Dirección creen un cargo manual con concepto e
  importe válidos para un alumno no anonimizado, el sistema deberá guardarlo
  con fecha de emisión de hoy, mostrando [M-12].
- **RF-11.8** El sistema deberá fijar el vencimiento de cada cargo 10 días
  naturales después de su fecha de emisión (D-11).
- **RF-11.9** El sistema deberá calcular el saldo de un cargo como su importe
  menos lo aplicado por pagos no anulados.
- **RF-11.10** El sistema deberá asignar a cada cargo uno de estos estados:
  *anulado*; *pagado* (saldo 0); *vencido* (saldo mayor que 0 y hoy posterior
  al vencimiento); *pendiente* (los demás).
- **RF-11.11** Cuando Dirección anule un cargo indicando un motivo, el sistema
  deberá marcarlo como anulado y excluirlo de la deuda, mostrando [M-13].
- **RF-11.12** Si el cargo que se intenta anular tiene pagos aplicados no
  anulados, entonces el sistema deberá rechazarlo con [E-26].
- **RF-11.13** Si el cargo o el pago que se intenta anular ya está anulado,
  entonces el sistema deberá rechazarlo con [E-38].

### RF-12 — Pagos (HU-10)

- **RF-12.1** Cuando Recepción o Dirección registren un pago válido de un
  alumno, el sistema deberá guardarlo con su importe, fecha, medio (efectivo,
  transferencia, tarjeta u otro) y una referencia opcional, mostrando [M-14].
  Un pago corresponde a un solo alumno: el pago conjunto de varios hermanos se
  registra como un pago por alumno, con la misma referencia.
- **RF-12.2** Cuando se guarde un pago, el sistema deberá aplicarlo a los cargos
  no anulados con saldo del alumno, empezando por la fecha de emisión más
  antigua y, a igual fecha, por el cargo creado antes, hasta agotar el importe.
- **RF-12.3** Si el alumno no tiene deuda pendiente, entonces el sistema deberá
  rechazar el pago con [E-23].
- **RF-12.4** Si el importe del pago supera la deuda pendiente del alumno,
  entonces el sistema deberá rechazarlo con [E-24] (D-18).
- **RF-12.5** Si la fecha del pago es posterior a hoy o anterior a 31 días antes
  de hoy, entonces el sistema deberá rechazarla con [E-25].
- **RF-12.6** Cuando Dirección anule un pago indicando un motivo, el sistema
  deberá devolver a cada cargo el importe que ese pago le había aplicado,
  mostrando [M-15].
- **RF-12.7** El sistema deberá usar la fecha del pago solo como dato
  informativo: la aplicación a cargos (RF-12.2) y la morosidad (RF-13.3)
  dependen del momento en que se registra el pago.

### RF-13 — Estado de cuenta y morosidad (HU-11)

- **RF-13.1** Cuando Recepción o Dirección consulten el estado de cuenta de un
  alumno, el sistema deberá mostrar sus cargos (concepto, emisión, vencimiento,
  importe, saldo y estado), sus pagos (fecha, importe, medio y si están
  anulados) y los totales de deuda pendiente y deuda vencida.
- **RF-13.2** El sistema deberá calcular la deuda pendiente como la suma de los
  saldos de los cargos no anulados, y la deuda vencida como la suma de los
  saldos de los cargos vencidos.
- **RF-13.3** El sistema deberá considerar moroso a un alumno, activo o de baja,
  mientras tenga deuda vencida.
- **RF-13.4** Cuando Recepción o Dirección consulten el listado de morosos, el
  sistema deberá mostrar cada alumno moroso con su nombre, estado, responsable
  de pago y su teléfono, deuda vencida y días de atraso, de más a menos días de
  atraso.
- **RF-13.5** El sistema deberá calcular los días de atraso como los días
  transcurridos desde el vencimiento del cargo vencido más antiguo hasta hoy.
- **RF-13.6** Mientras no haya alumnos morosos, el sistema deberá mostrar [M-16]
  en el listado de morosos.

### RF-14 — Vista del profesor (HU-12)

- **RF-14.1** Cuando una cuenta con rol Profesor inicie sesión, el sistema
  deberá mostrarle sus grupos no archivados con su horario.
- **RF-14.2** Mientras un profesor no tenga grupos no archivados, el sistema
  deberá mostrarle [M-29].
- **RF-14.3** Cuando un profesor abra uno de sus grupos, el sistema deberá
  mostrar los alumnos con matrícula activa en él, con su nombre, edad, teléfono
  propio (cuando lo tengan) y el nombre, la relación y el teléfono de cada
  contacto.
- **RF-14.4** El sistema deberá señalar en esa lista a los alumnos que tienen
  observaciones de salud, sin mostrar su contenido.
- **RF-14.5** Cuando un profesor pida ver las observaciones de salud de un
  alumno de sus grupos, el sistema deberá mostrárselas.
- **RF-14.6** Mientras una cuenta con rol Dirección sea profesora de algún
  grupo no archivado, el sistema deberá mostrarle en el inicio la lista de
  esos grupos, además de lo que ve Dirección.

### RF-15 — Derechos del titular (HU-13)

- **RF-15.1** Cuando Dirección exporte la ficha de un alumno, el sistema
  deberá generar un documento imprimible con secciones fijas (datos
  personales, contactos, autorizaciones, matrículas, cargos, pagos y
  solicitudes), en el que figuran todos los datos guardados del alumno con su
  etiqueta en español y los formatos de RNF-1, mostrando [M-21].
- **RF-15.2** Cuando Dirección exporte la ficha de un contacto, el sistema
  deberá generar un documento imprimible con todos sus datos guardados, los
  alumnos a los que está vinculado y sus solicitudes, con su etiqueta en
  español y los formatos de RNF-1, mostrando [M-21].
- **RF-15.3** Cuando Dirección pida suprimir los datos de un alumno de baja, el
  sistema deberá pedir confirmación con [M-19].
- **RF-15.4** Cuando se confirme la supresión, el sistema deberá anonimizar al
  alumno de inmediato según RF-16.3, mostrando [M-20].
- **RF-15.5** Si el alumno cuyos datos se intentan suprimir está activo,
  entonces el sistema deberá rechazarlo con [E-28].
- **RF-15.6** Si el alumno cuyos datos se intentan suprimir tiene deuda
  pendiente, entonces el sistema deberá rechazarlo con [E-27].
- **RF-15.7** Cuando Dirección suprima los datos de un contacto, el sistema
  deberá desvincularlo de todos sus alumnos y borrar sus datos, mostrando
  [M-31].
- **RF-15.8** Si el contacto cuyos datos se intentan suprimir es el único
  contacto de un alumno menor no anonimizado, entonces el sistema deberá
  rechazarlo con [E-9].
- **RF-15.9** Si el contacto cuyos datos se intentan suprimir es responsable de
  pago de algún alumno no anonimizado, entonces el sistema deberá rechazarlo
  con [E-40].
- **RF-15.10** Cuando Dirección registre una solicitud de un titular, el
  sistema deberá guardar su tipo (consulta, rectificación, supresión o
  revocación), el titular, la fecha de recepción y, cuando se responda, la
  fecha de respuesta.
- **RF-15.11** Si la fecha de respuesta de una solicitud es anterior a su
  fecha de recepción, entonces el sistema deberá rechazarla con [E-48].

La rectificación se hace editando la ficha (RF-7.6) y la revocación de los
datos de salud con RF-6.10. La revocación de la autorización general se
atiende con la baja (RF-8) y la supresión (RF-15.3); si hay deuda pendiente,
los datos se conservan hasta saldarla (RF-15.6, RF-16.6).

### RF-16 — Conservación y anonimización (HU-14)

- **RF-16.1** El sistema deberá revisar los plazos de conservación una vez al
  día; si un día la revisión no se ejecuta, la siguiente trata todo lo
  pendiente.
- **RF-16.2** Mientras hayan pasado al menos 2 años desde la fecha de baja de un
  alumno no anonimizado y no tenga deuda pendiente, el sistema deberá
  anonimizarlo en la revisión diaria (D-12).
- **RF-16.3** El sistema deberá anonimizar a un alumno sustituyendo su nombre
  y apellidos por «Alumno anonimizado {número}», borrando su fecha de
  nacimiento, teléfono, correo, observaciones de salud, autorizaciones y
  solicitudes, y eliminando sus vínculos con contactos.
- **RF-16.4** El sistema deberá conservar los cargos, los pagos y las
  matrículas de un alumno anonimizado, sin datos personales, hasta 10 años
  después de su fecha de baja.
- **RF-16.5** Mientras hayan pasado al menos 10 años desde la fecha de baja de
  un alumno anonimizado, el sistema deberá eliminar en la revisión diaria sus
  cargos, pagos, matrículas y su propio registro.
- **RF-16.6** Mientras un alumno con el plazo de 2 años vencido tenga deuda
  pendiente, el sistema deberá conservar sus datos sin anonimizar.
- **RF-16.7** El sistema deberá eliminar las entradas de auditoría con más de 5
  años de antigüedad.
- **RF-16.8** Mientras hayan pasado al menos 5 años desde la desactivación de
  una cuenta, el sistema deberá sustituir en la revisión diaria su nombre por
  «Cuenta anonimizada {número}» y borrar su correo, su credencial y su segundo
  factor.
- **RF-16.9** Cuando se anonimice un alumno, el sistema deberá sustituir el
  concepto de sus cargos manuales por «Cargo manual» y borrar las referencias
  de sus pagos y los motivos de anulación de sus cargos y pagos.
- **RF-16.10** El sistema deberá excluir a los alumnos anonimizados de todas
  las búsquedas, listas y fichas; sus registros económicos solo cuentan en los
  totales.

### RF-17 — Auditoría (HU-15)

- **RF-17.1** El sistema deberá registrar en la auditoría (D-4): altas,
  cambios, bajas, reactivaciones, supresiones y anonimizaciones de alumnos y
  contactos; vínculos y desvínculos; registro y revocación de autorizaciones;
  altas y finalizaciones de matrículas; creación y anulación de cargos y
  pagos; cada consulta de observaciones de salud; cada exportación de una
  ficha; el registro y la respuesta de solicitudes; y la creación, el cambio
  de rol, la desactivación, la reactivación, el restablecimiento de acceso, la
  activación, el desbloqueo, el cierre de sesiones y la anonimización de las
  cuentas.
- **RF-17.2** El sistema deberá guardar en cada entrada de auditoría la fecha y
  la hora, la cuenta que actúa (o «sistema»), la acción y el tipo y el número
  interno del registro afectado, sin ningún valor de datos personales.
- **RF-17.3** Cuando Dirección consulte la auditoría filtrando por alumno, por
  cuenta o por rango de fechas, el sistema deberá mostrar las entradas que
  cumplan el filtro, de la más reciente a la más antigua.
- **RF-17.4** El sistema deberá impedir a toda cuenta, sea cual sea su rol,
  modificar o borrar una entrada de auditoría; solo la revisión diaria elimina
  las de más de 5 años (RF-16.7).
- **RF-17.5** Si no se puede escribir la entrada de auditoría de una operación,
  entonces el sistema deberá cancelar la operación entera con [E-36].

### RF-18 — Inicio (HU-16)

- **RF-18.1** Mientras alguna matrícula activa el día 1 del mes en curso no
  tenga la cuota de ese mes, el sistema deberá mostrar [M-11] en el inicio de
  Recepción y Dirección.
- **RF-18.2** El sistema deberá mostrar en el inicio de Recepción y Dirección la
  lista de alumnos con la autorización pendiente de renovar (RF-6.7).
- **RF-18.3** El sistema deberá mostrar en el inicio de Recepción y Dirección el
  número de alumnos morosos y la deuda vencida total.
- **RF-18.4** Mientras haya alumnos en la situación de RF-16.6, el sistema
  deberá mostrar [M-30] en el inicio de Dirección.
- **RF-18.5** Mientras haya solicitudes de titulares sin responder, el sistema
  deberá mostrar [M-36] en el inicio de Dirección, con los días naturales
  transcurridos desde la recepción de cada una.

El inicio de un profesor es la lista de sus grupos (RF-14.1).

## 5. Matriz de permisos

«Sí» permite la acción; «No» la rechaza con [E-1] (RF-3.2).

| Acción | RF | Dirección | Recepción | Profesor |
|--------|----|-----------|-----------|----------|
| Crear cuentas, cambiar su rol, desactivarlas, reactivarlas, restablecer su acceso, desbloquearlas y cerrar sus sesiones | RF-2.7–RF-2.16, RF-2.21, RF-2.25 | Sí | No | No |
| Buscar y listar alumnos | RF-7.1–RF-7.3 | Sí | Sí | No |
| Ver la ficha completa de un alumno | RF-7.4 | Sí | Sí | No |
| Ver los alumnos de un grupo con edad y contactos | RF-14.3 | Sí, todos los grupos | Sí, todos los grupos | Solo sus grupos |
| Ver observaciones de salud | RF-7.5, RF-14.5 | Sí | No | Solo alumnos de sus grupos |
| Escribir o sustituir observaciones de salud, sin ver las anteriores | RF-6.5, RF-7.11 | Sí | Sí | No |
| Dar de alta y editar alumnos y contactos; vincular y desvincular | RF-4, RF-5, RF-7.6 | Sí | Sí | No |
| Registrar autorizaciones y revocar la de salud | RF-6 | Sí | Sí | No |
| Dar de baja y reactivar alumnos | RF-8 | Sí | Sí | No |
| Crear, editar, archivar y desarchivar grupos | RF-9.1–RF-9.13 | Sí | No | No |
| Consultar la lista de grupos | RF-9.14, RF-14.1 | Sí | Sí | Solo sus grupos |
| Matricular y finalizar matrículas | RF-10 | Sí | Sí | No |
| Generar cuotas y crear cargos manuales | RF-11.2, RF-11.7 | Sí | Sí | No |
| Anular cargos | RF-11.11 | Sí | No | No |
| Registrar pagos | RF-12.1 | Sí | Sí | No |
| Anular pagos | RF-12.6 | Sí | No | No |
| Ver estados de cuenta y el listado de morosos | RF-13 | Sí | Sí | No |
| Exportar fichas de titulares | RF-15.1, RF-15.2 | Sí | No | No |
| Suprimir datos a petición del titular | RF-15.3–RF-15.9 | Sí | No | No |
| Registrar y responder solicitudes de titulares | RF-15.10, RF-15.11 | Sí | No | No |
| Consultar la auditoría | RF-17.3 | Sí | No | No |
| Ver los avisos del inicio | RF-18 | Sí | Sí, salvo RF-18.4 y RF-18.5 | No |

La anulación automática de RF-10.10 la hace el «sistema», no la cuenta que
finaliza la matrícula, así que no exige el permiso de anular cargos.

## 6. Mensajes

`{...}` se sustituye por su valor: `{nombre completo}` es «nombre apellidos»;
`{importe}` y `{mes}` siguen el formato de RNF-1.

| Id | Cuándo | Texto exacto |
|----|--------|--------------|
| M-1 | Alumno dado de alta (RF-4.1) | `Alumno dado de alta: {nombre completo}.` |
| M-2 | Cambios guardados (RF-7.6) | `Cambios guardados.` |
| M-3 | Confirmar baja (RF-8.1) | `¿Dar de baja a {nombre completo}? Se finalizarán sus {n} matrículas activas y se borrarán sus observaciones de salud. La deuda pendiente se conserva.` |
| M-4 | Baja hecha (RF-8.2) | `Se ha dado de baja a {nombre completo}.` |
| M-5 | Reactivación (RF-8.6) | `Se ha reactivado a {nombre completo}.` |
| M-6 | Matrícula creada (RF-10.1) | `Matrícula creada: {nombre completo} en {grupo}.` |
| M-7 | Matricular a un moroso (RF-10.2) | `{nombre completo} tiene una deuda vencida de {importe}. ¿Matricular de todos modos?` |
| M-8 | Matrícula finalizada (RF-10.7) | `Matrícula finalizada: {nombre completo} en {grupo}.` |
| M-9 | Cuotas generadas (RF-11.2) | `Cuotas de {mes} generadas: {n} nuevas.` |
| M-10 | Nada que generar (RF-11.4) | `Las cuotas de {mes} ya estaban generadas. No se ha creado ninguna nueva.` |
| M-11 | Cuotas pendientes de generar (RF-18.1) | `Las cuotas de {mes} aún no se han generado.` |
| M-12 | Cargo creado (RF-11.7) | `Cargo creado: {concepto} por {importe}.` |
| M-13 | Cargo anulado (RF-11.11) | `Cargo anulado.` |
| M-14 | Pago registrado (RF-12.1) | `Pago registrado: {importe}. Deuda pendiente: {importe}.` |
| M-15 | Pago anulado (RF-12.6) | `Pago anulado. Deuda pendiente: {importe}.` |
| M-16 | Sin morosos (RF-13.6) | `No hay alumnos con deuda vencida.` |
| M-17 | Autorización pendiente de renovar (RF-6.8) | `{nombre completo} cumplió 18 años el {fecha}. Registra una nueva autorización de tratamiento de datos otorgada por el propio alumno.` |
| M-18 | Teléfono repetido (RF-5.6) | `Ya existe un contacto con este teléfono: {nombre completo del contacto}. ¿Quieres vincular ese contacto?` |
| M-19 | Confirmar supresión (RF-15.3) | `Se anonimizarán de forma irreversible los datos personales de {nombre completo}. Los registros económicos se conservan sin datos personales. ¿Continuar?` |
| M-20 | Supresión hecha (RF-15.4) | `Datos suprimidos. El registro queda como {alias}.` |
| M-21 | Ficha exportada (RF-15.1, RF-15.2) | `Ficha exportada. Entrégala solo al titular o a su representante y no guardes copias.` |
| M-22 | Cuenta creada (RF-2.7, RF-2.16) | `Cuenta creada para {nombre} con rol {rol}. Código de activación: {código} (válido 72 horas).` |
| M-23 | Cuenta desactivada (RF-2.9) | `Cuenta desactivada: {nombre}.` |
| M-24 | Búsqueda sin resultados (RF-7.3) | `No hay alumnos que coincidan con la búsqueda.` |
| M-25 | Grupo creado (RF-9.1) | `Grupo creado: {grupo}.` |
| M-26 | Grupo archivado (RF-9.10) | `Grupo archivado: {grupo}.` |
| M-27 | Revocación de salud (RF-6.10) | `Autorización de datos de salud revocada. Se han borrado las observaciones de salud.` |
| M-28 | Sesión caducada (RF-2.6) | `Tu sesión se cerró por inactividad. Vuelve a iniciar sesión.` |
| M-29 | Profesor sin grupos (RF-14.2) | `No tienes grupos asignados.` |
| M-30 | Conservación retenida por deuda (RF-18.4) | `{n} alumnos han superado el plazo de conservación, pero no se pueden anonimizar porque tienen deuda pendiente.` |
| M-31 | Contacto suprimido (RF-15.7) | `Datos del contacto suprimidos.` |
| M-32 | Cuenta reactivada (RF-2.12) | `Cuenta reactivada: {nombre}.` |
| M-33 | Acceso restablecido (RF-2.13) | `Acceso restablecido para {nombre}. Nuevo código de activación: {código} (válido 72 horas).` |
| M-34 | Grupo desarchivado (RF-9.12) | `Grupo desarchivado: {grupo}.` |
| M-35 | Aviso en campos de texto libre (RF-1.17) | `No escribas aquí datos personales ni de salud.` |
| M-36 | Solicitudes sin responder (RF-18.5) | `Solicitudes de titulares sin responder: {n}. La Ley 1581 da 10 días hábiles para las consultas y 15 para los reclamos.` |
| M-37 | Cuenta desbloqueada (RF-2.21) | `Cuenta desbloqueada: {nombre}.` |
| M-38 | Contraseña definida (RF-2.17) | `Contraseña guardada. Ya puedes iniciar sesión.` |
| M-39 | Sesiones cerradas (RF-2.25) | `Se han cerrado todas las sesiones de {nombre}.` |
| E-1 | Sin permiso (RF-3.2) | `No tienes permiso para realizar esta acción.` |
| E-2 | Campo obligatorio vacío (RF-1.3, RF-6.9) | `Este campo es obligatorio.` |
| E-3 | Texto demasiado largo (RF-1.4) | `Máximo {n} caracteres.` |
| E-4 | Caracteres de control (RF-1.5) | `Contiene caracteres no permitidos.` |
| E-5 | Teléfono no válido (RF-1.8) | `El teléfono debe tener 10 dígitos (puede empezar por +57).` |
| E-6 | Correo no válido (RF-1.9) | `El correo electrónico no es válido.` |
| E-7 | Fecha de nacimiento no válida (RF-4.3) | `La fecha de nacimiento debe corresponder a una edad entre 2 y 100 años.` |
| E-8 | Alumno duplicado (RF-4.4) | `Ya existe un alumno con ese nombre y fecha de nacimiento: {nombre completo} ({estado}).` |
| E-9 | Menor sin tutor (RF-4.5, RF-5.9, RF-15.8) | `Un alumno menor de edad necesita al menos un tutor.` |
| E-10 | Demasiados contactos (RF-5.5) | `Un alumno puede tener como máximo 2 contactos.` |
| E-11 | Falta la autorización (RF-6.2, RF-8.7) | `Registra la autorización de tratamiento de datos antes de continuar.` |
| E-12 | Otorgante no válido (RF-6.3) | `La autorización debe otorgarla el propio alumno si es adulto, o uno de sus tutores si es menor.` |
| E-13 | Salud sin autorización (RF-6.5) | `Las observaciones de salud requieren la autorización de datos de salud.` |
| E-14 | Alumno de baja (RF-7.8, RF-10.6) | `El alumno está de baja. Reactívalo antes de continuar.` |
| E-15 | Ya matriculado (RF-10.3) | `{nombre completo} ya tiene una matrícula activa en {grupo}.` |
| E-16 | Grupo lleno (RF-10.4, RF-10.9) | `El grupo {grupo} no tiene plazas libres.` |
| E-17 | Grupo archivado (RF-10.5) | `El grupo {grupo} está archivado.` |
| E-18 | Nombre de grupo repetido (RF-9.3, RF-9.13) | `Ya existe un grupo sin archivar llamado {grupo}.` |
| E-19 | Franja no válida (RF-9.5) | `La hora de fin debe ser posterior a la de inicio.` |
| E-20 | Cupo menor que las matrículas (RF-9.9) | `El cupo no puede ser menor que las {n} matrículas activas.` |
| E-21 | Archivar con matrículas (RF-9.11) | `No se puede archivar un grupo con matrículas activas.` |
| E-22 | Importe no válido (RF-1.11) | `El importe debe ser un número entero entre 1 y 10.000.000.` |
| E-23 | Pago sin deuda (RF-12.3) | `{nombre completo} no tiene deuda pendiente.` |
| E-24 | Pago mayor que la deuda (RF-12.4) | `El pago supera la deuda pendiente ({importe}).` |
| E-25 | Fecha de pago no válida (RF-12.5) | `La fecha del pago no puede ser futura ni de hace más de 31 días.` |
| E-26 | Anular cargo con pagos (RF-11.12) | `El cargo tiene pagos aplicados. Anula primero esos pagos.` |
| E-27 | Suprimir con deuda (RF-15.6) | `No se pueden suprimir los datos de un alumno con deuda pendiente.` |
| E-28 | Suprimir a un alumno activo (RF-15.5) | `Da de baja al alumno antes de suprimir sus datos.` |
| E-29 | Última cuenta de Dirección (RF-2.10) | `Debe quedar al menos una cuenta activa con rol Dirección.` |
| E-30 | Cuenta con grupos (RF-2.11) | `{nombre} es profesor de grupos sin archivar. Reasígnalos antes de continuar.` |
| E-31 | Acceso incorrecto (RF-2.3, RF-2.23) | `Correo o contraseña incorrectos.` |
| E-32 | Cuenta bloqueada (RF-2.4) | `Cuenta bloqueada temporalmente por intentos fallidos. Inténtalo de nuevo en 15 minutos.` |
| E-33 | Correo de cuenta repetido (RF-2.8) | `Ya existe una cuenta con ese correo.` |
| E-34 | Número de franjas (RF-9.4) | `El horario debe tener entre 1 y 7 franjas.` |
| E-35 | Cambio simultáneo (RF-1.15) | `Otra persona ha modificado estos datos. Vuelve a cargarlos e inténtalo de nuevo.` |
| E-36 | No se pudo guardar (RF-17.5) | `No se han podido guardar los cambios. Inténtalo de nuevo.` |
| E-37 | Alumno anonimizado (RF-7.9) | `Los datos de este alumno se suprimieron; no se pueden modificar ni reactivar.` |
| E-38 | Ya anulado (RF-11.13) | `Este registro ya estaba anulado.` |
| E-39 | Responsable de pago no válido (RF-4.7) | `El responsable de pago debe ser uno de los contactos del alumno o, si es adulto, el propio alumno.` |
| E-40 | Desvincular al responsable de pago (RF-5.10, RF-15.9) | `Este contacto es responsable de pago. Elige otro responsable antes de continuar.` |
| E-41 | Fecha futura (RF-1.14) | `La fecha no puede ser posterior a hoy.` |
| E-42 | Cupo no válido (RF-9.6) | `El cupo debe ser un número entero entre 1 y 100.` |
| E-43 | Profesor no válido (RF-9.7) | `Elige como profesor una cuenta activa con rol Profesor o Dirección.` |
| E-44 | Código de activación no válido (RF-2.18) | `El código de activación no es válido o ha caducado. Pide uno nuevo a Dirección.` |
| E-45 | Contraseña corta (RF-2.19) | `La contraseña debe tener al menos 12 caracteres.` |
| E-46 | Franjas solapadas (RF-9.15) | `Dos franjas del mismo día no pueden solaparse.` |
| E-47 | Falta la opinión del menor (RF-6.11) | `Confirma que se tuvo en cuenta la opinión del menor.` |
| E-48 | Respuesta anterior a la recepción (RF-15.11) | `La fecha de respuesta no puede ser anterior a la de recepción.` |

## 7. Datos que se guardan

Nivel lógico, sin tecnología. Cada dato cita el requisito que lo justifica
(principio 7). No se guardan documento de identidad (D-20), dirección postal,
fotografías ni documentos escaneados.

| Entidad | Dato | Obligatorio | Límite | Requisito |
|---------|------|-------------|--------|-----------|
| Cuenta | Nombre | Sí | 60 caracteres | RF-2.7 |
| Cuenta | Correo de acceso | Sí | 254 caracteres | RF-2.2, RF-2.8 |
| Cuenta | Credencial (nunca la contraseña legible) | Sí | — | RF-2.2, RNF-5 |
| Cuenta | Rol | Sí | Dirección, Recepción o Profesor | RF-2.14 |
| Cuenta | Activa | Sí | sí / no | RF-2.9 |
| Cuenta | Intentos fallidos y fin del bloqueo | No | — | RF-2.4, RF-2.20 |
| Cuenta | Código de activación (nunca legible) y su caducidad | No | 72 horas | RF-2.16 |
| Cuenta | Segundo factor (solo rol Dirección) | Sí en Dirección | — | RF-2.22 |
| Cuenta | Fecha de desactivación | No | — | RF-16.8 |
| Alumno | Número interno | Sí | — | RF-16.3, RF-17.2 |
| Alumno | Nombre / Apellidos | Sí | 60 caracteres cada uno | RF-4.2 |
| Alumno | Fecha de nacimiento | Sí | — | RF-1.12, RF-4.3 |
| Alumno | Teléfono propio | Sí si es adulto | 10 dígitos | RF-4.8, RF-14.3 |
| Alumno | Correo | No | 254 caracteres | RF-4.2 |
| Alumno | Observaciones de salud | No | 500 caracteres | RF-6.5, RF-14.5 |
| Alumno | Estado y fecha de baja | Sí | activo / de baja | RF-8.2, RF-16.2 |
| Alumno | Responsable de pago | Sí | el alumno o uno de sus contactos | RF-4.6, RF-13.4 |
| Alumno | Anonimizado | Sí | sí / no | RF-16.3 |
| Contacto | Nombre / Apellidos | Sí | 60 caracteres cada uno | RF-5.2 |
| Contacto | Teléfono | Sí | 10 dígitos | RF-5.2, RF-14.3 |
| Contacto | Correo | No | 254 caracteres | RF-5.2 |
| Vínculo | Alumno, contacto y relación | Sí | relación: 30 caracteres | RF-5.2 |
| Autorización | Alumno, fecha de firma, nombre completo y relación del otorgante, incluye salud | Sí | — | RF-6.1 |
| Autorización | Opinión del menor tenida en cuenta | Sí en menores de 12 años o más | sí | RF-6.11 |
| Autorización | Revocación de salud (fecha) | No | — | RF-6.10 |
| Grupo | Nombre | Sí | 60 caracteres | RF-9.2 |
| Grupo | Estilo | Sí | 40 caracteres | RF-9.2 |
| Grupo | Profesor | Sí | una cuenta | RF-9.2 |
| Grupo | Cupo | Sí | 1–100 | RF-9.6 |
| Grupo | Cuota mensual | Sí | 1–10.000.000 pesos | RF-9.2, RF-11.6 |
| Grupo | Archivado | Sí | sí / no | RF-9.10 |
| Franja | Grupo, día de la semana, hora de inicio, hora de fin | Sí | 1–7 por grupo | RF-9.2 |
| Matrícula | Alumno, grupo, fecha de alta | Sí | — | RF-10.1 |
| Matrícula | Fecha de baja | No | — | RF-10.7 |
| Cargo | Alumno, tipo (cuota mensual o manual), concepto, importe, fecha de emisión | Sí | concepto: 100 caracteres | RF-11.6, RF-11.7 |
| Cargo | Matrícula, grupo y mes (solo cuotas mensuales) | Sí en cuotas | — | RF-11.1 |
| Cargo | Anulación: fecha, cuenta y motivo | No | motivo: 200 caracteres | RF-11.11 |
| Pago | Alumno, importe, fecha, medio | Sí | — | RF-12.1 |
| Pago | Referencia | No | 50 caracteres | RF-12.1 |
| Pago | Anulación: fecha, cuenta y motivo | No | motivo: 200 caracteres | RF-12.6 |
| Aplicación | Pago, cargo e importe aplicado | Sí | — | RF-12.2 |
| Solicitud | Titular, tipo, fecha de recepción | Sí | consulta, rectificación, supresión o revocación | RF-15.10 |
| Solicitud | Fecha de respuesta | No | — | RF-15.10, RF-15.11 |
| Auditoría | Fecha y hora, cuenta o «sistema», acción, tipo y número del registro | Sí | — | RF-17.2 |

El vencimiento, el saldo, el estado de un cargo, la edad y la deuda se
calculan; no se guardan.

## 8. Requisitos no funcionales

| Id | Requisito | Cómo se verifica |
|----|-----------|------------------|
| RNF-1 | **Idioma y formatos:** todo lo que ve el personal está en español. Fechas `dd/mm/aaaa`; importes `$ 1.250.000`; teléfonos `300 123 4567`; meses `octubre de 2026`. | Tests de las funciones de formato; revisión de que todos los textos están en la sección 6. |
| RNF-2 | **Capacidad:** 1.000 alumnos (contando los de baja), 2.000 contactos, 50 grupos, 20 cuentas, 5 años de cargos y pagos (unos 60.000 cargos) y 10 personas usando la app a la vez (D-15). | Prueba de carga con datos ficticios generados de ese volumen. |
| RNF-3 | **Rapidez:** con el volumen de RNF-2 y 10 personas a la vez repartiéndose a partes iguales buscar alumnos, abrir una ficha, registrar un pago, matricular, ver el listado de morosos y abrir un grupo como profesor, el 95 % de esas operaciones responde en menos de 1 segundo y ninguna en más de 3; generar las cuotas del mes tarda menos de 10 segundos. | La misma prueba de carga, en el entorno de pruebas, midiendo los percentiles. |
| RNF-4 | **Dispositivos:** las pantallas de Dirección y Recepción se usan en un ordenador de 1280 px de ancho o más; las del profesor (RF-14) también en un teléfono de 360 px de ancho, sin desplazamiento horizontal. | Prueba automatizada de las pantallas en ambos anchos. |
| RNF-5 | **Seguridad del acceso:** toda comunicación con la app va cifrada; las contraseñas tienen al menos 12 caracteres y solo se guarda su resumen criptográfico; la sesión y el bloqueo siguen RF-2.4 y RF-2.5. | Tests de RF-2; revisión de la configuración de despliegue (principio 8). |
| RNF-6 | **Registros técnicos sin datos personales:** los registros técnicos y los mensajes de error no contienen nombres, teléfonos, correos, fechas de nacimiento ni observaciones de salud. | Test que recorre los flujos principales con datos ficticios y busca esos valores en los registros generados. |
| RNF-7 | **Datos de prueba ficticios:** ningún dato real sale del entorno de producción; las pruebas usan datos ficticios del repositorio. | Revisión de las fixtures y del procedimiento de copias (principio 8). |
| RNF-8 | **Copias de seguridad:** diaria, cifrada, conservada 30 días; pérdida máxima de 24 horas de datos; restauración completa en menos de 4 horas, probada cada trimestre (D-5). Tras restaurar, se ejecuta la revisión de plazos (RF-16.1) antes de abrir la app y Dirección repite las supresiones a petición posteriores a la copia, a partir de las respuestas enviadas a los titulares. | Registro de cada prueba de restauración con su fecha, su duración y la comprobación de que se ejecutó la revisión de plazos. |
| RNF-9 | **Integridad:** cada operación se guarda entera o no se guarda nada; en particular, un pago con sus aplicaciones, una baja con sus matrículas y su borrado de salud, y cualquier operación con su entrada de auditoría. | Tests que fuerzan un fallo a mitad de cada una de esas operaciones y comprueban que no cambió nada. |
| RNF-10 | **Disponibilidad:** la app está disponible el 99 % del horario de apertura (lunes a sábado, de 7:00 a 21:00, hora de Bogotá) de cada mes, sin contar paradas programadas avisadas con 48 horas. | Monitor externo que comprueba la app cada 5 minutos; informe mensual. |
| RNF-11 | **Verificabilidad:** las pruebas pueden fijar la fecha y la hora de «hoy» y usar datos ficticios aislados en cualquier operación (principio 4). | Existe al menos un test por RF que fija la fecha. |
| RNF-12 | **Accesibilidad básica:** todos los campos tienen etiqueta y todos los formularios se pueden completar solo con el teclado. | Revisión automática de accesibilidad sin errores de nivel A de WCAG 2.1, y prueba manual con teclado. |
| RNF-13 | **Nada guardado en el dispositivo:** las pantallas no guardan datos personales en el dispositivo para usarlos sin conexión; al cerrar la sesión no queda ningún dato personal accesible en él. | Revisión registrada en un teléfono y un ordenador de prueba tras cerrar la sesión. |

## 9. Casos límite

| # | Situación | Resultado esperado |
|---|-----------|--------------------|
| CL-1 | Alumno que cumple 18 años hoy | Es adulto (RF-1.13) |
| CL-2 | Alumno que cumple 18 años mañana | Es menor y necesita al menos un tutor (RF-4.5) |
| CL-3 | Nacido el 29/02 y hoy es 28/02 de un año no bisiesto | Aún no ha cumplido años; los cumple el 01/03 (RF-1.12) |
| CL-4 | Fecha de nacimiento igual a hoy | [E-7] (RF-4.3) |
| CL-5 | Alta de «maria  perez» existiendo «María Pérez» con la misma fecha de nacimiento | [E-8] (RF-1.2, RF-1.6, RF-4.4) |
| CL-6 | Alta de «Ana Pena» existiendo «Ana Peña» con la misma fecha de nacimiento | Se permite: la «ñ» distingue (RF-1.6) |
| CL-7 | Alta de alguien con el mismo nombre y fecha que un alumno anonimizado | Se permite (RF-4.4) |
| CL-8 | Teléfono «+57 (300) 123-4567» / teléfono de 9 dígitos | Se guarda `3001234567` / [E-5] (RF-1.7, RF-1.8) |
| CL-9 | Un menor cumple 18 años | Sus tutores pasan a ser contactos de emergencia; [M-17] en su ficha y aparece en el inicio; nada se bloquea (RF-5.4, RF-6.7, RF-6.8, RF-18.2) |
| CL-10 | Vincular un tercer contacto a un alumno | [E-10] (RF-5.5) |
| CL-11 | Desvincular al único tutor de un menor | [E-9] (RF-5.9) |
| CL-12 | Desvincular al contacto que es responsable de pago | [E-40] (RF-5.10) |
| CL-13 | Contacto vinculado a dos hermanos; uno se anonimiza | El contacto se conserva por el otro hermano (RF-5.11, RF-16.3) |
| CL-14 | Nuevo contacto con el teléfono fijo de otro contacto | [M-18]; se puede crear igualmente (RF-5.6) |
| CL-15 | Guardar observaciones de salud con una autorización que no incluye la salud | [E-13] (RF-6.5) |
| CL-16 | Baja de un alumno con 3 matrículas y deuda vencida | Matrículas finalizadas, salud borrada; sigue siendo moroso (RF-8.3, RF-8.4, RF-8.5) |
| CL-17 | Reactivar a un alumno de baja | Exige nueva autorización; vuelve sin matrículas ni observaciones de salud (RF-8.6, RF-8.7, RF-8.9) |
| CL-18 | Matrícula creada el día 15 | Cuota del mes generada al momento, emitida el día 15 y con vencimiento el 25 (RF-11.3, RF-11.6, RF-11.8) |
| CL-19 | Matrícula creada el día 16 | Sin cuota ese mes; la del mes siguiente se crea al generar las cuotas (RF-11.2, RF-11.3) |
| CL-20 | Generar las cuotas dos veces en el mismo mes | La segunda vez, [M-10] y ninguna cuota nueva (RF-11.1, RF-11.4) |
| CL-21 | Matrícula finalizada el día 1, antes de generar las cuotas | No se genera su cuota: no estaba activa el día 1 (RF-10.8, RF-11.2) |
| CL-22 | Matrícula creada y finalizada el mismo día por error | Su cuota se anula sola si no tiene pagos (RF-10.10) |
| CL-23 | Se olvidó generar las cuotas del mes anterior | No se pueden generar; se crean cargos manuales (RF-11.5) |
| CL-24 | Pago de $ 150.000 con una deuda pendiente de $ 120.000 | [E-24] (RF-12.4) |
| CL-25 | Pago parcial de $ 50.000 con dos cargos de $ 80.000 | Se aplica al más antiguo: saldos $ 30.000 y $ 80.000 (RF-12.2) |
| CL-26 | Anular un cargo que tiene pagos aplicados | [E-26] (RF-11.12) |
| CL-27 | Anular un pago aplicado a dos cargos | Ambos cargos recuperan su saldo (RF-12.6) |
| CL-28 | Cargo que vence hoy | Pendiente, no vencido; mañana pasa a vencido (RF-11.10) |
| CL-29 | Pago con fecha de hace 32 días | [E-25] (RF-12.5) |
| CL-30 | Cambiar la cuota de un grupo a mitad de mes | Las cuotas ya generadas no cambian (RF-9.8) |
| CL-31 | Dos personas ocupan a la vez la última plaza de un grupo | Solo se crea una matrícula; la otra recibe [E-16] (RF-10.9) |
| CL-32 | Reducir el cupo por debajo de las matrículas activas | [E-20] (RF-9.9) |
| CL-33 | Archivar un grupo con matrículas activas | [E-21] (RF-9.11) |
| CL-34 | Desactivar a un profesor con grupos / a la última cuenta de Dirección | [E-30] / [E-29] (RF-2.10, RF-2.11) |
| CL-35 | Un profesor intenta abrir la ficha de un alumno de otro grupo | [E-1] sin mostrar datos (RF-3.2, RF-3.4) |
| CL-36 | Un profesor abre su grupo con alumnos que tienen observaciones de salud | Aparecen señalados; el contenido solo se ve al pedirlo y queda en la auditoría (RF-14.4, RF-14.5, RF-17.1) |
| CL-37 | Alumno con 2 años de baja y deuda pendiente | No se anonimiza y cuenta en [M-30]; al saldar la deuda se anonimiza en la siguiente revisión (RF-16.2, RF-16.6, RF-18.4) |
| CL-38 | Alumno dado de baja hace exactamente 2 años | Se anonimiza en la revisión de hoy; una baja del 29/02 cumple el plazo el 01/03 (RF-1.12, RF-16.2) |
| CL-39 | Suprimir los datos de un alumno activo / de uno de baja con deuda | [E-28] / [E-27] (RF-15.5, RF-15.6) |
| CL-40 | Falla la escritura de la auditoría durante un pago | No se guarda el pago; [E-36] (RF-17.5, RNF-9) |
| CL-41 | Dos personas editan la misma ficha a la vez | La segunda en guardar recibe [E-35] (RF-1.15) |
| CL-42 | Quinto intento fallido de acceso | Bloqueo de 15 minutos, aunque luego la contraseña sea correcta (RF-2.4) |
| CL-43 | Alumno adulto cuyas cuotas paga su padre | El padre es su contacto y su responsable de pago (RF-4.6) |
| CL-44 | La directora también da clase | Puede ser profesora de un grupo con su cuenta de Dirección (RF-9.2) |
| CL-45 | Alta de «Ana Ruiz-López» existiendo «Ana Ruiz López» con la misma fecha de nacimiento | Se permite: el guion cuenta (RF-1.6) |
| CL-46 | Cuenta nueva con «Ana@Escuela.co» existiendo «ana@escuela.co» | [E-33] (RF-1.16, RF-2.8) |
| CL-47 | Pago registrado hoy con fecha de hace 20 días, anterior a la emisión de un cargo | Se aplica igualmente a ese cargo; la fecha es solo informativa (RF-12.2, RF-12.7) |
| CL-48 | Matrícula finalizada el día 5 y nueva matrícula en el mismo grupo el día 10 | No se genera una segunda cuota de ese grupo y mes (RF-11.1, RF-11.3) |
| CL-49 | Una madre que baila y es tutora de su hijo | Tiene un registro de alumno y otro de contacto, sin relación entre ellos (sección 10) |
| CL-50 | Una transferencia paga las cuotas de dos hermanos | Se registran dos pagos, uno por alumno, con la misma referencia (RF-12.1) |
| CL-51 | Dos personas generan las cuotas del mes a la vez | Cada cuota se crea una sola vez; cada persona ve en [M-9] las que creó su operación, o [M-10] si no quedaba ninguna (RF-11.1, RF-11.2, RF-11.4) |
| CL-52 | Reactivar a un alumno que se dio de baja siendo menor y ya es adulto | La autorización nueva la otorga el propio alumno y debe tener teléfono propio; sus tutores quedan como contactos de emergencia (RF-5.4, RF-6.3, RF-8.8) |
| CL-53 | Recepción edita las observaciones de salud de un alumno que ya tenía | No ve el texto anterior; el nuevo lo sustituye entero (RF-7.11) |
| CL-54 | Grupo con dos franjas el lunes, de 17:00 a 18:00 y de 17:30 a 18:30 | [E-46] (RF-9.15) |
| CL-55 | Autorización de un alumno de 13 años sin confirmar su opinión / de uno de 8 años | [E-47] / se acepta (RF-6.11) |
| CL-56 | Código de activación usado después de 72 horas | [E-44] (RF-2.18) |
| CL-57 | El día 3, una matrícula creada por error se finaliza el mismo día (su cuota se anula) y el alumno se vuelve a matricular en ese grupo | Se genera una cuota nueva del mes: la anulada no cuenta (RF-10.10, RF-11.1, RF-11.3) |

## 10. Fuera de alcance

- Asistencia a clase (D-6).
- Portal o acceso para alumnos y familias (D-7).
- Pagos en línea, pasarelas de pago y datos de tarjetas (D-10).
- Facturación electrónica, recibos con validez fiscal y contabilidad.
- Envío de avisos o recordatorios por correo, SMS o mensajería (D-11).
- Descuentos, becas y prorrateos (D-17, D-19).
- Saldos a favor y devoluciones (D-18).
- Documento de identidad, dirección postal, fotografías y documentos escaneados (D-14, D-20).
- Temporadas, salas y control de solapes de horario (D-13).
- Nómina y horas de los profesores.
- Importación de datos desde hojas de cálculo u otros sistemas.
- Varias sedes y otros idiomas distintos del español.
- Unificar en un solo registro a una persona que es a la vez alumno y contacto (H-20).
- Calcular los plazos legales de las solicitudes en días hábiles (H-31).

## 11. Criterios de finalización

El MVP está terminado cuando:

1. cada RF y cada CL tiene al menos un test automático que lo cita y la suite
   completa pasa (principios 2 y 4);
2. cada fila de la matriz de permisos tiene un test que comprueba que los roles
   con «No» reciben [E-1] sin ver datos (principio 7);
3. todos los textos que ve el personal coinciden con la sección 6;
4. cada RNF se ha verificado con el método de la sección 8 (prueba o revisión
   registrada) y el resultado está registrado, salvo RNF-10, que se mide
   durante el primer mes en producción;
5. la comprobación principio por principio del plan no tiene incumplimientos;
6. la revisión de QA de esta spec no tiene hallazgos sin resolver.

## 12. Dudas abiertas

Al redactar la spec quedaron cinco dudas marcadas [NECESITA ACLARACIÓN]. Se
resolvieron con la regla «usa tus recomendaciones»; el detalle está en
[`clarifications.md`](clarifications.md).

| Duda | Pregunta | Estado | Dónde |
|------|----------|--------|-------|
| D-16 | ¿Qué pasa cuando un menor cumple 18 años? | Resuelta | RF-5.4, RF-6.7, RF-6.8, RF-18.2, M-17, CL-9 |
| D-17 | ¿Qué cuota se cobra si la matrícula empieza a mitad de mes? | Resuelta | RF-11.3, CL-18, CL-19 |
| D-18 | ¿Qué pasa si un pago supera la deuda? | Resuelta | RF-12.4, E-24, CL-24 |
| D-19 | ¿Hay descuentos? | Resuelta: fuera de alcance | Sección 10 |
| D-20 | ¿Se guarda el documento de identidad? | Resuelta: no | Secciones 7 y 10 |

No quedan dudas abiertas.
