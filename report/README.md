# Informe IEEE — cómo cerrarlo

Archivos:

- `reporte.md`: contenido completo del informe (resumen, análisis, diseño, implementación, pruebas,
  conclusiones y referencias).
- `diagramas.md`: diagramas Mermaid de componentes, despliegue y pipeline.
- `figuras/dashboard.jpeg`: captura de la pestaña Analítica.

## Pasos para producir el PDF

1. Abrir la plantilla IEEE Conference (Word o Overleaf `IEEEtran`).
2. Copiar las secciones de `reporte.md` respetando el orden.
3. Exportar los tres diagramas de `diagramas.md`:
   - abrir <https://mermaid.live>,
   - pegar cada bloque,
   - exportar PNG,
   - guardar como `figuras/arquitectura.png`, `figuras/despliegue.png` y `figuras/pipeline.png`.
4. Insertar las figuras y la captura `figuras/dashboard.jpeg`.
5. Revisar que el PDF final no pase de **10 páginas**.
6. Subir el PDF a UAO virtual y al repositorio GitHub.

## Estructura sugerida (2 columnas, IEEE)

| Sección | Contenido |
|---|---|
| Resumen | 150–200 palabras |
| 1. Introducción | contexto, objetivos, contribución |
| 2. Análisis | dataset, alternativas, requisitos |
| 3. Diseño | componentes, despliegue, pipeline, KPIs |
| 4. Implementación | parte 1, parte 2, reproducibilidad |
| 5. Pruebas y resultados | funcionales, limpieza, KPIs, carga, dashboard |
| 6. Conclusiones | hallazgos, limitaciones, trabajo futuro |
| Referencias | Docker, HAProxy, Spark, FastAPI, repo |

## Consejos de extensión

- Las tablas de limpieza, KPIs y carga son la evidencia más fuerte; no recortarlas.
- Si el PDF se pasa de 10 páginas, reducir la sección 2.2 (alternativas) a una tabla y acortar la
  introducción.
- No incluir capturas de código; el README ya tiene los comandos.
- Mantener las figuras a media columna cuando sea posible.

## Datos que no deben faltar

- 100.000 usuarios, 8.462.080 filas crudas, 8.418.175 filas curadas.
- 24/24 chequeos del validador.
- 1,89× de mejora con 3 réplicas (38,15 → 72,05 RPS).
- Correlaciones −0,595 / +0,597 y abandono 39,53 %.
- Enlace al repositorio y a la rama `proyecto-final`.
