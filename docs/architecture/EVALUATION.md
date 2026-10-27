# EVALUATION — Qué se mide

Estado: Aprobada
Fecha: 2026-10-27

Un número entra al README solo si el comando de evaluación lo imprimió sobre el conjunto fijo.

## Conjuntos

Dos archivos versionados, escritos a mano.

El de preguntas tiene del orden de 50 ítems. Cada uno trae id, pregunta y el número de oro como cadena decimal. No se usa como ejemplos dentro del prompt. Si se filtra al modelo, el número deja de medir generalización.

Incluye, a propósito:

- un total de una cuenta en un periodo
- un total que cruza dos entidades
- un saldo que queda en cero
- un importe negativo
- una pregunta cuya respuesta no está en el esquema

El de sentencias prohibidas es SQL ya escrito, no preguntas. Cubre inserción, actualización, borrado, `MERGE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`, `COPY`, `CALL`, `DO`, `LOCK`, `SELECT INTO`, `SET ROLE` y un script de más de una sentencia. Si el parser no entiende el texto, también se rechaza: no se ejecuta “a ver qué pasa”.

## Métricas de esta versión

| Métrica | Definición | Barra |
| --- | --- | --- |
| Execution accuracy | fracción de preguntas con número de oro cuyo valor ejecutado es ese decimal | se publica el valor; no hay una barra inventada antes de la primera corrida |
| Bloqueo | sentencias prohibidas rechazadas, sobre el conjunto prohibido | 100%. Si falta una, el comando termina con error |
| SQL y valor visibles | entre las respuestas no rechazadas, cuántas traen la sentencia ejecutada y el valor | 100%. Es un chequeo del servidor, no una opinión |
| Rechazo indebido | preguntas con oro que se rechazaron | se publica aparte. Un sistema que rechaza todo no pasa |

Execution accuracy no incluye el conjunto prohibido. Mezclarlos esconde si el fallo fue dejar pasar un `DROP` o devolver el número equivocado.

Una pregunta con oro que devuelve otro número cuenta como fallo de accuracy, no como rechazo. El analista igual recibe el SQL y el valor.

## Qué no se imprime todavía

Si la prosa del modelo explica bien un número equivocado. Hasta tener accuracy, esa prosa no se puntúa.

Latencia p95 y el total de tokens salen del log de la corrida de evaluación, no de una sola llamada manual. Esta versión no imprime un importe.

## Comando

El informe nombra el modelo de lenguaje. Separa execution accuracy, el bloqueo del conjunto prohibido y los rechazos indebidos. Si el bloqueo no es 1, o si una respuesta no rechazada no trae SQL y valor, el comando termina con error. Imprime latencia p95 y tokens. No imprime un importe.

CI de esta versión corre los tests con un doble. La corrida con modelo de pago no es obligatoria en CI: si lo fuera, el build dependería de una clave y de una factura. El informe con modelo real se genera a mano y se pega en el README con la fecha. [ADR-0006](../adr/0006-model-is-a-port.md).
