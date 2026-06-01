# Traspaso SENSOR VIRTUAL FLUJO NaSH (SVFN) - MLP UAT

## 1) Qué monitorea

- **Tags:** valida los últimos valores guardados en cache por `mlp-uat-caj-svfn-job02` durante una ventana de 5 minutos. Alerta si algún valor viene vacío, `NaN`, `null`, no numérico, menor o igual a 0, o mayor o igual a 15000.
- **Transformación:** valida las últimas 60 señales de ejecución de `mlp-uat-caj-svfn-job01` y `mlp-uat-caj-svfn-job02` dentro de 1 hora. Alerta si todas las muestras recientes de cualquiera de los jobs son fallas.
- **Predicción:** valida las últimas predicciones publicadas por `mlp-uat-caj-svfn-job02` para `tph prediction`, `concol prediction` y `flow prediction`. Alerta ante valores vacíos, `NaN`, no numéricos, menores o iguales a 0, o mayores o iguales a 15000.

## 2) Mapa técnico

- Panel resumen ejecutivo: variable Grafana `var_mlp_svfn_global`.
- Panel detalle: variables Grafana `var_mlp_svfn_tags`, `var_mlp_svfn_transformacion` y `var_mlp_svfn_prediccion`.
- Wrappers Grafana: `refactor_ada_optimized/grafana_wrappers/uat/mlp/svfn/`.
- Función dominio: `fn_uat_mlp_svfn_dom_resumen_status(startTime, endTime)`.
- Source LAW: `fn_src_mlp_uat_ws_svfn(sourceType, startTime, endTime)`.
- Workspace LAW: `MLP-UAT-RG-SVFN / mlp-uat-law-svfn`.

## 3) Orden de despliegue LAW

1. `refactor_ada_optimized/law_functions/uat/mlp/sources/fn_src_mlp_uat_ws_svfn.kql`
2. `refactor_ada_optimized/law_functions/uat/mlp/svfn/domains/fn_uat_mlp_svfn_dom_resumen_status.kql`
3. Wrappers Grafana en `refactor_ada_optimized/grafana_wrappers/uat/mlp/svfn/`
4. Query Power Automate `refactor_ada_optimized/power_automate_queries/uat/mlp/svfn/resumen_estado.kql`

## 4) Queries operativas para soporte

```kusto
fn_uat_mlp_svfn_dom_resumen_status(ago(1h), now())
```

```kusto
fn_uat_mlp_svfn_dom_resumen_status(ago(1h), now())
| project Tags, Transformacion, Prediccion, EstadoGlobal, color
```

## 5) Criterio de escalamiento

- Escalar cuando `EstadoGlobal` sea `Alertar`.
- Evidencia mínima: dominio en alerta (`Tags`, `Transformacion` o `Prediccion`), ventana evaluada y últimos logs de `mlp-uat-caj-svfn-job01` / `mlp-uat-caj-svfn-job02`.
- Runbook portal soporte: **Por definir**.
- Responsable técnico/funcional: **Por definir**.
