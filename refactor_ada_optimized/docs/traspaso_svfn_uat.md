# Traspaso SENSOR VIRTUAL FLUJO NaSH (SVFN) - MLP UAT

## 1) Qué monitorea

- **Fuente NotPII_Interpolated:** valida las últimas 5 señales del job `mlp-prd-caj-pisystem-job01` en una ventana de 30 minutos. Entrega `ALERT` si las 5 últimas señales son fallas.
- **Tags:** valida los últimos valores guardados en cache por `mlp-uat-caj-svfn-job02` durante una ventana de 5 minutos. Entrega `ALERT` si algún valor viene vacío, `NaN`, `null`, no numérico, menor o igual a 0, o mayor o igual a 15000.
- **Transformación:** valida las últimas 60 señales de ejecución de `mlp-uat-caj-svfn-job01` y `mlp-uat-caj-svfn-job02` dentro de 1 hora. Entrega `ALERT` si todas las muestras recientes de cualquiera de los jobs son fallas.
- **Predicción:** valida las últimas predicciones publicadas por `mlp-uat-caj-svfn-job02` para `tph prediction`, `concol prediction` y `flow prediction`. Entrega `ALERT` ante valores vacíos, `NaN`, no numéricos, menores o iguales a 0, o mayores o iguales a 15000.

## 2) Mapa técnico

- Panel resumen ejecutivo: variable Grafana `var_mlp_svfn_global`.
- Panel detalle: variables Grafana `var_mlp_svfn_fuente_notpii_interpolated`, `var_mlp_svfn_tags`, `var_mlp_svfn_transformacion` y `var_mlp_svfn_prediccion`.
- Wrappers Grafana: `refactor_ada_optimized/grafana_wrappers/uat/mlp/svfn/`.
- Funciones dominio desacopladas: `fn_uat_mlp_svfn_dom_fuente_notpii_interpolated_status(startTime, endTime)`, `fn_uat_mlp_svfn_dom_tags_status(startTime, endTime)`, `fn_uat_mlp_svfn_dom_transformacion_status(startTime, endTime)`, `fn_uat_mlp_svfn_dom_prediccion_status(startTime, endTime)` y `fn_uat_mlp_svfn_dom_resumen_status(startTime, endTime)`. Todas terminan con `print status` para exponer `print_0` en Grafana.
- Sources LAW: `fn_src_mlp_uat_ws_svfn(sourceType, startTime, endTime)` y `fn_src_mlp_uat_ws_notpii_interpolated(sourceType, startTime, endTime)`.
- Workspaces LAW: `MLP-UAT-RG-SVFN / mlp-uat-law-svfn` para SVFN y `MLP-PRD-RG-PISYSTEM / mlp-prd-law-pisystem` para la fuente `NotPII_Interpolated`.

## 3) Orden de despliegue LAW

1. `refactor_ada_optimized/law_functions/uat/mlp/sources/fn_src_mlp_uat_ws_svfn.kql`
2. `refactor_ada_optimized/law_functions/uat/mlp/sources/fn_src_mlp_uat_ws_notpii_interpolated.kql`
3. Funciones de dominio desacopladas en `refactor_ada_optimized/law_functions/uat/mlp/svfn/domains/`
4. `refactor_ada_optimized/law_functions/uat/mlp/svfn/domains/fn_uat_mlp_svfn_dom_resumen_status.kql`
5. Wrappers Grafana en `refactor_ada_optimized/grafana_wrappers/uat/mlp/svfn/`
6. Query Power Automate `refactor_ada_optimized/power_automate_queries/uat/mlp/svfn/resumen_estado.kql`

## 4) Queries operativas para soporte

```kusto
fn_uat_mlp_svfn_dom_resumen_status(ago(1h), now())
| project color = fn_mon_status_to_color(print_0)
```

```kusto
union
  (fn_uat_mlp_svfn_dom_fuente_notpii_interpolated_status(ago(1h), now()) | project dominio="NotPII_Interpolated", estado=print_0),
  (fn_uat_mlp_svfn_dom_tags_status(ago(1h), now()) | project dominio="Tags", estado=print_0),
  (fn_uat_mlp_svfn_dom_transformacion_status(ago(1h), now()) | project dominio="Transformacion", estado=print_0),
  (fn_uat_mlp_svfn_dom_prediccion_status(ago(1h), now()) | project dominio="Prediccion", estado=print_0)
```

## 5) Criterio de escalamiento

- Escalar cuando el resumen global retorne `ALERT`.
- Evidencia mínima: dominio en alerta (`NotPII_Interpolated`, `Tags`, `Transformacion` o `Prediccion`), ventana evaluada y últimos logs de `mlp-prd-caj-pisystem-job01`, `mlp-uat-caj-svfn-job01` y `mlp-uat-caj-svfn-job02`.
- Runbook portal soporte: **Por definir**.
- Responsable técnico/funcional: **Por definir**.
