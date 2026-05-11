# Convenciones de nombrado

## Objetivo

Mantener consistencia entre archivos, funciones LAW, wrappers Grafana, productos, dominios, fuentes y ambientes.

## Naming para funciones

| Tipo | Patrón | Ejemplo correcto |
|---|---|---|
| Source por workspace | `fn_src_mlp_ws_<fuente>` | `fn_src_mlp_ws_ada` |
| Source agregada | `fn_src_mlp_<tipo>_all` | `fn_src_mlp_systemlogs_all` |
| Helper cross-producto | `fn_mon_<accion>` | `fn_mon_status_to_color` |
| Helper específico | `fn_prd_mlp_<producto>_<proposito>` | `fn_prd_mlp_ada_jobs_status_detail` |
| Dominio | `fn_prd_mlp_<producto>_dom_<dominio>_status` | `fn_prd_mlp_ada_dom_dispatch_status` |
| Global | `fn_prd_mlp_<producto>_dom_global_status` | `fn_prd_mlp_notpii_dom_global_status` |

## Naming para wrappers

Patrón:

```text
var_mlp_<producto>_<dominio>.kql
```

Ejemplos correctos:

- `var_mlp_ada_global.kql`
- `var_mlp_notpii_ingesta.kql`
- `var_mlp_sirosag_resumen.kql`

Ejemplos incorrectos:

- `query1.kql` — no indica producto ni dominio.
- `ada-global-prod.kql` — no sigue prefijo `var_mlp_`.
- `var_mlp_ada.kql` — no indica dominio.

## Naming para archivos

- El archivo de una función LAW debe llamarse igual que la función: `fn_prd_mlp_ada_dom_dispatch_status.kql`.
- El archivo de wrapper debe llamarse igual que la variable/wrapper: `var_mlp_ada_dispatch.kql`.
- Evitar espacios, mayúsculas y caracteres especiales.
- Usar guion bajo `_` para separar conceptos.

## Naming para productos

- Usar nombre corto en minúsculas.
- Mantener consistencia entre path, función y wrapper.
- Ejemplos observados: `ada`, `ada_amg`, `notpii`, `sirosag`/`ssag`.
- Si existe alias histórico, documentar equivalencia y elegir uno como canónico. Para SIROSAG/SSAG la equivalencia queda **Por validar**.

## Naming para dominios

- Usar nombres funcionales reconocibles por soporte.
- Evitar abreviaturas ambiguas si no están consolidadas.
- Ejemplos: `dispatch`, `drillit`, `blockgrade`, `pi`, `plans`, `meteodata`, `alarm`, `front`, `kpi`, `ingesta`, `autoloader_dev`, `autoloader_uat`, `resumen`.

## Naming para fuentes

- Para sources por workspace usar `fn_src_mlp_ws_<fuente>`.
- Para fuentes agregadas usar sufijo `_all`.
- El parámetro de tabla debe llamarse `sourceType` o `tableName` de forma consistente dentro del source.

## Naming para ambientes

- Usar `prd`, `uat`, `dev` en minúsculas.
- Reflejar ambiente en path: `law_functions/prd/mlp/...`.
- Si una función mezcla ambientes mediante parámetro `env`, documentar valores válidos.

## Ejemplos correctos e incorrectos

| Caso | Correcto | Incorrecto | Motivo |
|---|---|---|---|
| Dominio ADA Dispatch | `fn_prd_mlp_ada_dom_dispatch_status` | `dispatch_status` | Falta ambiente/producto/modelo. |
| Wrapper Grafana | `var_mlp_ada_dispatch.kql` | `ada_dispatch_variable.kql` | No cumple prefijo estándar. |
| Source LAW | `fn_src_mlp_ws_dispatch` | `fn_dispatch_law` | No sigue patrón source. |
| Helper color | `fn_mon_status_to_color` | `fn_prd_mlp_ada_color` | La lógica es cross-producto. |
| Archivo | `fn_prd_mlp_notpii_dom_ingesta_status.kql` | `Ingesta NotPII.kql` | Evita espacios/mayúsculas y alinea con función. |

## Convención de carpetas

```text
refactor_ada_optimized/
  law_functions/<ambiente>/<faena>/<producto>/
  law_functions/<ambiente>/<faena>/sources/
  law_functions/<ambiente>/<faena>/cross_product/helpers/
  grafana_wrappers/<ambiente>/<faena>/<producto>/
```

La carpeta ADA AMG actualmente usa `domain` en singular; para mantener consistencia con otros productos se recomienda validar si debe normalizarse a `domains`.
