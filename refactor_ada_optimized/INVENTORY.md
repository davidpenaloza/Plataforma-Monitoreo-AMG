# INVENTORY — Funciones activas

Inventario derivado del grafo real: `wrappers -> domains -> helpers -> sources`.


## 0) Organización de carpetas

- `law_functions/ada/{domains,helpers}`
- `law_functions/notpii/{domains,helpers}`
- `law_functions/sirosag/{domains,helpers}`
- `law_functions/cross_product/helpers`
- `law_functions/sources` (mismo nivel que carpetas de productos)

El mismo layout aplica para `law_functions_body_only/`.

## 1) Wrappers activos

- ADA: `var_mlp_ada_global`, `var_mlp_ada_dispatch`, `var_mlp_ada_drillit`, `var_mlp_ada_pi`, `var_mlp_ada_plans`, `var_mlp_ada_blockgrade`, `var_mlp_ada_meteodata`, `var_mlp_ada_kpi`, `var_mlp_ada_alarm`, `var_mlp_ada_front`.
- NOTPII: `var_mlp_notpii_autoloader_dev`, `var_mlp_notpii_autoloader_uat`, `var_mlp_notpii_ingesta`, `var_mlp_notpii_difusion_global`.
- SIROSAG: `var_mlp_sirosag_resumen`.

## 2) Domains activos

- ADA (10):
  - `fn_prd_mlp_ada_dom_dispatch_status`
  - `fn_prd_mlp_ada_dom_drillit_status`
  - `fn_prd_mlp_ada_dom_blockgrade_status`
  - `fn_prd_mlp_ada_dom_pi_status`
  - `fn_prd_mlp_ada_dom_plans_status`
  - `fn_prd_mlp_ada_dom_meteodata_status`
  - `fn_prd_mlp_ada_dom_alarm_status`
  - `fn_prd_mlp_ada_dom_front_status`
  - `fn_prd_mlp_ada_dom_kpi_status`
  - `fn_prd_mlp_ada_dom_global_status`

- NOTPII (4):
  - `fn_prd_mlp_notpii_dom_autoloader_dev_status`
  - `fn_prd_mlp_notpii_dom_autoloader_uat_status`
  - `fn_prd_mlp_notpii_dom_ingesta_status`
  - `fn_prd_mlp_notpii_dom_global_status`

- SIROSAG (1):
  - `fn_prd_mlp_ssag_dom_resumen_status`

## 3) Helpers activos

- Cross-product:
  - `fn_mon_status_to_color`
  - `fn_mon_global_from_color_set`

- ADA:
  - `fn_prd_mlp_ada_alert_from_tables_lag`
  - `fn_prd_mlp_ada_alert_from_dispatch_nrt_logs`
  - `fn_prd_mlp_ada_kpi_alert_rows`

- NOTPII:
  - `fn_prd_mlp_notpii_autoloader_alert`
  - `fn_prd_mlp_notpii_ingesta_job04_alert`

- SIROSAG:
  - `fn_prd_mlp_ssag_eval_desactualizacion`
  - `fn_prd_mlp_ssag_eval_desfase`
  - `fn_prd_mlp_ssag_eval_ejecucion`

## 4) Sources activos

### 4.1 Base genérica por workspace
- `fn_src_mlp_ws_ada(tableName, startTime, endTime)`
- `fn_src_mlp_ws_pisystem(tableName, startTime, endTime)`
- `fn_src_mlp_ws_ssag(tableName, startTime, endTime)`
- `fn_src_mlp_ws_dispatch(tableName, startTime, endTime)`
- `fn_src_mlp_ws_drillit(tableName, startTime, endTime)`
- `fn_src_mlp_ws_blkgrde(tableName, startTime, endTime)`
- `fn_src_mlp_ws_meteo(tableName, startTime, endTime)`
- `fn_src_mlp_ws_plans(tableName, startTime, endTime)`
- `fn_src_mlp_ws_pdmsagi(tableName, startTime, endTime)`
- `fn_src_mlp_ws_notpii_databricksjobs(env, startTime, endTime)`

### 4.2 Wrappers de compatibilidad (legacy estable)
- `fn_src_mlp_ws_ada_table`
- `fn_src_mlp_ws_ada_systemlogs`
- `fn_src_mlp_ws_ada_consolelogs`
- `fn_src_mlp_ws_pisystem_table`
- `fn_src_mlp_ws_pisystem_systemlogs`
- `fn_src_mlp_ws_pisystem_consolelogs`
- `fn_src_mlp_ws_ssag_table`
- `fn_src_mlp_ws_ssag_systemlogs`
- `fn_src_mlp_ws_ssag_consolelogs`
- `fn_src_mlp_ws_dispatch_pipelineruns`
- `fn_src_mlp_ws_drillit_pipelineruns`
- `fn_src_mlp_ws_blkgrde_pipelineruns`
- `fn_src_mlp_ws_meteo_systemlogs`
- `fn_src_mlp_ws_plans_systemlogs`
- `fn_src_mlp_ws_pdmsagi_systemlogs`
- `fn_src_mlp_ws_notpii_databricksjobs_dev`
- `fn_src_mlp_ws_notpii_databricksjobs_uat`

### 4.3 Product-level agregadas
- `fn_src_mlp_pipeline_runs_all`
- `fn_src_mlp_systemlogs_all`
- `fn_src_mlp_ssag_systemlogs_all`
- `fn_src_mlp_notpii_databricksjobs_all`

## 5) Regla de limpieza

Si una función no aparece en este inventario y no forma parte del grafo de dependencias de wrappers activos, es candidata a eliminación.
