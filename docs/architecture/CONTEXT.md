# CONTEXT — Numera

Estado: Aprobada
Fecha: 2026-10-27

Numera responde preguntas de un analista sobre un warehouse financiero sintético. La verdad es el número que devuelve la sentencia ejecutada. La base que atiende la pregunta no puede escribir.

## Actores

| Actor | Qué hace |
| --- | --- |
| Analista | Hace una pregunta en lenguaje natural y lee el SQL que corrió y el número |
| Autor del warehouse | Publica el esquema y la semilla sintética en el repositorio. No hay un editor dentro del servicio |
| Evaluación | Corre el conjunto fijo y lee los números. No es un usuario de la API |

## Dentro de esta versión

Esquema y semilla sintéticos en inglés, una sentencia propuesta por un modelo, un cerrojo que solo deja pasar un `SELECT`, ejecución con un rol de solo lectura, respuesta con el SQL ejecutado y un número, comando de evaluación, Docker y CI. El diseño se escribe en español. [ADR-0008](../adr/0008-public-warehouse-is-english.md).

## Fuera

Identidad real, interfaz web, carga de archivos, gráficos, escritura de asientos, varias empresas inquilinas y AWS. El detalle está en [ARCHITECTURE.md](ARCHITECTURE.md).

## Sistemas externos

Un modelo de lenguaje, detrás de un puerto, que propone SQL. Las pruebas no lo llaman: usan un doble determinista. La clave, si hace falta en local, viene del entorno.

No hay cola, caché, bus de eventos ni segundo servicio. El warehouse cabe en una base.
