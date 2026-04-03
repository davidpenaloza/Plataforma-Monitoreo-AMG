# ADA optimized refactor inventory

## Criterion
- Domain functions query only minimum sources/tables required for that domain.
- Global function only composes domain outputs and does not recompute source-level logic.

## Domain mapping

| Variable | Domain function | Minimal source focus |
|---|---|---|
| var_mlp_ada_dispatch | fn_prd_ada_dom_dispatch_status | DISPATCH PipelineRuns + dispatch lag tables |
| var_mlp_ada_drillit | fn_prd_ada_dom_drillit_status | DRILLIT PipelineRuns + drillit lag tables |
| var_mlp_ada_blockgrade | fn_prd_ada_dom_blockgrade_status | BLKGRDE PipelineRuns + blockgrade lag table |
| var_mlp_ada_plans | fn_prd_ada_dom_plans_status | plans job + plans lag tables |
| var_mlp_ada_pi | fn_prd_ada_dom_pi_status | pisystem job + pisystem lag table |
| var_mlp_ada_meteodata | fn_prd_ada_dom_meteodata_status | meteo jobs + meteodata lag table |
| var_mlp_ada_alarm | fn_prd_ada_dom_alarm_status | job06/job07 + alarm errors count |
| var_mlp_ada_front | fn_prd_ada_dom_front_status | AppServiceConsoleLogs front errors |
| var_mlp_ada_kpi | fn_prd_ada_dom_kpi_status | ADA KPI jobs + KPI error logs |
| var_mlp_ada_global | fn_prd_ada_dom_global_status | composition only (domain colors) |

## LAW files
- `law_functions/fn_prd_ada_helpers.kql`
- `law_functions/fn_prd_ada_dom_*.kql`

## Grafana wrappers
- `grafana_wrappers/var_mlp_ada_*.kql`
