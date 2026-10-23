# Revisión de QA — Spec 001 (MVP de la escuela de danza)

- **Documento revisado:** spec 001, versión 1 (aprobada el 2026-10-23)
- **Referencia:** [constitución](../../docs/constitution.md) y [aclaraciones](clarifications.md)
- **Fecha de la revisión:** 2026-10-23
- **Alcance:** las secciones 1 a 7 solo detectan, sin proponer soluciones. Las
  resoluciones (fase 4) están en la sección 8 y se aplican en la versión 2 de
  la spec.

Los números de requisito (RF-x.y, RNF-x, CL-x, M-x, E-x) se refieren a la
**versión 1** de la spec.

## 1. Ambigüedades

- **H-1 — RF-1.2:** no define qué cuenta como «espacio» (tabulador, salto de línea, espacio de no separación) ni si los textos se llevan a una forma Unicode única antes de compararlos; una «á» compuesta y otra descompuesta podrían no ser iguales en RF-1.6.
- **H-2 — RF-1.6:** no dice cómo se tratan guiones y apóstrofos («Ruiz-López» frente a «Ruiz López», «D'Angelo» frente a «DAngelo») ni otros signos diacríticos distintos de tildes y diéresis («ç»).
- **H-3 — RF-1.9:** la validación del correo admite valores claramente inválidos (espacios, «a@b.» o «a@.b»), y no dice si el correo se compara o guarda sin distinguir mayúsculas, salvo en las cuentas (RF-2.8).
- **H-4 — RF-2.2 / RF-2.7 / RF-2.13:** no dice cómo obtiene su primera contraseña una cuenta recién creada ni cómo define la nueva tras un restablecimiento; la longitud mínima solo aparece en RNF-5.
- **H-5 — RF-2.4:** no dice si un acceso correcto reinicia el contador de intentos fallidos, si el contador se reinicia al acabar el bloqueo ni si cuentan los intentos con un correo que no corresponde a ninguna cuenta.
- **H-6 — RF-2.5:** «actividad» no está definida: no se sabe si tener una pantalla abierta, escribir en un formulario sin guardarlo o una actualización automática cuentan como actividad.
- **H-7 — RF-3.4 / RF-14 frente a CL-44:** RF-3.4 y RF-14.1 hablan de «cuenta con rol Profesor», pero CL-44 permite que una cuenta de Dirección sea profesora de un grupo. No se sabe si esa cuenta ve también la vista del profesor.
- **H-8 — RF-4.4 / RF-7.7:** RF-4.4 rechaza «el alta» de un duplicado, pero no queda claro si también se rechaza editar un alumno de forma que coincida con otro, ni si RF-7.7 lo incluye.
- **H-9 — RF-5.11:** «deje de estar vinculado a algún alumno no anonimizado» se puede leer como «a uno cualquiera» (se borraría el contacto al desvincularlo de un solo hermano) o como «a ninguno». CL-13 sugiere la segunda lectura.
- **H-10 — RF-6.7:** no dice qué dispara el evento «cumplir 18 años» (la revisión diaria, la apertura de la ficha…), ni si se aplica también a los alumnos de baja.
- **H-11 — RF-6.4 / RF-6.5 / RF-6.10:** la revocación de salud se guarda como una fecha en la autorización (sección 7), pero RF-6.5 solo mira si la autorización vigente «incluye» la salud. No queda claro que una autorización revocada deje de permitir observaciones, ni qué hace falta para volver a guardarlas.
- **H-12 — RF-9.2:** no dice si las franjas de un grupo pueden solaparse entre sí o repetir día, ni con qué precisión se dan las horas.
- **H-13 — Terminología de grupos:** la spec usa «no archivado» en los RF, pero «grupo activo» en E-18 y «grupos activos» en E-30, sin definir que sean lo mismo.
- **H-14 — RF-16.1 / RF-16.5:** RF-16.5 está escrito como evento («Cuando pasen 10 años»): si la revisión diaria no se ejecuta ese día, no queda claro que la eliminación ocurra después. RF-16.1 tampoco dice qué pasa con los días en que la revisión no se ejecuta.

## 2. Contradicciones entre requisitos

- **H-15 — RF-11.6 frente a la sección 7:** el concepto de una cuota es «Cuota {mes} - {grupo}». Con el mes más largo («septiembre de 2026») y un nombre de grupo de 60 caracteres salen 87 caracteres, por encima del límite de 80 del concepto.
- **H-16 — RF-10.10 frente a RF-11.11 y la matriz de permisos:** RF-10.10 anula una cuota de forma automática cuando Recepción finaliza una matrícula, pero RF-11.11 reserva la anulación a Dirección, con motivo obligatorio, y la matriz dice que Recepción no anula cargos.
- **H-17 — RF-7.7 frente a RF-6.7 y D-16:** al editar se aplican las validaciones del alta, entre ellas RF-6.3 (la autorización de un adulto la otorga él mismo) y RF-4.8 (un adulto necesita teléfono propio). Un alumno que acaba de cumplir 18 años no cumple ninguna de las dos hasta renovar, así que no se podría editar su ficha, lo que contradice «nada se bloquea» (D-16, CL-9).
- **H-18 — RF-12.5 frente a RF-12.2 y RF-13.5:** se admiten pagos con fecha de hasta 31 días atrás, pero la aplicación y los días de atraso ignoran esa fecha. Un pago fechado antes de que existiera un cargo se aplica a ese cargo, y un pago fechado antes del vencimiento no evita que el alumno haya contado como moroso.

## 3. Casos límite no cubiertos

- **H-19 — Rematrícula en el mismo mes:** si una matrícula se finaliza el día 5 y el alumno se vuelve a matricular en el mismo grupo el día 10, RF-11.1 («una cuota por matrícula y mes») permite cobrar dos cuotas del mismo grupo ese mes. Lo mismo ocurre al dar de baja y reactivar a un alumno dentro del mismo mes.
- **H-20 — Misma persona como alumno y como contacto:** un adulto que baila y además es tutor de su hijo queda registrado dos veces (alumno y contacto) sin relación entre ambos registros; no se sabe qué ocurre con RF-5.6 si el teléfono coincide con el de un alumno.
- **H-21 — Otorgante de una autorización que se borra:** si se desvincula o suprime al tutor que otorgó la autorización vigente de un menor (quedando el otro tutor), RF-5.11 borra sus datos y la autorización queda apuntando a una persona que ya no existe.
- **H-22 — Un pago para varios hermanos:** una familia que paga las cuotas de dos hijos con una sola transferencia no tiene forma de registrarla; no se dice si hay que dividirla ni cómo se relacionan las dos partes.
- **H-23 — Generación simultánea de cuotas:** si dos personas generan las cuotas del mes a la vez, RF-11.1 impide duplicados, pero no se dice qué cifra muestra cada una en [M-9].
- **H-24 — Menor que cumple 18 años estando de baja y luego se reactiva:** no se dice si la reactivación exige que la autorización la otorgue el propio alumno ni si debe aportar teléfono propio, ni qué pasa con sus tutores.
- **H-25 — Datos del personal:** no se define qué pasa con los datos de una cuenta desactivada (nombre y correo) ni cuánto tiempo se conservan, aunque la auditoría la referencie.

## 4. Conflictos con la constitución

- **H-26 — Principio 7 (mínimo acceso) frente a la matriz de permisos:** Recepción puede ver las observaciones de salud de todos los alumnos, aunque para su trabajo (alta, cobro, matrícula) solo necesita escribirlas; la constitución pide que solo las vean los roles que las necesitan.
- **H-27 — Principio 8 (borrado al vencer el plazo) frente a RF-16.4 y la sección 7:** los campos de texto libre que se conservan 10 años tras la anonimización (concepto de un cargo manual, motivo de anulación, referencia de pago) pueden contener nombres o datos de salud («anulado por lesión de rodilla»), así que el registro anonimizado podría no estarlo.
- **H-28 — Principio 8 frente a RNF-8 (principio 5):** las copias de seguridad guardan durante 30 días los datos de alumnos que ya se anonimizaron o suprimieron; restaurar una copia los volvería a identificar.

## 5. Riesgos de privacidad y seguridad

- **H-29 — Exportaciones (RF-15.1, RF-15.2):** el documento exportado contiene todos los datos de un menor, incluida la salud, y sale del control del sistema; la spec no dice cómo se entrega al titular ni qué se hace con el archivo después.
- **H-30 — Revocación general de la autorización:** la Ley 1581 permite revocar la autorización, pero la spec solo contempla revocar la de salud (RF-6.10); no se sabe qué ocurre si un titular revoca la autorización general.
- **H-31 — Plazos legales de respuesta:** la Ley 1581 fija plazos para atender consultas y reclamos, pero la spec no registra cuándo se recibió una solicitud ni cuándo se respondió, así que no se puede demostrar el cumplimiento.
- **H-32 — Bloqueo de cuentas por terceros (RF-2.4):** cualquiera que conozca el correo de una cuenta de Dirección puede bloquearla 15 minutos tantas veces como quiera con intentos fallidos.
- **H-33 — Cuentas con acceso total sin segundo factor:** las cuentas de Dirección ven todos los datos de menores y su salud, y solo las protege una contraseña.
- **H-34 — Datos en el teléfono del profesor (RNF-4, RF-14):** los teléfonos de los tutores y las observaciones de salud se consultan desde teléfonos personales; la spec no dice qué pasa si el teléfono se pierde con la sesión abierta, más allá de la caducidad de 30 minutos.
- **H-35 — Reidentificación de anonimizados (RF-16.3, RF-16.4):** en una escuela pequeña, el grupo, las fechas de matrícula y los importes de un «Alumno anonimizado» pueden bastar para saber de quién se trata.
- **H-36 — Opinión del menor:** la normativa colombiana pide tener en cuenta la opinión del menor cuando su representante autoriza el tratamiento de sus datos (Decreto 1377, conviene confirmarlo con quien lleve la protección de datos); la spec no lo recoge.

## 6. Requisitos que no se pueden probar

- **H-37 — RF-15.1 / RF-15.2:** «documento legible e imprimible» no tiene formato ni contenido mínimo comprobable.
- **H-38 — RF-17.4:** «impedir que se modifique o borre una entrada» es absoluto; no se puede probar frente a quien administra la base de datos, y no dice frente a quién se garantiza.
- **H-39 — RNF-3:** «el 95 % de las operaciones» no define qué operaciones ni en qué proporción forman la carga de la prueba.
- **H-40 — RNF-7:** «ningún dato real sale del entorno de producción» solo se puede comprobar por revisión, no con una prueba automática, y la sección 11 exige verificar cada RNF.
- **H-41 — RNF-10:** la disponibilidad del 99 % solo se puede medir con la app en producción durante un mes, pero la sección 11 la exige para dar el MVP por terminado.
- **H-42 — RF-2.5 / RNF-5:** sin definir «actividad» (H-6), no se puede probar cuándo caduca una sesión.

## 7. Principios sin conflictos

Los principios **1** (stack simple), **2** (spec antes que código), **3**
(dominio sin E/S), **4** (tests obligatorios), **5** (persistencia controlada) y
**6** (idioma) no tienen conflictos con la spec. Los hallazgos de la sección 4
afectan a los principios **7** (H-26) y **8** (H-27, H-28); H-28 nace de las
copias que exige el principio 5, pero el conflicto es con el borrado del
principio 8.

## 8. Resoluciones

Decididas con la regla «usa tus recomendaciones». Los «Dónde» se refieren a la
**versión 2** de la spec. Ninguna resolución contradice la constitución ni las
decisiones D-1…D-20 ya aprobadas.

| Hallazgo | Decisión | Dónde está en la spec |
|----------|----------|------------------------|
| H-1 | Todo texto se lleva a la forma Unicode compuesta y se define «espacio en blanco» como cualquier espacio de Unicode. | RF-1.2 |
| H-2 | Se ignoran todos los diacríticos salvo la «ñ»; guiones y apóstrofos sí distinguen. | RF-1.6, CL-45 |
| H-3 | Regla de correo más estricta (sin espacios, dominio con partes no vacías); los correos se guardan y comparan en minúsculas. | RF-1.9, RF-1.16, CL-46 |
| H-4 | Dirección recibe un código de activación de un solo uso (72 horas) que entrega en persona; con él se define una contraseña de al menos 12 caracteres. Motivo: no exige enviar correos, que están fuera de alcance. | RF-2.13, RF-2.16–RF-2.19, M-22, M-33, M-38, E-44, E-45, CL-56 |
| H-5 | El contador se reinicia tras un acceso correcto y al terminar el bloqueo; los correos inexistentes no bloquean nada. | RF-2.20 |
| H-6 | Se define «actividad» como toda operación pedida por la persona; las actualizaciones automáticas no cuentan. | RF-2.5 |
| H-7 | Una cuenta de Dirección que da clase ve todo lo de Dirección y, además, la lista de sus grupos en el inicio. | RF-14.6 |
| H-8 | La comprobación de duplicados se aplica también al editar. | RF-4.4 |
| H-9 | Se reescribe: el contacto se borra cuando se queda sin vínculos con alumnos no anonimizados. | RF-5.11 |
| H-10 | La renovación pendiente pasa a ser un estado calculado con la fecha de hoy (sin evento) y solo afecta a alumnos activos; los de baja se tratan al reactivar (H-24). | RF-6.7 |
| H-11 | La revocación marca como revocada la inclusión de salud en la autorización vigente; volver a guardar observaciones exige una autorización nueva con salud. | RF-6.5, RF-6.10 |
| H-12 | Dos franjas del mismo día de un grupo no pueden solaparse; las horas son libres (hh:mm). | RF-9.15, E-46, CL-54 |
| H-13 | Los mensajes usan «sin archivar», igual que los RF. | E-18, E-30 |
| H-14 | RF-16.5 pasa a ser un estado («Mientras…») y la revisión diaria trata lo pendiente de los días en que no se ejecutó. | RF-16.1, RF-16.5 |
| H-15 | El límite del concepto sube a 100 caracteres (el máximo de una cuota es 87). | Sección 7 |
| H-16 | La anulación automática la hace el «sistema» con un motivo fijo, sin exigir el permiso de anular cargos. | RF-10.10, sección 5 |
| H-17 | Al editar solo se validan los datos modificados; las reglas de la autorización se aplican al registrar una nueva, y con la autorización pendiente de renovar no se exige teléfono propio. | RF-7.7, RF-7.10 |
| H-18 | La fecha del pago es solo informativa: la aplicación y la morosidad dependen de cuándo se registra. Motivo: mantener una sola regla de aplicación, fácil de probar. | RF-12.7, CL-47 |
| H-19 | Como máximo una cuota por alumno, grupo y mes, aunque haya varias matrículas. | RF-11.1–RF-11.3, CL-48 |
| H-20 | Se acepta la limitación: alumno y contacto son registros distintos aunque sean la misma persona; unificarlos queda fuera de alcance. | Sección 10, CL-49 |
| H-21 | La autorización guarda una copia del nombre y la relación de quien la otorga, que no depende de que el contacto siga existiendo. | RF-6.1, sección 7 |
| H-22 | Un pago es de un solo alumno; el pago conjunto se registra como un pago por alumno con la misma referencia. | RF-12.1, CL-50 |
| H-23 | Cada operación informa solo de las cuotas que creó ella; si no quedaba ninguna, muestra [M-10]. | RF-11.2, CL-51 |
| H-24 | Al reactivar se aplican las reglas actuales: si ya es adulto, autoriza él mismo y debe tener teléfono propio; sus tutores quedan como contactos de emergencia. | CL-52 (RF-5.4, RF-6.3, RF-8.8) |
| H-25 | Las cuentas desactivadas se anonimizan a los 5 años de su desactivación, igual que el plazo de la auditoría que las referencia. | RF-16.8, sección 7 |
| H-26 | Recepción puede escribir o sustituir las observaciones de salud, pero no verlas; las ven Dirección y el profesor de sus grupos. | RF-7.4, RF-7.5, RF-7.11, sección 5, CL-53 |
| H-27 | Al anonimizar se sustituye el concepto de los cargos manuales y se borran referencias y motivos; los campos de texto libre muestran un aviso para no escribir datos personales. | RF-1.17, RF-16.9, M-35 |
| H-28 | Tras restaurar una copia se ejecuta la revisión de plazos antes de abrir la app y Dirección repite las supresiones posteriores a la copia. Riesgo residual aceptado: depende de las respuestas guardadas fuera del sistema. | RNF-8 |
| H-29 | El aviso de la exportación pide entregarla solo al titular y no guardar copias; queda en la auditoría (RF-17.1). | M-21 |
| H-30 | La revocación general se atiende con la baja y la supresión; con deuda, los datos se conservan hasta saldarla. | Nota al final de RF-15 |
| H-31 | Registro de solicitudes de titulares (tipo, fechas de recepción y respuesta) con aviso en el inicio de Dirección; el cálculo en días hábiles queda fuera de alcance. | RF-15.10, RF-15.11, RF-18.5, M-36, E-48, sección 7, sección 10 |
| H-32 | Riesgo aceptado: el bloqueo de 15 minutos limita la fuerza bruta. Para acotar el abuso, Dirección puede desbloquear una cuenta al momento. | RF-2.21, M-37 |
| H-33 | Las cuentas de Dirección exigen un segundo factor de autenticación. | RF-2.22–RF-2.24, sección 7 |
| H-34 | No se guardan datos personales en el dispositivo y Dirección puede cerrar todas las sesiones de una cuenta (por ejemplo, si se pierde un teléfono). | RNF-13, RF-2.25, M-39 |
| H-35 | Los alumnos anonimizados quedan fuera de toda búsqueda, lista y ficha; solo cuentan en los totales. | RF-16.10 |
| H-36 | En menores de 12 años o más, la autorización exige confirmar que se tuvo en cuenta su opinión. Motivo: a partir de los 12 años la normativa colombiana considera adolescente al menor; conviene validarlo con quien lleve la protección de datos. | RF-6.1, RF-6.11, E-47, sección 7, CL-55 |
| H-37 | Se fija el contenido de la exportación: secciones fijas y todos los datos guardados con su etiqueta. | RF-15.1, RF-15.2 |
| H-38 | La garantía se acota a las cuentas de la app, de cualquier rol. | RF-17.4 |
| H-39 | Se define la mezcla de operaciones de la prueba de carga. | RNF-3 |
| H-40 | La sección 11 admite la verificación por revisión registrada donde la sección 8 la indica. | Sección 11 |
| H-41 | RNF-10 se mide durante el primer mes en producción y no bloquea el fin del MVP. | Sección 11 |
| H-42 | Resuelto con H-6. | RF-2.5 |
