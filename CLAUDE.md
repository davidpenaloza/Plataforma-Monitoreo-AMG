# Plataforma de Monitoreo AMG — Guía Completa de Traspaso

**Versión:** 1.0 — Mayo 2026  
**Dirigido a:** Equipo de Soporte / Equipos de Producto AMG  
**Objetivo:** Transferir el conocimiento completo para operar, mantener e implementar este modelo de monitoreo en nuevos productos.

---

## Índice

1. [¿Qué es esta plataforma y para qué sirve?](#1-qué-es-esta-plataforma-y-para-qué-sirve)
2. [Tecnologías involucradas](#2-tecnologías-involucradas)
3. [Arquitectura del sistema](#3-arquitectura-del-sistema)
4. [Convenciones de nombres](#4-convenciones-de-nombres)
5. [Capa 1 — Sources (Fuentes de datos)](#5-capa-1--sources-fuentes-de-datos)
6. [Capa 2 — Helpers (Lógica de negocio)](#6-capa-2--helpers-lógica-de-negocio)
7. [Capa 3 — Domains (Estado final)](#7-capa-3--domains-estado-final)
8. [Capa 4 — Grafana Wrappers (Entrypoint)](#8-capa-4--grafana-wrappers-entrypoint)
9. [Productos monitoreados](#9-productos-monitoreados)
10. [Estructura de carpetas del repositorio](#10-estructura-de-carpetas-del-repositorio)
11. [Cómo desplegar funciones en Azure Log Analytics](#11-cómo-desplegar-funciones-en-azure-log-analytics)
12. [Cómo integrar con Grafana](#12-cómo-integrar-con-grafana)
13. [Cómo integrar con Power Automate](#13-cómo-integrar-con-power-automate)
14. [Cómo implementar este modelo en un nuevo producto](#14-cómo-implementar-este-modelo-en-un-nuevo-producto)
15. [Patrones de alertas y valores de estado](#15-patrones-de-alertas-y-valores-de-estado)
16. [Ventanas de mantenimiento y exclusiones](#16-ventanas-de-mantenimiento-y-exclusiones)
17. [Validación y calidad del paquete KQL](#17-validación-y-calidad-del-paquete-kql)
18. [Inventario completo de funciones](#18-inventario-completo-de-funciones)
19. [Mapa de dependencias entre funciones](#19-mapa-de-dependencias-entre-funciones)
20. [Operación diaria y troubleshooting](#20-operación-diaria-y-troubleshooting)
21. [Reglas para cambios futuros](#21-reglas-para-cambios-futuros)
22. [Glosario](#22-glosario)

---

## 1. ¿Qué es esta plataforma y para qué sirve?

La **Plataforma de Monitoreo AMG** es un sistema de observabilidad operativa construido en **Azure Log Analytics** y visualizado en **Grafana**. Su propósito es dar visibilidad en tiempo real sobre la salud de los pipelines de datos, jobs de ingesta, modelos de optimización y sistemas frontales de los productos digitales de Antofagasta Minerals Group (AMG).

### Qué monitorea actualmente

| Producto | Descripción | Faena |
|---|---|---|
| **ADA** | Advanced Data Analytics — pipelines de Dispatch, Drillit, Blockgrade, PI System, Plans, Meteodata, KPIs, Alarmas, Front-end, Optimizador Mezcla, Settings | Minera Los Pelambres (MLP) |
| **NOTPII** | Not PII — compliance de privacidad de datos, autoloaders Databricks DEV/UAT y PI System ingesta | MLP |
| **SIROSAG** | Sistema Integrado de Recomendación Operacional SAG — SAG Mill, celdas, sólidos, ingestas upstream | MLP |

### Qué problema resuelve

Sin esta plataforma, el equipo de soporte dependería de:
- Revisar logs manualmente en múltiples workspaces de Azure Log Analytics.
- Alertas reactivas de clientes cuando los datos ya llevan horas desactualizados.
- Queries ad-hoc sin estándares ni reutilización.

Con la plataforma:
- Un **panel Grafana** muestra en verde/rojo el estado de cada pipeline en tiempo real.
- Un flujo de **Power Automate** puede enviar alertas proactivas cuando cualquier dominio entra en estado `ALERT`.
- Toda la lógica de alertas está centralizada en funciones KQL versionadas en Git, auditables y reutilizables.

---

## 2. Tecnologías involucradas

| Tecnología | Rol en la plataforma |
|---|---|
| **Azure Log Analytics (LAW)** | Base de datos de logs; donde se almacenan y ejecutan las funciones KQL |
| **KQL (Kusto Query Language)** | Lenguaje de consultas; toda la lógica de monitoreo está escrita en KQL |
| **Grafana** | Dashboard de visualización; lee datos via Azure Monitor connector |
| **Power Automate** | Automatización de alertas; ejecuta queries KQL y envía notificaciones |
| **Git (este repositorio)** | Control de versiones de todas las funciones KQL |
| **Python** | Scripts de validación estática del paquete KQL |
| **Azure Container Apps** | Plataforma de ejecución de los jobs monitoreados |
| **Databricks** | Plataforma de jobs para NOTPII y Optimizador Mezcla |

### Workspaces de Azure Log Analytics involucrados

| Workspace lógico | Recurso Azure | Producto |
|---|---|---|
| `mlp-prd-law-ada` | `/subscriptions/c68213bf.../mlp-prd-law-ada` | ADA (principal) |
| `ams-prd-law-genshare` | `/subscriptions/c68213bf.../ams-prd-law-genshare` | ADA (Optimizador) |
| `mlp-prd-law-prfci` | `/subscriptions/c68213bf.../mlp-prd-law-prfci` | ADA (Settings) |
| `mlp-prd-law-pisystem` | `/subscriptions/c68213bf.../mlp-prd-law-pisystem` | PI System (ADA, NOTPII, SIROSAG) |
| `mlp-prd-law-ssag` | `/subscriptions/c68213bf.../mlp-prd-law-ssag` | SIROSAG |
| `ams-dev-dataplatform-laws` | `/subscriptions/c68213bf.../ams-dev-dataplatform-laws` | NOTPII (DEV) |
| `ams-uat-dataplatform-laws` | `/subscriptions/c68213bf.../ams-uat-dataplatform-laws` | NOTPII (UAT) |
| `mlp-prd-law-dispatch` | Pipeline logs Dispatch | ADA |
| `mlp-prd-law-drillit` | Pipeline logs Drillit | ADA |
| `mlp-prd-law-blkgrde` | Pipeline logs Blockgrade | ADA |
| `mlp-prd-law-meteo` | Logs Meteodata | ADA |
| `mlp-prd-law-plans` | Logs Plans | ADA / SIROSAG |
| `mlp-prd-law-pdmsagi` | Logs PDM SAG | SIROSAG |

---

## 3. Arquitectura del sistema

El sistema sigue una arquitectura en capas. Cada capa tiene una responsabilidad única:

```
┌─────────────────────────────────────────────────────────┐
│  GRAFANA / POWER AUTOMATE                               │
│  (consume variables y ejecuta queries)                  │
└──────────────────────┬──────────────────────────────────┘
                       │ llama a
┌──────────────────────▼──────────────────────────────────┐
│  CAPA 4: WRAPPERS  (grafana_wrappers/)                  │
│  Función ligera: llama al domain y extrae el color      │
│  Ejemplo: var_mlp_ada_dispatch                          │
└──────────────────────┬──────────────────────────────────┘
                       │ llama a
┌──────────────────────▼──────────────────────────────────┐
│  CAPA 3: DOMAINS  (law_functions/.../domains/)          │
│  Estado final (OK/ALERT): agrega señales de helpers     │
│  Ejemplo: fn_prd_mlp_ada_dom_dispatch_status            │
└──────────────────────┬──────────────────────────────────┘
                       │ llama a
┌──────────────────────▼──────────────────────────────────┐
│  CAPA 2: HELPERS  (law_functions/.../helpers/)          │
│  Lógica de negocio: lag, fallas, umbrales, ventanas     │
│  Ejemplo: fn_prd_mlp_ada_lag_helpers                    │
└──────────────────────┬──────────────────────────────────┘
                       │ llama a
┌──────────────────────▼──────────────────────────────────┐
│  CAPA 1: SOURCES  (law_functions/.../sources/)          │
│  Acceso estandarizado a tablas de Log Analytics         │
│  Ejemplo: fn_src_mlp_ws_ada                             │
└──────────────────────┬──────────────────────────────────┘
                       │ consulta
┌──────────────────────▼──────────────────────────────────┐
│  AZURE LOG ANALYTICS WORKSPACES                         │
│  ContainerAppSystemLogs_CL, AzureDiagnostics, etc.      │
└─────────────────────────────────────────────────────────┘
```

### Por qué esta arquitectura

- **Separación de responsabilidades:** Si cambia el nombre de un workspace, solo hay que editar el source, no los 5 dominios que lo usan.
- **Reutilización:** El mismo source de PI System es usado por ADA, NOTPII y SIROSAG sin duplicar código.
- **Testeabilidad:** Cada capa puede ejecutarse de forma independiente en LAW para depuración.
- **Escalabilidad:** Agregar un nuevo producto solo requiere crear nuevos domains/helpers que reutilicen sources existentes.

---

## 4. Convenciones de nombres

### Patrón general

```
fn_<tipo>_<faena>_<producto>_<componente>_<función>
```

### Tabla completa de prefijos

| Prefijo | Categoría | Dónde vive | Ejemplo |
|---|---|---|---|
| `fn_prd_mlp_<prod>_dom_` | Domain function | `law_functions/prd/mlp/<prod>/domains/` | `fn_prd_mlp_ada_dom_dispatch_status` |
| `fn_prd_mlp_<prod>_` | Helper function | `law_functions/prd/mlp/<prod>/helpers/` | `fn_prd_mlp_ada_lag_helpers` |
| `fn_src_mlp_ws_` | Source genérico por workspace | `law_functions/prd/mlp/sources/` | `fn_src_mlp_ws_ada` |
| `fn_src_mlp_` | Source agregador multi-workspace | `law_functions/prd/mlp/sources/` | `fn_src_mlp_systemlogs_all` |
| `fn_mon_` | Helper cross-product compartido | `law_functions/prd/mlp/cross_product/helpers/` | `fn_mon_status_to_color` |
| `var_mlp_` | Grafana wrapper | `grafana_wrappers/prd/mlp/<prod>/` | `var_mlp_ada_dispatch` |

### Sufijos comunes

| Sufijo | Significado |
|---|---|
| `_status` | Función domain; retorna estado final (OK/ALERT) |
| `_alert` | Función helper; evalúa condición de alerta |
| `_helpers` | Función helper genérica de evaluación |
| `_detail` | Retorna tabla diagnóstica (no solo estado) |
| `_legacyfmt` | Variante con formato visual del sistema legacy |
| `_all` | Source agregador (union de múltiples workspaces) |
| `_global_status` | Domain consolidado de todos los sub-dominios del producto |

### Regla de archivos

Cada función vive en **un archivo `.kql` con el mismo nombre que la función**. Por ejemplo:

```
fn_prd_mlp_ada_dom_dispatch_status.kql
  contiene:
  let fn_prd_mlp_ada_dom_dispatch_status = (startTime:datetime, endTime:datetime) { ... };
```

---

## 5. Capa 1 — Sources (Fuentes de datos)

### Propósito

Los sources son el **único punto de acceso** a los workspaces de Azure Log Analytics. Ninguna función de helper o domain debe hacer llamadas directas a `workspace(...)` — todo pasa por un source.

Esto permite:
1. Cambiar un workspace URI en un solo lugar si migra de suscripción.
2. Agregar filtros globales (time range, environment) sin tocar la lógica de negocio.
3. Auditar qué tablas consume cada producto.

### Tipos de sources

**Source genérico por workspace** — consulta un workspace puntual y acepta el tipo de tabla como parámetro:

```kql
fn_src_mlp_ws_<workspace>(sourceType:string, startTime:datetime, endTime:datetime)
```

**Source agregador product-level** — hace union de múltiples workspaces, proyectando columnas comunes:

```kql
fn_src_mlp_<nombre>_all(startTime:datetime, endTime:datetime)
```

### Ejemplo completo: `fn_src_mlp_ws_ada`

Este source agrupa tres workspaces relacionados con el producto ADA bajo una sola función:

```kql
// Archivo: law_functions/prd/mlp/sources/fn_src_mlp_ws_ada.kql

let fn_src_mlp_ws_ada = (sourceType:string, startTime:datetime, endTime:datetime) {

  union isfuzzy=true
    (
      workspace("/subscriptions/c68213bf-7453-4ba4-9aaa-56b822af4c20/resourceGroups/MLP-PRD-RG-ADA/providers/Microsoft.OperationalInsights/workspaces/mlp-prd-law-ada")
        .table("ContainerAppConsoleLogs_CL")
      | where TimeGenerated between (startTime .. endTime)
      | where sourceType == "ContainerAppConsoleLogs_CL"
      | extend source_table = "ContainerAppConsoleLogs_CL"
    ),
    (
      workspace("/subscriptions/c68213bf-7453-4ba4-9aaa-56b822af4c20/resourceGroups/MLP-PRD-RG-ADA/providers/Microsoft.OperationalInsights/workspaces/mlp-prd-law-ada")
        .table("ContainerAppSystemLogs_CL")
      | where TimeGenerated between (startTime .. endTime)
      | where sourceType == "ContainerAppSystemLogs_CL"
      | extend source_table = "ContainerAppSystemLogs_CL"
    ),
    (
      workspace("/subscriptions/c68213bf-7453-4ba4-9aaa-56b822af4c20/resourceGroups/AMS-PRD-RG-GENSHARE/providers/Microsoft.OperationalInsights/workspaces/ams-prd-law-genshare")
        .table("ContainerAppSystemLogs_CL")
      | where TimeGenerated between (startTime .. endTime)
      | where sourceType == "ContainerAppSystemLogs_CL"
      | extend source_table = "ContainerAppSystemLogs_CL"
    ),
    (
      workspace("/subscriptions/c68213bf-7453-4ba4-9aaa-56b822af4c20/resourceGroups/MLP-PRD-RG-ADA/providers/Microsoft.OperationalInsights/workspaces/mlp-prd-law-ada")
        .table("AppServiceConsoleLogs")
      | where TimeGenerated between (startTime .. endTime)
      | where sourceType == "AppServiceConsoleLogs"
      | extend source_table = "AppServiceConsoleLogs"
    )
};
```

**Cómo se usa:**
```kql
// Obtener logs de sistema de ADA en las últimas 3 horas
fn_src_mlp_ws_ada("ContainerAppSystemLogs_CL", ago(3h), now())
| where JobName_s == "mlp-prd-caj-ada-job17"
| take 100
```

### Ejemplo: source con enum de ambiente (NOTPII Databricks)

Cuando un producto tiene múltiples ambientes (DEV/UAT), se usa un parámetro `env` controlado en lugar de exponer el URI directamente:

```kql
// fn_src_mlp_ws_notpii_databricksjobs(env: "dev" | "uat" | "all", startTime, endTime)
// Uso:
fn_src_mlp_ws_notpii_databricksjobs("dev", ago(24h), now())
| where JobName_s == "autoloader-job01"
```

### Catálogo de sources activos

| Source | Workspace | Tabla principal | Criticidad |
|---|---|---|---|
| `fn_src_mlp_ws_ada` | `mlp-prd-law-ada` + genshare + prfci | `ContainerAppSystemLogs_CL`, `ContainerAppConsoleLogs_CL` | Alta |
| `fn_src_mlp_ws_pisystem` | `mlp-prd-law-pisystem` | `ContainerAppSystemLogs_CL`, `ContainerAppConsoleLogs_CL` | Alta |
| `fn_src_mlp_ws_ssag` | `mlp-prd-law-ssag` | `ContainerAppSystemLogs_CL` | Media |
| `fn_src_mlp_ws_dispatch` | `mlp-prd-law-dispatch` | `AzureDiagnostics` | Media |
| `fn_src_mlp_ws_drillit` | `mlp-prd-law-drillit` | `AzureDiagnostics` | Media |
| `fn_src_mlp_ws_blkgrde` | `mlp-prd-law-blkgrde` | `AzureDiagnostics` | Media |
| `fn_src_mlp_ws_meteo` | `mlp-prd-law-meteo` | `ContainerAppSystemLogs_CL` | Media |
| `fn_src_mlp_ws_plans` | `mlp-prd-law-plans` | `ContainerAppSystemLogs_CL` | Alta |
| `fn_src_mlp_ws_pdmsagi` | `mlp-prd-law-pdmsagi` | `ContainerAppSystemLogs_CL` | Media |
| `fn_src_mlp_ws_notpii_databricksjobs` | dev-dataplatform + uat-dataplatform | `DatabricksJobs` | Alta |
| `fn_src_mlp_ws_genshare` | `ams-prd-law-genshare` | `ContainerAppSystemLogs_CL` | Alta |
| `fn_src_mlp_ws_prfci` | `mlp-prd-law-prfci` | `ContainerAppSystemLogs_CL` | Alta |
| `fn_src_mlp_ws_dataplatform` | `ams-dev-dataplatform-laws` | `Logs_MLP_ADA_CL` | Alta |
| `fn_src_mlp_pipeline_runs_all` | dispatch + drillit + blkgrde | `AzureDiagnostics` | Alta |
| `fn_src_mlp_systemlogs_all` | ada + meteo + pisystem + plans | `ContainerAppSystemLogs_CL` | Alta |
| `fn_src_mlp_ssag_systemlogs_all` | ssag + plans + pdmsagi + pisystem | `ContainerAppSystemLogs_CL` | Alta |

---

## 6. Capa 2 — Helpers (Lógica de negocio)

Los helpers contienen la **lógica de evaluación**: calculan si hay un problema o no, y bajo qué condiciones. No tienen opinión sobre el estado final del dominio — eso lo decide el domain.

### Patrón de retorno

La mayoría de los helpers retorna un escalar `"ALERT"` o `"OK"`. Los más complejos retornan una tabla de diagnóstico.

### Helper 1: Detección de lag de tablas (`fn_prd_mlp_ada_lag_helpers`)

**Propósito:** Detecta si alguna tabla de datos lleva demasiado tiempo sin actualizarse, según umbrales configurados por tabla.

**Cómo funciona:**
1. Lee los logs del job02 de ADA, que cada cierto tiempo registra en JSON el último timestamp de cada tabla.
2. Calcula la diferencia en minutos entre la fecha del log y el último timestamp registrado.
3. Compara contra un umbral configurado (puede ser por tabla o el default de 60 min).
4. Retorna `ALERT` si alguna tabla excede su umbral.

```kql
// Archivo: law_functions/prd/mlp/ada/helpers/fn_prd_mlp_ada_lag_helpers.kql

let fn_prd_mlp_ada_lag_helpers = (tables:dynamic, startTime:datetime, endTime:datetime) {
  let lag_thresholds = fn_prd_mlp_ada_lag_thresholds();
  let default_umbral = toscalar(
      lag_thresholds | where tabla == "__DEFAULT__" | project umbral_minutos | take 1
  );
  let t = fn_src_mlp_ws_ada("ContainerAppConsoleLogs_CL", startTime, endTime)
      | where ContainerGroupName_s startswith "mlp-prd-caj-ada-job02"
      | where Log_s startswith '{"fecha'
      | project parsed = parse_json(Log_s)
      | project mensaje=tostring(parsed.mensaje), fecha_log_UTC=todatetime(parsed.fecha_log_UTC)
      | where mensaje startswith "timestamp_"
      | extend tabla = replace_string(replace_string(
            substring(mensaje, 10, indexof(mensaje, ": ") - 10),
            "last_record_", ""), "last_reg_", "")
      | where tabla in (tables)
      | extend ultimo_timestamp = todatetime(substring(mensaje, indexof(mensaje, ": ") + 2, 19))
      | extend ultimo_timestamp = datetime_local_to_utc(ultimo_timestamp, "America/Santiago")
      | extend diff_minutos = round(datetime_diff("second", fecha_log_UTC, ultimo_timestamp) / 60.0, 1)
      | join kind=leftouter (lag_thresholds | where tabla != "__DEFAULT__") on tabla
      | extend umbral = coalesce(umbral_minutos, default_umbral)
      | extend alert = iff(isempty(diff_minutos) or diff_minutos > umbral, 1, 0)
      | summarize has_alert=max(alert);
  iff(toscalar(t) == 1, "ALERT", "OK")
};
```

**Ejemplo de uso:**
```kql
// Verificar lag de tablas de Dispatch en las últimas 2 horas
fn_prd_mlp_ada_lag_helpers(
    dynamic(["StdShiftLoads2","StdShiftDumps","dispatch_shiftstate"]),
    ago(2h),
    now()
)
// Retorna: "ALERT" o "OK"
```

### Helper 2: Evaluación de ejecución de jobs (`fn_prd_mlp_ssag_eval_ejecucion`)

**Propósito:** Cuenta cuántas fallas tuvo un job en una ventana de tiempo y compara contra un umbral máximo permitido.

```kql
// Archivo: law_functions/prd/mlp/sirosag/helpers/fn_prd_mlp_ssag_eval_ejecucion.kql

let fn_prd_mlp_ssag_eval_ejecucion = (job_name:string, endTime:datetime, ventana_min:int, max_fallas:int, operador:string) {
    let startTime = endTime - totimespan(ventana_min * 60s);
    let fallas = toscalar(
        fn_src_mlp_ssag_systemlogs_all(startTime, endTime)
        | where JobName_s == job_name
        | where Type_s == 'Warning'
              and Reason_s in ('FailedCreate', 'DeadlineExceeded', 'BackoffLimitExceeded')
        | summarize Fallas = count()
        | project Fallas
    );
    print Status = case(
        operador == "lte", iff(fallas <= max_fallas, 'OK', 'NOOK'),
        operador == "lt",  iff(fallas <  max_fallas, 'OK', 'NOOK'),
        operador == "eq",  iff(fallas == max_fallas, 'OK', 'NOOK'),
        'NOOK')
};
```

**Parámetros explicados:**
- `job_name`: nombre exacto del container job (ej: `mlp-prd-caj-ssag-job01`)
- `endTime`: tiempo de referencia (generalmente `now()`)
- `ventana_min`: ventana de observación en minutos (ej: `60` = última hora)
- `max_fallas`: límite de fallas permitidas
- `operador`: `"lte"` (≤), `"lt"` (<), `"eq"` (==)

**Ejemplo de uso:**
```kql
// Job01 SIROSAG: no puede tener más de 5 fallas en la última hora
fn_prd_mlp_ssag_eval_ejecucion('mlp-prd-caj-ssag-job01', now(), 60, 5, 'lte')
// Retorna tabla con columna: Status = "OK" | "NOOK"
```

### Helper 3: Detección de KPIs con error (`fn_prd_mlp_ada_kpi_alert_rows`)

**Propósito:** Detecta qué funciones KPI están fallando y aplica reglas de exclusión por horario laboral, mantenimiento programado y ventanas especiales.

**Lógica de exclusiones (ventanas donde no se alerta):**
- `COND_2_0700_1000` — Entre 07:00 y 10:00 (Hora Chile): proceso de apertura de turno
- `COND_3_1900_2100` — Entre 19:00 y 21:00: cierre de turno
- `COND_4_MIE1900_VIE2100` — Miércoles 19:00 a Viernes 21:00: mantenimiento semanal
- `COND_5_FUERA_HORARIO` — Fuera de horario laboral (fines de semana, antes de 9am, después 19pm)
- `MANTENCION` — Bandera de mantenimiento activa en catálogo
- `EXCLUSION_FIJA` — KPIs específicos excluidos permanentemente

```kql
// Ejemplo de invocación (retorna tabla de KPIs con error activo):
fn_prd_mlp_ada_kpi_alert_rows(ago(4h), now())
// Resultado ejemplo:
// KPINoEsperado          | minutos_desde_error
// ---------------------- | -------------------
// calcula_blend          | 47.3
// genera_reporte_turno   | 123.8
```

### Helper 4: Alertas NRT desde logs de Dispatch (`fn_prd_mlp_ada_alert_from_dispatch_nrt_logs`)

**Propósito:** Detecta lag near-real-time en el job17 de Dispatch evaluando si el último log de éxito tiene más de 6 minutos de antigüedad.

### Helper 5: Evaluación de SLA en autoloaders NOTPII (`fn_prd_mlp_notpii_autoloader_alert`)

**Propósito:** Evalúa si los jobs de Databricks autoloader están dentro de su SLA. Soporta tres tipos de jobs:
- `CONTINUO`: debe estar en estado `Running`
- `BATCH_CORTO`: debe haber completado `Succeeded` dentro de la ventana SLA
- `BATCH_LARGO`: basta con que esté `Running` o `Succeeded`

```kql
// Ejemplo de configuración de jobs:
let jobs_dev = dynamic([
    {"jobID": "123", "nombre": "autoloader-continuous", "tipo": "CONTINUO", "sla_min": 0},
    {"jobID": "124", "nombre": "autoloader-batch-short", "tipo": "BATCH_CORTO", "sla_min": 30},
    {"jobID": "125", "nombre": "autoloader-batch-long",  "tipo": "BATCH_LARGO", "sla_min": 240}
]);

fn_prd_mlp_notpii_autoloader_alert(jobs_dev, ago(6h), now(), 1h)
// Retorna: EstadoGlobal = "Alertar" | "No Alertar"
```

---

## 7. Capa 3 — Domains (Estado final)

Los domains son el corazón de la plataforma. **Cada domain responde una sola pregunta:** "¿Está bien el pipeline X?"

### Contrato de retorno

Un domain siempre retorna una sola fila con una o más columnas de estado:

```kql
// Ejemplo retorno domain simple:
print status = "ALERT"     -- o "OK"

// Ejemplo retorno domain global (ADA):
// Dispatch | Drillit | Blockgrade | PI | Plans | Meteodata | KPI | Alarmas | Front | Optimizador Mezcla | Settings
// ALERT    | OK      | OK         | OK | ALERT | OK        | OK  | OK      | OK    | OK                 | OK
```

### Ejemplo completo: Domain Dispatch ADA

Este domain agrega **tres señales independientes** sobre el pipeline de Dispatch:

```kql
// Archivo: law_functions/prd/mlp/ada/domains/fn_prd_mlp_ada_dom_dispatch_status.kql

let fn_prd_mlp_ada_dom_dispatch_status = (startTime:datetime, endTime:datetime) {
  let dispatch_tables = dynamic([
    "StdShiftLoads2","stdshiftdumpsnodicavel","StdShiftDumps","StdShiftLoads","tiempos_mlp",
    "StdShiftState","ShiftInfo","SHIFTShiftLoad","StdGrade",
    "dispatch_shiftdumps","dispatch_shiftloads","dispatch_shiftloads2","dispatch_shiftstate","dispatch_tiempos"
  ]);

  // Señal 1: ¿Alguna tabla de Dispatch lleva demasiado tiempo sin actualizar?
  let lag_classic = fn_prd_mlp_ada_lag_helpers(dispatch_tables, startTime, endTime);

  // Señal 2: ¿Hay lag NRT en los logs del job17?
  let lag_nrt = fn_prd_mlp_ada_alert_from_dispatch_nrt_logs(dispatch_tables, startTime, endTime);

  // Señal 3: ¿Fallaron 2 ejecuciones consecutivas del job17 en los últimos 40 minutos?
  let consec_fail_job17 = toscalar(
    range TimeGeneratedBin_Chile from bin(endTime - 40m, 10m) to bin(endTime - 10m, 10m) step 10m
    | join kind=leftouter (
      fn_src_mlp_ws_ada("ContainerAppSystemLogs_CL", endTime - 45m, endTime)
      | where JobName_s == "mlp-prd-caj-ada-job17"
      | where Log_s contains "has successfully completed"
      | extend TimeGeneratedBin_Chile = bin(TimeGenerated - 7m, 10m)
      | summarize valorReal = count() by TimeGeneratedBin_Chile
    ) on TimeGeneratedBin_Chile
    | project-away TimeGeneratedBin_Chile1
    | extend esperado = 1, valorReal = coalesce(valorReal, 0)
    | extend status = iff(valorReal == 0 and esperado == 1, "a", "n")
    | order by TimeGeneratedBin_Chile desc
    | serialize
    | extend is_fail = iff(status == "a", 1, 0)
    | extend next_fail = next(is_fail, 1), rn = row_number()
    | where rn == 1
    | project alerta = is_fail == 1 and next_fail == 1
  );

  // Estado final: ALERT si cualquiera de las 3 señales está en ALERT
  let status = iff(lag_classic == "ALERT" or lag_nrt == "ALERT" or consec_fail_job17, "ALERT", "OK");
  print status = status
};
```

### Ejemplo: Domain consolidado SIROSAG

SIROSAG evalúa 13 jobs usando tres tipos de señales (fallas, desfase, desactualización) y los agrupa en 8 dimensiones de negocio:

```kql
// Uso:
fn_prd_mlp_ssag_dom_resumen_status(ago(4h), now())

// Retorna columnas:
// Ingesta_PI | Ingesta_PDM_Sag | Ingesta_Planes | Salud_ITOT | Procesamiento_PI |
// Procesamiento_Restricciones | Celdas | Solidos | Front | Alarmas
// Todos con valores "Alertar" o "No Alertar"
```

### Ejemplo: Domain global ADA

El domain global consolida los 11 dominios de ADA en una sola fila:

```kql
// Uso:
fn_prd_mlp_ada_dom_global_status(ago(3h), now())

// Retorna:
// Dispatch | Drillit | Blockgrade | PI | Plans | Meteodata | KPI | Alarmas | Front | Optimizador Mezcla | Settings
// ALERT    | OK      | OK         | OK | OK    | OK        | OK  | OK      | OK    | OK                 | OK
```

---

## 8. Capa 4 — Grafana Wrappers (Entrypoint)

Los wrappers son funciones **extremadamente simples** que actúan como interfaz entre Grafana y los domains. Grafana no ejecuta domains directamente — ejecuta wrappers.

### Por qué wrappers

Grafana necesita variables con formato específico (generalmente un valor escalar de color o estado). Los wrappers normalizan el output del domain para que Grafana lo pueda interpretar directamente.

### Ejemplo de wrapper

```kql
// Archivo: grafana_wrappers/prd/mlp/ada/var_mlp_ada_dispatch.kql
// Variable Grafana: var_mlp_ada_dispatch

fn_prd_mlp_ada_dom_dispatch_status(bin($__timeFrom, 1m), bin($__timeTo, 1m))
| project color
| take 1
```

Grafana inyecta `$__timeFrom` y `$__timeTo` desde el time picker del dashboard.

### Wrapper con color explícito

Para paneles de tipo "Stat" con colores visuales, el wrapper puede transformar el estado en un color HEX:

```kql
// Ejemplo extendido de wrapper con color:
fn_prd_mlp_ada_dom_dispatch_status(bin($__timeFrom, 1m), bin($__timeTo, 1m))
| extend color = case(
    status == "ALERT", "#E53935",   // rojo
    status == "WARNING", "#FFF4CC", // amarillo
    "#EAF4EA"                        // verde
)
| project color
| take 1
```

### Lista de wrappers activos

**ADA (12 wrappers):**
| Wrapper | Domain que llama |
|---|---|
| `var_mlp_ada_global` | `fn_prd_mlp_ada_dom_global_status` |
| `var_mlp_ada_dispatch` | `fn_prd_mlp_ada_dom_dispatch_status` |
| `var_mlp_ada_drillit` | `fn_prd_mlp_ada_dom_drillit_status` |
| `var_mlp_ada_pi` | `fn_prd_mlp_ada_dom_pi_status` |
| `var_mlp_ada_plans` | `fn_prd_mlp_ada_dom_plans_status` |
| `var_mlp_ada_blockgrade` | `fn_prd_mlp_ada_dom_blockgrade_status` |
| `var_mlp_ada_meteodata` | `fn_prd_mlp_ada_dom_meteodata_status` |
| `var_mlp_ada_kpi` | `fn_prd_mlp_ada_dom_kpi_status` |
| `var_mlp_ada_alarm` | `fn_prd_mlp_ada_dom_alarm_status` |
| `var_mlp_ada_front` | `fn_prd_mlp_ada_dom_front_status` |
| `var_mlp_ada_jobs_detail` | `fn_prd_mlp_ada_jobs_status_detail` |
| `var_mlp_ada_jobs_detail_legacyfmt` | `fn_prd_mlp_ada_jobs_status_detail` (formato legacy) |

**NOTPII (4 wrappers):**
| Wrapper | Domain que llama |
|---|---|
| `var_mlp_notpii_autoloader_dev` | `fn_prd_mlp_notpii_dom_autoloader_dev_status` |
| `var_mlp_notpii_autoloader_uat` | `fn_prd_mlp_notpii_dom_autoloader_uat_status` |
| `var_mlp_notpii_ingesta` | `fn_prd_mlp_notpii_dom_ingesta_status` |
| `var_mlp_notpii_difusion_global` | `fn_prd_mlp_notpii_dom_global_status` |

**SIROSAG (1 wrapper):**
| Wrapper | Domain que llama |
|---|---|
| `var_mlp_sirosag_resumen` | `fn_prd_mlp_ssag_dom_resumen_status` |

---

## 9. Productos monitoreados

### 9.1 ADA — Advanced Data Analytics

**Qué hace ADA:** Sistema de analítica de datos mineros que integra información de Dispatch (movimiento de camiones), Drillit (perforación), Blockgrade (modelo de bloques), PI System (sensores industriales), Plans (planes de producción), Meteodata (meteorología), KPIs de negocio, alarmas y optimizador de mezcla.

**Jobs clave:**
| Job | Función |
|---|---|
| `mlp-prd-caj-ada-job01` a `job06` | Procesamiento ETL de datos (logs en `ContainerAppConsoleLogs_CL`) |
| `mlp-prd-caj-ada-job02` | Tracking de timestamps de tablas (base para detección de lag) |
| `mlp-prd-caj-ada-job17` | Pipeline NRT de Dispatch (se ejecuta cada ~10 min) |
| `mlp-prd-caj-genshare-job01` | Optimizador Mezcla en Databricks |
| `mlp-prd-caj-prfci-job01/02` | Settings (validación de configuración) |

**Dominios y señales:**

| Dominio | Señales monitoreadas | Umbral de alerta |
|---|---|---|
| Dispatch | Lag tablas, NRT job17, fallas consecutivas job17 | Lag > umbral por tabla; ≥2 fallas consecutivas en 40 min |
| Drillit | Pipeline runs fallidos | Runs fallidos en ventana |
| Blockgrade | Pipeline runs fallidos | Runs fallidos en ventana |
| PI System | Expected vs real (job01/02) | < 85% de ejecuciones esperadas |
| Plans | Expected vs real | < 85% de ejecuciones esperadas |
| Meteodata | Expected vs real (job01: min 0/15/30/45; job02: min 1/16/31/46) | < 85% |
| KPI | Errores en funciones KPI (con exclusiones horarias) | Cualquier error persistente fuera de ventana de exclusión |
| Alarmas | Incidentes largos, errores de conexión a storage | Cualquier incidente activo |
| Front | Errores de app, errores de token | Cualquier error en ventana |
| Optimizador | Ejecución job01 genshare (Databricks) | Job no ejecutado en ventana |
| Settings | Expected vs real jobs PRFCI | < 85% |

### 9.2 NOTPII — Data Privacy Compliance

**Qué hace NOTPII:** Asegura que los datos de PI System se ingresten cumpliendo las reglas de privacidad. Corre en ambientes DEV y UAT de Databricks.

**Jobs clave:**
| Job | Ambiente | Tipo | SLA |
|---|---|---|---|
| autoloader-job-continuous | DEV/UAT | CONTINUO | Siempre Running |
| autoloader-batch-short | DEV/UAT | BATCH_CORTO | < 30 min |
| autoloader-batch-long | DEV/UAT | BATCH_LARGO | < 240 min |
| job04 PI System | — | Ingesta | Expected vs real |

**Dominios:**
- `fn_prd_mlp_notpii_dom_autoloader_dev_status` — estado DEV
- `fn_prd_mlp_notpii_dom_autoloader_uat_status` — estado UAT
- `fn_prd_mlp_notpii_dom_ingesta_status` — estado ingesta PI job04
- `fn_prd_mlp_notpii_dom_global_status` — consolidado

### 9.3 SIROSAG — SAG Mill Operations

**Qué hace SIROSAG:** Sistema de recomendación operacional para el molino SAG. Recibe datos del sistema ITOT, PDM, PI y Plans, genera recomendaciones de operación de celdas y sólidos.

**Jobs clave (13 jobs):**
| Jobs | Función |
|---|---|
| job01–03 | ITOT (sistema operativo SAG), procesamiento PI, restricciones |
| job04–11 | Procesamiento de celdas y sólidos (4 celdas × 2 = 8 jobs) |
| job12 | Front-end de recomendaciones |
| job13 | Sistema de alarmas SAG |

**Tres tipos de señales por job:**
1. **Ejecución** (`eval_ejecucion`): ¿Cuántas fallas tuvo en N minutos?
2. **Desfase** (`eval_desfase`): ¿Cuánto tiempo tardó más de lo esperado?
3. **Desactualización** (`eval_desactualizacion`): ¿Los datos que procesa son frescos?

---

## 10. Estructura de carpetas del repositorio

```
Plataforma-Monitoreo-AMG/
│
├── CLAUDE.md                              ← Este documento
├── Plataforma_Monitoreo_AMG.json          ← Definición del dashboard Grafana
│
└── refactor_ada_optimized/                ← Paquete KQL principal (fuente de verdad)
    │
    ├── README.md                          ← Guía funcional del paquete
    ├── INVENTORY.md                       ← Inventario de funciones activas
    ├── KQL_SOURCES_TECH_AUDIT_2026-04-28.md
    │
    ├── law_functions/prd/mlp/             ← Funciones completas (con declaración)
    │   ├── ada/
    │   │   ├── domains/                   ← 12 domain functions ADA
    │   │   └── helpers/                   ← 4 helper functions ADA
    │   ├── ada_amg/                       ← Variante AMG de ADA (paralela)
    │   │   ├── domain/
    │   │   └── ...
    │   ├── notpii/
    │   │   ├── domains/                   ← 4 domain functions NOTPII
    │   │   └── helpers/                   ← 2 helper functions NOTPII
    │   ├── sirosag/
    │   │   ├── domains/                   ← 1 domain function SIROSAG
    │   │   └── helpers/                   ← 3 helper functions SIROSAG
    │   ├── cross_product/helpers/         ← fn_mon_status_to_color
    │   └── sources/                       ← 14 source functions
    │
    ├── law_functions_body_only/prd/mlp/   ← Espejo (solo body, sin declaración)
    │   └── ...                            ← Mismo layout que law_functions/
    │
    ├── grafana_wrappers/prd/mlp/          ← Wrappers para Grafana
    │   ├── ada/                           ← 12 wrappers ADA
    │   ├── ada_amg/                       ← Wrappers variante AMG
    │   ├── notpii/                        ← 4 wrappers NOTPII
    │   └── sirosag/                       ← 1 wrapper SIROSAG
    │
    ├── power_automate_queries/prd/mlp/    ← Queries para Power Automate
    │   ├── ada/
    │   │   ├── resumen_estado.kql         ← Query de estado global ADA
    │   │   └── legacy_parity_check.kql   ← Validación paridad vs legacy
    │   ├── notpii/
    │   └── sirosag/
    │
    ├── docs/                              ← Documentación técnica detallada
    │   ├── source_catalog.md
    │   ├── source_dependency_map.md
    │   ├── ada_legacy_equivalencia.md
    │   ├── dispatch_nrt_alignment_validation.md
    │   ├── observability_of_observability.md
    │   └── pattern_reference_error_troubleshooting.md
    │
    ├── validate_kql_references.py         ← Validación estática del paquete
    ├── check_conflict_markers.py          ← Detección de conflictos de merge
    └── analyze_source_catalog.py          ← Análisis del catálogo de sources
```

### Diferencia entre `law_functions/` y `law_functions_body_only/`

| Carpeta | Contiene | Para qué sirve |
|---|---|---|
| `law_functions/prd/mlp/` | Declaración completa: `let fn_X = (...) { ... };` | Deploy via Azure CLI / ARM template |
| `law_functions_body_only/prd/mlp/` | Solo el body: `(...) { ... }` | Pegar directamente en la UI de Log Analytics |

---

## 11. Cómo desplegar funciones en Azure Log Analytics

### Opción A: Desde la UI de Azure Log Analytics (manual)

1. Abrir el workspace de Log Analytics en Azure Portal.
2. Ir a **Logs** → **Functions** → **+ New function**.
3. Copiar el contenido del archivo `law_functions_body_only/.../fn_nombre.kql` (solo el body).
4. Configurar:
   - **Function name:** nombre exacto de la función (ej: `fn_prd_mlp_ada_dom_dispatch_status`)
   - **Parameters:** los parámetros del archivo (ej: `startTime:datetime, endTime:datetime`)
   - **Category (Folder):** categoría lógica (ej: `ada/domains`)
5. Guardar. La función queda disponible en ese workspace.

> **Importante:** Las funciones deben desplegarse en el workspace desde el que las consultará Grafana. Si el workspace de Grafana es `mlp-prd-law-ada`, los domains y wrappers van en ese workspace. Los sources que referencian otros workspaces se despliegan en el mismo workspace de ejecución pero usan la función `workspace(...)` para cruzar.

### Opción B: Deploy via Azure CLI (recomendado para actualizaciones masivas)

```bash
# Ejemplo de deploy de una función vía REST API de Log Analytics
az monitor log-analytics workspace saved-search create \
  --resource-group MLP-PRD-RG-ADA \
  --workspace-name mlp-prd-law-ada \
  --name "fn_prd_mlp_ada_dom_dispatch_status" \
  --display-name "fn_prd_mlp_ada_dom_dispatch_status" \
  --category "ada/domains" \
  --saved-query "$(cat law_functions_body_only/prd/mlp/ada/domains/fn_prd_mlp_ada_dom_dispatch_status.kql)"
```

### Orden de deploy

Las funciones deben desplegarse **de abajo hacia arriba** (sources antes que helpers, helpers antes que domains, domains antes que wrappers):

```
1. Sources         (fn_src_mlp_*)
2. Cross-product   (fn_mon_*)
3. Helpers         (fn_prd_mlp_*_<helper>)
4. Domains         (fn_prd_mlp_*_dom_*)
5. Wrappers        (var_mlp_*)
```

Si un domain se despliega antes que su helper, fallará al ejecutarse.

### Verificar que una función fue desplegada correctamente

```kql
// Ejecutar en Log Analytics directamente:
fn_prd_mlp_ada_dom_dispatch_status(ago(1h), now())
// Si retorna una fila con columna "status", el deploy fue exitoso.
```

---

## 12. Cómo integrar con Grafana

### Prerrequisitos

1. Un workspace de Grafana con el **plugin Azure Monitor** configurado y autenticado.
2. Una data source de tipo **Azure Log Analytics** apuntando al workspace donde están las funciones.

### Paso 1: Crear variables de Grafana

Cada wrapper se convierte en una **variable de Grafana** de tipo "Query":

1. Ir al dashboard → **Settings** → **Variables** → **+ New variable**.
2. Tipo: **Query**.
3. Data source: tu Azure Log Analytics data source.
4. Query: contenido del archivo wrapper, por ejemplo:

```kql
fn_prd_mlp_ada_dom_dispatch_status(bin($__timeFrom, 1m), bin($__timeTo, 1m))
| project color
| take 1
```

5. Refresh: **On time range change**.
6. Nombre de la variable: `var_mlp_ada_dispatch` (igual que el nombre del archivo).

### Paso 2: Usar la variable en paneles

En un panel de tipo **Stat** o **Text**:
- Referenciar la variable como `$var_mlp_ada_dispatch`.
- Configurar el mapping de color: si el valor es `#E53935` → rojo; `#EAF4EA` → verde.

### Paso 3: Panel de diagnóstico tabular

Para ver el detalle por job, usar el wrapper `var_mlp_ada_jobs_detail`:

```kql
fn_prd_mlp_ada_jobs_status_detail(bin($__timeFrom, 1m), bin($__timeTo, 1m))
```

Esto retorna una tabla con columnas: `job`, `status`, `real`, `esperado`, `porcentaje`.

### Variables de tiempo en Grafana

| Variable Grafana | Equivalente KQL |
|---|---|
| `$__timeFrom` | `startTime` (inicio del rango seleccionado) |
| `$__timeTo` | `endTime` (fin del rango seleccionado) |
| `bin($__timeFrom, 1m)` | Truncar a minuto para consistencia |

---

## 13. Cómo integrar con Power Automate

Power Automate puede ejecutar queries de Log Analytics periódicamente y enviar alertas cuando el estado es `ALERT`.

### Query de estado global ADA

```kql
// Archivo: power_automate_queries/prd/mlp/ada/resumen_estado.kql

let lookback = 3h;
fn_prd_mlp_ada_dom_global_status(ago(lookback), now())
| extend rows = pack_array(
    pack("orden", 1, "producto", "Dispatch",          "estado", Dispatch),
    pack("orden", 2, "producto", "Drillit",            "estado", Drillit),
    pack("orden", 3, "producto", "Blockgrade",         "estado", Blockgrade),
    pack("orden", 4, "producto", "PI",                 "estado", PI),
    pack("orden", 5, "producto", "Plans",              "estado", Plans),
    pack("orden", 6, "producto", "Meteodata",          "estado", Meteodata),
    pack("orden", 7, "producto", "KPI",                "estado", KPI),
    pack("orden", 8, "producto", "Alarmas",            "estado", Alarmas),
    pack("orden", 9, "producto", "Front",              "estado", Front),
    pack("orden", 10, "producto", "Optimizador Mezcla","estado", ['Optimizador Mezcla']),
    pack("orden", 11, "producto", "Settings",          "estado", Settings)
)
| mv-expand row = rows
| project
    orden   = toint(row.orden),
    producto = tostring(row.producto),
    estado   = tostring(row.estado)
| extend color = case(
    estado == "ALERT",   "#E53935",
    estado == "WARNING", "#FFF4CC",
                         "#EAF4EA"
)
| extend icono = case(
    estado == "ALERT",   "🔴",
    estado == "WARNING", "🟡",
    estado == "OK",      "🟢",
    "⚪"
)
| project orden, producto, estado, color, icono
| order by orden asc
```

### Configuración del flujo en Power Automate

1. **Trigger:** Recurrence (cada 15 minutos, o el intervalo que corresponda).
2. **Action:** "Run query and list results" (conector Azure Log Analytics).
   - Subscription, Resource Group, Workspace: los del workspace donde están desplegadas las funciones.
   - Query: el contenido del archivo KQL de power_automate_queries.
   - Time Range: `Last 3 hours` (o el lookback que use la query).
3. **Condition:** Si alguna fila tiene `estado == "ALERT"`.
4. **Action (si alerta):** Enviar email / mensaje Teams / ticket ServiceNow con el detalle de productos en alerta.

### Ejemplo de condición en Power Automate

```
@contains(string(body('Run_query_and_list_results')?['value']), '"estado": "ALERT"')
```

---

## 14. Cómo implementar este modelo en un nuevo producto

Esta sección es la más importante para equipos que quieran replicar el modelo en sus propios productos.

### Pasos generales

```
1. Identificar los pipelines/jobs a monitorear
2. Crear source(s) para el workspace del nuevo producto
3. Crear helpers con la lógica de evaluación
4. Crear domain(s) que agreguen los helpers
5. Crear un domain global si hay múltiples dominios
6. Crear wrappers para Grafana
7. Crear queries para Power Automate
8. Desplegar en Log Analytics
9. Configurar Grafana
```

### Paso 1: Identificar los pipelines/jobs

Responder estas preguntas:
- ¿Qué jobs existen? (nombres en `JobName_s` de `ContainerAppSystemLogs_CL`)
- ¿Con qué frecuencia esperada corren?
- ¿Qué es una falla? (timeout, error, ausencia de ejecución)
- ¿Hay datos que puedan desactualizarse? (lag de tablas)
- ¿Hay ventanas de mantenimiento conocidas?

### Paso 2: Crear el source

**Template para un nuevo workspace:**

```kql
// Archivo: law_functions/prd/mlp/sources/fn_src_mlp_ws_<producto>.kql

let fn_src_mlp_ws_<producto> = (sourceType:string, startTime:datetime, endTime:datetime) {
  union isfuzzy=true
    (
      workspace("/subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.OperationalInsights/workspaces/<WORKSPACE_NAME>")
        .table("ContainerAppSystemLogs_CL")
      | where TimeGenerated between (startTime .. endTime)
      | where sourceType == "ContainerAppSystemLogs_CL"
      | extend source_table = "ContainerAppSystemLogs_CL"
    ),
    (
      workspace("/subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.OperationalInsights/workspaces/<WORKSPACE_NAME>")
        .table("ContainerAppConsoleLogs_CL")
      | where TimeGenerated between (startTime .. endTime)
      | where sourceType == "ContainerAppConsoleLogs_CL"
      | extend source_table = "ContainerAppConsoleLogs_CL"
    )
};
```

**Reemplazar:**
- `<producto>`: nombre corto del producto (ej: `miproducto`)
- `<SUB_ID>`: ID de suscripción Azure
- `<RG>`: nombre del Resource Group
- `<WORKSPACE_NAME>`: nombre del workspace de Log Analytics

**Verificar que el source funciona:**
```kql
fn_src_mlp_ws_<producto>("ContainerAppSystemLogs_CL", ago(1h), now())
| summarize count() by JobName_s
| order by count_ desc
```

### Paso 3: Crear helpers

**Template para helper de ejecución (jobs con frecuencia esperada):**

```kql
// Archivo: law_functions/prd/mlp/<producto>/helpers/fn_prd_mlp_<producto>_eval_ejecucion.kql

let fn_prd_mlp_<producto>_eval_ejecucion = (job_name:string, endTime:datetime, ventana_min:int, max_fallas:int, operador:string) {
    let startTime = endTime - totimespan(ventana_min * 60s);
    let fallas = toscalar(
        fn_src_mlp_ws_<producto>("ContainerAppSystemLogs_CL", startTime, endTime)
        | where JobName_s == job_name
        | where Type_s == 'Warning'
              and Reason_s in ('FailedCreate', 'DeadlineExceeded', 'BackoffLimitExceeded')
        | summarize Fallas = count()
        | project Fallas
    );
    print Status = case(
        operador == "lte", iff(fallas <= max_fallas, 'OK', 'NOOK'),
        operador == "lt",  iff(fallas <  max_fallas, 'OK', 'NOOK'),
        operador == "eq",  iff(fallas == max_fallas, 'OK', 'NOOK'),
        'NOOK')
};
```

**Template para helper de lag de tablas:**

```kql
// Archivo: law_functions/prd/mlp/<producto>/helpers/fn_prd_mlp_<producto>_lag_helpers.kql
// Requiere que el job de tracking registre timestamps en formato:
// {"fecha_log_UTC": "...", "mensaje": "timestamp_<tabla>: <datetime>"}

let fn_prd_mlp_<producto>_lag_helpers = (tables:dynamic, startTime:datetime, endTime:datetime) {
  let umbral_default = 60; // minutos
  let t = fn_src_mlp_ws_<producto>("ContainerAppConsoleLogs_CL", startTime, endTime)
      | where ContainerGroupName_s startswith "<job_de_tracking>"
      | where Log_s startswith '{"fecha'
      | project parsed = parse_json(Log_s)
      | project mensaje=tostring(parsed.mensaje), fecha_log_UTC=todatetime(parsed.fecha_log_UTC)
      | where mensaje startswith "timestamp_"
      | extend tabla = substring(mensaje, 10, indexof(mensaje, ": ") - 10)
      | where tabla in (tables)
      | extend ultimo_timestamp = todatetime(substring(mensaje, indexof(mensaje, ": ") + 2, 19))
      | extend ultimo_timestamp = datetime_local_to_utc(ultimo_timestamp, "America/Santiago")
      | extend diff_minutos = round(datetime_diff("second", fecha_log_UTC, ultimo_timestamp) / 60.0, 1)
      | extend alert = iff(isempty(diff_minutos) or diff_minutos > umbral_default, 1, 0)
      | summarize has_alert=max(alert);
  iff(toscalar(t) == 1, "ALERT", "OK")
};
```

### Paso 4: Crear el domain

**Template para domain simple (un solo tipo de señal):**

```kql
// Archivo: law_functions/prd/mlp/<producto>/domains/fn_prd_mlp_<producto>_dom_<pipeline>_status.kql

let fn_prd_mlp_<producto>_dom_<pipeline>_status = (startTime:datetime, endTime:datetime) {
    let signal_1 = fn_prd_mlp_<producto>_eval_ejecucion('<job_name>', endTime, 60, 3, 'lte');
    let signal_2 = fn_prd_mlp_<producto>_lag_helpers(dynamic(["tabla_1", "tabla_2"]), startTime, endTime);
    let status = iff(signal_1 == "NOOK" or signal_2 == "ALERT", "ALERT", "OK");
    print status = status
};
```

**Template para domain con múltiples métricas (patrón SIROSAG):**

```kql
let fn_prd_mlp_<producto>_dom_global_status = (startTime:datetime, endTime:datetime) {
    let metric_status = union
        (fn_prd_mlp_<producto>_eval_ejecucion('job01', endTime, 60, 5, 'lte') | extend Metric='Fallas_job_01'),
        (fn_prd_mlp_<producto>_eval_ejecucion('job02', endTime, 60, 5, 'lte') | extend Metric='Fallas_job_02')
    | summarize Status = take_any(Status) by Metric
    | evaluate pivot(Metric, take_any(Status));

    metric_status
    | project
        Pipeline_A = iff(column_ifexists('Fallas_job_01', 'OK') == 'NOOK', 'Alertar', 'No Alertar'),
        Pipeline_B = iff(column_ifexists('Fallas_job_02', 'OK') == 'NOOK', 'Alertar', 'No Alertar')
};
```

### Paso 5: Crear el wrapper

```kql
// Archivo: grafana_wrappers/prd/mlp/<producto>/var_mlp_<producto>_<pipeline>.kql

fn_prd_mlp_<producto>_dom_<pipeline>_status(bin($__timeFrom, 1m), bin($__timeTo, 1m))
| project color
| take 1
```

### Paso 6: Agregar al INVENTORY.md

Actualizar el archivo `refactor_ada_optimized/INVENTORY.md` con las nuevas funciones.

### Paso 7: Validar

```bash
python refactor_ada_optimized/validate_kql_references.py
# Debe terminar con: KQL package audit OK
```

### Ejemplo completo — Nuevo producto "MIPRODUCTO"

Suponer que se quiere monitorear un nuevo producto con dos jobs:
- `mlp-prd-caj-miproducto-job01`: corre cada hora, no puede fallar más de 2 veces en 4 horas.
- `mlp-prd-caj-miproducto-job02`: corre una vez al día, cero fallas permitidas.

**Archivo 1 — Source:**
```kql
// law_functions/prd/mlp/sources/fn_src_mlp_ws_miproducto.kql
let fn_src_mlp_ws_miproducto = (sourceType:string, startTime:datetime, endTime:datetime) {
  workspace("/subscriptions/c68213bf-7453-4ba4-9aaa-56b822af4c20/resourceGroups/MLP-PRD-RG-MIPRODUCTO/providers/Microsoft.OperationalInsights/workspaces/mlp-prd-law-miproducto")
    .table(sourceType)
  | where TimeGenerated between (startTime .. endTime)
  | extend source_table = sourceType
};
```

**Archivo 2 — Helper:**
```kql
// law_functions/prd/mlp/miproducto/helpers/fn_prd_mlp_miproducto_eval_fallas.kql
let fn_prd_mlp_miproducto_eval_fallas = (job_name:string, endTime:datetime, ventana_min:int, max_fallas:int) {
    let startTime = endTime - totimespan(ventana_min * 60s);
    let fallas = toscalar(
        fn_src_mlp_ws_miproducto("ContainerAppSystemLogs_CL", startTime, endTime)
        | where JobName_s == job_name
        | where Type_s == 'Warning' and Reason_s in ('FailedCreate', 'DeadlineExceeded')
        | summarize Fallas = count()
    );
    print Status = iff(fallas <= max_fallas, 'OK', 'NOOK')
};
```

**Archivo 3 — Domain:**
```kql
// law_functions/prd/mlp/miproducto/domains/fn_prd_mlp_miproducto_dom_global_status.kql
let fn_prd_mlp_miproducto_dom_global_status = (startTime:datetime, endTime:datetime) {
    let job01 = toscalar(fn_prd_mlp_miproducto_eval_fallas('mlp-prd-caj-miproducto-job01', endTime, 240, 2) | project Status);
    let job02 = toscalar(fn_prd_mlp_miproducto_eval_fallas('mlp-prd-caj-miproducto-job02', endTime, 1440, 0) | project Status);
    let status = iff(job01 == "NOOK" or job02 == "NOOK", "ALERT", "OK");
    print status = status
};
```

**Archivo 4 — Wrapper:**
```kql
// grafana_wrappers/prd/mlp/miproducto/var_mlp_miproducto_global.kql
fn_prd_mlp_miproducto_dom_global_status(bin($__timeFrom, 1m), bin($__timeTo, 1m))
| project color
| take 1
```

---

## 15. Patrones de alertas y valores de estado

### Valores de estado estándar

| Valor | Significado | Color HEX | Usado en |
|---|---|---|---|
| `OK` | Sistema saludable | `#EAF4EA` (verde) | ADA, NOTPII |
| `ALERT` | Problema detectado | `#E53935` (rojo) | ADA, NOTPII |
| `NOOK` | No OK (interno) | — | SIROSAG helpers |
| `"Alertar"` | Alerta activa | — | SIROSAG domains, NOTPII domains |
| `"No Alertar"` | Sin alerta | — | SIROSAG domains, NOTPII domains |
| `WARNING` | Advertencia | `#FFF4CC` (amarillo) | Wrappers con color |

### Valores de status granular (fn_prd_mlp_ada_jobs_status_detail)

| Código | Significado |
|---|---|
| `a` | Alert (falla en esta ventana) |
| `s` | Success |
| `w` | Warning |
| `n` | Normal (sin dato para evaluar) |

### Patrón: expected vs real

Muchos dominios usan este patrón para evaluar si un job cumplió su frecuencia esperada:

```kql
// Ejemplo conceptual:
let expected_runs = 12; // se esperan 12 ejecuciones en 1 hora (cada 5 min)
let real_runs = toscalar(
    fn_src_mlp_ws_ada("ContainerAppSystemLogs_CL", ago(1h), now())
    | where JobName_s == "mlp-prd-caj-ada-job01"
    | where Log_s contains "has successfully completed"
    | count
);
let threshold = 0.85; // al menos 85% de las ejecuciones esperadas
iff(todouble(real_runs) / expected_runs >= threshold, "OK", "ALERT")
```

### Patrón: fallas consecutivas

Detecta cuando un job falla en N intervalos consecutivos:

```kql
// Patrón usado en Dispatch job17:
range TimeGeneratedBin from bin(endTime - 40m, 10m) to bin(endTime - 10m, 10m) step 10m
| join kind=leftouter (...ejecuciones reales...) on TimeGeneratedBin
| extend status = iff(valorReal == 0, "a", "n")
| order by TimeGeneratedBin desc
| serialize
| extend next_fail = next(is_fail, 1), rn = row_number()
| where rn == 1
| project alerta = is_fail == 1 and next_fail == 1  // 2 fallas consecutivas
```

---

## 16. Ventanas de mantenimiento y exclusiones

### Mantenimiento ADA KPIs

La función `fn_prd_mlp_ada_kpi_alert_rows` aplica 8 reglas de exclusión basadas en el horario de Chile:

| Regla | Condición | Razón de negocio |
|---|---|---|
| `COND_2_0700_1000` | 07:00–10:00 Chile | Carga de turno matutino genera datos incompletos |
| `COND_3_1900_2100` | 19:00–21:00 Chile | Cierre de turno |
| `COND_4_MIE1900_VIE2100` | Miércoles 19:00 – Viernes 21:00 | Mantenimiento semanal programado |
| `COND_5_FUERA_HORARIO` | Fines de semana, antes 9am, después 19pm | Operación no productiva |
| `COND_6_JUE2100_VIE1030` | Jueves 21:00 – Viernes 10:30 | Ventana de mantenimiento extendida |
| `COND_7_0900_0930` | 09:00–09:30 | Reconsolidación de datos matutina |
| `COND_8_2100_2130` | 21:00–21:30 | Reconsolidación nocturna |
| `MANTENCION` | Bandera en catálogo activa | Mantenimiento bajo demanda |
| `EXCLUSION_FIJA` | KPIs específicos en catálogo | KPIs con falsos positivos conocidos |

### Consideración de zona horaria

Todos los logs en Azure se almacenan en **UTC**. Las exclusiones de mantenimiento se calculan en **hora local de Chile (America/Santiago)**.

```kql
// Conversión estándar usada en todo el paquete:
let CurrentTimeChile = datetime_utc_to_local(now(), 'America/Santiago');

// Para timestamps de tablas (los jobs reportan hora Chile):
let ultimo_timestamp = datetime_local_to_utc(ultimo_timestamp_raw, "America/Santiago");
```

---

## 17. Validación y calidad del paquete KQL

### Script de validación de referencias

Antes de hacer deploy de cualquier cambio, ejecutar:

```bash
python refactor_ada_optimized/validate_kql_references.py
```

Este script verifica:
- Que todas las funciones referenciadas en wrappers, domains y helpers existen como archivos.
- Que no existan wrappers legacy de sources.
- Que haya espejo 1:1 entre `law_functions/.../sources` y `law_functions_body_only/.../sources`.
- Que no existan marcadores de conflicto de merge.

### Script de detección de conflictos de merge

```bash
python refactor_ada_optimized/check_conflict_markers.py
```

Detecta `<<<<<<<`, `=======`, `>>>>>>>` en archivos KQL (errores de merge que romperían las funciones).

### Estado esperado post-validación

```
KQL package audit OK
```

Cualquier otro output indica un problema que debe resolverse antes de hacer deploy.

---

## 18. Inventario completo de funciones

### Wrappers (21 total)

| Wrapper | Producto | Domain que llama |
|---|---|---|
| `var_mlp_ada_global` | ADA | `fn_prd_mlp_ada_dom_global_status` |
| `var_mlp_ada_dispatch` | ADA | `fn_prd_mlp_ada_dom_dispatch_status` |
| `var_mlp_ada_drillit` | ADA | `fn_prd_mlp_ada_dom_drillit_status` |
| `var_mlp_ada_pi` | ADA | `fn_prd_mlp_ada_dom_pi_status` |
| `var_mlp_ada_plans` | ADA | `fn_prd_mlp_ada_dom_plans_status` |
| `var_mlp_ada_blockgrade` | ADA | `fn_prd_mlp_ada_dom_blockgrade_status` |
| `var_mlp_ada_meteodata` | ADA | `fn_prd_mlp_ada_dom_meteodata_status` |
| `var_mlp_ada_kpi` | ADA | `fn_prd_mlp_ada_dom_kpi_status` |
| `var_mlp_ada_alarm` | ADA | `fn_prd_mlp_ada_dom_alarm_status` |
| `var_mlp_ada_front` | ADA | `fn_prd_mlp_ada_dom_front_status` |
| `var_mlp_ada_jobs_detail` | ADA | `fn_prd_mlp_ada_jobs_status_detail` |
| `var_mlp_ada_jobs_detail_legacyfmt` | ADA | `fn_prd_mlp_ada_jobs_status_detail` |
| `var_mlp_notpii_autoloader_dev` | NOTPII | `fn_prd_mlp_notpii_dom_autoloader_dev_status` |
| `var_mlp_notpii_autoloader_uat` | NOTPII | `fn_prd_mlp_notpii_dom_autoloader_uat_status` |
| `var_mlp_notpii_ingesta` | NOTPII | `fn_prd_mlp_notpii_dom_ingesta_status` |
| `var_mlp_notpii_difusion_global` | NOTPII | `fn_prd_mlp_notpii_dom_global_status` |
| `var_mlp_sirosag_resumen` | SIROSAG | `fn_prd_mlp_ssag_dom_resumen_status` |

### Domains (17 total)

| Domain | Producto | Señales principales |
|---|---|---|
| `fn_prd_mlp_ada_dom_dispatch_status` | ADA | lag_classic, lag_nrt, consec_fail_job17 |
| `fn_prd_mlp_ada_dom_drillit_status` | ADA | pipeline runs fallidos |
| `fn_prd_mlp_ada_dom_blockgrade_status` | ADA | pipeline runs fallidos |
| `fn_prd_mlp_ada_dom_pi_status` | ADA | expected vs real job01/02 |
| `fn_prd_mlp_ada_dom_plans_status` | ADA | expected vs real |
| `fn_prd_mlp_ada_dom_meteodata_status` | ADA | expected vs real job01/02 por minuto |
| `fn_prd_mlp_ada_dom_kpi_status` | ADA | errores KPI con exclusiones horarias |
| `fn_prd_mlp_ada_dom_alarm_status` | ADA | incidentes largos, errores storage |
| `fn_prd_mlp_ada_dom_front_status` | ADA | errores app, errores token |
| `fn_prd_mlp_ada_dom_optimizador_status` | ADA | ejecución job01 genshare |
| `fn_prd_mlp_ada_dom_settings_status` | ADA | expected vs real jobs PRFCI |
| `fn_prd_mlp_ada_dom_global_status` | ADA | union de los 11 domains anteriores |
| `fn_prd_mlp_notpii_dom_autoloader_dev_status` | NOTPII | SLA jobs Databricks DEV |
| `fn_prd_mlp_notpii_dom_autoloader_uat_status` | NOTPII | SLA jobs Databricks UAT |
| `fn_prd_mlp_notpii_dom_ingesta_status` | NOTPII | errores/warnings job04 PI |
| `fn_prd_mlp_notpii_dom_global_status` | NOTPII | union autoloader + ingesta |
| `fn_prd_mlp_ssag_dom_resumen_status` | SIROSAG | 13 jobs × 3 señales = 8 dimensiones |

### Helpers (10 total)

| Helper | Producto | Propósito |
|---|---|---|
| `fn_prd_mlp_ada_lag_helpers` | ADA | Lag de tablas via job02 logs |
| `fn_prd_mlp_ada_alert_from_dispatch_nrt_logs` | ADA | Lag NRT job17 |
| `fn_prd_mlp_ada_kpi_alert_rows` | ADA | Errores KPI con exclusiones horarias |
| `fn_prd_mlp_ada_jobs_status_detail` | ADA | Diagnóstico tabular por job |
| `fn_prd_mlp_notpii_autoloader_alert` | NOTPII | SLA evaluation por tipo de job |
| `fn_prd_mlp_notpii_ingesta_job04_alert` | NOTPII | Errores/warnings job04 PI |
| `fn_prd_mlp_ssag_eval_ejecucion` | SIROSAG | Conteo de fallas vs umbral |
| `fn_prd_mlp_ssag_eval_desfase` | SIROSAG | Desfase temporal de jobs |
| `fn_prd_mlp_ssag_eval_desactualizacion` | SIROSAG | Frescura de datos procesados |
| `fn_mon_status_to_color` | Cross-product | Convierte status a color HEX |

### Sources (14 total)

Ver tabla completa en [Sección 5](#5-capa-1--sources-fuentes-de-datos).

---

## 19. Mapa de dependencias entre funciones

```
var_mlp_ada_dispatch
  └── fn_prd_mlp_ada_dom_dispatch_status
        ├── fn_prd_mlp_ada_lag_helpers
        │     ├── fn_prd_mlp_ada_lag_thresholds (catálogo)
        │     └── fn_src_mlp_ws_ada
        ├── fn_prd_mlp_ada_alert_from_dispatch_nrt_logs
        │     └── fn_src_mlp_ws_ada
        └── fn_src_mlp_ws_ada

var_mlp_ada_kpi
  └── fn_prd_mlp_ada_dom_kpi_status
        └── fn_prd_mlp_ada_kpi_alert_rows
              ├── fn_prd_mlp_ada_kpi_catalogs (catálogo)
              ├── fn_prd_mlp_ada_en_mantencion (catálogo)
              └── fn_src_mlp_ws_ada

var_mlp_ada_pi
  └── fn_prd_mlp_ada_dom_pi_status
        └── fn_src_mlp_systemlogs_all
              ├── fn_src_mlp_ws_ada
              ├── fn_src_mlp_ws_meteo
              ├── fn_src_mlp_ws_pisystem
              └── fn_src_mlp_ws_plans

var_mlp_sirosag_resumen
  └── fn_prd_mlp_ssag_dom_resumen_status
        ├── fn_prd_mlp_ssag_eval_ejecucion (×16)
        │     └── fn_src_mlp_ssag_systemlogs_all
        │           ├── fn_src_mlp_ws_ssag
        │           ├── fn_src_mlp_ws_plans
        │           ├── fn_src_mlp_ws_pdmsagi
        │           └── fn_src_mlp_ws_pisystem
        ├── fn_prd_mlp_ssag_eval_desfase (×14)
        │     └── fn_src_mlp_ssag_systemlogs_all
        └── fn_prd_mlp_ssag_eval_desactualizacion (×4)
              └── fn_src_mlp_ws_ssag

var_mlp_notpii_autoloader_dev
  └── fn_prd_mlp_notpii_dom_autoloader_dev_status
        └── fn_prd_mlp_notpii_autoloader_alert
              └── fn_src_mlp_ws_notpii_databricksjobs (env="dev")
```

---

## 20. Operación diaria y troubleshooting

### Flujo de investigación ante un ALERT

Cuando Grafana muestra un dominio en rojo, el procedimiento es:

**Paso 1:** Identificar el dominio en alerta (ej: "Dispatch en ALERT").

**Paso 2:** Ejecutar el domain directamente en Log Analytics:
```kql
fn_prd_mlp_ada_dom_dispatch_status(ago(3h), now())
// Si retorna ALERT → confirmar que es real
```

**Paso 3:** Ejecutar cada helper del domain para aislar la señal:
```kql
// ¿Cuál señal disparó la alerta?
let t = dynamic(["StdShiftLoads2","StdShiftDumps"]);
print lag_classic = fn_prd_mlp_ada_lag_helpers(t, ago(3h), now())
// Si = "ALERT" → hay lag en tablas de Dispatch
```

**Paso 4:** Ir al source para ver los logs crudos:
```kql
fn_src_mlp_ws_ada("ContainerAppSystemLogs_CL", ago(2h), now())
| where JobName_s contains "job17"
| order by TimeGenerated desc
| take 50
// Ver si hay errores o ausencia de logs
```

**Paso 5:** Revisar historial de ejecución del job:
```kql
fn_prd_mlp_ada_jobs_status_detail(ago(6h), now())
| where job contains "job17"
// Ver columnas: status, real, esperado, porcentaje
```

### Troubleshooting por escenario

#### "El dashboard muestra verde pero hay quejas de datos desactualizados"

```kql
// Verificar el lag real de tablas Dispatch en las últimas 6 horas
fn_src_mlp_ws_ada("ContainerAppConsoleLogs_CL", ago(6h), now())
| where ContainerGroupName_s startswith "mlp-prd-caj-ada-job02"
| where Log_s startswith '{"fecha'
| project parsed = parse_json(Log_s)
| project mensaje=tostring(parsed.mensaje), fecha_log_UTC=todatetime(parsed.fecha_log_UTC)
| where mensaje startswith "timestamp_"
| extend tabla = substring(mensaje, 10, indexof(mensaje, ": ") - 10)
| extend ultimo_timestamp = todatetime(substring(mensaje, indexof(mensaje, ": ") + 2, 19))
| extend diff_minutos = round(datetime_diff("second", fecha_log_UTC, ultimo_timestamp) / 60.0, 1)
| project fecha_log_UTC, tabla, diff_minutos
| order by diff_minutos desc
```

#### "Alerta en KPI que parece falso positivo"

Verificar si hay una exclusión horaria activa:
```kql
let now_chile = datetime_utc_to_local(now(), 'America/Santiago');
print
    hora = datetime_part("hour", now_chile),
    dia  = dayofweek(now_chile) / 1d,
    fuera_horario = (dayofweek(now_chile) / 1d == 6 or dayofweek(now_chile) / 1d == 0
                     or datetime_part("hour", now_chile) < 9
                     or datetime_part("hour", now_chile) >= 19)
```

Si `fuera_horario = true` y hay alerta activa, puede ser que el catálogo de exclusiones no cubra ese KPI específico — revisar `fn_prd_mlp_ada_kpi_catalogs()`.

#### "SIROSAG muestra NOOK pero no sé en qué job"

```kql
fn_prd_mlp_ssag_dom_resumen_status(ago(4h), now())
// Revisar cuáles columnas son "Alertar"
// Cada columna (Ingesta_PI, Celdas, Solidos, etc.) agrupa múltiples jobs
```

Para ir más al detalle:
```kql
// Ver fallas del job04 SIROSAG en las últimas 4 horas
fn_prd_mlp_ssag_eval_ejecucion('mlp-prd-caj-ssag-job04', now(), 240, 1, 'lt')
// Si Status = "NOOK" → el job tuvo ≥1 falla en 4 horas
```

#### "Función no encontrada al ejecutar en LAW"

Verificar que la función esté desplegada en el workspace correcto:
```kql
// Listar todas las funciones del workspace:
// En Azure Portal → Log Analytics → Logs → Functions (tab izquierdo)
// Buscar por nombre
```

Si falta, redeplegar desde `law_functions_body_only/prd/mlp/...`.

### Checklist de guardia (primera respuesta)

```
[ ] ¿El workspace de Log Analytics está disponible? (Azure Status Page)
[ ] ¿El job con alerta aparece en ContainerAppSystemLogs_CL?
[ ] ¿El error es aislado (un solo job) o sistémico (múltiples jobs)?
[ ] ¿Hay mantenimiento programado en curso?
[ ] ¿La alerta apareció por primera vez o es recurrente?
[ ] ¿El domain retorna ALERT cuando se ejecuta manualmente?
```

---

## 21. Reglas para cambios futuros

### Al agregar un nuevo dominio

1. Crear el archivo de domain en `law_functions/prd/mlp/<producto>/domains/`.
2. Crear su espejo en `law_functions_body_only/prd/mlp/<producto>/domains/`.
3. Crear el wrapper correspondiente en `grafana_wrappers/prd/mlp/<producto>/`.
4. Actualizar `INVENTORY.md` con el nuevo domain y wrapper.
5. Ejecutar `python refactor_ada_optimized/validate_kql_references.py`.

### Al agregar un nuevo helper

1. Crear en `law_functions/prd/mlp/<producto>/helpers/`.
2. Crear espejo en `law_functions_body_only/prd/mlp/<producto>/helpers/`.
3. Asegurarse de que usa el prefijo `fn_prd_mlp_<producto>_`.
4. No duplicar lógica que ya existe en helpers cross-product (`fn_mon_*`).

### Al agregar un nuevo source

1. Crear en `law_functions/prd/mlp/sources/`.
2. Crear espejo en `law_functions_body_only/prd/mlp/sources/`.
3. Usar el patrón `fn_src_mlp_ws_<workspace>`.
4. Para multi-ambiente, usar parámetro `env` controlado (no URIs libres).
5. Actualizar `docs/source_catalog.md`.

### Al modificar una función existente

1. Nunca editar la función de producción directamente sin probar primero.
2. Probar en un workspace de desarrollo con un nombre temporal.
3. Validar que los consumers no se rompen.
4. Actualizar el archivo correspondiente en el repositorio.
5. Hacer deploy al workspace de producción.
6. Verificar Grafana y Power Automate post-deploy.

### Al retirar una función

1. Verificar en `INVENTORY.md` que no aparece como activa.
2. Verificar con `validate_kql_references.py` que ningún otro archivo la referencia.
3. Eliminar el archivo del repositorio.
4. Eliminar la función del workspace de Log Analytics.
5. Actualizar `INVENTORY.md`.

### Qué NO hacer

- No crear funciones con prefijo `fn_prd_` sin el infijo `mlp_` (ambigüedad de faena).
- No hacer llamadas directas a `workspace(...)` en domains o helpers — siempre via source.
- No parametrizar workspace URIs libremente — usar sources con enum controlado.
- No duplicar lógica de un helper en múltiples domains — extraerla a un helper compartido.
- No dejar conflictos de merge en archivos KQL — el script `check_conflict_markers.py` los detecta.

---

## 22. Glosario

| Término | Definición |
|---|---|
| **AMG** | Antofagasta Minerals Group — grupo minero dueño de los productos monitoreados |
| **MLP** | Minera Los Pelambres — faena (operación minera) donde corre la plataforma |
| **ADA** | Advanced Data Analytics — producto de analítica de datos de MLP |
| **NOTPII** | Not Personally Identifiable Information — producto de compliance de privacidad |
| **SIROSAG** | Sistema Integrado de Recomendación Operacional SAG — sistema de recomendación para molino SAG |
| **LAW** | Log Analytics Workspace — base de datos de logs de Azure donde se ejecuta KQL |
| **KQL** | Kusto Query Language — lenguaje de consultas usado en Azure Log Analytics |
| **Domain** | Función KQL que retorna el estado final de un pipeline o componente |
| **Helper** | Función KQL que evalúa una señal específica (lag, fallas, desfase) |
| **Source** | Función KQL que encapsula el acceso a un workspace de Log Analytics |
| **Wrapper** | Función KQL ligera que adapta el output de un domain para Grafana |
| **Lag** | Tiempo de desactualización de datos (diferencia entre el log y el último dato procesado) |
| **NRT** | Near Real-Time — procesamiento casi en tiempo real |
| **Expected vs Real** | Patrón que compara ejecuciones esperadas contra ejecutadas en una ventana |
| **Fallas consecutivas** | Patrón que detecta N fallos seguidos (más grave que N fallos dispersos) |
| **Desfase** | Tiempo adicional que tarda un job más allá de su ventana esperada (SIROSAG) |
| **Desactualización** | Datos cuyo último timestamp es más antiguo que un umbral máximo (SIROSAG) |
| **NOOK** | Not OK — valor de estado interno de helpers SIROSAG |
| **Faena** | Operación minera (planta, mina) — unidad de organización de los productos |
| **prd** | Producción — ambiente de ejecución real (vs dev/uat) |
| **mlp** | Minera Los Pelambres — identificador de faena en nombres de funciones |
| **ContainerAppSystemLogs_CL** | Tabla Azure con logs de sistema de Container Apps (estado de ejecución de jobs) |
| **ContainerAppConsoleLogs_CL** | Tabla Azure con logs de consola de Container Apps (output de jobs con datos) |
| **AzureDiagnostics** | Tabla Azure con logs de diagnóstico de Data Factory y otros servicios |
| **DatabricksJobs** | Tabla Azure con métricas de ejecución de jobs de Databricks |
| **Grafana variable** | Variable en Grafana cuyo valor se obtiene ejecutando una query (wrapper KQL) |
| **Power Automate** | Plataforma de automatización de Microsoft para flujos de trabajo |
| **ITOT** | Sistema operativo industrial del molino SAG — fuente primaria de SIROSAG |
| **PDM** | Predictive Data Management — sistema de datos predictivos (upstream de SIROSAG) |
| **job17** | Job de Dispatch NRT — pipeline crítico que corre cada ~10 minutos |
| **job02** | Job de tracking de timestamps de ADA — base del sistema de detección de lag |

---

*Documento generado: Mayo 2026 — Plataforma de Monitoreo AMG*  
*Repositorio: `Plataforma-Monitoreo-AMG`*  
*Contacto técnico: equipo AMG Digital*
