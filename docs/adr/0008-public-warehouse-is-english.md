# ADR-0008: El warehouse público está en inglés

Estado: Accepted
Fecha: 2026-10-27

## Context

Lo que un extraño lee tiene que poder evaluarlo sin depender de un idioma de trabajo. Mezclar idiomas en la primera corrida mediría a la vez el SQL y la comprensión del texto.

## Decision

Lo que un extraño lee está en inglés: nombres de tablas y columnas, la semilla, las preguntas, el README, los mensajes de la API, los tests y los commits. Lo que fija el diseño está en español: la arquitectura y estos ADR.

El conjunto de evaluación no mezcla idiomas.

## Alternatives

**Semilla y preguntas en español.** Descartado para esta versión: el primer execution accuracy mediría el modelo y el idioma a la vez.

**Traducir también la arquitectura.** Descartado: el diseño se discute en español, y volver a redactarlo no cambia el comportamiento.

## Trade-offs

Se gana una línea de base explicable. Se paga que un analista de un mayor en español no es el usuario de esta versión.

## Consequences

Los identificadores SQL públicos quedan en inglés. Una pregunta en español, si entra, se compara en el mismo conjunto y con el mismo oro, en una corrida posterior. Hasta esa corrida, las preguntas publicadas son inglés.
