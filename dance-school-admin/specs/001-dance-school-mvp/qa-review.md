# Revisión de QA — Spec 001 (MVP de la escuela de danza)

- **Documento revisado:** spec 001, versión 1 (aprobada el 2026-10-23)
- **Referencia:** [constitución](../../docs/constitution.md) y [aclaraciones](clarifications.md)
- **Fecha de la revisión:** 2026-10-23
- **Alcance:** solo detección, sin proponer soluciones. Las resoluciones se
  añadirán en la fase 4.

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
