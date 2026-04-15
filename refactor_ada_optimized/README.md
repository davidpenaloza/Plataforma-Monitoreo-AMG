# Plataforma Monitoreo AMG — Refactor ADA (estado actual, documentación detallada)

> Documento de referencia para entender **qué se refactorizó**, **qué problemas resuelve**, **cómo está organizado** el código KQL y **cuáles son los próximos pasos recomendados**.

---

## 1) Objetivo del refactor

El refactor de ADA busca separar responsabilidades para que el monitoreo sea:

- **Más mantenible** (menos lógica duplicada entre dominios y UI).
- **Más confiable** (mejor detección de alertas reales y menor ruido).
- **Más trazable** (fuentes comunes + helpers por producto + dominios claros).
- **Más portable** (estructura simétrica entre funciones completas y body-only).

En términos prácticos, se pasó desde consultas extensas y repetitivas hacia una arquitectura por capas:

1. **sources/** → acceso a datos base (logs, pipeline runs).
2. **helpers/** → reglas compartidas (lags, parsing, agregaciones).
3. **domains/** → estado por producto/dominio (Dispatch, KPI, PI, etc.).
4. **global** → consolidación final para color global.

---

## 2) Estructura del proyecto

```text
refactor_ada_optimized/
├─ law_functions/
│  ├─ sources/
│  ├─ helpers_cross_product/
│  ├─ helpers_ada/
│  └─ domains/
├─ law_functions_body_only/
│  ├─ sources/
│  ├─ helpers_cross_product/
│  ├─ helpers_ada/
│  └─ domains/
└─ grafana_wrappers/
```

### Convención principal
- **`law_functions/`**: archivo KQL completo (`let fn... { ... };`).
- **`law_functions_body_only/`**: mismo contenido lógico, solo body para pegar en LAW UI.
- **`grafana_wrappers/`**: wrappers consumidos por variables/paneles de Grafana.

---

## 3) Catálogo funcional (estado actual)

## 3.1 Sources compartidos

- `fn_src_pipeline_runs_all(startTime:datetime, endTime:datetime)`
- `fn_src_systemlogs_all(startTime:datetime, endTime:datetime)`
- `fn_src_ada_consolelogs(startTime:datetime, endTime:datetime)`

**Qué aportan:** unifican accesos recurrentes a tablas base para que los dominios filtren temprano por su contexto.

## 3.2 Helpers cross-product

- `fn_mon_status_to_color(status:string)`
- `fn_mon_global_from_color_set(colors:dynamic, alert_color:string="#E53935", ok_color:string="#EAF4EA")`

**Qué aportan:** normalizan traducción de estado lógico (`OK/ALERT`) a color y consolidación global.

## 3.3 Helpers ADA

- `fn_prd_ada_alert_from_tables_lag(tables:dynamic, startTime:datetime, endTime:datetime)`
- `fn_prd_ada_alert_from_dispatch_nrt_logs(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_kpi_alert_rows(startTime:datetime, endTime:datetime)`

**Qué aportan:**
- Reglas de lag por tabla con umbrales configurados.
- Detección NRT para Dispatch (logs de `job17`, diferencia temporal SQL vs ejecución).
- Cálculo centralizado de KPI “no esperado” (exclusiones horarias, mantención, umbrales, continuidad de error).

## 3.4 Domain functions

- `fn_prd_ada_dom_dispatch_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_drillit_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_blockgrade_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_pi_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_plans_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_meteodata_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_alarm_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_front_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_kpi_status(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_kpi_detalle_html(startTime:datetime, endTime:datetime)`
- `fn_prd_ada_dom_global_status(startTime:datetime, endTime:datetime)`

**Qué aportan:** cada dominio transforma señales técnicas en un estado único (color/status) alineado con el tablero.

---

## 4) Qué problemas resolvió este refactor

## 4.1 Ruido de alertas por mantención

Problema: durante mantención de chancadores se levantaban alertas que no representaban incidentes reales.

Solución aplicada:
- Detección `en_mantencion` vía `DISPATCH_CONDICION_OPERACIONAL` en `Logs_MLP_ADA_CL`.
- Supresión de alertas en dominios sensibles (KPI y Blockgrade) cuando corresponde.

Impacto:
- Menos falsos positivos.
- Mejor credibilidad del panel para operación.

## 4.2 Dispatch sub-detectado en ventanas cortas

Problema: con validación clásica de lag podían escaparse incidentes de ejecución rápida o degradaciones intermitentes.

Solución aplicada:
- `lag_classic` por tablas + `lag_nrt` por parsing de logs (`job17`) + validación de fallas consecutivas (`consec_fail_job17`).

Impacto:
- Mayor sensibilidad para detectar incidentes reales en Dispatch sin depender de un único indicador.

## 4.3 Duplicación KPI entre estado y detalle

Problema: reglas de KPI “sin datos/no esperado” estaban repetidas y podían divergir entre:
- `fn_prd_ada_dom_kpi_status`
- `fn_prd_ada_dom_kpi_detalle_html`

Solución aplicada:
- Centralización en helper único: `fn_prd_ada_kpi_alert_rows`.
- Ambos dominios consumen la misma salida.

Impacto:
- Coherencia entre color y detalle visual.
- Menor riesgo de drift funcional.

## 4.4 Umbrales heterogéneos y faltantes

Problema: mapa de umbrales de lag insuficiente para nuevas tablas o cadencias distintas.

Solución aplicada:
- Ampliación/ajuste de `mapUmbralAlerta` en helper de lag.

Impacto:
- Alertas más ajustadas al comportamiento real de cada dataset.

---

## 5) Flujo lógico (resumen operativo)

1. **Sources** leen eventos base en la ventana `[startTime, endTime)`.
2. **Helpers ADA** aplican reglas especializadas:
   - lag por tabla,
   - NRT logs dispatch,
   - KPI rows alertables.
3. **Domains** combinan señales por producto y devuelven `status`/`color`.
4. **Global status** consolida todos los dominios y publica color global.
5. **Grafana wrappers** consumen funciones de dominio para variables/chips.

---

## 6) Reglas de diseño aplicadas

- **Filtro temprano** por dominio (`ResourceGroup`, `JobName_s`, `ContainerJobName_s`, etc.).
- **Funciones pequeñas por responsabilidad** (source/helper/domain).
- **Paridad exacta** entre `law_functions/` y `law_functions_body_only/`.
- **Formato de salida estable** para wrappers Grafana (color/status únicos).

---

## 7) Qué revisar cuando algo “se vea raro” en dashboard

Checklist de diagnóstico rápido:

1. ¿El dominio está en `ALERT` por jobs caídos o por lag?
2. ¿Hay mantención activa (`en_mantencion`) que deba suprimir parte del ruido?
3. ¿El helper de KPI está devolviendo filas (`fn_prd_ada_kpi_alert_rows`)?
4. ¿El umbral de la tabla existe y es correcto en `mapUmbralAlerta`?
5. ¿El wrapper de Grafana está leyendo el campo esperado (`color` o `detalle_html`)?
6. ¿La versión en `body_only` está alineada con la versión completa?

---

## 8) Próximos pasos recomendados (roadmap)

## 8.1 Corto plazo (alto impacto / bajo riesgo)

1. **Externalizar configuración de exclusiones KPI por condición horaria**
   - Pasar de `iff` encadenados a configuración declarativa (diccionario/tabla de reglas).
   - Beneficio: mantenimiento rápido sin tocar lógica principal.

2. **Normalizar detección de mantención en helper común**
   - Evitar repetir `en_mantencion` en múltiples dominios.

3. **Suite mínima de validación manual estandarizada**
   - Queries de smoke test por dominio y helper.
   - Checklist de regresión por release.

## 8.2 Mediano plazo

4. **Source helper parametrizable por workspace resource id**
   - Crear helper base + wrappers por dominio (enfoque híbrido).
   - Beneficio: menos hardcode y mejor portabilidad entre entornos.

5. **Tabla de configuración externa para umbrales y exclusiones**
   - Umbrales lag, ventanas horarias KPI, flags de supresión.
   - Beneficio: gobernanza y trazabilidad de cambios sin editar KQL central.

6. **Telemetría de calidad de reglas**
   - Métricas de falsos positivos / tiempo en alerta / dominios más ruidosos.

## 8.3 Largo plazo

7. **Versionado formal de reglas de monitoreo**
   - Cambios con vigencia (`valid_from`, `valid_to`) y rollback sencillo.

8. **Automatización CI para sincronía full/body-only**
   - Verificación automática de paridad funcional entre carpetas espejo.

---

## 9) Guía de actualización segura

Cuando se modifique una función:

1. Cambiar primero en `law_functions/...`.
2. Replicar en `law_functions_body_only/...`.
3. Validar sintaxis (`git diff --check`) y consistencia de nombres/salidas.
4. Revisar consumo en wrappers Grafana.
5. Documentar en este README: objetivo, impacto y riesgos.

---

## 10) Notas de operación

- Los colores esperados de salida son consistentes con el dashboard actual:
  - `ALERT` → rojo (`#E53935`)
  - `OK` → verde claro (`#EAF4EA`)
- Ventanas temporales y timezone se manejan con foco en operación Chile (`America/Santiago`) cuando aplica.
- Mantener funciones de dominio acotadas: evitar mover lógica pesada al wrapper de Grafana.

---

## 11) Estado de documentación

Este README representa el estado actual del refactor ADA en la rama de trabajo, incluyendo:

- arquitectura por capas,
- catálogo funcional vigente,
- problemas ya resueltos,
- criterios operacionales,
- y plan de evolución recomendado.

---

## 12) Extensión SIROSAG MLP (panel Resumen)

Se incorporó la migración del bloque de consulta embebido en JSON a funciones LAW + wrapper para el resumen SIROSAG:

### Sources SIROSAG
- `fn_src_ssag_systemlogs_all(startTime:datetime, endTime:datetime)`
- `fn_src_ssag_consolelogs_all(startTime:datetime, endTime:datetime)`

### Helpers SIROSAG
- `fn_prd_ssag_eval_ejecucion(job_name:string, endTime:datetime, ventana_min:int, max_fallas:int, operador:string)`
- `fn_prd_ssag_eval_desfase(job_name:string, endTime:datetime, ventana_min:int, max_minutos:int)`
- `fn_prd_ssag_eval_desactualizacion(job_name:string, endTime:datetime, ventana_min:int, log_prefix:string, ts_offset:int, ts_length:int, max_minutos:int)`

### Dominio SIROSAG
- `fn_prd_ssag_dom_resumen_status(startTime:datetime, endTime:datetime)`

### Wrapper Grafana
- `grafana_wrappers/var_mlp_sirosag_resumen.kql`

### Resultado funcional
La función de dominio devuelve directamente las columnas de negocio del panel:
- `Ingesta_PI`
- `Ingesta_PDM_Sag`
- `Ingesta_Planes`
- `Salud_ITOT`
- `Procesamiento_PI`
- `Procesamiento_Restricciones`
- `Celdas`
- `Solidos`
- `Front`
- `Alarmas`

Cada columna retorna `Alertar` / `No Alertar`, preservando la semántica del panel original.
