# ADR-0005: Un acierto es un solo decimal

Estado: Accepted
Fecha: 2026-10-27

## Context

Un `SELECT` puede devolver un listado, dos columnas o un texto. Si el servidor elige “la primera celda” y la compara con el oro, un listado largo puede acertar por casualidad y el analista no ve el resto. Había que fijar la forma que cuenta como número.

## Decision

Cuenta como número una fila, una columna y una celda numérica. Cero filas, más de una fila, más de una columna o un valor no numérico es `not_a_number`: no se publica un recorte. Una celda nula es un valor ejecutado nulo, y no iguala al oro. El oro del conjunto se guarda como cadena decimal. La comparación usa igualdad decimal, de modo que la escala (`10.50` y `10.5`) no cambia el acierto.

El servidor lee como máximo dos filas.

## Alternatives

**Comparar el JSON de todas las filas.** Descartado para esta versión: el producto promete un número, y un oro tabular es otra métrica.

**Quedarse con la primera fila.** Descartado: premia una sentencia que no respondió la pregunta.

## Trade-offs

Se gana un accuracy sin ambigüedad. Se paga que una pregunta cuya respuesta honesta es una tabla queda fuera de esta versión. El conjunto no incluye esa pregunta.

## Consequences

El contrato HTTP distingue `not_a_number` de un valor nulo. El test de forma cubre cero filas, dos filas y dos columnas. Cambiar a resultados tabulares pide otro ADR y otro oro.
