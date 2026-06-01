# INVENTORY — Funciones activas

Inventario derivado del grafo real: `wrappers -> domains -> helpers -> sources`.


## 0) Organización de carpetas

- `law_functions/prd/mlp/ada/{domains,helpers}`
- `law_functions/prd/mlp/notpii/{domains,helpers}`
- `law_functions/prd/mlp/sirosag/{domains,helpers}`
- `law_functions/prd/mlp/cross_product/helpers`
- `law_functions/prd/mlp/sources`
- `grafana_wrappers/prd/mlp/{ada,notpii,sirosag}`
- `law_functions/uat/mlp/{sources,svfn/domains}`
- `grafana_wrappers/uat/mlp/svfn`

El mismo layout aplica para `law_functions_body_only/prd/mlp/`.

## 1) Wrappers activos

- ADA: `var_mlp_ada_global`, `var_mlp_ada_dispatch`, `var_mlp_ada_drillit`, `var_mlp_ada_pi`, `var_mlp_ada_plans`, `var_mlp_ada_blockgrade`, `var_mlp_ada_meteodata`, `var_mlp_ada_kpi`, `var_mlp_ada_alarm`, `var_mlp_ada_front`, `var_mlp_ada_jobs_detail`, `var_mlp_ada_jobs_detail_legacyfmt`.
- NOTPII: `var_mlp_notpii_autoloader_dev`, `var_mlp_notpii_autoloader_uat`, `var_mlp_notpii_ingesta`, `var_mlp_notpii_difusion_global`.
- SIROSAG: `var_mlp_sirosag_resumen`.
- SVFN UAT: `var_mlp_svfn_resumen`, `var_mlp_svfn_global`, `var_mlp_svfn_fuente_notpii_interpolated`, `var_mlp_svfn_tags`, `var_mlp_svfn_transformacion`, `var_mlp_svfn_prediccion`.

## 2) Domains activos

- ADA (12):
  - `fn_prd_mlp_ada_dom_dispatch_status`
  - `fn_prd_mlp_ada_dom_drillit_status`
  - `fn_prd_mlp_ada_dom_blockgrade_status`
  - `fn_prd_mlp_ada_dom_pi_status`
  - `fn_prd_mlp_ada_dom_plans_status`
  - `fn_prd_mlp_ada_dom_meteodata_status`
  - `fn_prd_mlp_ada_dom_alarm_status`
  - `fn_prd_mlp_ada_dom_front_status`
  - `fn_prd_mlp_ada_dom_kpi_status`
  - `fn_prd_mlp_ada_dom_optimizador_status`
  - `fn_prd_mlp_ada_dom_settings_status`
  - `fn_prd_mlp_ada_dom_global_status`

- NOTPII (4):
  - `fn_prd_mlp_notpii_dom_autoloader_dev_status`
  - `fn_prd_mlp_notpii_dom_autoloader_uat_status`
  - `fn_prd_mlp_notpii_dom_ingesta_status`
  - `fn_prd_mlp_notpii_dom_global_status`

- SIROSAG (1):
  - `fn_prd_mlp_ssag_dom_resumen_status`

- SVFN UAT (5):
  - `fn_uat_mlp_svfn_dom_fuente_notpii_interpolated_status`
  - `fn_uat_mlp_svfn_dom_tags_status`
  - `fn_uat_mlp_svfn_dom_transformacion_status`
  - `fn_uat_mlp_svfn_dom_prediccion_status`
  - `fn_uat_mlp_svfn_dom_resumen_status`

## 3) Helpers activos

- Cross-product:
  - `fn_mon_status_to_color`

- ADA:
  - `fn_prd_mlp_ada_lag_helpers`
  - `fn_prd_mlp_ada_alert_from_dispatch_nrt_logs`
  - `fn_prd_mlp_ada_kpi_alert_rows`
  - `fn_prd_mlp_ada_jobs_status_detail`

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
- `fn_src_mlp_ws_dataplatform(tableName, startTime, endTime)`
- `fn_src_mlp_ws_pisystem(tableName, startTime, endTime)`
- `fn_src_mlp_ws_ssag(tableName, startTime, endTime)`
- `fn_src_mlp_ws_dispatch(tableName, startTime, endTime)`
- `fn_src_mlp_ws_drillit(tableName, startTime, endTime)`
- `fn_src_mlp_ws_blkgrde(tableName, startTime, endTime)`
- `fn_src_mlp_ws_meteo(tableName, startTime, endTime)`
- `fn_src_mlp_ws_plans(tableName, startTime, endTime)`
- `fn_src_mlp_ws_plans_local(tableName, startTime, endTime)` *(diagnóstico/local, usa workspace de ejecución)*
- `fn_src_mlp_ws_pdmsagi(tableName, startTime, endTime)`
- `fn_src_mlp_ws_notpii_databricksjobs(env, startTime, endTime)`

### 4.2 Product-level agregadas
- `fn_src_mlp_pipeline_runs_all`
- `fn_src_mlp_systemlogs_all`
- `fn_src_mlp_ssag_systemlogs_all`
- `fn_src_mlp_uat_ws_svfn(sourceType, startTime, endTime)`
- `fn_src_mlp_uat_ws_notpii_interpolated(sourceType, startTime, endTime)`

## 5) Regla de limpieza

Si una función no aparece en este inventario y no forma parte del grafo de dependencias de wrappers activos, es candidata a eliminación.
