# Informe IEEE — cómo compilarlo

Archivos:

- `reporte.tex`: fuente LaTeX con la plantilla IEEE (`IEEEtran`). Es la versión que se compila.
- `reporte.pdf`: PDF final, 7 páginas.
- `reporte.md`: versión de trabajo en Markdown; la fuente del PDF es `reporte.tex`.
- `diagramas.md`: diagramas Mermaid de componentes, despliegue y pipeline.
- `figuras/`: `arquitectura-logica.png`, `componentes.png`, `despliegue.png`, `pipeline.png`,
  `dashboard.jpeg` y `dashboard-crop.jpeg`.

## Compilación

Con Tectonic:

```powershell
tectonic reporte.tex
```

También funciona con pdfLaTeX en Overleaf: crear un proyecto con la plantilla IEEE Conference,
subir `reporte.tex` y la carpeta `figuras/`, y compilar. El PDF final no debe pasar de 10 páginas;
la versión actual tiene 7.

Si se regenera la captura del dashboard, el corte de `dashboard-crop.jpeg` debe terminar en el
separador gris que hay después de la tarjeta de retención por cohorte (`y = 1996` en la captura de
1863×4591).

## Estructura

| Sección | Contenido |
|---|---|
| Resumen | contexto, resultados y aporte |
| 1. Introducción | problema, objetivos, contribución |
| 2. Análisis | dataset, alternativas, requisitos |
| 3. Diseño | arquitectura lógica, componentes, despliegue, pipeline, KPIs |
| 4. Implementación | Docker/Swarm, Spark, roles, reproducibilidad |
| 5. Pruebas y resultados | funcionales, limpieza, KPIs, carga, estrés, failover, dashboard |
| 6. Conclusiones | hallazgos, limitaciones, trabajo futuro |
| Referencias | Docker, Spark, HAProxy, FastAPI, dataset y repositorio |

## Datos que no deben faltar

- 100.000 usuarios, 8.462.080 filas crudas, 8.418.175 filas curadas.
- 24/24 chequeos del validador.
- 1,89× de mejora con 3 réplicas en un nodo (38,15 → 72,05 RPS).
- 99,70 % de éxito en failover y recuperación del enrutamiento en 8 s.
- Correlaciones −0,595 / +0,597 y abandono temprano 39,53 %.
- Enlace al repositorio y al tag `v4.1-proyecto-final`.
