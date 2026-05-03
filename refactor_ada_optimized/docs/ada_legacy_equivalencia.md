# Comparación y equivalencia: dominios ADA (refactor) vs query legado

## Objetivo
Entregar una comparación directa entre la lógica refactorizada por dominio y la semántica esperada del resumen ADA legado.

## Resumen ejecutivo
- **Equivalencia alta** en dominios principales (Dispatch, KPIs, Alarmas) cuando se evalúa estado `ALERT/OK`.
- **Equivalencia funcional extendida** para `Optimizador Mezcla` y `Settings`, dominios agregados al consolidado actual y al resumen de Power Automate.
- Para dominios sin señal directa en `jobs_status_detail`, la validación marca **`NO_JOB_SIGNAL`** (no se interpreta como brecha funcional por sí sola).

## Comparación por dominio

| Dominio | Query legado (semántica) | Refactor actual | Equivalencia esperada |
|---|---|---|---|
| Dispatch | Alerta por atraso clásico, atraso NRT o fallas consecutivas job17 | `fn_prd_mlp_ada_dom_dispatch_status`: `lag_classic OR lag_nrt OR consec_fail_job17` | **Alta** |
| KPIs | Estado por ejecución de jobs KPI y alertas de disponibilidad | `fn_prd_mlp_ada_dom_kpi_status` + `fn_prd_mlp_ada_jobs_status_detail` | **Alta** |
| Alarmas | Señales duras operacionales + errores de conectividad | `fn_prd_mlp_ada_dom_alarm_status` (incidentes largos + storage errors + apoyo job-level) | **Alta** |
| Optimizador Mezcla | Cobertura parcial/no explícita en legado histórico | `fn_prd_mlp_ada_dom_optimizador_status` (Databricks + ejecución + lag) | **Funcional (extensión)** |
| Settings | Cobertura parcial/no explícita en legado histórico | `fn_prd_mlp_ada_dom_settings_status` (expected-vs-real, PRFCI) | **Funcional (extensión)** |

## Criterio de equivalencia aplicado
1. Se compara estado de dominio en salida refactor (`ALERT` / `OK`) contra señal de referencia job-level cuando existe.
2. Si un dominio no tiene señal job-level directa en `jobs_status_detail`, se etiqueta como `NO_JOB_SIGNAL`.
3. `NO_JOB_SIGNAL` implica **falta de proxy job-level**, no necesariamente falta de equivalencia de negocio.

## Query de validación recomendada
Usar:
- `refactor_ada_optimized/power_automate_queries/prd/mlp/ada/legacy_parity_check.kql`

Esta consulta ya:
- incluye `Dispatch`, `KPIs`, `Alarmas`, `Optimizador Mezcla`, `Settings`,
- compara estado de dominio vs proxy job-level,
- marca `MATCH`, `DIFF` o `NO_JOB_SIGNAL`.

## Lectura práctica de resultados
- **MATCH**: dominio alineado en semántica operativa.
- **DIFF**: revisar ventana temporal, tolerancias de dominio y/o fuente de datos.
- **NO_JOB_SIGNAL**: validar contra lógica de dominio (no contra jobs_detail), especialmente para extensiones como Settings/Optimizador.
