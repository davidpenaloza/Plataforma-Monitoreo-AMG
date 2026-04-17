# INVENTORY — Funciones activas (solo en uso)

> Este inventario lista únicamente funciones activas en el grafo de ejecución actual (wrappers -> domains -> helpers -> sources).

## 1) Wrappers -> Domain

| Wrapper | Domain function |
|---|---|
| var_mlp_ada_dispatch | fn_prd_mlp_ada_dom_dispatch_status |
| var_mlp_ada_drillit | fn_prd_mlp_ada_dom_drillit_status |
| var_mlp_ada_blockgrade | fn_prd_mlp_ada_dom_blockgrade_status |
| var_mlp_ada_plans | fn_prd_mlp_ada_dom_plans_status |
| var_mlp_ada_pi | fn_prd_mlp_ada_dom_pi_status |
| var_mlp_ada_meteodata | fn_prd_mlp_ada_dom_meteodata_status |
| var_mlp_ada_alarm | fn_prd_mlp_ada_dom_alarm_status |
| var_mlp_ada_front | fn_prd_mlp_ada_dom_front_status |
| var_mlp_ada_kpi | fn_prd_mlp_ada_dom_kpi_status |
| var_mlp_ada_global | fn_prd_mlp_ada_dom_global_status |
| var_mlp_notpii_autoloader_dev | fn_prd_mlp_notpii_dom_autoloader_dev_status |
| var_mlp_notpii_autoloader_uat | fn_prd_mlp_notpii_dom_autoloader_uat_status |
| var_mlp_notpii_ingesta | fn_prd_mlp_notpii_dom_ingesta_status |
| var_mlp_notpii_difusion_global | fn_prd_mlp_notpii_dom_global_status |
| var_mlp_sirosag_resumen | fn_prd_mlp_ssag_dom_resumen_status |

## 2) Domains activos

- ADA (10): `fn_prd_mlp_ada_dom_dispatch_status`, `fn_prd_mlp_ada_dom_drillit_status`, `fn_prd_mlp_ada_dom_blockgrade_status`, `fn_prd_mlp_ada_dom_pi_status`, `fn_prd_mlp_ada_dom_plans_status`, `fn_prd_mlp_ada_dom_meteodata_status`, `fn_prd_mlp_ada_dom_alarm_status`, `fn_prd_mlp_ada_dom_front_status`, `fn_prd_mlp_ada_dom_kpi_status`, `fn_prd_mlp_ada_dom_global_status`.
- NOTPII (4): `fn_prd_mlp_notpii_dom_autoloader_dev_status`, `fn_prd_mlp_notpii_dom_autoloader_uat_status`, `fn_prd_mlp_notpii_dom_ingesta_status`, `fn_prd_mlp_notpii_dom_global_status`.
- SIROSAG (1): `fn_prd_mlp_ssag_dom_resumen_status`.

## 3) Helpers activos

- Cross-product (2): `fn_mon_status_to_color`, `fn_mon_global_from_color_set`.
- ADA (3): `fn_prd_mlp_ada_alert_from_tables_lag`, `fn_prd_mlp_ada_alert_from_dispatch_nrt_logs`, `fn_prd_mlp_ada_kpi_alert_rows`.
- NOTPII (2): `fn_prd_mlp_notpii_autoloader_alert`, `fn_prd_mlp_notpii_ingesta_job04_alert`.
- SIROSAG (3): `fn_prd_mlp_ssag_eval_desactualizacion`, `fn_prd_mlp_ssag_eval_desfase`, `fn_prd_mlp_ssag_eval_ejecucion`.

## 4) Sources activos

### 4.1 Product/faena level
- `fn_src_mlp_pipeline_runs_all`
- `fn_src_mlp_systemlogs_all`
- `fn_src_mlp_ada_consolelogs`
- `fn_src_mlp_ssag_systemlogs_all`
- `fn_src_mlp_ssag_consolelogs_all`
- `fn_src_mlp_notpii_pisystem_systemlogs`
- `fn_src_mlp_notpii_pisystem_consolelogs`
- `fn_src_mlp_notpii_databricksjobs_all`

### 4.2 Workspace level
- `fn_src_mlp_ws_ada_table`, `fn_src_mlp_ws_ada_systemlogs`, `fn_src_mlp_ws_ada_consolelogs`
- `fn_src_mlp_ws_dispatch_pipelineruns`, `fn_src_mlp_ws_drillit_pipelineruns`, `fn_src_mlp_ws_blkgrde_pipelineruns`
- `fn_src_mlp_ws_meteo_systemlogs`, `fn_src_mlp_ws_plans_systemlogs`
- `fn_src_mlp_ws_pisystem_table`, `fn_src_mlp_ws_pisystem_systemlogs`, `fn_src_mlp_ws_pisystem_consolelogs`
- `fn_src_mlp_ws_ssag_table`, `fn_src_mlp_ws_ssag_systemlogs`, `fn_src_mlp_ws_ssag_consolelogs`
- `fn_src_mlp_ws_pdmsagi_systemlogs`
- `fn_src_mlp_ws_notpii_databricksjobs_dev`, `fn_src_mlp_ws_notpii_databricksjobs_uat`

## 5) Regla de limpieza

Si una función no aparece en este inventario y no es referenciada por wrappers/domains/helpers activos, debe considerarse candidata a eliminación.


## 6) Dirección de dependencias (arquitectura)

- Correcto: `wrapper -> domain -> helper -> source product/faena -> source workspace`.
- No aplicado aquí como regla general: `domain -> source workspace` directo.
- Motivo: mantener contrato estable y evitar duplicación de acceso a datos entre dominios.
