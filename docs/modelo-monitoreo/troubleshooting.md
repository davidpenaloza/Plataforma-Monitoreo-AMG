# Troubleshooting del modelo de monitoreo

## Objetivo

Guiar el diagnóstico de errores frecuentes en LAW, KQL, Grafana y operación de soporte.

## Flujo general de diagnóstico

1. Identificar producto, dominio, ambiente y ventana temporal.
2. Ejecutar el wrapper de Grafana en LAW reemplazando macros por fechas manuales.
3. Ejecutar la función de dominio directamente.
4. Ejecutar helpers relevantes.
5. Ejecutar sources con `take 10`.
6. Revisar si el problema es de datos, función, permisos, dashboard o criterio operativo.
7. Recopilar evidencia antes de escalar.

## Errores frecuentes

| Síntoma | Causa probable | Diagnóstico | Acción |
|---|---|---|---|
| `Unknown function` | Función no creada, typo o dependencia faltante. | Buscar nombre exacto en catálogo y LAW. | Crear dependencia o corregir wrapper. |
| `Failed to resolve table` | Tabla no existe en workspace o permisos insuficientes. | Probar source directo con ventana amplia. | Confirmar workspace, tabla y RBAC. |
| Panel vacío | Sin datos, rango corto, macro mal evaluada o función falla. | Reemplazar macros por `ago()`/`now()`. | Ajustar rango o corregir función. |
| Estado OK con datos ausentes | Función trata ausencia como OK. | Revisar `coalesce`, `count` y condiciones default. | Definir comportamiento sin datos. |
| ALERT inesperada | Umbral, lag o job esperado mal calibrado. | Revisar helper y criterios documentados. | Ajustar umbral con validación funcional. |
| Timeout | Consulta amplia, `union` grande o proyección tardía. | Ejecutar por source y medir. | Filtrar temprano y reducir columnas. |
| Color incorrecto | Threshold local de Grafana no coincide con helper. | Comparar status y color devueltos. | Alinear thresholds del panel. |

## Workspace y permisos

Problemas típicos:

- Usuario o datasource sin acceso al workspace.
- Función creada en workspace distinto al datasource de Grafana.
- Source apunta a workspace que no contiene la tabla esperada.

Diagnóstico:

```kusto
fn_src_mlp_ws_<fuente>("<tabla>", ago(2h), now())
| take 10
```

Si falla en LAW, no es un problema de Grafana.

## Funciones desconocidas

Cuando aparezca `Unknown function`:

1. Verificar el nombre exacto en `catalogo-funciones.md`.
2. Confirmar si es source, helper o dominio.
3. Revisar dependencias y orden de creación.
4. Ejecutar validador local.
5. Para ADA AMG, revisar brecha conocida de `fn_prd_mlp_ada_amg_jobs_status_detail` marcada como **Por validar**.

## Problemas con `union`

Causas frecuentes:

- Columnas incompatibles entre tablas.
- Tabla ausente en un workspace.
- Falta de `project` para normalizar schema.
- `union isfuzzy=true` ocultando ausencia de una tabla esperada.

Acción:

- Probar cada rama del `union` por separado.
- Proyectar columnas comunes.
- Agregar columna `source_table` o `source_workspace` cuando sea seguro y útil.

## Problemas con `toscalar`

Riesgos:

- La subconsulta devuelve más de una fila.
- La subconsulta no devuelve filas y el valor queda null.
- Se usa `take 1` sin orden determinístico.

Acción:

- Usar `summarize` para asegurar una fila.
- Aplicar `coalesce()` para defaults explícitos.
- Ordenar antes de `take 1` si aplica.

## Rutas y archivos

Si una función existe en KQL pero el validador la marca mal:

- Confirmar que el archivo se llama igual que la función.
- Confirmar carpeta esperada: `domains` vs `domain`.
- Revisar mirrors `law_functions_body_only` si el proceso lo requiere.
- Revisar markers de conflicto con el script local.

## Variables Grafana

Problemas frecuentes:

- Wrapper apunta a función inexistente.
- Macro `$__timeFrom`/`$__timeTo` no se evalúa como datetime esperado.
- Panel usa variable legacy en vez de wrapper versionado.
- Dashboard tiene threshold local diferente al contrato KQL.

Diagnóstico:

1. Copiar la query del wrapper.
2. Reemplazar macros por `bin(ago(2h), 1m)` y `bin(now(), 1m)`.
3. Ejecutar en LAW.
4. Comparar columnas con lo esperado por el panel.

## Zonas horarias

LAW opera típicamente en UTC para `TimeGenerated`. Grafana puede mostrar hora local del navegador o del dashboard. Ante diferencias:

- Registrar hora UTC y hora local observada.
- Confirmar timezone configurado en dashboard.
- Comparar `TimeGenerated` con `now()` en LAW.
- Evitar criterios operativos basados en hora local sin conversión explícita.

## Límites de Kusto

Síntomas:

- Timeout.
- Memoria excedida.
- Resultado truncado.
- Query throttled.

Acciones:

- Reducir ventana temporal.
- Filtrar por tabla/fuente temprano.
- Proyectar columnas necesarias.
- Evitar joins o unions innecesarios.
- Considerar materialización o preagregación si el patrón se repite.

## Evidencia para escalar

Recopilar:

- Producto, dominio y ambiente.
- Hora de detección en UTC.
- Rango temporal usado.
- Wrapper o función ejecutada.
- Resultado de dominio.
- Resultado del source con `take 10` o conteo.
- Captura del panel si aplica.
- Mensaje de error exacto.
- Cambios recientes conocidos: **Por definir** si no se conocen.
- Runbook consultado en portal de soporte.
