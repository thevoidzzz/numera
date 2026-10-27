# ADR-0004: El rol que ejecuta no puede escribir

Estado: Accepted
Fecha: 2026-10-27

## Context

Un cerrojo en el proceso puede tener un hueco. Si la misma conexión que crea tablas atiende la pregunta, un hueco del cerrojo escribe. Había que separar, en la base, quién migra y quién lee.

## Decision

El dueño crea el esquema `warehouse` y carga la semilla. El rol de lectura tiene `SELECT` sobre esas tablas y nada más. `statement_timeout` de ese rol queda en 2 segundos. La pregunta usa solo el rol de lectura. El dueño no aparece en el camino de la pregunta.

Un fallo de permisos al ejecutar no se convierte en una escritura reintentada con el dueño. Se rechaza.

## Alternatives

**Un solo superusuario y el cerrojo como única defensa.** Descartado: un error del parser quedaría con permiso de borrar la semilla.

**Revocar escritura después de cada migración, en el mismo rol.** Descartado: una migración olvidada deja el rol a medias. Dos roles hacen el permiso visible.

## Trade-offs

Se gana que un `INSERT` que atravesara el cerrojo sigue sin poder escribir. Se paga mantener dos cadenas de conexión. La de lectura es la única que el proceso de preguntas lee del entorno.

## Consequences

Los tests de integración intentan escribir con el rol de lectura y esperan el fallo. La semilla no se carga por la conexión de preguntas. El contenedor, cuando exista, no publica el puerto de la base en el anfitrión.
