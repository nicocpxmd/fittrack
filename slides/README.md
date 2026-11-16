# Diapositivas — sustentación del 2026-11-20

`slides.md` es un deck **Marp**: 17 diapositivas con notas del presentador y marcas de tiempo.
Cada bloque dura 3 minutos y el video ocupa 2:20.

## Exportar

Los archivos `fittrack.pdf` y `fittrack.pptx` están versionados, así que no hace falta exportar para
presentar. Solo si cambia el `.md`:

```bash
npx -y @marp-team/marp-cli slides/slides.md --allow-local-files -o slides/fittrack.pptx
npx -y @marp-team/marp-cli slides/slides.md --allow-local-files -o slides/fittrack.pdf
```

El `.pptx` conserva las notas del presentador, útiles en la vista de orador de PowerPoint.

## Estructura

| Bloque | Diapositivas | Tema | Tiempo |
|---|---|---|---|
| 1 | 1–3 | Contexto, requerimientos y dataset | 3:00 |
| 2 | 4–7 | Arquitectura, componentes, despliegue y Swarm | 3:00 |
| 3 | 8–10 | Carga, estrés y failover | 3:00 |
| 4 | 11–13 | Acceso por rol, pipeline y KPIs | 3:00 |
| — | 14 | Video de demostración | 2:20 |
| 5 | 15–17 | Conclusiones, límites y cierre | 3:00 |

Total: 17:20, dentro del máximo de 18 minutos.

## Notas del presentador

En Marp las notas son los comentarios `<!-- ... -->`. No se ven en la presentación, se exportan al
`.pptx` y contienen el guion y el minuto exacto de cada diapositiva.

## Reglas para la sustentación

1. **No leer.** Cada persona usa la diapositiva y las notas como guion, no como texto.
2. **Cronómetro.** El ensayo debe cerrar en 17:30, no en 20.
3. **Contingencia.** Si el laboratorio no responde, el video y la captura del dashboard cubren la demo.
4. **Preguntas.** El reparto y las preguntas probables de cada bloque están en
   `docs/practicas/reparto-sustentacion-2026-11-20.md` del repo de infraestructura.
