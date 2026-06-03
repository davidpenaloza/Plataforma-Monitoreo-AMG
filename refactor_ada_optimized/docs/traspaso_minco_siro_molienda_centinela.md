# Traspaso MINCO - Siro Molienda Centinela - UAT

## 1) Qué monitorea

El modelo queda alineado con las dimensiones exportadas en `paneles_minco_siro_molienda_centinela.txt`:

- **Ingesta_PISystem**: revisa completitud de los jobs PI System `cen-dev-caj-pisystem-job01`, `cen-dev-caj-pisystem-job02` y `cen-dev-caj-pisystem-job03` contra la frecuencia esperada del panel legacy.
- **Ingesta_MT**: revisa el job MT `cen-dev-caj-mt-job01` en el slot vigente con ventana de gracia y lag de ingesta.
- **Procesamiento_Features**: agrega el estado de los jobs SMOL `cen-uat-caj-smol-job01` a `cen-uat-caj-smol-job05`.
- **Recomendacion**: revisa el job de optimización/recomendación `cen-uat-caj-smol-job06`.
- **Reentrenamiento**: revisa el job de entrenamiento `cen-uat-caj-smol-job07`; por criterio del panel, una falla o warning en esta dimensión queda como `Warning`, no como `Critical`.

Los estados expuestos para Grafana/Power Automate son `OK`, `Warning` o `Critical`. Las dimensiones de ingesta que en el panel legacy aparecían como `Alertar`/`No Alertar` se normalizan a `Critical`/`OK` para mantener la misma semántica visual que las otras dimensiones.

La lógica de negocio no queda concentrada en `fn_uat_cen_minco_sm_status_dimensions`: esa función solo orquesta resultados. Las reglas específicas viven en helpers separados por responsabilidad (`eval_ingesta_pisystem`, `eval_ingesta_mt` y `eval_smol_jobs`) para reducir riesgo de cambios cruzados.

## 2) Mapa técnico

| Dimensión | Wrapper Grafana | Dominio | Helper / sources |
|---|---|---|---|
| Ingesta_PISystem | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_ingesta_pisystem.kql` | `fn_uat_cen_minco_sm_dom_ingesta_pisystem_status` | `fn_uat_cen_minco_sm_eval_ingesta_pisystem`, `fn_uat_cen_minco_sm_status_dimensions`, `fn_src_cen_dev_ws_pisystem` |
| Ingesta_MT | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_ingesta_mt.kql` | `fn_uat_cen_minco_sm_dom_ingesta_mt_status` | `fn_uat_cen_minco_sm_eval_ingesta_mt`, `fn_uat_cen_minco_sm_status_dimensions`, `fn_src_cen_dev_ws_mt` |
| Procesamiento_Features | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_procesamiento_features.kql` | `fn_uat_cen_minco_sm_dom_procesamiento_features_status` | `fn_uat_cen_minco_sm_eval_smol_jobs`, `fn_uat_cen_minco_sm_status_dimensions`, `fn_src_cen_uat_ws_smol` |
| Recomendacion | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_recomendacion.kql` | `fn_uat_cen_minco_sm_dom_recomendacion_status` | `fn_uat_cen_minco_sm_eval_smol_jobs`, `fn_uat_cen_minco_sm_status_dimensions`, `fn_src_cen_uat_ws_smol` |
| Reentrenamiento | `grafana_wrappers/uat/cen/minco_siro_molienda/var_cen_minco_sm_reentrenamiento.kql` | `fn_uat_cen_minco_sm_dom_reentrenamiento_status` | `fn_uat_cen_minco_sm_eval_smol_jobs`, `fn_uat_cen_minco_sm_status_dimensions`, `fn_src_cen_uat_ws_smol` |

## 3) Orden de despliegue LAW

1. Sources:
   - `fn_src_cen_dev_ws_pisystem`
   - `fn_src_cen_dev_ws_mt`
   - `fn_src_cen_uat_ws_smol`
2. Helpers:
   - `fn_uat_cen_minco_sm_eval_ingesta_pisystem`
   - `fn_uat_cen_minco_sm_eval_ingesta_mt`
   - `fn_uat_cen_minco_sm_eval_smol_jobs`
   - `fn_uat_cen_minco_sm_status_dimensions`
3. Dominios:
   - `fn_uat_cen_minco_sm_dom_ingesta_pisystem_status`
   - `fn_uat_cen_minco_sm_dom_ingesta_mt_status`
   - `fn_uat_cen_minco_sm_dom_procesamiento_features_status`
   - `fn_uat_cen_minco_sm_dom_recomendacion_status`
   - `fn_uat_cen_minco_sm_dom_reentrenamiento_status`
4. Wrappers Grafana y Power Automate.

## 4) Queries operativas para soporte

```kusto
fn_uat_cen_minco_sm_status_dimensions(ago(3h), now())
```

```kusto
fn_uat_cen_minco_sm_dom_ingesta_pisystem_status(ago(3h), now())
```

```kusto
fn_uat_cen_minco_sm_dom_ingesta_mt_status(ago(3h), now())
```

```kusto
fn_uat_cen_minco_sm_dom_procesamiento_features_status(ago(3h), now())
```

```kusto
fn_uat_cen_minco_sm_dom_recomendacion_status(ago(3h), now())
```

```kusto
fn_uat_cen_minco_sm_dom_reentrenamiento_status(ago(3h), now())
```

## 5) Criterio de escalamiento

- Escalar como incidente crítico cuando `Ingesta_PISystem`, `Ingesta_MT`, `Procesamiento_Features` o `Recomendacion` retornen `Critical`.
- Escalar como advertencia cuando cualquier dimensión retorne `Warning`.
- `Reentrenamiento` se mantiene no crítico: sus estados anómalos retornan `Warning`.
- Evidencia mínima: dimensión afectada, ventana consultada, job asociado y último bucket evaluado.
