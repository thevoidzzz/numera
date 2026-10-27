# ADR-0002: El servidor ejecuta la sentencia y la devuelve

Estado: Accepted
Fecha: 2026-10-27

## Context

El modelo puede describir un `SELECT` y luego inventar el total en la misma frase. Si la respuesta solo lleva prosa, el analista no puede ver qué se ejecutó. Si el modelo también redacta el resultado, ese resultado puede no ser el de la base.

## Decision

El modelo devuelve una sentencia. El servidor la ejecuta, si el cerrojo la deja pasar, y la respuesta no rechazada lleva esa sentencia y el valor que devolvió la base. La frase del modelo no se publica como resultado. Una respuesta no rechazada sin sentencia o sin valor hace fallar el comando de evaluación.

## Alternatives

**Devolver solo la prosa.** Descartado: sin el SQL ejecutado, Numera es un chat sobre contabilidad.

**Dejar que el modelo ejecute y pegue el número.** Descartado: el proceso dejaría de ser la única vía hacia la base, y el número dejaría de ser comprobable.

## Trade-offs

Se gana que el valor mostrado es el valor leído. Se paga que el analista ve SQL. Es el producto: la frase no sustituye al número.

## Consequences

El esquema de salida del modelo es una sentencia, no un párrafo con un total. El test del contrato exige que el valor de una respuesta no rechazada salga de la ejecución, no de un campo libre del modelo.
