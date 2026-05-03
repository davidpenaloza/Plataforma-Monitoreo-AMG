# Comparación y equivalencia: dominios ADA (refactor) vs query legacy

## Objetivo
Validar equivalencia funcional por dominio entre la implementación refactorizada ADA y la semántica del KQL legacy.

## Equivalencia por dominio (completa)

| Dominio | Regla funcional refactor | Equivalencia vs legacy |
|---|---|---|
| Dispatch | `ALERT` si `lag_classic OR lag_nrt OR consec_fail_job17` | Alta |
| Drillit | `ALERT` si no hay ingesta pipeline OK o lag en tablas drillit | Alta |
| Blockgrade | `ALERT` si falla ingesta ADF o hay lag `blockgrade_bybucket` | Alta |
| PI | `ALERT` si `job01/job02` quedan bajo expected-vs-real (85%) o hay lag `pisystem_interpolated` | Alta |
| Plans | `ALERT` si `job01_plans` queda bajo expected-vs-real (85%, ventana horaria legacy) o hay lag en tablas de planes | Alta |
| Meteodata | `ALERT` si faltan jobs meteo o hay lag `meteodata` | Alta |
| KPI | `ALERT` por alertas job-level KPI o KPI no esperado | Alta |
| Alarmas | `ALERT` por alertas job-level alarmas, incidentes largos o error storage | Alta |
| Front | `ALERT` por errores de app/token en AppServiceConsoleLogs | Alta |
| Optimizador Mezcla | `ALERT` por `runFailed`, falta job01 genshare o lag optimizador | Alta |
| Settings | `ALERT` por expected-vs-real de job01/job02 (PRFCI) | Alta |

## Criterio de evaluación
1. Se compara salida binaria de dominio (`ALERT/OK`) con la semántica esperada del legacy.
2. Cuando existe proxy job-level, se usa contraste directo `MATCH/DIFF`.
3. Cuando no existe proxy job-level directo, se mantiene verificación funcional por regla de dominio y se reporta `NO_JOB_SIGNAL` para trazabilidad.

## Query recomendada
- `refactor_ada_optimized/power_automate_queries/prd/mlp/ada/legacy_parity_check.kql`

Incluye: `Dispatch`, `KPIs`, `Alarmas`, `Optimizador Mezcla`, `Settings`.

## Revisión adicional de equivalencia (2026-05-03)
- `Meteo`: ajustado a patrón expected-vs-real del legacy (`job01` minutos 0/15/30/45, `job02` minutos 1/16/31/46) con umbral `85%` + lag de `meteodata`.
- `Settings`: ajustado a evaluación expected-vs-real con umbral `85%` para `job01`/`job02` sobre PRFCI.
- `Front`, `PI`, `Blockgrade`: previamente alineados a reglas legacy (`>2` errores front, job01+job02 en PI, y alerta blockgrade sin compuerta de mantención).
