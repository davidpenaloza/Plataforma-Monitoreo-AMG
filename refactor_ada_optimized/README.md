# ADA Refactor Final (Optimized)

Carpeta final y oficial del refactor ADA, agrupada y categorizada para implementación directa.

## Estructura final
- `law_functions/helpers_cross_product/`: helpers reutilizables entre productos.
- `law_functions/helpers_ada/`: helpers específicos ADA.
- `law_functions/domains/`: funciones ADA por dominio.
- `grafana_wrappers/`: queries finales de variables `var_mlp_ada_*`.

## Decisión sobre función global cross-product
Sí conviene una global transversal **solo para consolidar estados ya resueltos** (sin queries pesadas).
Por eso existe `fn_mon_global_from_color_set(...)`: recibe un set de colores y devuelve el color global.
No depende de ADA ni de tablas/workspaces específicos.

## Funciones necesarias (LAW)
### 1) Cross-product helpers
- `helpers_cross_product/fn_mon_core_helpers.kql`
  - `fn_mon_status_to_color`
  - `fn_mon_alert_from_job_success`
  - `fn_mon_alert_from_pipeline_success`
  - `fn_mon_global_from_color_set`
  - `fn_prd_ada_alert_from_job_success` (alias)
  - `fn_prd_ada_alert_from_pipeline_success` (alias)

> Nota de compatibilidad: también existen alias `fn_prd_ada_alert_from_job_success` y
> `fn_prd_ada_alert_from_pipeline_success` para evitar quiebres con snippets antiguos.

### 2) ADA-only helpers
- `helpers_ada/fn_prd_ada_lag_helpers.kql`
  - `fn_prd_ada_alert_from_tables_lag`

### 3) ADA domain functions
- `domains/fn_prd_ada_dom_dispatch_status.kql`
- `domains/fn_prd_ada_dom_drillit_status.kql`
- `domains/fn_prd_ada_dom_blockgrade_status.kql`
- `domains/fn_prd_ada_dom_pi_status.kql`
- `domains/fn_prd_ada_dom_plans_status.kql`
- `domains/fn_prd_ada_dom_meteodata_status.kql`
- `domains/fn_prd_ada_dom_alarm_status.kql`
- `domains/fn_prd_ada_dom_front_status.kql`
- `domains/fn_prd_ada_dom_kpi_status.kql`
- `domains/fn_prd_ada_dom_global_status.kql`

## Variables necesarias (Grafana wrappers)
- `var_mlp_ada_global.kql`
- `var_mlp_ada_dispatch.kql`
- `var_mlp_ada_drillit.kql`
- `var_mlp_ada_pi.kql`
- `var_mlp_ada_plans.kql`
- `var_mlp_ada_blockgrade.kql`
- `var_mlp_ada_meteodata.kql`
- `var_mlp_ada_kpi.kql`
- `var_mlp_ada_alarm.kql`
- `var_mlp_ada_front.kql`

## Orden de implementación recomendado
1. Crear `fn_mon_core_helpers.kql` en LAW.
2. Crear `fn_prd_ada_lag_helpers.kql` en LAW.
3. Crear las 10 funciones de `law_functions/domains/`.
4. Reemplazar en Grafana cada variable por su wrapper homónimo en `grafana_wrappers/`.

## Mapeo variable -> función de dominio
- `var_mlp_ada_dispatch` -> `fn_prd_ada_dom_dispatch_status`
- `var_mlp_ada_drillit` -> `fn_prd_ada_dom_drillit_status`
- `var_mlp_ada_blockgrade` -> `fn_prd_ada_dom_blockgrade_status`
- `var_mlp_ada_plans` -> `fn_prd_ada_dom_plans_status`
- `var_mlp_ada_pi` -> `fn_prd_ada_dom_pi_status`
- `var_mlp_ada_meteodata` -> `fn_prd_ada_dom_meteodata_status`
- `var_mlp_ada_alarm` -> `fn_prd_ada_dom_alarm_status`
- `var_mlp_ada_front` -> `fn_prd_ada_dom_front_status`
- `var_mlp_ada_kpi` -> `fn_prd_ada_dom_kpi_status`
- `var_mlp_ada_global` -> `fn_prd_ada_dom_global_status`

## Nota de límite conocido
`global` sigue recomponiendo estados de dominios ADA. Con las restricciones actuales (sin materialización/caché compartido), ese costo no se elimina por completo.
