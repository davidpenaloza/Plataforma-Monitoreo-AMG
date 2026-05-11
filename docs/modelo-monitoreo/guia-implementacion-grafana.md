# Guía de implementación en Grafana

## Objetivo

Establecer cómo Grafana debe consumir el modelo de monitoreo sin duplicar reglas de negocio ni lógica KQL pesada en el dashboard.

## Consumo de funciones desde Grafana

Los paneles y variables deben llamar wrappers `var_mlp_*` o directamente funciones de dominio cuando aplique. El patrón recomendado es:

```kusto
fn_prd_mlp_<producto>_dom_<dominio>_status(bin($__timeFrom, 1m), bin($__timeTo, 1m))
```

Reglas:

- Usar macros de tiempo de Grafana para respetar el rango seleccionado.
- Mantener wrappers de una línea o con lógica mínima de presentación.
- Evitar copiar el cálculo completo del dominio dentro del panel.
- Versionar wrappers en `refactor_ada_optimized/grafana_wrappers`.

## Variables y wrappers

Un wrapper debe:

- Tener nombre `var_mlp_<producto>_<dominio>.kql`.
- Apuntar a una función de dominio o helper de diagnóstico estable.
- Usar `bin($__timeFrom, 1m)` y `bin($__timeTo, 1m)`.
- No incluir IDs sensibles ni rutas productivas completas.

Si se necesita una variable para listar dominios, productos o ambientes, la fuente debe ser una función KQL o datatable controlada; no una lista manual divergente del catálogo.

## Estructura recomendada de paneles

1. **Resumen ejecutivo:** estado global por producto con stat panels.
2. **Detalle por dominio:** tabla o grid con estado, color y detalle técnico.
3. **Diagnóstico de jobs/pipelines:** tabla con esperado, real, última ejecución, lag y estado.
4. **Evidencia técnica:** links o paneles con logs filtrados, sin exponer información sensible.
5. **Panel de contexto:** descripción del dominio, criterios OK/WARN/ALERT y enlace a runbook.

## Interpretación de colores y estados

| Estado | Color recomendado | Interpretación operativa |
|---|---|---|
| `OK` | Verde claro `#EAF4EA` | Sin condición de alerta detectada por el dominio. |
| `WARN` / `WARNING` | Amarillo `#FFF4CC` | Condición degradada o preventiva. Puede requerir seguimiento. |
| `ALERT` | Rojo `#E53935` | Condición de alerta que requiere diagnóstico operativo. |
| Sin datos | Gris o texto explícito | No asumir OK. Revisar source, rango temporal y permisos. |

## Recomendaciones por tipo de panel

### Text panels

- Explicar qué mide el dominio.
- Incluir link al runbook del portal y a esta documentación.
- Describir el rango temporal usado y el significado de colores.

### Stat panels

- Usar un único valor por panel: estado o color global.
- Configurar thresholds coherentes con `fn_mon_status_to_color`.
- Mostrar texto `OK/WARN/ALERT`, no solo color.

### Tablas

- Incluir columnas de evidencia: job, fuente, última ejecución, esperado, real, lag, detalle.
- Ordenar alertas al inicio.
- Evitar columnas sensibles o rutas completas.

## Errores comunes en Grafana

| Síntoma | Causa probable | Acción |
|---|---|---|
| Panel vacío | Macro temporal, función sin datos o permisos. | Probar el wrapper en LAW con fechas manuales. |
| Color no coincide con estado | Threshold local distinto al helper KQL. | Alinear thresholds con contrato de colores. |
| Variable falla | Wrapper llama función inexistente. | Revisar catálogo y validador. |
| Consulta lenta | Lógica pesada en panel o rango amplio. | Mover lógica a dominio/helper y filtrar temprano. |
| Diferencias por zona horaria | Interpretación local del dashboard. | Comparar UTC de LAW con configuración de Grafana. |

## Relación con el dashboard exportado

El dashboard `Plataforma_Monitoreo_AMG.json` debe considerarse un artefacto versionado, pero la lógica oficial debe permanecer en KQL. Si se modifica un panel, actualizar también wrappers o documentación cuando cambie el contrato visual.
