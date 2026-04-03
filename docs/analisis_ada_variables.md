# Propuesta técnica concreta ADA (performance real)

## A) Veredicto técnico (mejor estrategia real)

**Veredicto:** para reducir costo real, la mejor estrategia es **B. Función KQL común en LAW/ADX + variables wrapper livianas en Grafana**.

Motivo técnico:
- En este dashboard, cada variable `query` de Grafana ejecuta su propia consulta al datasource (son variables independientes en `templating.list`, todas tipo `query` con `queryType: Azure Log Analytics` y `refresh: 2`).
- Aunque una variable “base” exista en JSON, las demás variables no reutilizan en memoria el resultado de esa base; si mantienen KQL pesada, vuelven a consultar LAW.
- Por tanto, mover la lógica repetida al lado KQL (función) permite consolidar una sola definición y reducir costo de mantenimiento/drift; y si además se combina con caché del datasource/workspace o materialización externa, el beneficio operativo es mayor que solo reorganizar JSON.

## B) Comparación de estrategias A/B/C

### Estrategia A — Reutilización dentro del JSON model / variables Grafana
**Qué es:** mantener lógica en variables del dashboard, intentando derivar variables específicas desde una variable base.

- **Viabilidad real:** media para orden, **baja para ahorro real** de cómputo si cada variable sigue siendo `query` pesada.
- **Impacto performance esperado:** bajo a medio (depende de si se logra transformar variables específicas en wrappers realmente cortos; si no, casi nulo).
- **Complejidad implementación:** baja.
- **Riesgos:** falsa sensación de optimización; cada variable puede seguir disparando LAW.
- **Compatibilidad panel HTML:** alta si se conservan nombres `${var_mlp_ada_*:raw}`.
- **¿Mantiene `${var_mlp_ada_*:raw}`?:** sí, si no se renombran variables.

### Estrategia B — Función KQL común en LAW + variables wrapper
**Qué es:** crear función KQL común (ej. `fn_ada_health_base`) y que cada variable ejecute wrappers mínimos (`project`/`extend` final).

- **Viabilidad real:** alta.
- **Impacto performance esperado:** medio-alto (eliminas duplicación de texto/lógica en dashboard, facilitas optimización en un punto, reduces riesgo de drift; y habilitas estrategias de caching/materialización fuera de Grafana).
- **Complejidad implementación:** media (requiere crear función en entorno KQL + permisos + despliegue controlado).
- **Riesgos:** coordinación entre repositorio de dashboard y entorno LAW; versionado de función.
- **Compatibilidad panel HTML:** alta manteniendo los mismos nombres de variable.
- **¿Mantiene `${var_mlp_ada_*:raw}`?:** sí, 100% si wrappers preservan salida `color`.

### Estrategia C — Refactor parcial manteniendo variables separadas
**Qué es:** no crear función, pero minimizar duplicación copiando menos bloques y adelantando filtros donde sea posible.

- **Viabilidad real:** alta.
- **Impacto performance esperado:** bajo-medio (mejora algo, pero seguirá habiendo múltiples consultas pesadas).
- **Complejidad implementación:** media-baja.
- **Riesgos:** drift futuro persiste, aunque menor.
- **Compatibilidad panel HTML:** alta.
- **¿Mantiene `${var_mlp_ada_*:raw}`?:** sí.

## C) Bloque común identificado (repetición real)

Las siguientes variables comparten casi toda la misma estructura KQL: 
`var_mlp_ada_global`, `var_mlp_ada_dispatch`, `var_mlp_ada_blockgrade`, `var_mlp_ada_plans`, `var_mlp_ada_pi`, `var_mlp_ada_meteodata`, `var_mlp_ada_alarm`, `var_mlp_ada_front`, `var_mlp_ada_drillit`.

Bloques repetidos observados:
1. `estado_chancadores`.
2. `statusFuentes` (ingestas contenedores + ADF/pipelines, `bins_expected_logs`, `bins_real_data`, joins, acumulados, pivots).
3. `ultimaActualizacionFuentes` (timestamps por tabla, umbrales, NRT merge).
4. `statusKpisAlarms` (estado jobs ADA + detalle KPI sin datos + alertas front/alarmas).
5. `JOIN RESULT` con varios `join kind=fullouter` y `summarize` de alertas por dominio.
6. Construcción `mapa` y luego **diferencia final** por `extract(...)` para dominio específico.

En números: estas variables están entre ~35k y ~42k chars, con ~8 `join` y ~9 `summarize` cada una (excepto `kpi`).

## D) Propuesta concreta de refactor

### D.1 Función base sugerida

**Nombre:** `fn_ada_health_base`

**Inputs sugeridos:**
- `startTime: datetime`
- `endTime: datetime`
- `includeNrt: bool = true`

**Output (1 fila):**
- `DispatchStatus:string`
- `PIStatus:string`
- `DrillitStatus:string`
- `BlockgradeStatus:string`
- `PlansStatus:string`
- `KPIsStatus:string`
- `AlarmasStatus:string`
- `FrontStatus:string`
- `GlobalStatus:string`
- `Mapa:string`

### D.2 Esqueleto real de función KQL

```kusto
.create-or-alter function with (folder = "monitoring/ada", docstring = "Estado consolidado ADA para dashboard resumen")
fn_ada_health_base(startTime:datetime, endTime:datetime, includeNrt:bool=true)
{
    // 1) Bloques comunes actualmente repetidos:
    //    - estado_chancadores
    //    - statusFuentes
    //    - ultimaActualizacionFuentes
    //    - statusKpisAlarms
    //    - join result + summarize final

    let estado_chancadores =
        Logs_MLP_ADA_CL
        | where product_origin == "DISPATCH_CONDICION_OPERACIONAL"
        | sort by TimeGenerated desc
        | take 1
        | extend CH1=tostring(detail["CH-1"]), CH2=tostring(detail["CH-02"])
        | extend en_mantencion = iff(trim(" ",tolower(CH1)) != "efectivo" or trim(" ",tolower(CH2)) != "efectivo", true, false)
        | project en_mantencion;

    // TODO: insertar aquí lógica completa consolidada tomada desde las variables ADA repetidas
    // y terminar en una sola fila de estados.

    datatable(DispatchStatus:string, PIStatus:string, DrillitStatus:string, BlockgradeStatus:string, PlansStatus:string, KPIsStatus:string, AlarmasStatus:string, FrontStatus:string, GlobalStatus:string, Mapa:string)
    ["OK","OK","OK","OK","OK","OK","OK","OK","OK","Dispatch:OK;PI:OK;Drillit:OK;Blockgrade:OK;Plans:OK;KPIs:OK;Alarmas:OK;Front:OK"]
}
```

### D.3 Wrappers de variables (manteniendo `${var_mlp_ada_*:raw}`)

**`var_mlp_ada_dispatch`**
```kusto
fn_ada_health_base(bin($__timeFrom, 1m), bin($__timeTo, 1m), true)
| extend status = DispatchStatus
| extend color = case(status == "ALERT", "#E53935", status in ("Warn","WARN"), "#FFF4CC", "#EAF4EA")
| project color
| take 1
```

**`var_mlp_ada_blockgrade`**
```kusto
fn_ada_health_base(bin($__timeFrom, 1m), bin($__timeTo, 1m), true)
| extend status = BlockgradeStatus
| extend color = case(status == "ALERT", "#E53935", status in ("Warn","WARN"), "#FFF4CC", "#EAF4EA")
| project color
| take 1
```

**`var_mlp_ada_pi`**
```kusto
fn_ada_health_base(bin($__timeFrom, 1m), bin($__timeTo, 1m), true)
| extend status = PIStatus
| extend color = case(status == "ALERT", "#E53935", status in ("Warn","WARN"), "#FFF4CC", "#EAF4EA")
| project color
| take 1
```

**`var_mlp_ada_global`**
```kusto
fn_ada_health_base(bin($__timeFrom, 1m), bin($__timeTo, 1m), true)
| extend status = GlobalStatus
| extend color = case(status == "ALERT", "#E53935", status in ("Warn","WARN"), "#FFF4CC", "#EAF4EA")
| project color
| take 1
```

## E) Ejemplos antes/después

### Antes (ejemplo real observado)
- Cada variable específica repite casi toda la KQL y solo cambia al final:
  - `extract(@"Dispatch:(\w+)", 1, mapa)`
  - `extract(@"Blockgrade:(\w+)", 1, mapa)`
  - `extract(@"PI:(\w+)", 1, mapa)`
  - `extract(@"(ALERT)", 1, mapa)` (global)

### Después (objetivo)
- Todas las variables específicas llaman la misma función base y solo hacen:
  - `extend status = <ColumnaDominio>`
  - `extend color = case(...)`
  - `project color | take 1`

Resultado: mismas salidas para HTML (`color`), menor superficie duplicada y mejor control de performance.

## F) Riesgos de implementación

1. **Permisos y gobierno** para crear/alterar función en LAW.
2. **Paridad funcional** (edge cases de `Dispatch` vs `NRT Dispatch`, horarios especiales, umbrales por tabla).
3. **Dependencias visuales** del panel HTML que espera exactamente `${var_mlp_ada_*:raw}`.
4. **Timing/refresh** de variables (actualmente `refresh: 2`), revisar latencia perceptible.

## G) Plan incremental seguro

1. **Fase 0 (baseline):** congelar snapshot de colores actuales por variable durante una semana.
2. **Fase 1:** crear `fn_ada_health_base` sin conectar variables productivas; validar resultados con query paralela.
3. **Fase 2:** migrar una variable de bajo riesgo (ej. `var_mlp_ada_pi`) a wrapper.
4. **Fase 3:** migrar `dispatch`, `blockgrade`, `plans`, `global`, `front`, `alarm`, `drillit`, `meteodata`.
5. **Fase 4:** retirar KQL duplicada antigua y dejar wrappers finales.
6. **Fase 5:** hardening (alertas de drift, checklist de operación, rollback simple por variable).

## H) Respuestas explícitas solicitadas

1. **¿“Variable base ADA + derivadas” reduce costo real en Grafana?**
   - **No necesariamente.** Si cada derivada sigue siendo una query pesada independiente, solo ordena diseño. El ahorro real aparece cuando las derivadas son wrappers mínimos y la lógica pesada se centraliza fuera del JSON.

2. **¿Dónde conviene centralizar para beneficio real de performance?**
   - **En KQL/LAW (función común) y, si es posible, con estrategia de caching/materialización del lado de datos.** Grafana por sí solo no garantiza reuso de resultado entre variables.

3. **¿Recomendación final con objetivo performance sin romper dashboard actual?**
   - Implementar **Estrategia B**: función `fn_ada_health_base` + wrappers por variable conservando nombres `var_mlp_ada_*` y salida `color`, migración incremental y validación paralela.

## Evidencia mínima del JSON model actual usada para esta propuesta

- Existe un único modelo JSON en el repo: `Plataforma_Monitoreo_AMG.json`.
- Variables ADA existen en `templating.list` (`var_mlp_ada_*`).
- El panel HTML consume `${var_mlp_ada_*:raw}` para chips ADA.
- Se observa referencia comentada a `${var_mlp_ada_ingestas_global:raw}` en el HTML.
