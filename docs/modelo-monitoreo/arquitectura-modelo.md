# Arquitectura del modelo de monitoreo

## Visión general

El modelo implementa una arquitectura por capas para separar acceso a datos, reglas de evaluación, agregación por dominio y consumo visual en Grafana. La ruta esperada de una consulta es:

```text
Dashboard Grafana
  -> wrapper Grafana var_mlp_*
    -> función de dominio fn_prd_mlp_*_dom_*_status
      -> helper específico o cross-producto
        -> source fn_src_mlp_*
          -> tabla en Azure Log Analytics Workspace
```

Esta separación permite versionar el criterio de monitoreo en KQL y mantener los dashboards livianos. El dashboard debe renderizar resultados y no convertirse en la única ubicación de reglas operativas.

## Capas consideradas

### 1. Fuentes

Las funciones `fn_src_mlp_*` encapsulan consultas a tablas de LAW y, cuando aplica, uniones entre workspaces o tablas equivalentes. Su responsabilidad es exponer un contrato técnico reutilizable y filtrar por ventana temporal.

Ejemplos observados:

- `fn_src_mlp_ws_ada(sourceType, startTime, endTime)`.
- `fn_src_mlp_ws_dispatch(sourceType, startTime, endTime)`.
- `fn_src_mlp_pipeline_runs_all(startTime, endTime)`.
- `fn_src_mlp_systemlogs_all(startTime, endTime)`.

> Nota de seguridad: las rutas internas, suscripciones completas, IDs o workspaces productivos no deben repetirse en documentación operativa. Si se requiere trazabilidad exacta, debe revisarse el archivo KQL versionado con permisos adecuados.

### 2. Helpers

Los helpers encapsulan reglas reutilizables o cálculos intermedios. Existen dos tipos:

- **Cross-producto:** helpers reutilizables en varios productos, por ejemplo conversión de estado a color.
- **Específicos:** helpers acoplados a un producto o dominio, por ejemplo evaluación de lag, detalle de jobs, desfase o alertas por logs.

### 3. Dominios

Las funciones de dominio representan una unidad funcional monitoreable: dispatch, PI, KPI, ingesta, autoloader, resumen, alarmas, front, etc. Deben devolver un resultado estable para que Grafana y soporte lo interpreten sin conocer todos los detalles internos.

Contrato recomendado para dominio de estado:

- Entrada: `startTime:datetime`, `endTime:datetime`.
- Salida mínima: una fila con `status` y/o `color`.
- Salida ampliada recomendada: `dominio`, `producto`, `status`, `color`, `detalle`, `metricas` o columnas equivalentes cuando se requiera diagnóstico.

### 4. Wrappers para Grafana

Los wrappers `var_mlp_*` son queries pequeñas que adaptan macros de Grafana a funciones LAW. Deben ser delgados y evitar lógica de negocio nueva.

Ejemplo de patrón:

```kusto
fn_prd_mlp_<producto>_dom_<dominio>_status(bin($__timeFrom, 1m), bin($__timeTo, 1m))
```

### 5. Dashboard Grafana

El archivo `Plataforma_Monitoreo_AMG.json` contiene el dashboard exportado. La regla de diseño del modelo es que Grafana consuma wrappers o funciones, no que duplique reglas complejas en variables o paneles.

### 6. Power Automate

Las consultas en `refactor_ada_optimized/power_automate_queries` sirven como puntos de integración o validación externa. Deben alinearse con dominios y helpers para evitar criterios divergentes.

## Relación entre LAW, KQL y Grafana

- **LAW** almacena logs, diagnósticos y funciones KQL guardadas.
- **KQL** define fuentes, reglas de negocio/técnicas, agregaciones y estados.
- **Grafana** visualiza estados calculados y ofrece navegación para diagnóstico.

La responsabilidad primaria de la lógica debe quedar en KQL. Grafana debe encargarse de variables, paneles, colores y experiencia visual.

## Reutilizable cross-producto

Elementos reutilizables entre productos:

- Convenciones de naming.
- Contrato temporal `startTime`/`endTime`.
- Helpers de color y agregación global.
- Patrón source -> helper -> domain -> wrapper.
- Checklist de implementación y pruebas.
- Paneles estándar de resumen, detalle y evidencia.

## Específico por producto

Elementos específicos por producto:

- Fuentes y tablas consultadas.
- Umbrales de lag, desfase, freshness o completitud.
- Jobs, pipelines y nombres funcionales.
- Criterios OK/WARN/ALERT.
- Dominios monitoreados.
- Reglas de mantenimiento o excepciones operativas.

Cuando un criterio aplique a más de un producto, debe evaluarse moverlo a helper cross-producto. Si depende de nombres de tablas, jobs o semántica del producto, debe mantenerse específico.

## Brechas observadas que requieren validación

- El validador KQL reporta mirrors `law_functions_body_only` faltantes para sources.
- Algunos wrappers ADA AMG apuntan a funciones bajo carpeta `domain` y el validador las marca como no dominio por convención esperada.
- `fn_prd_mlp_ada_amg_jobs_status_detail` aparece referenciada pero no fue encontrada como definición en las funciones LAW actuales.

Estas brechas no se corrigen en esta documentación; quedan como **Por validar** para normalización técnica.
