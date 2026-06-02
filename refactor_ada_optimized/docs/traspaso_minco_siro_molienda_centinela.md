# Traspaso MINCO - Siro Molienda Centinela - UAT

## 1) Qué monitorea

- **Ingestas**: revisa alertas vigentes en logs datamart para módulos de PI System y Jigsaw asociados a `SIRO Molienda`.
- **Regla de negocio**: revisa alertas vigentes de calidad de datos para `SIRO Molienda`.
- **Procesamiento**: revisa ejecuciones Databricks cuyo `taskKey` contiene `molienda`; alerta cuando todos los intervalos observados fallan.
- **Frontend**: revisa disponibilidad de `AppServiceHTTPLogs` filtrando aplicaciones que contienen `siro-molienda`.
- **Global/Resumen**: agrega los dominios anteriores y queda en `ALERT` si cualquiera de ellos alerta.

> Nota operativa: `paneles_minco_siro_molienda_centinela.txt` quedó vacío en el repositorio. Se implementó el set mantenible estándar del modelo para Centinela: ingestas, regla de negocio, procesamiento, frontend, resumen y global.

## 2) Mapa técnico

| Panel / variable | Wrapper Grafana | Dominio | Helpers / sources |
|---|---|---|---|
| Ingestas | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_ingestas.kql` | `fn_uat_cen_minco_sm_dom_ingestas_status` | `fn_uat_cen_minco_sm_alert_from_datamart`, `fn_uat_cen_minco_sm_status_rollup`, `fn_src_cen_uat_ws_dataplatform` |
| Regla de negocio | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_regla_negocio.kql` | `fn_uat_cen_minco_sm_dom_regla_negocio_status` | `fn_uat_cen_minco_sm_alert_from_datamart`, `fn_src_cen_uat_ws_dataplatform` |
| Procesamiento | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_procesamiento.kql` | `fn_uat_cen_minco_sm_dom_procesamiento_status` | `fn_uat_cen_minco_sm_databricks_task_status`, `fn_src_cen_uat_ws_dataplatform` |
| Frontend | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_frontend.kql` | `fn_uat_cen_minco_sm_dom_frontend_status` | `fn_uat_cen_minco_sm_frontend_availability`, `fn_src_cen_uat_ws_dataplatform` |
| Resumen | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_resumen.kql` | `fn_uat_cen_minco_sm_dom_resumen_status` | dominios anteriores, `fn_uat_cen_minco_sm_status_rollup` |
| Global | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_global.kql` | `fn_uat_cen_minco_sm_dom_global_status` | `fn_uat_cen_minco_sm_dom_resumen_status` |

## 3) Orden de despliegue LAW

1. Source: `fn_src_cen_uat_ws_dataplatform`.
2. Helpers:
   - `fn_uat_cen_minco_sm_catalog`
   - `fn_uat_cen_minco_sm_alert_from_datamart`
   - `fn_uat_cen_minco_sm_databricks_task_status`
   - `fn_uat_cen_minco_sm_frontend_availability`
   - `fn_uat_cen_minco_sm_status_rollup`
3. Dominios:
   - `fn_uat_cen_minco_sm_dom_ingestas_status`
   - `fn_uat_cen_minco_sm_dom_regla_negocio_status`
   - `fn_uat_cen_minco_sm_dom_procesamiento_status`
   - `fn_uat_cen_minco_sm_dom_frontend_status`
   - `fn_uat_cen_minco_sm_dom_resumen_status`
   - `fn_uat_cen_minco_sm_dom_global_status`
4. Wrappers Grafana y Power Automate.

## 4) Queries operativas para soporte

```kusto
fn_uat_cen_minco_sm_dom_global_status(ago(3h), now())
```

```kusto
fn_uat_cen_minco_sm_dom_ingestas_status(ago(3h), now())
```

```kusto
fn_uat_cen_minco_sm_dom_regla_negocio_status(ago(3h), now())
```

```kusto
fn_uat_cen_minco_sm_dom_procesamiento_status(ago(3h), now())
```

```kusto
fn_uat_cen_minco_sm_dom_frontend_status(ago(3h), now())
```

## 5) Criterio de escalamiento

- Escalar cuando cualquier dominio retorne `ALERT`.
- Evidencia mínima: dominio afectado, ventana consultada, última fila con `alertar == true` o bucket Databricks fallido.
- Runbook portal soporte: **Por definir**.
- Responsable técnico/funcional: **Por definir**.

## 6) Parámetros por validar en despliegue

Los parámetros reutilizables quedaron centralizados en `fn_uat_cen_minco_sm_catalog`:

| Parámetro | Valor inicial |
|---|---|
| `product_origin` | `SIRO Molienda` |
| `task_key_contains` | `molienda` |
| `frontend_app_contains` | `siro-molienda` |
| `datamart_detail_key` | `table` |

Validar estos valores contra los logs reales de Centinela antes del despliegue UAT definitivo.
