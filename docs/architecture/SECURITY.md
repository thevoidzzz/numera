# SECURITY — Qué está cerrado

Estado: Aprobada
Fecha: 2026-10-27

## Cerrado en esta versión

- La pregunta no se ejecuta como SQL. El modelo propone una sentencia y el cerrojo la mira antes de la base. [ADR-0003](../adr/0003-only-one-select-passes-the-gate.md).
- Texto que el parser no acepta no llega a la base.
- Más de una sentencia no llega a la base.
- La ejecución usa el rol de lectura. Aunque el cerrojo fallara, ese rol no puede insertar, actualizar, borrar ni cambiar el esquema. [ADR-0004](../adr/0004-reader-role-cannot-write.md).
- El dueño del esquema no atiende preguntas.
- El log no lleva la clave del modelo ni la contraseña del rol. Un 503 no devuelve la cadena de conexión.
- `statement_timeout` del rol de lectura está fijado. Una consulta no se queda abierta.

## Hueco que se admite

En esta versión quien pueda llamar a la API puede leer el warehouse. No hay sesión ni firma. El warehouse es sintético. Presentar el endpoint como acceso de una empresa sería falso. [ADR-0007](../adr/0007-no-identity-in-this-version.md).

Cerrarlo de verdad es otro cambio: una identidad, antes de cargar datos que no sean de la semilla, y antes de AWS.

## Lo que el modelo puede intentar

Una pregunta puede pedir un `DROP` o un segundo statement. Esta versión no afirma que el modelo se niegue. Afirma que la sentencia, si no es un solo `SELECT`, no se ejecuta, y que el rol no puede escribir. El conjunto prohibido mide el cerrojo con SQL ya escrito. Medir si una pregunta en lenguaje natural empuja al modelo a proponer ese SQL es una corrida posterior, contra esta misma API. Este repositorio no publica una colección de ataques.

## Datos

La semilla no tiene personas, cuentas bancarias reales ni documentos de un empleador. La pregunta sí se registra, porque sin ella no se depura una sentencia. El día que el warehouse tenga datos de personas, ese campo se apaga.
