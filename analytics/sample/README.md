# Muestra de analítica

`analytics.json` es una instantánea de los KPIs generados con el dataset completo de 100.000
usuarios. Sirve para que el dashboard tenga datos desde el primer arranque, sin necesidad de correr
Spark.

## Uso en el quick start

```bash
mkdir -p analytics/data
cp analytics/sample/analytics.json analytics/data/analytics.json
```

En PowerShell:

```powershell
New-Item -ItemType Directory -Force analytics/data
Copy-Item analytics/sample/analytics.json analytics/data/analytics.json
```

El servicio `analytics` monta `analytics/data` en `/data` (solo lectura). Si después se ejecuta
`spark/run_all.sh`, el JSON se sobrescribe y la API toma la versión nueva por `mtime`, sin reiniciar.

## Qué no es

No es el dataset ni un sustituto del pipeline: son solo los agregados que consume el dashboard. Para
recalcularlos, sigue la sección de Spark del `README.md`.
