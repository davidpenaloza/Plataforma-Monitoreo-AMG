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
2. `law_functions/helpers_cross_product/fn_mon_alert_from_job_success.kql`
3. `law_functions/helpers_cross_product/fn_mon_alert_from_pipeline_success.kql`
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
15. `law_functions/domains/fn_prd_ada_dom_global_status.kql`

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

## Orden de implementación
1. Crear en LAW los 4 `helpers_cross_product`.
2. Crear en LAW el helper ADA-only.
3. Crear en LAW las 10 funciones de dominio (global al final).
4. Reemplazar en Grafana cada variable por su wrapper homónimo.

## Nota de alcance
- `fn_prd_ada_dom_global_status` consolida colores de dominios ya resueltos.
- No hay archivos redundantes ni agrupadores legacy en este paquete final.
