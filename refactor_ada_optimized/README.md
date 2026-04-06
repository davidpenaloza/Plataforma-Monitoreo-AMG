# ADA Refactor Final (Implementación mínima)

Este paquete quedó en formato final **1 archivo `.kql` = 1 función** (LAW) y **1 archivo `.kql` = 1 wrapper** (Grafana).

## Estructura final
- `law_functions/helpers_cross_product/`
- `law_functions/helpers_ada/`
- `law_functions/domains/`
- `grafana_wrappers/`

## LAW — archivos a crear (exactos)

### Cross-product helpers
1. `law_functions/helpers_cross_product/fn_mon_status_to_color.kql`
2. `law_functions/helpers_cross_product/fn_mon_alert_from_job_success_src_v2.kql`
3. `law_functions/helpers_cross_product/fn_mon_alert_from_pipeline_success_src_v2.kql`
4. `law_functions/helpers_cross_product/fn_mon_global_from_color_set.kql`

### ADA-only helper
5. `law_functions/helpers_ada/fn_prd_ada_lag_helpers.kql`

### Domain functions
6. `law_functions/domains/fn_prd_ada_dom_dispatch_status.kql`
7. `law_functions/domains/fn_prd_ada_dom_drillit_status.kql`
8. `law_functions/domains/fn_prd_ada_dom_blockgrade_status.kql`
9. `law_functions/domains/fn_prd_ada_dom_pi_status.kql`
10. `law_functions/domains/fn_prd_ada_dom_plans_status.kql`
11. `law_functions/domains/fn_prd_ada_dom_meteodata_status.kql`
12. `law_functions/domains/fn_prd_ada_dom_alarm_status.kql`
13. `law_functions/domains/fn_prd_ada_dom_front_status.kql`
14. `law_functions/domains/fn_prd_ada_dom_kpi_status.kql`
15. `law_functions/domains/fn_prd_ada_dom_kpi_detalle_html.kql`
16. `law_functions/domains/fn_prd_ada_dom_global_status.kql`

## Grafana — wrappers a usar (exactos)
1. `grafana_wrappers/var_mlp_ada_dispatch.kql`
2. `grafana_wrappers/var_mlp_ada_drillit.kql`
3. `grafana_wrappers/var_mlp_ada_blockgrade.kql`
4. `grafana_wrappers/var_mlp_ada_pi.kql`
5. `grafana_wrappers/var_mlp_ada_plans.kql`
6. `grafana_wrappers/var_mlp_ada_meteodata.kql`
7. `grafana_wrappers/var_mlp_ada_alarm.kql`
8. `grafana_wrappers/var_mlp_ada_front.kql`
9. `grafana_wrappers/var_mlp_ada_kpi.kql`
10. `grafana_wrappers/var_mlp_ada_global.kql`

## Versión lista para copiar en LAW UI (sin `let ... { }`)
- Se agregó la carpeta `law_functions_body_only/` con los mismos archivos y estructura que `law_functions/`.
- Cada archivo en `law_functions_body_only/` contiene **solo el body interno** de la función (sin `let fn_xxx = (...) {` ni `};`).
- Esta versión está pensada para copiar/pegar directo en el campo **Body** al crear la función manualmente en LAW UI.

## Parámetros para crear cada función en LAW (firmas)

> Usa exactamente estos parámetros al crear cada función en LAW.

### Cross-product helpers
- `fn_mon_status_to_color(status:string)`
- `fn_mon_alert_from_job_success_src_v2(src:(TimeGenerated:datetime, JobName_s:string, Log_s:string), job_name:string, lookback_min:int, startTime:datetime, endTime:datetime)`
- `fn_mon_alert_from_pipeline_success_src_v2(src:(TimeGenerated:datetime, Category:string, ResourceGroup:string, OperationName:string), resource_group:string, lookback_min:int, startTime:datetime, endTime:datetime)`
- `fn_mon_global_from_color_set(colors:dynamic, alert_color:string = "#E53935", ok_color:string = "#EAF4EA")`

### ADA-only helper
- `fn_prd_ada_alert_from_tables_lag(tables:dynamic, startTime:datetime, endTime:datetime)`

### Domain functions
- `fn_prd_ada_dom_dispatch_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_drillit_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_blockgrade_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_pi_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_plans_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_meteodata_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_alarm_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_front_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_kpi_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_kpi_detalle_html(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_global_status(startTime:datetime, endTime:datetime)`

## Cómo completar "Function parameters" en LAW UI (una por una)

> En LAW UI, al crear la función:
> 1) En **Function name** usa el nombre exacto.
> 2) En **Function parameters** agrega los parámetros exactamente como se listan abajo (mismo nombre y tipo).
> 3) En **Body** pega el contenido desde `law_functions_body_only/...`.

### Cross-product helpers

#### 1) `fn_mon_status_to_color`
- `status:string`

#### 2) `fn_mon_alert_from_job_success_src_v2`
- `src:(TimeGenerated:datetime, JobName_s:string, Log_s:string)`
- `job_name:string`
- `lookback_min:int`
- `startTime:datetime`
- `endTime:datetime`

#### 3) `fn_mon_alert_from_pipeline_success_src_v2`
- `src:(TimeGenerated:datetime, Category:string, ResourceGroup:string, OperationName:string)`
- `resource_group:string`
- `lookback_min:int`
- `startTime:datetime`
- `endTime:datetime`

#### 4) `fn_mon_global_from_color_set`
- `colors:dynamic`
- `alert_color:string = "#E53935"` *(opcional, con default)*
- `ok_color:string = "#EAF4EA"` *(opcional, con default)*

### ADA-only helper

#### 5) `fn_prd_ada_alert_from_tables_lag`
- `tables:dynamic`
- `startTime:datetime`
- `endTime:datetime`

### Domain functions

#### 6) `fn_prd_ada_dom_dispatch_status`
- `startTime:datetime`
- `endTime:datetime`

#### 7) `fn_prd_ada_dom_drillit_status`
- `startTime:datetime`
- `endTime:datetime`

#### 8) `fn_prd_ada_dom_blockgrade_status`
- `startTime:datetime`
- `endTime:datetime`

#### 9) `fn_prd_ada_dom_pi_status`
- `startTime:datetime`
- `endTime:datetime`

#### 10) `fn_prd_ada_dom_plans_status`
- `startTime:datetime`
- `endTime:datetime`

#### 11) `fn_prd_ada_dom_meteodata_status`
- `startTime:datetime`
- `endTime:datetime`

#### 12) `fn_prd_ada_dom_alarm_status`
- `startTime:datetime`
- `endTime:datetime`

#### 13) `fn_prd_ada_dom_front_status`
- `startTime:datetime`
- `endTime:datetime`

#### 14) `fn_prd_ada_dom_kpi_status`
- `startTime:datetime`
- `endTime:datetime`

#### 15) `fn_prd_ada_dom_kpi_detalle_html`
- `startTime:datetime`
- `endTime:datetime`

#### 16) `fn_prd_ada_dom_global_status`
- `startTime:datetime`
- `endTime:datetime`

## Orden de implementación
1. Crear en LAW los 4 `helpers_cross_product`.
2. Crear en LAW el helper ADA-only.
3. Crear en LAW las 11 funciones de dominio (dejar `fn_prd_ada_dom_global_status` al final).
4. Reemplazar en Grafana cada variable por su wrapper homónimo.

## Nota de alcance
- `fn_prd_ada_dom_global_status` consolida colores de dominios ya resueltos.
- `fn_prd_ada_dom_kpi_detalle_html` devuelve HTML compacto para panel detalle KPI (solo caídos y sobre umbral).
- No hay archivos redundantes ni agrupadores legacy en este paquete final.


## Importante al crear funciones en LAW (evitar error "Body of the callable expression cannot be empty")
Los archivos `.kql` del repo están en formato:

```kql
let fn_xxx = (parametros) {
  ...body...
};
```

Cuando crees la función en LAW desde la UI, define el nombre y parámetros en el formulario y pega **solo el body interno** (sin `let fn_xxx = ...` ni `};`).
Si pegas el archivo completo como body, LAW puede guardar una función con cuerpo no ejecutable y devolver:
`Body of the callable expression cannot be empty`.


## Nota técnica (workspace literal)
`workspace()` exige argumentos literales.
Por eso los helpers `fn_mon_alert_from_job_success_src_v2` y `fn_mon_alert_from_pipeline_success_src_v2` ahora reciben un `src` tabular y cada dominio pasa `workspace("...").table(...)` de forma explícita.
Esto evita el error: `Expecting all arguments to be literals`.
