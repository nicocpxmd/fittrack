#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valida el dataset FitTrack-Synth: conteos, integridad entre tablas, suciedad inyectada
y patrones sembrados. Termina con codigo 0 si todo esta bien y 1 si algo falla.

Carga los CSV en memoria: unos 2 GB de RAM por cada 100.000 usuarios.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

LB = 2.20462
INI = pd.Timestamp("2025-01-06")
FIN = pd.Timestamp("2026-07-05")
resultados = []


def chequeo(nombre, ok, detalle):
    resultados.append(bool(ok))
    print(f"[{'OK' if ok else 'FALLA'}] {nombre}: {detalle}")


def a_fecha(serie):
    """Convierte a fecha aceptando ISO (aaaa-mm-dd) y dd/mm/aaaa; devuelve (fechas, cuantas_en_otro_formato)."""
    f = pd.to_datetime(serie, format="%Y-%m-%d", errors="coerce")
    otro = f.isna()
    if otro.any():
        f[otro] = pd.to_datetime(serie[otro], format="%d/%m/%Y", errors="coerce")
    return f, int(otro.sum())


def main():
    p = argparse.ArgumentParser(description="Validador del dataset FitTrack-Synth")
    p.add_argument("--dir", default="data", help="carpeta con los CSV")
    d = p.parse_args().dir
    meta = json.load(open(os.path.join(d, "clave_respuestas", "metadatos.json"), encoding="utf-8"))
    sucio = meta["suciedad_inyectada"]
    u = pd.read_csv(os.path.join(d, "usuarios.csv"))
    m = pd.read_csv(os.path.join(d, "medidas.csv"))
    g = pd.read_csv(os.path.join(d, "metas.csv"))
    r = pd.read_csv(os.path.join(d, "rutinas.csv"))
    print(f"Dataset: {meta['usuarios']} usuarios, semilla {meta['semilla']}, {meta['filas_total']} filas\n")

    # ---- 1. conteos e integridad ----
    for nombre, df in [("usuarios", u), ("medidas", m), ("metas", g), ("rutinas", r)]:
        chequeo(f"filas de {nombre}", len(df) == meta["filas"][nombre], f"{len(df)} (esperadas {meta['filas'][nombre]})")
    chequeo("user_id unico en usuarios", u.user_id.is_unique, f"{u.user_id.nunique()} ids")
    todos = set(u.user_id)
    for nombre, df in [("medidas", m), ("metas", g), ("rutinas", r)]:
        huerfanos = int((~df.user_id.isin(todos)).sum())
        chequeo(f"integridad de {nombre}.user_id", huerfanos == 0, f"{huerfanos} filas sin usuario")

    # ---- 2. suciedad inyectada (se compara contra lo que registro el generador) ----
    dup_m = len(m) - m.medida_id.nunique()
    dup_r = len(r) - r.rutina_id.nunique()
    chequeo("duplicados en medidas", dup_m == sucio["duplicados_medidas"], f"{dup_m} (inyectados {sucio['duplicados_medidas']})")
    chequeo("duplicados en rutinas", dup_r == sucio["duplicados_rutinas"], f"{dup_r} (inyectados {sucio['duplicados_rutinas']})")
    m = m.drop_duplicates().reset_index(drop=True)
    r = r.drop_duplicates().reset_index(drop=True)
    for col in ["cintura", "brazo", "pecho"]:
        tasa = m[col].isna().mean()
        chequeo(f"nulos en medidas.{col}", 0.02 <= tasa <= 0.04, f"{tasa:.2%} (objetivo ~3 %)")
    m["f"], otro_m = a_fecha(m.fecha)
    r["f"], otro_r = a_fecha(r.fecha)
    chequeo("fechas dd/mm/aaaa en medidas", otro_m == sucio["fechas_otro_formato_medidas"], f"{otro_m} (inyectadas {sucio['fechas_otro_formato_medidas']})")
    chequeo("fechas dd/mm/aaaa en rutinas", otro_r == sucio["fechas_otro_formato_rutinas"], f"{otro_r} (inyectadas {sucio['fechas_otro_formato_rutinas']})")
    unidad = u.set_index("user_id").unidad_peso
    m["kg"] = m.peso / np.where(m.user_id.map(unidad) == "lb", LB, 1.0)
    absurdos = int(((m.kg < 30) | (m.kg > 250)).sum())
    chequeo("pesos absurdos", absurdos == sucio["atipicos_peso"], f"{absurdos} (inyectados {sucio['atipicos_peso']})")
    chequeo("fechas dentro del periodo", m.f.between(INI, FIN).all() and r.f.between(INI, FIN).all(), f"{INI.date()} a {FIN.date()}")
    f_cre, _ = a_fecha(g.fecha_creacion)
    f_lim, _ = a_fecha(g.fecha_limite)
    chequeo("metas: limite posterior a creacion", (f_lim > f_cre).all(), f"{len(g)} metas")
    chequeo("metas: estados validos", g.estado.isin(["cumplida", "vencida", "abandonada", "activa"]).all(),
            ", ".join(f"{k} {v:.0%}" for k, v in g.estado.value_counts(normalize=True).items()))

    # ---- 3. patrones sembrados (lo que Spark deberia descubrir) ----
    mk = m[(m.kg >= 30) & (m.kg <= 250)].sort_values(["user_id", "f"])
    a = mk.groupby("user_id").agg(n=("kg", "size"), p0=("kg", "first"), p1=("kg", "last"), f0=("f", "first"), f1=("f", "last"))
    a = a[(a.n >= 6) & ((a.f1 - a.f0).dt.days >= 56)]
    a["delta"] = a.p1 - a.p0
    t = r.groupby("user_id").agg(n_ses=("rutina_id", "size"), g0=("f", "min"), g1=("f", "max"))
    t["ses_sem"] = t.n_ses / ((t.g1 - t.g0).dt.days / 7).clip(lower=1)
    a = a.join(t[["ses_sem"]], how="inner").join(u.set_index("user_id").objetivo_fitness)
    corr = {obj: gdf.ses_sem.corr(gdf.delta) for obj, gdf in a.groupby("objetivo_fitness")}
    chequeo("bajar_peso: mas sesiones, mas baja el peso", corr["bajar_peso"] < -0.3, f"correlacion {corr['bajar_peso']:.2f}")
    chequeo("ganar_musculo: mas sesiones, mas sube el peso", corr["ganar_musculo"] > 0.3, f"correlacion {corr['ganar_musculo']:.2f}")

    act = pd.concat([mk[["user_id", "f"]], r[["user_id", "f"]]]).groupby("user_id").f.max()
    x = u.set_index("user_id").join(act.rename("ultima"))
    x["reg"] = pd.to_datetime(x.fecha_registro)
    abandona = ((x.ultima - x.reg).dt.days <= 84) & (x.ultima < FIN - pd.Timedelta(days=28))
    chequeo("abandono en las primeras 12 semanas", 0.25 <= abandona.mean() <= 0.50, f"{abandona.mean():.0%} de los usuarios (objetivo ~un tercio)")

    por_sem = ((x.reg - INI).dt.days // 7).value_counts()
    enero = por_sem.reindex(range(0, 4)).mean()
    resto = por_sem.reindex(range(4, 61)).mean()
    chequeo("pico de registros en enero", enero / resto >= 1.4, f"{enero:.0f} vs {resto:.0f} registros por semana")

    g = g.assign(ambicion=(g.valor_objetivo / g.valor_inicial - 1).abs())
    g["nivel"] = pd.qcut(g.ambicion, 3, labels=["baja", "media", "alta"])
    cumpl = g.groupby("nivel", observed=True).estado.apply(lambda s: (s == "cumplida").mean())
    chequeo("metas ambiciosas fallan mas", cumpl["baja"] > cumpl["alta"],
            f"cumplidas: ambicion baja {cumpl['baja']:.0%}, media {cumpl['media']:.0%}, alta {cumpl['alta']:.0%}")

    fallas = resultados.count(False)
    print(f"\nResultado: {resultados.count(True)} chequeos OK, {fallas} con falla")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
