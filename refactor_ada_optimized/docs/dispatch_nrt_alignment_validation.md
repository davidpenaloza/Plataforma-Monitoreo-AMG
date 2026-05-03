# Validación de alineamiento: `dispatch_status` vs lógica de panel “NRT Dispatch”

Fecha: 2026-04-28

## Alcance

Se validó si la función de producto `fn_prd_mlp_ada_dom_dispatch_status` implementa la misma intención funcional que la lógica de panel compartida para `NRT Dispatch`.

## Funciones revisadas

- `fn_prd_mlp_ada_dom_dispatch_status`
- `fn_prd_mlp_ada_alert_from_dispatch_nrt_logs`
- `fn_prd_mlp_ada_lag_helpers`

## Resultado

**Conclusión: Sí, concuerda funcionalmente con la lógica del panel para `NRT Dispatch`.**

La función de dominio alerta cuando se cumple cualquiera de estas condiciones:

1. Desactualización clásica de tablas Dispatch (`lag_classic == "ALERT"`).
2. Desfase NRT en logs del job17 (`lag_nrt == "ALERT"`, umbral 6 minutos).
3. Al menos 2 fallas consecutivas recientes del job17 (`consec_fail_job17 == true`).

Esto replica la regla de alto nivel usada en el panel: desactualización de tablas Dispatch **o** consecutividad de fallas del job17.

## Comparación técnica (resumen)

| Regla panel NRT Dispatch | Implementación en funciones KQL | Estado |
|---|---|---|
| Alertar si alguna tabla Dispatch está desactualizada (`Std*`, `dispatch_*`, etc.) | `fn_prd_mlp_ada_lag_helpers(dispatch_tables, ...)` con umbrales por tabla en `mapUmbralAlerta` | Alineado |
| Alertar si en logs NRT (`Diff sql query`) el desfase supera 6 min | `fn_prd_mlp_ada_alert_from_dispatch_nrt_logs(...)` con `diff_minutos > 6` | Alineado |
| Alertar si Job17 presenta 2 fallas consecutivas recientes | `consec_fail_job17` en `fn_prd_mlp_ada_dom_dispatch_status` | Alineado |
| Estado final de Dispatch | `ALERT` si cualquiera de las 3 condiciones anteriores se cumple | Alineado |

## Observaciones

- La capa actual usa sources (`fn_src_mlp_systemlogs_all`, `fn_src_mlp_ws_ada`) y no usa accesos directos a workspaces fuera de `/sources`.
- No se aplicaron cambios funcionales en esta validación, porque la lógica ya está alineada con la intención del panel.

## Comandos ejecutados

- `sed -n '1,220p' refactor_ada_optimized/law_functions/ada/domains/fn_prd_mlp_ada_dom_dispatch_status.kql`
- `sed -n '1,220p' refactor_ada_optimized/law_functions/ada/helpers/fn_prd_mlp_ada_alert_from_dispatch_nrt_logs.kql`
- `sed -n '1,260p' refactor_ada_optimized/law_functions/ada/helpers/fn_prd_mlp_ada_lag_helpers.kql`



## Actualización 2026-05-02

- Se retiró la condición extra `adaJobsDispatchAlert` del dominio Dispatch para mantener alineamiento estricto con la semántica legacy de panel.
- Estado final permanece basado en: `lag_classic OR lag_nrt OR consec_fail_job17`.
