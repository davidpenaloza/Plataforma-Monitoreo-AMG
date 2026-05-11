# Guía para incorporar un nuevo producto

## Objetivo

Definir un proceso repetible para agregar un producto al modelo de monitoreo sin duplicar lógica ni romper contratos de soporte.

## Información mínima requerida

Antes de crear funciones, documentar:

- Nombre corto del producto.
- Ambiente(s) a monitorear.
- Dominios funcionales o técnicos.
- Fuentes LAW y tablas requeridas.
- Jobs, pipelines o procesos críticos.
- Criterios OK/WARN/ALERT por dominio.
- Frecuencia esperada de ejecución o actualización.
- Evidencia mínima para soporte.
- Runbook o enlace del portal de soporte: **Por definir** si no existe.
- Responsable técnico/funcional: **Por definir** si no está en el repositorio.

## Paso 1: definir fuentes

Crear o reutilizar funciones `fn_src_mlp_*`.

Checklist:

- ¿Existe source reutilizable para el workspace/tabla?
- ¿La función filtra por `startTime`/`endTime`?
- ¿Proyecta columnas necesarias?
- ¿Evita exponer detalles sensibles en documentación?
- ¿Tiene ejemplo de prueba?

## Paso 2: definir dominios

Un dominio debe representar algo que soporte pueda interpretar: ingesta, job, pipeline, KPI, front, alarmas, disponibilidad, freshness, etc.

Para cada dominio documentar:

- Propósito.
- Fuentes usadas.
- Métricas calculadas.
- Criterios OK/WARN/ALERT.
- Evidencia para escalar.
- Wrapper Grafana asociado.

## Paso 3: crear helpers

Crear helpers solo si la lógica se reutiliza o mejora la legibilidad:

- Helpers cross-producto para color, agregación o normalización genérica.
- Helpers específicos para reglas del producto.
- Catálogos o umbrales en datatables versionadas cuando corresponda.

## Paso 4: crear funciones de dominio

Patrón recomendado:

```kusto
let fn_prd_mlp_<producto>_dom_<dominio>_status = (startTime:datetime, endTime:datetime) {
  ...
};
```

La salida debe ser estable para Grafana. Si el panel necesita detalle, preferir una función de detalle explícita en vez de sobrecargar el dominio global.

## Paso 5: crear wrappers

Crear archivos en:

```text
refactor_ada_optimized/grafana_wrappers/<ambiente>/<faena>/<producto>/
```

Ejemplo:

```text
var_mlp_<producto>_<dominio>.kql
```

## Paso 6: documentar criterios OK/WARN/ALERT

Para cada dominio registrar:

| Campo | Valor |
|---|---|
| Dominio | Por definir |
| OK | Por definir |
| WARN | Por definir |
| ALERT | Por definir |
| Ventana temporal | Por definir |
| Evidencia requerida | Por definir |
| Runbook portal soporte | Por definir |

## Paso 7: validar

- Ejecutar validador KQL local.
- Probar sources con `take 10`.
- Probar helpers con datos recientes y ventanas ampliadas.
- Probar dominios en LAW.
- Probar wrappers desde Grafana.
- Confirmar visualización y colores.
- Actualizar catálogo y documentación.

## Checklist de incorporación

- [ ] Producto y ambiente definidos.
- [ ] Fuentes identificadas y validadas.
- [ ] Dominios definidos con criterios operativos.
- [ ] Sources creadas o reutilizadas.
- [ ] Helpers creados o reutilizados.
- [ ] Funciones de dominio creadas.
- [ ] Wrappers Grafana creados.
- [ ] Paneles actualizados.
- [ ] Runbook enlazado desde portal de soporte.
- [ ] Evidencia de pruebas adjunta.
- [ ] Catálogo actualizado.
- [ ] Sin secretos ni IDs sensibles en documentación.
