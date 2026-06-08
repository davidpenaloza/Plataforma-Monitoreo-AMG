# Propósito y contrato operativo del dashboard CROSS

## 1. Propósito

El dashboard CROSS es la puerta de entrada de soporte para revisar el estado operacional de productos digitales distribuidos en distintas faenas y ambientes. Su función principal es **triage**, no reemplazar los dashboards técnicos de cada producto ni concentrar todo el diagnóstico en una sola pantalla.

La pregunta que debe responder es:

> ¿La anomalía está en una fuente compartida, en un producto o en uno de sus componentes, y a qué dashboard debe entrar soporte para continuar el diagnóstico?

## 2. Usuarios y momento de uso

El usuario principal es soporte operacional/N1-N2 durante:

- revisión periódica del estado global;
- recepción o validación de una alerta;
- identificación de una fuente común afectada;
- priorización de productos en rojo o amarillo;
- navegación hacia el dashboard especializado;
- recopilación de evidencia para escalar o descartar un falso positivo.

No es una herramienta para editar reglas de negocio, reemplazar Azure Log Analytics ni mostrar toda la evidencia técnica de cada job.

## 3. Flujo visual original

El orden vertical del dashboard representa el flujo de diagnóstico y debe conservarse.

### Nivel 1 — `Ingestas Cross`

Presenta fuentes compartidas agrupadas por faena: MLP, Centinela, Antucoya, Zaldívar y AMSA CROSS.

Objetivo: detectar si varios productos pueden estar afectados por una misma fuente upstream, por ejemplo Dispatch, PI System, Jigsaw, Planes, Meteodata o SharePoint.

### Nivel 2 — `Resumen Ejecutivo`

Presenta el estado global de los productos agrupados por faena.

Objetivo: permitir a soporte identificar rápidamente qué producto requiere atención antes de entrar al detalle.

### Nivel 3 — `Monitoreo Analítica Avanzada`

Descompone los productos en etapas operacionales, principalmente:

- ingestas;
- procesamiento o transformación;
- recomendación/predicción;
- front.

Las tarjetas enlazan a dashboards especializados. El CROSS indica dónde mirar; el dashboard de producto entrega el diagnóstico profundo.

### Nivel 4 — `Monitoreo Reportabilidad`

Aplica el mismo patrón a productos de reportabilidad, separándolos de analítica avanzada para no mezclar flujos operacionales distintos.

## 4. Contrato visual

Los siguientes elementos son funcionales y deben considerarse invariantes durante una migración:

- orden fuente → producto → componente;
- agrupación por faena;
- separación entre analítica avanzada y reportabilidad;
- chips/tarjetas coloreados mediante variables Grafana;
- leyenda verde/amarillo/rojo;
- etiquetas de ambiente PRD/UAT/DEV;
- enlaces desde las tarjetas detalladas hacia dashboards especializados;
- HTML con estilos inline, compatible con el comportamiento actual de Azure Managed Grafana;
- nombres de variables trazables a producto y dominio.

Una migración de versión no debe reemplazar estas decisiones por una nueva arquitectura visual.

## 5. Contrato de datos

El dashboard consume variables que funcionan como wrappers visuales. La salida esperada es un color o estado simple que pueda aplicarse a una tarjeta o chip.

La lógica de evaluación debe residir preferentemente en funciones KQL desplegadas en Log Analytics. El JSON puede conservar consultas legacy durante la migración, pero su refactor debe realizarse como iniciativa separada, con validación funcional por producto.

## 6. Alcance de una migración a Grafana 12

La migración debe enfocarse en compatibilidad y continuidad:

- importar sin errores;
- resolver datasources y permisos;
- preservar variables y consultas;
- preservar HTML, colores y enlaces;
- confirmar que los estados coinciden con la instancia anterior;
- permitir rollback usando el export original.

Quedan fuera de la migración inicial:

- rediseño visual;
- cambio del orden de secciones;
- conversión a dashboard schema v2;
- sustitución masiva de KQL legacy;
- incorporación o eliminación de productos;
- cambio de semántica de colores o estados;
- creación de nuevos estados globales.

## 7. Criterios de aceptación funcional

La migración se considera correcta cuando soporte puede repetir el flujo original:

1. identificar una fuente afectada en `Ingestas Cross`;
2. identificar el producto afectado en `Resumen Ejecutivo`;
3. ubicar el componente en Analítica Avanzada o Reportabilidad;
4. abrir el dashboard especializado;
5. continuar el diagnóstico sin diferencias de estado respecto del dashboard anterior.
