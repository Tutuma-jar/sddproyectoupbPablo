# Aclaraciones — spec 001

Preguntas de la fase 2 para eliminar ambigüedades antes de redactar la
[spec](spec.md), y dudas abiertas que surgieron al redactarla.

Rige la regla «usa tus recomendaciones» (activada por el usuario en la fase 1,
desde D-5): Claude elige la opción recomendada y registra el motivo. La
numeración D-x continúa la de la [constitución](../../docs/constitution-proposal.md)
(D-1…D-5).

## Preguntas de aclaración (D-6…D-15)

### D-6. ¿Qué entra en el MVP?

- (a) **(Recomendada)** Alumnos y sus contactos, grupos, matrículas, cuotas, pagos y morosidad. La asistencia queda fuera.
- (b) Lo de (a) más la asistencia.
- (c) Solo las fichas de alumnos y contactos, sin dinero.
- **Decisión:** (a).
- **Motivo:** saber quién está matriculado y quién debe es el problema administrativo diario; la asistencia es útil, pero no la necesita la recepción para cobrar y puede ser la spec 002.

### D-7. ¿Qué roles hay y qué puede hacer cada uno?

- (a) **(Recomendada)** Tres roles: **Dirección** (todo, incluidas cuentas, grupos, anulaciones, derechos de los titulares y auditoría); **Recepción** (alumnos, contactos, matrículas, cuotas, cargos y pagos; sin anular ni suprimir); **Profesor** (solo sus grupos: alumnos, edad, contactos y observaciones de salud; nada de dinero).
- (b) Solo Dirección y Recepción; los profesores no entran en la app.
- (c) Lo de (a) más un portal para familias y alumnos.
- **Decisión:** (a).
- **Motivo:** el profesor necesita los contactos y las observaciones de salud para dar clase con seguridad, pero no los datos económicos; anular y suprimir son acciones delicadas que conviene reservar a Dirección. El portal de familias multiplica la superficie de datos personales expuesta.

### D-8. ¿Cuál es el ciclo de vida de un alumno?

- (a) **(Recomendada)** Dos estados, **activo** y **de baja**. La baja cierra sus matrículas y conserva el histórico; un alumno de baja se puede **reactivar** mientras sus datos no se hayan anonimizado.
- (b) La baja borra los datos al momento.
- (c) Más estados: preinscrito, activo, suspendido temporalmente, de baja.
- **Decisión:** (a).
- **Motivo:** es habitual que un alumno vuelva la temporada siguiente; dos estados bastan y son fáciles de probar. El borrado se gestiona por plazo de conservación (D-12).

### D-9. ¿Cómo se representan los menores y sus tutores?

- (a) **(Recomendada)** Los contactos son personas propias que se pueden vincular a varios alumnos (hermanos). Un menor tiene 1 o 2 contactos, que son sus tutores (representantes legales); un adulto tiene 0, 1 o 2 contactos de emergencia. Cada alumno tiene un responsable de pago: uno de sus tutores si es menor; él mismo o uno de sus contactos si es adulto.
- (b) Los datos del tutor son campos de texto dentro de la ficha del alumno.
- **Decisión:** (a).
- **Motivo:** evita duplicar los datos de unos padres con varios hijos (mínimo dato) y permite que, al cumplir 18 años, los tutores pasen a ser contactos de emergencia sin copiar nada.

### D-10. ¿Cómo funcionan las cuotas y los pagos?

- (a) **(Recomendada)** Cada grupo tiene una cuota mensual en pesos. El sistema genera un cargo mensual por cada matrícula; además se pueden crear cargos manuales (inscripción, vestuario…). Recepción registra los pagos recibidos (efectivo, transferencia, tarjeta u otro); se admiten pagos parciales, que se aplican al cargo más antiguo. No hay pagos en línea.
- (b) Solo se anotan los pagos, sin generar cargos ni calcular deuda.
- (c) Lo de (a) con pasarela de pago en línea.
- **Decisión:** (a).
- **Motivo:** sin cargos no se puede calcular la morosidad; una pasarela de pago añade proveedor, contratos y datos de tarjetas, contra los principios 1 y 7.

### D-11. ¿Cuándo es moroso un alumno y qué ocurre?

- (a) **(Recomendada)** Cada cargo vence 10 días después de su fecha de emisión. Es moroso quien tiene algún cargo vencido con saldo pendiente. Hay un listado de morosos y un aviso al matricularlos, pero nada se bloquea y el sistema no envía avisos.
- (b) Lo de (a), pero la morosidad impide nuevas matrículas.
- (c) Lo de (a) más avisos automáticos por correo o mensaje.
- **Decisión:** (a).
- **Motivo:** la decisión de cortar el acceso a clase es de la escuela, no del sistema; los avisos automáticos exigen un proveedor de mensajería y más datos de contacto.

### D-12. ¿Cuánto se conservan los datos y cómo se borran?

- (a) **(Recomendada)** Las observaciones de salud se borran en el momento de la baja. Dos años después de la baja, y si no hay deuda pendiente, los datos personales del alumno se anonimizan y sus contactos sin otros alumnos se borran. Los registros económicos se conservan anonimizados 10 años desde la baja y luego se eliminan. La auditoría se conserva 5 años. Dirección puede adelantar la supresión a petición del titular.
- (b) Se conserva todo indefinidamente.
- (c) Todo se borra al dar de baja.
- **Decisión:** (a).
- **Motivo:** la Ley 1581 (D-1) exige no conservar los datos más de lo necesario y atender la supresión; dos años cubren el regreso habitual de un alumno; los 10 años de los registros económicos siguen el plazo de conservación de papeles del comerciante (Código de Comercio, art. 60), sin datos personales. No es asesoría legal: conviene validarlo con quien lleve la protección de datos de la escuela.

### D-13. ¿Cómo son los grupos y las matrículas?

- (a) **(Recomendada)** Un grupo tiene nombre, estilo, profesor, horario semanal (1 a 7 franjas), cupo y cuota mensual. Un alumno puede estar en varios grupos. Con el cupo lleno no se puede matricular. Los grupos no se borran: se archivan. Sin temporadas ni salas.
- (b) Lo de (a) más temporadas con fecha de inicio y fin.
- **Decisión:** (a).
- **Motivo:** cubre la operación diaria con el mínimo de conceptos; las temporadas y las salas pueden añadirse en otra spec.

### D-14. ¿Cómo se registra la autorización de tratamiento de datos?

- (a) **(Recomendada)** La escuela recoge la autorización firmada en papel y la guarda fuera del sistema; en la ficha se registran la fecha, quién la otorgó y si incluye los datos de salud. Sin autorización no se puede dar de alta a un alumno, y sin autorización de salud no se pueden guardar observaciones de salud.
- (b) Se sube el documento escaneado a la ficha.
- (c) Firma electrónica dentro del sistema.
- **Decisión:** (a).
- **Motivo:** deja constancia de la autorización previa e informada que exige la Ley 1581 sin almacenar documentos con firmas (mínimo dato, principio 1).

### D-15. ¿Cuántos datos y usuarios debe soportar y desde dónde se usa?

- (a) **(Recomendada)** Hasta 1.000 alumnos (contando los de baja), 50 grupos, 20 cuentas y 10 personas a la vez; Dirección y Recepción desde un ordenador, y los profesores también desde el teléfono móvil.
- (b) Un único ordenador en recepción.
- **Decisión:** (a).
- **Motivo:** cubre con margen una escuela mediana y permite al profesor consultar contactos y observaciones de salud en el aula.

## Dudas abiertas de la spec (D-16…D-20)

Se marcaron [NECESITA ACLARACIÓN] al redactar la spec y se resolvieron con la
misma regla. La spec recoge el resultado en la sección 12.

### D-16. ¿Qué ocurre cuando un alumno menor cumple 18 años?

- (a) **(Recomendada)** Nada se bloquea. Sus tutores pasan a ser contactos de emergencia y la ficha muestra que la autorización está pendiente de renovar hasta que se registre una nueva otorgada por el propio alumno, junto con su teléfono.
- (b) La ficha queda bloqueada hasta renovar la autorización.
- (c) No se hace nada.
- **Decisión:** (a). **Dónde:** RF-5.4, RF-6.7, RF-6.8, RF-18.2, M-17, CL-9.
- **Motivo:** al ser mayor de edad pasa a ser el titular de sus datos, pero bloquear su ficha impediría cobrar y matricular.

### D-17. ¿Qué cuota se cobra si la matrícula empieza a mitad de mes?

- (a) **(Recomendada)** Si la matrícula empieza entre el día 1 y el 15, se cobra el mes completo; si empieza el 16 o después, ese mes no se cobra. Al finalizar una matrícula no se devuelve nada.
- (b) Prorrateo por días.
- (c) Siempre el mes completo.
- **Decisión:** (a). **Dónde:** RF-11.3, CL-18, CL-19.
- **Motivo:** regla fácil de explicar a las familias y de probar, sin cálculos de prorrateo.

### D-18. ¿Qué pasa si un pago supera la deuda?

- (a) **(Recomendada)** Se rechaza: no existen saldos a favor.
- (b) Se guarda el exceso como saldo a favor para cargos futuros.
- **Decisión:** (a). **Dónde:** RF-12.4, E-24, CL-24.
- **Motivo:** los saldos a favor añaden reglas de imputación futura y devoluciones; si una familia paga por adelantado, se crea antes el cargo correspondiente.

### D-19. ¿Hay descuentos (hermanos, becas)?

- (a) **(Recomendada)** No en el MVP.
- (b) Descuento porcentual por alumno.
- **Decisión:** (a). **Dónde:** sección 10 (fuera de alcance).
- **Motivo:** cada escuela tiene reglas distintas; mientras tanto, Dirección puede anular un cargo y crear uno manual con el importe acordado.

### D-20. ¿Se guarda el documento de identidad?

- (a) **(Recomendada)** No: nombre, apellidos y fecha de nacimiento bastan para identificar y detectar duplicados.
- (b) Sí, tipo y número de documento del alumno y del responsable de pago.
- **Decisión:** (a). **Dónde:** sección 7 (no figura en los datos) y sección 10.
- **Motivo:** ningún requisito del MVP lo necesita (principio 7); la facturación electrónica, que sí lo pediría, queda fuera de alcance.
