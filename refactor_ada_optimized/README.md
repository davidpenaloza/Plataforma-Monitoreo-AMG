# Plataforma Monitoreo AMG — Guía funcional (ADA, SIROSAG y NOTPII)

Este README describe **cómo está organizado el paquete KQL**, qué hace cada categoría de funciones y cuáles son las funciones activas por producto.

---

## 1) Estructura del paquete

```text
refactor_ada_optimized/
├─ law_functions/
│  ├─ ada/
│  │  ├─ domains/             # Domains de ADA
│  │  └─ helpers/             # Helpers de ADA
│  ├─ notpii/
│  │  ├─ domains/             # Domains de NOTPII
│  │  └─ helpers/             # Helpers de NOTPII
│  ├─ sirosag/
│  │  ├─ domains/             # Domains de SIROSAG
│  │  └─ helpers/             # Helpers de SIROSAG
│  ├─ cross_product/
│  │  └─ helpers/             # Utilidades compartidas
│  └─ sources/                # Fuentes comunes (mismo nivel que carpetas de productos)
├─ law_functions_body_only/   # Espejo por producto para pegar body en LAW UI
└─ grafana_wrappers/          # Variables/paneles de Grafana (entrypoints)
```


### Convención de ubicación

- Todo lo específico de producto vive bajo su carpeta (`ada/`, `notpii/`, `sirosag/`).
- Dentro de cada producto: `domains/` y `helpers/`.
- `sources/` queda al mismo nivel de las carpetas de producto para centralizar acceso a datos.
- Esta misma organización se replica en `law_functions_body_only/`.

### Flujo general de ejecución

`Grafana wrapper -> Domain -> Helper(s) -> Source(s) -> Workspace table`

- **Wrapper**: selecciona 1 domain function.
- **Domain**: define estado final (normalmente color rojo/verde).
- **Helper**: aplica reglas de negocio (lag, errores, ventanas, umbrales).
- **Source**: estandariza lectura de tablas del workspace.

---

## 2) Categorías de funciones

## 2.1 Domains (`fn_prd_mlp_*_dom_*`)
Funciones de “estado final” consumidas desde Grafana.

## 2.2 Helpers (`fn_prd_mlp_*_*`)
Funciones de evaluación de reglas: alertas, desactualización, fallas consecutivas, etc.

## 2.3 Sources (`fn_src_mlp_*` y `fn_src_mlp_ws_*`)
Funciones de acceso a logs/pipelines.

- `fn_src_mlp_ws_*`: acceso directo por workspace/tablas concretas.
- `fn_src_mlp_*` (agregadoras): cuando un dominio combina múltiples fuentes.

## 2.4 Cross product
Funciones compartidas entre productos:

- `fn_mon_status_to_color`
- `fn_mon_global_from_color_set`

---

## 3) ADA — funciones y propósito

## 3.1 Domains ADA
- `fn_prd_mlp_ada_dom_dispatch_status`: estado de Dispatch.
- `fn_prd_mlp_ada_dom_drillit_status`: estado de Drillit.
- `fn_prd_mlp_ada_dom_blockgrade_status`: estado de Blockgrade.
- `fn_prd_mlp_ada_dom_pi_status`: estado de PI.
- `fn_prd_mlp_ada_dom_plans_status`: estado de Plans.
- `fn_prd_mlp_ada_dom_meteodata_status`: estado de Meteodata.
- `fn_prd_mlp_ada_dom_alarm_status`: estado de Alarm.
- `fn_prd_mlp_ada_dom_front_status`: estado de Front.
- `fn_prd_mlp_ada_dom_kpi_status`: estado de KPI.
- `fn_prd_mlp_ada_dom_global_status`: consolidado global ADA.

## 3.2 Helpers ADA
- `fn_prd_mlp_ada_alert_from_tables_lag`: evalúa lag por tabla según umbrales dinámicos.
- `fn_prd_mlp_ada_alert_from_dispatch_nrt_logs`: evalúa alertas NRT desde logs de job17.
- `fn_prd_mlp_ada_kpi_alert_rows`: detecta KPIs con errores persistentes y aplica excepciones por horario/mantención.

## 3.3 Sources ADA
- Base genérica: `fn_src_mlp_ws_ada(tableName, startTime, endTime)`.
- Wrappers de compatibilidad:
  - `fn_src_mlp_ws_ada_table`
  - `fn_src_mlp_ws_ada_systemlogs`
  - `fn_src_mlp_ws_ada_consolelogs`
- Relacionadas de pipeline/systemlogs:
  - `fn_src_mlp_ws_dispatch(tableName, ...)`, `fn_src_mlp_ws_drillit(tableName, ...)`, `fn_src_mlp_ws_blkgrde(tableName, ...)`
  - `fn_src_mlp_ws_meteo(tableName, ...)`, `fn_src_mlp_ws_plans(tableName, ...)`
  - `fn_src_mlp_pipeline_runs_all`, `fn_src_mlp_systemlogs_all`

Ejemplo:
- `fn_src_mlp_ws_ada("ContainerAppSystemLogs_CL", startTime, endTime)`

---

## 4) NOTPII — funciones y propósito

## 4.1 Domains NOTPII
- `fn_prd_mlp_notpii_dom_autoloader_dev_status`
- `fn_prd_mlp_notpii_dom_autoloader_uat_status`
- `fn_prd_mlp_notpii_dom_ingesta_status`
- `fn_prd_mlp_notpii_dom_global_status`

## 4.2 Helpers NOTPII
- `fn_prd_mlp_notpii_autoloader_alert`: evaluación de autoloader (dev/uat).
- `fn_prd_mlp_notpii_ingesta_job04_alert`: evaluación de job04 PI System (errores/warnings/ejecución).

## 4.3 Sources NOTPII
- Base genérica PI System: `fn_src_mlp_ws_pisystem(tableName, startTime, endTime)`.
- Wrapper genérico Databricks por ambiente: `fn_src_mlp_ws_notpii_databricksjobs(env, startTime, endTime)` con `env = dev|uat|all`.
- Wrappers de compatibilidad:
  - `fn_src_mlp_ws_pisystem_table`, `fn_src_mlp_ws_pisystem_systemlogs`, `fn_src_mlp_ws_pisystem_consolelogs`
  - `fn_src_mlp_ws_notpii_databricksjobs_dev`, `fn_src_mlp_ws_notpii_databricksjobs_uat`
  - `fn_src_mlp_notpii_databricksjobs_all`

Ejemplos:
- `fn_src_mlp_ws_pisystem("ContainerAppConsoleLogs_CL", startTime, endTime)`
- `fn_src_mlp_ws_notpii_databricksjobs("all", startTime, endTime)`

---

## 5) SIROSAG — funciones y propósito

## 5.1 Domain SIROSAG
- `fn_prd_mlp_ssag_dom_resumen_status`: estado consolidado SIROSAG.

## 5.2 Helpers SIROSAG
- `fn_prd_mlp_ssag_eval_desactualizacion`: verifica si datos/logs están desactualizados.
- `fn_prd_mlp_ssag_eval_desfase`: evalúa desfase de datos.
- `fn_prd_mlp_ssag_eval_ejecucion`: evalúa ejecución esperada de jobs.

## 5.3 Sources SIROSAG
- Base genérica SSAG: `fn_src_mlp_ws_ssag(tableName, startTime, endTime)`.
- Wrappers de compatibilidad:
  - `fn_src_mlp_ws_ssag_table`, `fn_src_mlp_ws_ssag_systemlogs`, `fn_src_mlp_ws_ssag_consolelogs`
- Fuentes relacionadas usadas por agregación:
  - `fn_src_mlp_ws_pdmsagi(tableName, ...)`, `fn_src_mlp_ws_plans(tableName, ...)`, `fn_src_mlp_ws_pisystem(tableName, ...)`
  - `fn_src_mlp_ssag_systemlogs_all`

Ejemplo:
- `fn_src_mlp_ws_ssag("ContainerAppSystemLogs_CL", startTime, endTime)`

---

## 6) Wrappers activos de Grafana (entrypoint)

### ADA
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

### NOTPII
- `var_mlp_notpii_autoloader_dev`
- `var_mlp_notpii_autoloader_uat`
- `var_mlp_notpii_ingesta`
- `var_mlp_notpii_difusion_global`

### SIROSAG
- `var_mlp_sirosag_resumen`

---

## 7) Limpieza aplicada (funciones retiradas)

Se eliminaron archivos legacy/no utilizados (aliases o variantes antiguas) para evitar ruido y referencias obsoletas.  
El paquete ahora pasa la auditoría local:

```bash
python refactor_ada_optimized/validate_kql_references.py
# KQL package audit OK
```

---

## 8) Reglas para cambios futuros

1. Si agregas un nuevo dominio, debe tener wrapper en `grafana_wrappers/`.
2. Si agregas helper nuevo, preferir prefijo `fn_prd_mlp_*`.
3. Evitar duplicados legacy (`fn_prd_*` o `fn_src_*` sin `mlp_`) salvo compatibilidad justificada.
4. Mantener espejo en `law_functions_body_only/` cuando corresponda.
5. Validar siempre con:

```bash
python refactor_ada_optimized/validate_kql_references.py
```


## 9) Refactor de Sources — mapping old -> new

### 9.1 Base genérica por workspace
- `fn_src_mlp_ws_ada_table` -> `fn_src_mlp_ws_ada(tableName, ...)`
- `fn_src_mlp_ws_pisystem_table` -> `fn_src_mlp_ws_pisystem(tableName, ...)`
- `fn_src_mlp_ws_ssag_table` -> `fn_src_mlp_ws_ssag(tableName, ...)`

### 9.2 Wrappers mantenidos (compatibilidad)
- Se mantienen nombres históricos (`*_systemlogs`, `*_consolelogs`, `*_pipelineruns`) como wrappers finos para no romper consumidores.
- Internamente ahora delegan en funciones genéricas por workspace.

### 9.3 Limitación técnica KQL y tradeoff
- **Sí**, KQL permite pasar nombre de tabla como parámetro usando `workspace("...").table(tableName)`.
- **Limitación**: no se puede parametrizar de forma directa el identificador de workspace de manera libre y segura en una sola función universal sin introducir complejidad/ambigüedad.
- **Solución aplicada**: función genérica por workspace (ADA, PISYSTEM, SSAG, etc.) + wrappers de compatibilidad.
- **Tradeoff**: se mantiene algo de superficie API, pero se reduce drásticamente duplicación y se centraliza la parte crítica (workspace + filtro temporal).

### 9.4 Recomendación final
- Para tablas de un workspace conocido: usar `fn_src_mlp_ws_<workspace>(tableName, startTime, endTime)`.
- Para escenarios multi-entorno (NOTPII Databricks): usar función controlada por enum (`env = dev|uat|all`) en vez de string totalmente libre para workspace.
