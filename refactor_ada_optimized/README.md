# Plataforma Monitoreo AMG — Guía funcional (ADA, SIROSAG y NOTPII)

Este README describe **cómo está organizado el paquete KQL**, qué hace cada categoría de funciones y cuáles son las funciones activas por producto.

---

## 1) Estructura del paquete

```text
refactor_ada_optimized/
├─ law_functions/prd/mlp/
│  ├─ ada/{domains,helpers}   # ADA por ambiente/faena/producto
│  ├─ notpii/{domains,helpers}
│  ├─ sirosag/{domains,helpers}
│  ├─ cross_product/helpers
│  └─ sources                 # Fuentes comunes de prd/mlp
├─ law_functions_body_only/prd/mlp/  # Espejo para LAW UI
├─ power_automate_queries/prd/mlp/   # Queries listas para flujos Power Automate
└─ grafana_wrappers/prd/mlp/
   ├─ ada/                    # Wrappers de ADA
   ├─ notpii/                 # Wrappers de NOTPII
   └─ sirosag/                # Wrappers de SIROSAG
```


### Convención de ubicación

- Todo se organiza por `ambiente/faena/producto` (actual: `prd/mlp/<producto>`).
- Dentro de cada producto: `domains/` y `helpers/`.
- `sources/` queda al mismo nivel de las carpetas de producto para centralizar acceso a datos.
- Esta misma organización se replica en `law_functions_body_only/prd/mlp/`.

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
- `fn_prd_mlp_ada_dom_kpi_status`: estado de KPIs.
- `fn_prd_mlp_ada_dom_optimizador_status`: estado de Optimizador Mezcla (Databricks + ejecución job01 genshare).
- `fn_prd_mlp_ada_dom_settings_status`: estado de Settings (expected-vs-real sobre jobs PRFCI: job01 minuto 00, job02 a las 12/18).
- `fn_prd_mlp_ada_dom_global_status`: consolidado global ADA (incluye Settings y Optimizador Mezcla).

## 3.2 Helpers ADA
- `fn_prd_mlp_ada_lag_helpers`: evalúa lag por tabla según umbrales dinámicos.
- `fn_prd_mlp_ada_alert_from_dispatch_nrt_logs`: evalúa alertas NRT desde logs de job17.
- `fn_prd_mlp_ada_kpi_alert_rows`: detecta KPIs con errores persistentes y aplica excepciones por horario/mantención.
- `fn_prd_mlp_ada_jobs_status_detail`: diagnóstico tabular por job ADA (expected vs real), con umbral por job, tolerancia por rango (`range + mv-expand`), normalización especial de job17 y status granular (`a/s/w/n`).

## 3.3 Sources ADA
- Base genérica: `fn_src_mlp_ws_ada(sourceType, startTime, endTime)`.
- Sources dedicados de dominio:
  - `fn_src_mlp_ws_genshare(sourceType, startTime, endTime)`
  - `fn_src_mlp_ws_prfci(sourceType, startTime, endTime)`
- Relacionadas de pipeline/systemlogs:
  - `fn_src_mlp_ws_dispatch(sourceType, ...)`, `fn_src_mlp_ws_drillit(sourceType, ...)`, `fn_src_mlp_ws_blkgrde(sourceType, ...)`
  - `fn_src_mlp_ws_meteo(sourceType, ...)`, `fn_src_mlp_ws_plans(sourceType, ...)`
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
- Base genérica PI System: `fn_src_mlp_ws_pisystem(sourceType, startTime, endTime)`.
- Base genérica Databricks por ambiente: `fn_src_mlp_ws_notpii_databricksjobs(env, startTime, endTime)` con `env = dev|uat|all`.
- Consumo directo recomendado: `fn_src_mlp_ws_notpii_databricksjobs("DatabricksJobs", startTime, endTime)`.

Ejemplos:
- `fn_src_mlp_ws_pisystem("ContainerAppConsoleLogs_CL", startTime, endTime)`
- `fn_src_mlp_ws_notpii_databricksjobs("DatabricksJobs", startTime, endTime)`

---

## 5) SIROSAG — funciones y propósito

## 5.1 Domain SIROSAG
- `fn_prd_mlp_ssag_dom_resumen_status`: estado consolidado SIROSAG.

## 5.2 Helpers SIROSAG
- `fn_prd_mlp_ssag_eval_desactualizacion`: verifica si datos/logs están desactualizados.
- `fn_prd_mlp_ssag_eval_desfase`: evalúa desfase de datos.
- `fn_prd_mlp_ssag_eval_ejecucion`: evalúa ejecución esperada de jobs.

## 5.3 Sources SIROSAG
- Base genérica SSAG: `fn_src_mlp_ws_ssag(sourceType, startTime, endTime)`.
- Fuentes relacionadas usadas por agregación:
  - `fn_src_mlp_ws_pdmsagi(sourceType, ...)`, `fn_src_mlp_ws_plans(sourceType, ...)`, `fn_src_mlp_ws_pisystem(sourceType, ...)`
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
- `var_mlp_ada_jobs_detail` *(diagnóstico tabular por job para soporte)*
- `var_mlp_ada_jobs_detail_legacyfmt` *(diagnóstico con formato `status+real/esperado` para paridad visual legacy)*

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

1. Si agregas un nuevo dominio, debe tener wrapper en `grafana_wrappers/<ambiente>/<faena>/<producto>/`.
2. Si agregas helper nuevo, preferir prefijo `fn_prd_mlp_*`.
3. Evitar duplicados legacy (`fn_prd_*` o `fn_src_*` sin `mlp_`) salvo compatibilidad justificada.
4. Mantener espejo en `law_functions_body_only/<ambiente>/<faena>/` cuando corresponda.
5. Validar siempre con:

```bash
python refactor_ada_optimized/validate_kql_references.py
```

El validador también verifica que:
- no reaparezcan wrappers legacy de sources,
- exista espejo 1:1 entre `law_functions/<ambiente>/<faena>/sources` y `law_functions_body_only/<ambiente>/<faena>/sources`,
- no existan markers de merge-conflict (`<<<<<<<`, `=======`, `>>>>>>>`) en KQL.

Chequeo global recomendado (todo el repositorio):

```bash
python refactor_ada_optimized/check_conflict_markers.py
```


## 9) Refactor de Sources — mapping old -> new

### 9.1 Base genérica por workspace
- `fn_src_mlp_ws_ada(sourceType, startTime, endTime)`
- `fn_src_mlp_ws_dataplatform(sourceType, startTime, endTime)`
- `fn_src_mlp_ws_pisystem(sourceType, startTime, endTime)`
- `fn_src_mlp_ws_ssag(sourceType, startTime, endTime)`
- `fn_src_mlp_ws_dispatch(sourceType, startTime, endTime)`
- `fn_src_mlp_ws_drillit(sourceType, startTime, endTime)`
- `fn_src_mlp_ws_blkgrde(sourceType, startTime, endTime)`
- `fn_src_mlp_ws_meteo(sourceType, startTime, endTime)`
- `fn_src_mlp_ws_plans(sourceType, startTime, endTime)`
- `fn_src_mlp_ws_plans_local(sourceType, startTime, endTime)` *(diagnóstico/local, usa workspace de ejecución)*
- `fn_src_mlp_ws_pdmsagi(sourceType, startTime, endTime)`
- `fn_src_mlp_ws_notpii_databricksjobs(env, startTime, endTime)`

### 9.2 Estado de migración
- Los consumidores internos (`domains`, `helpers`, `product-level sources`) ya consumen directamente la capa genérica por workspace.
- Los wrappers legacy fueron retirados para dejar una base limpia y consistente.

### 9.3 Limitación técnica KQL y tradeoff
- **Sí**, KQL permite pasar nombre de tabla como parámetro usando API de tabla parametrizada en KQL (a través de funciones source).
- **Limitación**: no se puede parametrizar de forma directa el identificador de workspace de manera libre y segura en una sola función universal sin introducir complejidad/ambigüedad.
- **Solución aplicada**: función genérica por entorno/log-analytics (ADA, PISYSTEM, SSAG, etc.) consumida directamente por domains/helpers/sources agregadas.
- **Tradeoff**: se mantiene algo de superficie API, pero se reduce drásticamente duplicación y se centraliza la parte crítica (workspace + filtro temporal).

### 9.4 Recomendación final
- Para tablas de un workspace conocido: usar `fn_src_mlp_ws_<workspace>(sourceType, startTime, endTime)`.
- Para escenarios multi-entorno (NOTPII Databricks): usar función controlada por enum (`env = dev|uat|all`) en vez de string totalmente libre para workspace.


## 10) Estado de paridad legacy (ADA)

- Objetivo operativo: mantener alta equivalencia funcional frente a la query legacy de resumen ADA para evitar falsos positivos.
- Dispatch usa señales `lag_classic`, `lag_nrt` y `consec_fail_job17`.
- Alarmas usa señales duras (`incidentes_largos_alarmas` y `error_conexion_storage`).
- Settings se evalúa en esquema expected-vs-real con source PRFCI dedicado.
- Power Automate consume `fn_prd_mlp_ada_dom_global_status` vía `power_automate_queries/prd/mlp/ada/resumen_estado.kql`.
- La validación `power_automate_queries/prd/mlp/ada/legacy_parity_check.kql` compara dominio refactor vs señal job-level y marca `NO_JOB_SIGNAL` para dominios sin métrica directa en `jobs_status_detail` (p. ej. Optimizador/Settings).
