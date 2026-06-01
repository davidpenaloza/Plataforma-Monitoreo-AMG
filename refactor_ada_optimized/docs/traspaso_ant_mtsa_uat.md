# Traspaso Mineral Tracking SIRO Ácido - Antucoya UAT

## 1) Qué monitorea

- **Ingestas:** evalúa `Tabla PI System` y `Tablas Jigsaw` desde `Logs_ANT_Mineral_Tracking_datamart_CL`. La alerta de NotPII se inhibe cuando los tags indican detención de planta.
- **Regla negocio:** evalúa reglas de calidad de datos del producto `SIRO Acido` para descripciones con `Diferencia` o `Demora`.
- **Procesamiento:** evalúa el job Databricks `610886078807192` para la tarea `forecast_agglomeration_v2`, alertando si todos los intervalos evaluados fallan.
- **Frontend:** evalúa disponibilidad de `AppServiceHTTPLogs` en 1 día, alertando si la disponibilidad baja de 85%.

## 2) Mapa técnico

- Panel resumen ejecutivo: variable Grafana `var_ant_mtsa_global`.
- Panel detalle: variables Grafana `var_ant_mtsa_ingestas`, `var_ant_mtsa_regla_negocio`, `var_ant_mtsa_procesamiento` y `var_ant_mtsa_frontend`.
- Wrappers Grafana: `refactor_ada_optimized/grafana_wrappers/uat/ant/mtsa/`.
- Funciones dominio desacopladas: `fn_uat_ant_mtsa_dom_ingestas_status(startTime, endTime)`, `fn_uat_ant_mtsa_dom_regla_negocio_status(startTime, endTime)`, `fn_uat_ant_mtsa_dom_procesamiento_status(startTime, endTime)`, `fn_uat_ant_mtsa_dom_frontend_status(startTime, endTime)` y `fn_uat_ant_mtsa_dom_resumen_status(startTime, endTime)`. Todas terminan con `print status` para exponer `print_0` en Grafana.
- Source LAW: `fn_src_ant_uat_ws_dataplatform(sourceType, startTime, endTime)`.
- Workspace LAW: `ams-uat-dataplatform-rg / ams-uat-dataplatform-laws`.

## 3) Orden de despliegue LAW

1. `refactor_ada_optimized/law_functions/uat/ant/sources/fn_src_ant_uat_ws_dataplatform.kql`
2. Funciones de dominio desacopladas en `refactor_ada_optimized/law_functions/uat/ant/mtsa/domains/`
3. `refactor_ada_optimized/law_functions/uat/ant/mtsa/domains/fn_uat_ant_mtsa_dom_resumen_status.kql`
4. Wrappers Grafana en `refactor_ada_optimized/grafana_wrappers/uat/ant/mtsa/`
5. Query Power Automate `refactor_ada_optimized/power_automate_queries/uat/ant/mtsa/resumen_estado.kql`

## 4) Queries operativas para soporte

```kusto
fn_uat_ant_mtsa_dom_resumen_status(ago(2h), now())
| project color = fn_mon_status_to_color(print_0)
```

```kusto
union
  (fn_uat_ant_mtsa_dom_ingestas_status(ago(2h), now()) | project dominio="Ingestas", estado=print_0),
  (fn_uat_ant_mtsa_dom_regla_negocio_status(ago(2h), now()) | project dominio="Regla_Negocio", estado=print_0),
  (fn_uat_ant_mtsa_dom_procesamiento_status(ago(2h), now()) | project dominio="Procesamiento_job", estado=print_0),
  (fn_uat_ant_mtsa_dom_frontend_status(ago(2h), now()) | project dominio="Frontend", estado=print_0)
```

## 5) Criterio de escalamiento

- Escalar cuando el resumen global retorne `ALERT`.
- Evidencia mínima: dominio en alerta (`Ingestas`, `Regla_Negocio`, `Procesamiento_job` o `Frontend`), ventana evaluada y últimas filas de la tabla o job asociado.
- Runbook portal soporte: **Por definir**.
- Responsable técnico/funcional: **Por definir**.
