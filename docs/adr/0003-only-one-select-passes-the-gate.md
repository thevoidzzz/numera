# ADR-0003: Solo pasa el cerrojo un SELECT

Estado: Accepted
Fecha: 2026-10-27

## Context

El modelo propone texto que se parece a SQL. Ejecutar ese texto tal cual permite más de una sentencia, un `DROP` disfrazado de comentario o un `SELECT INTO` que escribe. Había que decidir el rechazo antes de abrir una conexión de pregunta.

## Decision

El cerrojo parsea el texto. Pasa una sola sentencia, y solo si es un `SELECT` (un `WITH` cuyo resultado es un `SELECT` también pasa). Todo lo demás se rechaza con `rejected_sql` y no se envía a la base. Eso incluye inserción, actualización, borrado, `MERGE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`, `COPY`, `CALL`, `DO`, `LOCK`, `SELECT INTO`, `SET ROLE` y cualquier script con más de una sentencia. Si el parser no acepta el texto, se rechaza igual.

El conjunto prohibido está versionado. El comando de evaluación exige que el bloqueo de ese conjunto sea total.

## Alternatives

**Una lista de palabras prohibidas.** Descartado: un comentario, un salto de línea o un literal parten la palabra y la lista miente.

**Ejecutar y fiarse del error de la base.** Descartado como único control: el rol de lectura es la segunda barrera, no la excusa para no mirar la sentencia. [ADR-0004](0004-reader-role-cannot-write.md).

## Trade-offs

Se gana un rechazo determinista, sin red. Se paga que un `SELECT` destructivo en espíritu pero válido en forma —un cruce cartesiano enorme— no lo para este cerrojo. Eso lo limitan el tope de filas leídas y `statement_timeout`.

## Consequences

Ningún camino de pregunta ejecuta texto sin parsear. El test del conjunto prohibido cubre las formas de este ADR, no una muestra. Añadir una forma nueva al producto obliga a añadirla al conjunto.
