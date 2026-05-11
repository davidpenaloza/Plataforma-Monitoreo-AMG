# Guía de implementación en Log Analytics Workspace

## Objetivo

Describir cómo llevar las funciones KQL del repositorio a Azure Log Analytics Workspace (LAW), respetando dependencias y validaciones mínimas.

## Preparación

1. Confirmar el workspace destino y permisos para crear o actualizar funciones.
2. Revisar que no se copien secretos ni credenciales en documentación o tickets.
3. Identificar el ambiente (`prd`, `uat`, `dev`) y producto.
4. Revisar [catalogo-funciones.md](catalogo-funciones.md) para dependencias.
5. Ejecutar el validador local antes de cualquier despliegue.

## Orden recomendado de creación

1. **Sources:** `fn_src_mlp_*`.
2. **Helpers cross-producto:** `fn_mon_*`.
3. **Helpers específicos:** `fn_prd_mlp_<producto>_*`.
4. **Funciones de dominio:** `fn_prd_mlp_<producto>_dom_<dominio>_status`.
5. **Funciones globales:** dominios globales que dependen de otros dominios.
6. **Wrappers Grafana:** se guardan en el repositorio y se copian a Grafana como queries/variables, no necesariamente como funciones LAW.
7. **Queries Power Automate:** publicar o actualizar solo después de validar dominios.

## Dependencias típicas

```text
fn_src_mlp_ws_*                 -> base de acceso a tablas
fn_src_mlp_*_all                -> agregaciones de sources
fn_mon_status_to_color          -> helper cross-producto para colores
fn_prd_mlp_<producto>_*helper*  -> reglas intermedias
fn_prd_mlp_<producto>_dom_*     -> estado de dominio
fn_prd_mlp_<producto>_dom_global_status -> consolidado global
var_mlp_*                       -> consumo desde Grafana
```

## Validaciones mínimas

- La función compila en LAW sin referencias desconocidas.
- `startTime` y `endTime` filtran correctamente la ventana esperada.
- Las tablas y columnas usadas existen en el workspace destino.
- El resultado de dominio devuelve al menos una fila y columnas interpretables por Grafana.
- Los colores/status se ajustan al contrato esperado.
- La consulta no excede límites de tiempo/costo en ventanas comunes de operación.
- No se publica documentación con suscripciones completas, tokens o IDs sensibles.

## Cómo probar una función después de crearla

Prueba básica de dominio:

```kusto
fn_prd_mlp_<producto>_dom_<dominio>_status(ago(2h), now())
```

Prueba de source:

```kusto
fn_src_mlp_ws_<fuente>("<tabla>", ago(2h), now())
| take 10
```

Prueba de wrapper equivalente:

```kusto
fn_prd_mlp_<producto>_dom_<dominio>_status(bin(ago(2h), 1m), bin(now(), 1m))
```

## Errores frecuentes

| Error | Causa probable | Acción recomendada |
|---|---|---|
| `Unknown function` | Dependencia no creada o nombre distinto. | Crear dependencias en orden y validar naming. |
| `Failed to resolve table` | Tabla no existe o workspace incorrecto. | Confirmar source y permisos. |
| Resultados vacíos | Ventana temporal sin datos o filtro de tabla incorrecto. | Ampliar ventana y probar source directo. |
| `toscalar` falla o devuelve valor inesperado | Subconsulta con múltiples filas o sin agregación. | Agregar `summarize`, `take 1` determinístico o `coalesce`. |
| Timeout/costo alto | Unión amplia, proyección insuficiente o rango grande. | Reducir columnas, filtrar temprano, evaluar materialización. |
| Diferencia Grafana vs LAW | Macros de tiempo, zona horaria o wrapper divergente. | Ejecutar query del wrapper reemplazando macros manualmente. |

## Estado actual de validación local

Al momento de generar esta documentación, `python refactor_ada_optimized/validate_kql_references.py` reporta brechas existentes en el paquete: mirrors `law_functions_body_only` faltantes, referencias ADA AMG pendientes y wrappers ADA AMG marcados fuera de convención. Estas brechas quedan como **Por validar** antes de una implementación formal completa.
