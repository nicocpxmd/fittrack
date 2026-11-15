# Diagramas del informe

Cuatro diagramas en Mermaid, con tres niveles de abstracción distintos. Las fuentes están en
`report/diagramas/` y los PNG que usa el informe, en `report/figuras/`.

| Fuente | PNG | Figura | Qué muestra |
|---|---|---|---|
| `01-arquitectura-logica.mmd` | `arquitectura-logica.png` | 1 | Componentes **funcionales**: qué hace el sistema, sin tecnologías ni ubicación |
| `02-componentes.mmd` | `componentes.png` | 2 | Servicios, interfaces y dependencias. Tecnología sí, ubicación no |
| `03-despliegue.mmd` | `despliegue.png` | 3 | Nodos, IPs, puertos, volúmenes y qué corre en cada máquina |
| `04-pipeline.mmd` | `pipeline.png` | 4 | Recorrido del dato: CSV, ETL, Parquet, KPIs, JSON, panel |

## Por qué tres niveles

El profesor lo pidió explícitamente: una arquitectura debe describir componentes lógicos, de forma
que alguien ajeno a la materia entienda **qué hace** el sistema aunque no sepa cómo se implementa. Los
detalles físicos —IPs, puertos, contenedores, tecnologías— van en el despliegue. El diagrama de
componentes es el paso intermedio: ya nombra las tecnologías y las interfaces, pero todavía no dice
en qué máquina vive cada cosa.

## Cómo se renderizan

```powershell
.\report\render-diagramas.ps1
```

Descarga `mermaid-cli` con `npx` la primera vez (incluye un Chromium) y genera los cuatro PNG en
`report/figuras/`. Para cambiar el ancho:

```powershell
.\report\render-diagramas.ps1 -Width 2000
```

Desde bash, el equivalente para una sola figura:

```bash
npx -y @mermaid-js/mermaid-cli \
  -i report/diagramas/01-arquitectura-logica.mmd \
  -o report/figuras/arquitectura-logica.png -w 1600 -b white
```

También se pueden pegar en <https://mermaid.live> para editarlos a mano.

## Cuándo hay que re-renderizar

Cada vez que cambie un `.mmd`. Los PNG están versionados, así que el informe compila sin necesidad de
tener Node instalado.
