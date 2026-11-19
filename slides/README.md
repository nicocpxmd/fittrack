# Diapositivas — sustentación del 2026-11-20

`slides.md` es un deck **Marp** de 18 diapositivas con la estructura que pidió el profesor:
introducción, análisis, diseño, implementación, pruebas, conclusiones y referencias. Cada diapositiva
lleva notas del presentador con su marca de tiempo.

## Exportar

El PDF está versionado: es el formato de presentación y no necesita exportarse. Solo si cambia el `.md`:

```bash
npx -y @marp-team/marp-cli slides/slides.md --allow-local-files -o slides/fittrack.pdf
```

Si alguna vez hace falta la vista de orador, se puede generar un `.pptx` aparte (no se versiona):

```bash
npx -y @marp-team/marp-cli slides/slides.md --allow-local-files -o slides/fittrack.pptx
```

Ojo: ese `.pptx` lleva las diapositivas como imágenes y conserva las notas, pero **no es editable** en
PowerPoint. Los cambios se hacen siempre en `slides.md` y se vuelve a exportar.

## Estructura y reparto

| Bloque | Persona | Diapositivas | Fase | Tiempo |
|---|---|---|---|---|
| 1 | Juan Camilo Serrano | 1–4 | Introducción y análisis | 3:00 |
| 2 | Diego Fernando Asprilla | 5–8 | Diseño | 3:00 |
| 3 | Juan David Ocampo | 9–12 | Implementación y pruebas | 3:00 |
| 4 | Nicolás Castro | 13–15 | Analítica | 3:00 |
| — | Video | fuera del PDF | Demostración | 2:00 |
| 5 | Lucio Matías Melendez | 16–18 | Conclusiones y referencias | 3:00 |

Total: **17:20**, que incluye 20 s de apertura y cierre del video, dentro del máximo de 18 minutos.
El video no tiene diapositiva: se reproduce directamente desde el archivo, con la última diapositiva
de analítica en pantalla.

## Guiones individuales

Cada persona recibe su guion en PDF por el canal del equipo. Las fuentes `.tex` viven en el
repositorio privado de infraestructura, no aquí: son material de ensayo y no forman parte de la
entrega.

## Reglas para la sustentación

1. **No leer.** Cada persona usa la diapositiva y sus notas como guion, no como texto.
2. **Cronómetro.** El ensayo debe cerrar en 17:30, no en 20.
3. **Contingencia.** Si el laboratorio no responde, el video y la captura del dashboard cubren la demo.
4. **Video.** Se reproduce desde el archivo, sin diapositiva de por medio. Nicolás lo abre al terminar
   su bloque y Lucio lo cierra antes de las conclusiones.
