# ADR-0007: Esta versión no tiene identidad

Estado: Accepted
Fecha: 2026-10-27

## Context

El warehouse es sintético y la operación peligrosa —escribir— ya está cerrada por el cerrojo y por el rol. Añadir sesiones, contraseñas o un proveedor de identidad ahora mezcla el permiso de leer con la corrección del SQL.

## Decision

La API no autentica. Quien puede llamar al endpoint puede hacer una pregunta y leer el warehouse de la semilla. No se presenta como autorización de una empresa.

## Alternatives

**Un token de demostración en el encabezado.** Descartado: parecería acceso de producción y no restringe nada que el repositorio no publique ya.

**Filas visibles según un rol de analista.** Descartado para esta versión: no hay dos audiencias en la semilla. Inventarlas retrasaría el número de oro.

## Trade-offs

Se gana un contrato corto, donde el fallo visible es el SQL. Se paga que el endpoint, si se expone, es de lectura abierta sobre datos sintéticos.

## Consequences

Antes de cargar datos que no sean la semilla, y antes de AWS, otro ADR tiene que sacar el acceso de una identidad. Hasta entonces, el README no habla de usuarios ni de permisos de empresa.
