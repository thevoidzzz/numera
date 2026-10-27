# ADR-0006: El modelo es un puerto

Estado: Accepted
Fecha: 2026-10-27

## Context

Puntuar SQL exige un modelo, y un modelo de pago exige una clave y una factura. Si el CI llama a ese modelo, el build depende de las dos. Había que poder correr el cerrojo, la ejecución y el informe sin red de proveedor.

## Decision

El modelo es un puerto: entra la pregunta y sale una sentencia, más el nombre del modelo y los tokens. CI enchufa un doble determinista, sin clave. El informe nombra el modelo que produjo las sentencias. Una corrida con modelo de pago se hace a mano y se pega en el README con la fecha. No sustituye al doble en el CI.

El comando no imprime un importe. Esta versión no tiene una tarifa.

## Alternatives

**Llamar al proveedor en cada pull request.** Descartado: el check fallaría por una clave ausente o por una factura, no por un SQL roto.

**No tener puerto y dejar el SQL escrito en el test.** Descartado como única vía: esconde el contrato que el modelo de pago tendrá que cumplir. El doble implementa ese contrato.

## Trade-offs

Se gana un CI repetible. Se paga que el accuracy publicado con el doble no es el de un modelo hospedado. El README tiene que decir el nombre del modelo junto al número.

## Consequences

El paquete de preguntas no importa un SDK. El log y el informe llevan el nombre del modelo. Ningún archivo versionado contiene una clave.
