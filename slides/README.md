# Diapositivas — sustentación del 2026-11-20

`slides.md` es un deck **Marp** de 18 diapositivas con la estructura que pidió el profesor:
introducción, análisis, diseño, implementación, pruebas, conclusiones y referencias. Cada diapositiva
lleva notas del presentador con su marca de tiempo.

## Exportar

Los archivos `fittrack.pdf` y `fittrack.pptx` están versionados, así que no hace falta exportar para
presentar. Solo si cambia el `.md`:

```bash
npx -y @marp-team/marp-cli slides/slides.md --allow-local-files -o slides/fittrack.pptx
npx -y @marp-team/marp-cli slides/slides.md --allow-local-files -o slides/fittrack.pdf
```

El `.pptx` conserva las notas del presentador, útiles en la vista de orador de PowerPoint.

## Estructura y reparto

| Bloque | Persona | Diapositivas | Fase | Tiempo |
|---|---|---|---|---|
| 1 | Juan Camilo Serrano | 1–4 | Introducción y análisis | 3:00 |
| 2 | Diego Fernando Asprilla | 5–8 | Diseño | 3:00 |
| 3 | Juan David Ocampo | 9–12 | Implementación y pruebas | 3:00 |
| 4 | Nicolás Castro | 13–15 + video | Analítica | 3:00 + 0:15 |
| — | Video | 16 | Demostración | 1:50 |
| 5 | Lucio Matías Melendez | 16–18 | Cierre y conclusiones | 0:15 + 3:00 |

Total: 17:20, dentro del máximo de 18 minutos.

## Guiones individuales

Cada persona recibe su guion en PDF por el canal del equipo. Las fuentes `.tex` viven en el
repositorio privado de infraestructura, no aquí: son material de ensayo y no forman parte de la
entrega.

## Reglas para la sustentación

1. **No leer.** Cada persona usa la diapositiva y sus notas como guion, no como texto.
2. **Cronómetro.** El ensayo debe cerrar en 17:30, no en 20.
3. **Contingencia.** Si el laboratorio no responde, el video y la captura del dashboard cubren la demo.
4. **Video.** Se reproduce desde el archivo, con la diapositiva 16 como portada; no está incrustado en
   el `.pptx`.
