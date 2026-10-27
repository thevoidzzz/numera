# DATA — Esquema, semilla y número

Estado: Aprobada
Fecha: 2026-10-27

## Warehouse

Una sola base. El esquema `warehouse` tiene cuatro tablas, sintéticas, de un cierre contable pequeño:

| Tabla | Qué guarda |
| --- | --- |
| `legal_entity` | `code`, `name` |
| `account` | `code`, `name`, `category` (`asset`, `liability`, `equity`, `income`, `expense`) |
| `fiscal_period` | `code`, `starts_on`, `ends_on` |
| `journal_line` | `line_id`, `entity_code`, `account_code`, `period_code`, `amount`, `memo` |

`amount` es `numeric(18,2)`. No hay columnas de punto flotante. Las claves de negocio son los códigos, estables, para que una pregunta de evaluación no dependa de un serial. La semilla vive en el repositorio, en inglés, y los números de oro se calculan desde esa semilla. Cambiar una cifra de la semilla sin cambiar el conjunto es un error de evaluación.

Dos roles. El dueño crea el esquema y carga la semilla. El rol de lectura solo tiene `SELECT` sobre esas tablas. La pregunta usa el rol de lectura. [ADR-0004](../adr/0004-reader-role-cannot-write.md).

## Forma de un resultado puntuable

Una pregunta con número de oro es correcta solo si la sentencia devuelve una fila y una columna, y esa celda es un número igual al oro. La comparación es decimal: `10.50` y `10.5` son el mismo valor. Cero filas, dos filas, dos columnas o un texto no son un número: la API rechaza con `not_a_number` y no recorta la tabla para forzar un acierto. Una celda nula sí es un resultado ejecutado, con `value` nulo, y no coincide con ningún oro. [ADR-0005](../adr/0005-a-score-is-one-decimal.md).

El servidor pide como máximo dos filas. Con la segunda ya sabe que no es un número, y no vuelca el warehouse.

## Límites de esta versión

| Límite | Valor | Por qué |
| --- | --- | --- |
| Pregunta | 2000 caracteres | El tope es del contrato, no un accidente del framework |
| Sentencia propuesta | 4000 caracteres | Una sentencia más larga se rechaza antes del parser |
| `statement_timeout` del rol de lectura | 2 segundos | Un `SELECT` puede ser caro. El valor no es un óptimo medido |
| Filas leídas | 2 | Alcanza para distinguir un número de un listado |

## Qué no entra en el esquema

Presupuestos, documentos, usuarios, permisos por fila y una tabla de auditoría de escrituras. No hay escrituras en el camino de la pregunta.
