<#
    Renderiza los diagramas Mermaid del informe a PNG en report/figuras.

    Uso:
        .\report\render-diagramas.ps1
        .\report\render-diagramas.ps1 -Scale 3

    Requiere Node y descarga mermaid-cli con npx la primera vez.
    La misma idea desde bash:
        npx -y @mermaid-js/mermaid-cli -i report/diagramas/01-arquitectura-logica.mmd \
            -o report/figuras/arquitectura-logica.png -b white -s 2
#>
param(
    [int]$Scale = 2
)

$ErrorActionPreference = 'Stop'

$here = $PSScriptRoot
$src = Join-Path $here 'diagramas'
$out = Join-Path $here 'figuras'

$items = @(
    @{ In = '01-arquitectura-logica.mmd'; Out = 'arquitectura-logica.png' },
    @{ In = '02-componentes.mmd';         Out = 'componentes.png' },
    @{ In = '03-despliegue.mmd';          Out = 'despliegue.png' },
    @{ In = '04-pipeline.mmd';            Out = 'pipeline.png' }
)

if (-not (Test-Path $out)) { New-Item -ItemType Directory -Path $out | Out-Null }

foreach ($item in $items) {
    $inFile = Join-Path $src $item.In
    $outFile = Join-Path $out $item.Out
    Write-Host "Renderizando $($item.In) -> $($item.Out)"
    npx -y '@mermaid-js/mermaid-cli' -i $inFile -o $outFile -b white -s $Scale
    if ($LASTEXITCODE -ne 0) { throw "Fallo al renderizar $($item.In)" }
}

Write-Host "Listo: $($items.Count) diagramas en $out"
