# ADR-0001: La verdad es el número ejecutado

Estado: Accepted
Fecha: 2026-10-27

## Context

Una frase puede sonar bien y citar un total que la base no tiene. Si el acierto se juzga leyendo la prosa, el número deja de ser comprobable y un cambio de redacción mueve la métrica. Había que decidir qué resultado se compara con el oro antes de escribir el contrato.

## Decision

Una pregunta con número de oro es correcta solo cuando el valor que devolvió la sentencia ejecutada es ese decimal. La prosa del modelo no entra en execution accuracy. El informe publica ese accuracy aparte del bloqueo de sentencias prohibidas y aparte de los rechazos indebidos.

## Alternatives

**Puntuar la frase con otro modelo.** Descartado para esta versión: un juez sobre un número que no se ejecutó mide redacción. El oro ya es un decimal, y compararlo no necesita un juez.

**Aceptar “cerca” del oro.** Descartado: un umbral de cercanía, sin una tolerancia de negocio medida, es una barra inventada. `numeric` permite igualdad exacta.

## Trade-offs

Se gana un acierto que cualquiera puede rehacer desde la semilla. Se paga que una explicación correcta, con el SQL equivocado, cuenta como fallo. El analista igual ve el número que salió.

## Consequences

El conjunto de oro guarda el decimal, no una frase esperada. El comando de evaluación ejecuta y compara. Una corrida que no ejecuta no publica accuracy.
