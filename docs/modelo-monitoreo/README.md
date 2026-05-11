# Modelo de monitoreo

## Propósito

Esta carpeta contiene la documentación técnica y operativa del **nuevo modelo de monitoreo** utilizado por el equipo de Soporte Data & Analítica Avanzada. Su objetivo es estandarizar cómo se monitorean productos, fuentes, dominios, jobs, pipelines, funciones KQL, dashboards Grafana y reglas operativas de soporte.

El repositorio es la **fuente oficial técnica** del modelo. El portal de soporte debe enlazar o resumir esta documentación, pero no duplicarla completa para evitar divergencias entre runbooks, dashboards y funciones KQL versionadas.

## Alcance

El modelo documentado cubre los artefactos observados en el repositorio:

- Funciones KQL para Azure Log Analytics Workspace (LAW), organizadas por fuentes, helpers cross-producto, helpers específicos y dominios.
- Wrappers KQL utilizados por Grafana para consultar funciones del workspace con macros de tiempo.
- Dashboard Grafana exportado como JSON.
- Consultas auxiliares de Power Automate.
- Documentación previa de auditoría, inventario, equivalencia legacy y análisis de fuentes.

Productos o paquetes identificados en el repositorio: **ADA**, **ADA AMG**, **NOTPII** y **SIROSAG**. Cualquier responsable, suscripción, credencial, ID productivo completo o ruta sensible que no esté documentado de forma segura queda como **Por definir** o **Por validar**.

## Qué problema resuelve

Antes de estandarizar el modelo, la lógica de monitoreo puede quedar distribuida entre paneles, variables de Grafana, consultas ad hoc, funciones sin contrato común y reglas operativas no versionadas. Este modelo resuelve esa dispersión mediante una arquitectura por capas:

```text
Grafana wrapper -> Función de dominio -> Helper -> Source -> Tabla LAW
```

Con esta separación se busca:

- Reutilizar fuentes y reglas comunes entre productos.
- Reducir consultas pesadas embebidas en dashboards.
- Mantener criterios OK/WARN/ALERT versionados en KQL.
- Facilitar diagnóstico de soporte desde un panel hacia la función que calculó el estado.
- Permitir incorporar nuevos productos con una guía repetible.

## Organización de esta documentación

| Documento | Uso principal |
|---|---|
| [arquitectura-modelo.md](arquitectura-modelo.md) | Entender capas, responsabilidades y relación LAW/KQL/Grafana. |
| [estandar-funciones-kql.md](estandar-funciones-kql.md) | Crear y mantener funciones KQL con contratos homogéneos. |
| [catalogo-funciones.md](catalogo-funciones.md) | Consultar funciones y wrappers encontrados en el repositorio. |
| [guia-implementacion-law.md](guia-implementacion-law.md) | Implementar funciones en Log Analytics Workspace y validar dependencias. |
| [guia-implementacion-grafana.md](guia-implementacion-grafana.md) | Consumir funciones desde Grafana y estructurar paneles. |
| [guia-nuevo-producto.md](guia-nuevo-producto.md) | Incorporar un nuevo producto al modelo. |
| [convenciones-nombrado.md](convenciones-nombrado.md) | Mantener naming consistente en funciones, wrappers, archivos y dominios. |
| [troubleshooting.md](troubleshooting.md) | Diagnosticar errores frecuentes de LAW, KQL y Grafana. |
| [traspaso-soporte.md](traspaso-soporte.md) | Guía operativa para soporte ante alertas e incidentes. |

## Cómo usar esta documentación

- **Para soporte:** partir por [traspaso-soporte.md](traspaso-soporte.md) y usar [troubleshooting.md](troubleshooting.md) durante una alerta.
- **Para implementar en LAW:** revisar [arquitectura-modelo.md](arquitectura-modelo.md), luego [guia-implementacion-law.md](guia-implementacion-law.md) y validar contra [catalogo-funciones.md](catalogo-funciones.md).
- **Para mantener Grafana:** usar [guia-implementacion-grafana.md](guia-implementacion-grafana.md) y respetar wrappers existentes.
- **Para agregar productos:** seguir [guia-nuevo-producto.md](guia-nuevo-producto.md) y las [convenciones de nombrado](convenciones-nombrado.md).

## Relación con el portal de soporte

El portal de soporte debe tratar esta documentación como fuente técnica oficial. En el portal se recomienda publicar:

- Enlaces a esta carpeta.
- Resúmenes ejecutivos por producto o dominio.
- Runbooks operativos que apunten a las funciones y paneles versionados aquí.

No se recomienda copiar el detalle completo de funciones, contratos o queries en el portal, porque el repositorio debe mantener la trazabilidad técnica y el historial de cambios.
