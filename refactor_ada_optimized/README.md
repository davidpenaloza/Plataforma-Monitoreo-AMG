# ADA Refactor Final (Optimized)

Este es el entregable final para implementación del refactor ADA.

## Qué contiene
- `law_functions/`: funciones KQL optimizadas por dominio (mínima consulta necesaria por variable) y helpers reutilizables.
- `grafana_wrappers/`: wrappers cortos para variables Grafana (`var_mlp_ada_*`) que devuelven `color`.
- `INVENTORY.md`: mapeo dominio/función/fuente mínima.

## Qué va en LAW
Crear/guardar primero (Logs -> Save as function):
1. `law_functions/fn_prd_ada_helpers.kql`
2. `law_functions/fn_prd_ada_dom_dispatch_status.kql`
3. `law_functions/fn_prd_ada_dom_drillit_status.kql`
4. `law_functions/fn_prd_ada_dom_blockgrade_status.kql`
5. `law_functions/fn_prd_ada_dom_pi_status.kql`
6. `law_functions/fn_prd_ada_dom_plans_status.kql`
7. `law_functions/fn_prd_ada_dom_meteodata_status.kql`
8. `law_functions/fn_prd_ada_dom_alarm_status.kql`
9. `law_functions/fn_prd_ada_dom_front_status.kql`
10. `law_functions/fn_prd_ada_dom_kpi_status.kql`
11. `law_functions/fn_prd_ada_dom_global_status.kql`

## Qué va en Grafana
Reemplazar la query de cada variable por su wrapper homónimo en `grafana_wrappers/`:
- `var_mlp_ada_global`
- `var_mlp_ada_dispatch`
- `var_mlp_ada_drillit`
- `var_mlp_ada_pi`
- `var_mlp_ada_plans`
- `var_mlp_ada_blockgrade`
- `var_mlp_ada_meteodata`
- `var_mlp_ada_kpi`
- `var_mlp_ada_alarm`
- `var_mlp_ada_front`

## Orden recomendado de implementación
1. Crear helpers en LAW.
2. Crear funciones de dominio en LAW.
3. Validar cada función en LAW (`ago(6h), now()`).
4. Migrar wrappers en Grafana variable por variable.
5. Verificar paridad visual de colores en el panel HTML.
