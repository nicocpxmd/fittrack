#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FitTrack-Synth: generador del dataset sintetico de seguimiento fisico.

Genera 4 CSV con el mismo vocabulario de los microservicios de FitTrack:
  usuarios.csv, medidas.csv, metas.csv, rutinas.csv
y una carpeta clave_respuestas/ con los parametros ocultos de cada usuario
(sirve para validar el analisis; NO debe entrar al pipeline de Spark).

El progreso NO se genera: lo calcula Spark a partir de medidas y metas.

Es reproducible: con la misma semilla y los mismos parametros produce
exactamente los mismos archivos.
"""
import argparse
import json
import os
import time
import uuid

import numpy as np
import pandas as pd

SEMANAS = 78                           # 78 semanas: del 2025-01-06 al 2026-07-05
INICIO = np.datetime64("2025-01-06")   # un lunes

CIUDADES = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena",
            "Bucaramanga", "Pereira", "Manizales", "Cúcuta", "Santa Marta"]
P_CIUDAD = np.array([0.28, 0.17, 0.14, 0.09, 0.06, 0.06, 0.05, 0.04, 0.06, 0.05])
P_CIUDAD = P_CIUDAD / P_CIUDAD.sum()

OBJETIVOS = ["bajar_peso", "ganar_musculo", "mantener", "resistencia"]
TIPOS = ["fuerza", "cardio", "hiit", "movilidad", "mixto"]
GRUPOS = ["pecho", "espalda", "piernas", "hombros", "brazos", "core", "cuerpo_completo"]
MEDIDAS = ["peso", "cintura", "brazo", "pecho"]

# Probabilidad de cada tipo de rutina segun el objetivo (filas = OBJETIVOS)
P_TIPO = np.array([
    [0.20, 0.35, 0.25, 0.05, 0.15],
    [0.65, 0.05, 0.10, 0.05, 0.15],
    [0.25, 0.25, 0.10, 0.10, 0.30],
    [0.10, 0.50, 0.20, 0.05, 0.15],
])
# Probabilidad de cada grupo muscular segun el tipo de rutina (filas = TIPOS)
P_GRUPO = np.array([
    [0.15, 0.15, 0.25, 0.12, 0.13, 0.10, 0.10],
    [0.00, 0.00, 0.30, 0.00, 0.00, 0.05, 0.65],
    [0.00, 0.00, 0.20, 0.00, 0.00, 0.10, 0.70],
    [0.00, 0.00, 0.10, 0.10, 0.00, 0.15, 0.65],
    [0.08, 0.08, 0.14, 0.06, 0.06, 0.08, 0.50],
])
P_DIA = np.array([0.17, 0.15, 0.17, 0.15, 0.16, 0.12, 0.08])  # lunes..domingo
LB = 2.20462


def parsear():
    p = argparse.ArgumentParser(description="Generador del dataset FitTrack-Synth")
    p.add_argument("--usuarios", type=int, default=10000, help="numero de usuarios (escala del dataset)")
    p.add_argument("--semilla", type=int, default=42, help="semilla aleatoria (misma semilla = mismo dataset)")
    p.add_argument("--salida", default="data", help="carpeta donde se escriben los CSV")
    p.add_argument("--bloque", type=int, default=2000, help="usuarios por bloque (controla la memoria)")
    return p.parse_args()


def calendario():
    """Estacionalidad semanal de la actividad y pesos para elegir la semana de registro."""
    dias = INICIO + np.arange(SEMANAS) * 7
    mes = dias.astype("datetime64[M]").astype(int) % 12 + 1
    factor = {1: 1.35, 2: 1.15, 3: 1.0, 4: 1.0, 5: 1.0, 6: 0.95,
              7: 0.95, 8: 0.95, 9: 1.0, 10: 1.0, 11: 0.9, 12: 0.8}
    estacion = np.array([factor[m] for m in mes])
    p_reg = np.ones(SEMANAS - 4)          # se registran hasta 4 semanas antes del final
    for w in range(SEMANAS - 4):
        if mes[w] == 1:
            p_reg[w] = 2.2                # pico de registros en enero
        elif mes[w] == 12:
            p_reg[w] = 0.8
    return estacion, p_reg / p_reg.sum()


def fecha_str(fechas):
    return np.datetime_as_string(fechas, unit="D")


def elegir_categoria(rng, matriz, filas):
    """Sortea una columna de `matriz` para cada fila indicada (probabilidades por fila)."""
    cum = np.cumsum(matriz, axis=1)[filas]
    u = rng.random(filas.size)[:, None]
    return np.minimum((u > cum).sum(axis=1), matriz.shape[1] - 1)


def inyectar_fechas_distintas(rng, fechas_iso, prob, cont, clave):
    """Cambia una pequena parte de las fechas al formato dd/mm/aaaa (suciedad controlada)."""
    mask = rng.random(fechas_iso.size) < prob
    out = fechas_iso.astype(object)
    for i in np.nonzero(mask)[0]:
        s = out[i]
        out[i] = s[8:10] + "/" + s[5:7] + "/" + s[0:4]
    cont[clave] += int(mask.sum())
    return out


def duplicar(rng, df, prob, cont, clave):
    """Duplica una pequena parte de las filas (copias exactas, con el mismo id)."""
    pos = np.nonzero(rng.random(len(df)) < prob)[0]
    cont[clave] += int(pos.size)
    return pd.concat([df, df.iloc[pos]], ignore_index=True)


def generar_bloque(rng, n, primer_num, estacion, p_reg, cont):
    T = SEMANAS
    sem = np.arange(T)

    # ---------------- perfil de cada usuario ----------------
    ids = np.array([str(uuid.UUID(bytes=rng.bytes(16), version=4)) for _ in range(n)])
    genero = rng.choice(["F", "M", "O"], size=n, p=[0.50, 0.47, 0.03])
    ciudad = rng.choice(CIUDADES, size=n, p=P_CIUDAD)
    objetivo = rng.choice(OBJETIVOS, size=n, p=[0.45, 0.25, 0.15, 0.15])
    obj_cod = np.array([OBJETIVOS.index(o) for o in objetivo])
    unidad = rng.choice(["kg", "lb"], size=n, p=[0.85, 0.15])
    reg_w = rng.choice(T - 4, size=n, p=p_reg)
    edad = np.clip(rng.normal(33, 9, n), 18, 65)
    altura = np.where(genero == "M", rng.normal(173, 7, n),
                      np.where(genero == "F", rng.normal(160, 6.5, n), rng.normal(166, 8, n)))
    altura = np.clip(altura, 145, 205).round(1)
    peso0 = np.where(genero == "M", rng.normal(84, 12, n),
                     np.where(genero == "F", rng.normal(70, 11, n), rng.normal(76, 12, n)))
    peso0 = np.clip(peso0 + 6.0 * (objetivo == "bajar_peso"), 45, 160)
    cint0 = 40 + 0.55 * peso0 + rng.normal(0, 3, n)
    bra0 = 20 + 0.16 * peso0 + rng.normal(0, 1.5, n)
    pec0 = 55 + 0.50 * peso0 + rng.normal(0, 3, n)

    # perfil oculto: constancia, sensibilidad del cuerpo al entrenamiento y abandono
    c = rng.beta(2.2, 2.8, n)
    sens = np.clip(rng.uniform(0.6, 1.4, n) * (1 - 0.006 * (edad - 30)), 0.3, 1.6)
    temprano = rng.random(n) < np.clip(0.15 + 0.35 * (1 - c), 0, 1)
    dur_temprano = rng.integers(2, 13, n)
    dur_normal = rng.geometric(0.004 + 0.02 * (1 - c) ** 2)
    drop_w = reg_w + np.where(temprano, dur_temprano, dur_normal)   # primera semana sin actividad
    signo = np.select([obj_cod == 0, obj_cod == 1, obj_cod == 3], [-1.0, 1.0, -0.3], default=0.0)

    fecha_reg = INICIO + (reg_w * 7 + rng.integers(0, 7, n)).astype("timedelta64[D]")
    fecha_nac = fecha_reg - (edad * 365.25).astype(int).astype("timedelta64[D]")
    usuarios = pd.DataFrame({
        "user_id": ids,
        "email": [f"usuario{primer_num + i + 1:07d}@fittrack.test" for i in range(n)],
        "fecha_nacimiento": fecha_str(fecha_nac),
        "genero": genero,
        "ciudad": ciudad,
        "altura_cm": altura,
        "fecha_registro": fecha_str(fecha_reg),
        "objetivo_fitness": objetivo,
        "unidad_peso": unidad,
    })

    # ---------------- simulacion semana a semana ----------------
    Mm = np.full((4, n, T), np.nan)    # medidas semanales (peso, cintura, brazo, pecho) en kg/cm
    w_act = peso0.copy()
    acum = np.zeros(n)
    med = {k: [] for k in ["u", "w", "d", "peso", "cintura", "brazo", "pecho"]}
    rut = {k: [] for k in ["u", "w", "d"]}
    for w in range(T):
        idx = np.nonzero((w >= reg_w) & (w < drop_w))[0]
        if idx.size == 0:
            continue
        lam = (0.6 + 5.0 * c[idx]) * estacion[w] * np.exp(-0.015 * (w - reg_w[idx]))
        s = np.minimum(rng.poisson(lam), 7)
        acum[idx] += s
        w_act[idx] += signo[idx] * 0.13 * sens[idx] * (s - 1.5) + rng.normal(0, 0.2, idx.size)
        w_act[idx] = np.clip(w_act[idx], 40, 200)

        sel = s > 0
        if sel.any():
            rep = np.repeat(idx[sel], s[sel])
            rut["u"].append(rep)
            rut["w"].append(np.full(rep.size, w))
            rut["d"].append(rng.choice(7, size=rep.size, p=P_DIA))

        k = (rng.random(idx.size) < np.clip(0.25 + 1.1 * c[idx], 0.1, 1.0)) * (1 + rng.poisson(0.6, idx.size))
        sel = k > 0
        if sel.any():
            rep = np.repeat(idx[sel], k[sel])
            dp = w_act[rep] - peso0[rep]
            pes = w_act[rep] + rng.normal(0, 0.35, rep.size)
            cin = cint0[rep] + 0.55 * dp + rng.normal(0, 0.6, rep.size)
            bra = (bra0[rep] + 0.03 * dp + 0.004 * acum[rep] * (obj_cod[rep] == 1)
                   + rng.normal(0, 0.25, rep.size))
            pec = pec0[rep] + 0.12 * dp + rng.normal(0, 0.5, rep.size)
            for j, v in enumerate([pes, cin, bra, pec]):
                Mm[j, rep, w] = v
            med["u"].append(rep)
            med["w"].append(np.full(rep.size, w))
            med["d"].append(rng.integers(0, 7, rep.size))
            for nombre, v in zip(["peso", "cintura", "brazo", "pecho"], [pes, cin, bra, pec]):
                med[nombre].append(v)

    # ---------------- tabla medidas (con suciedad controlada) ----------------
    if med["u"]:
        mu = np.concatenate(med["u"])
        mw = np.concatenate(med["w"])
        md = np.concatenate(med["d"])
        fechas = fecha_str(INICIO + (mw * 7 + md).astype("timedelta64[D]"))
        peso = np.concatenate(med["peso"]).round(1)
        cin = np.concatenate(med["cintura"]).round(1)
        bra = np.concatenate(med["brazo"]).round(1)
        pec = np.concatenate(med["pecho"]).round(1)
        peso = np.where(unidad[mu] == "lb", (peso * LB).round(1), peso)
        m = mu.size
        r = rng.integers(0, 3, m)
        malo = rng.random(m) < 0.001
        peso = np.where(malo, np.where(r == 0, peso * 10, np.where(r == 1, -peso, 0.0)), peso)
        cont["atipicos_peso"] += int(malo.sum())
        cols = {}
        for nombre, v in [("cintura", cin), ("brazo", bra), ("pecho", pec)]:
            nulo = rng.random(m) < 0.03
            cont["nulos_" + nombre] += int(nulo.sum())
            cols[nombre] = np.where(nulo, np.nan, v)
        fechas = inyectar_fechas_distintas(rng, fechas, 0.003, cont, "fechas_otro_formato_medidas")
        medidas = pd.DataFrame({
            "medida_id": np.arange(cont["ids_medidas"] + 1, cont["ids_medidas"] + m + 1),
            "user_id": ids[mu], "fecha": fechas, "peso": peso,
            "cintura": cols["cintura"], "brazo": cols["brazo"], "pecho": cols["pecho"],
        })
        cont["ids_medidas"] += m
        medidas = duplicar(rng, medidas, 0.005, cont, "duplicados_medidas")
    else:
        medidas = pd.DataFrame(columns=["medida_id", "user_id", "fecha", "peso", "cintura", "brazo", "pecho"])

    # ---------------- tabla rutinas ----------------
    if rut["u"]:
        ru = np.concatenate(rut["u"])
        rw = np.concatenate(rut["w"])
        rd = np.concatenate(rut["d"])
        m = ru.size
        fechas = fecha_str(INICIO + (rw * 7 + rd).astype("timedelta64[D]"))
        t_idx = elegir_categoria(rng, P_TIPO, obj_cod[ru])
        g_idx = elegir_categoria(rng, P_GRUPO, t_idx)
        tipo = np.array(TIPOS)[t_idx]
        grupo = np.array(GRUPOS)[g_idx]
        base = np.array([52, 40, 35, 30, 50])[t_idx]
        dur = np.clip(rng.normal(base, 12), 15, 120).round().astype(int)
        nej = np.where(np.isin(t_idx, [0, 4]), 2 + rng.poisson(4, m), 1 + rng.poisson(2, m))
        inten = np.clip(np.round(rng.normal(4.5 + 3.0 * c[ru] + 1.0 * (t_idx == 2), 1.5)), 1, 10).astype(int)
        nombre = np.char.add(np.char.capitalize(tipo), np.char.add(" ", np.char.replace(grupo, "_", " ")))
        fechas = inyectar_fechas_distintas(rng, fechas, 0.003, cont, "fechas_otro_formato_rutinas")
        rutinas = pd.DataFrame({
            "rutina_id": np.arange(cont["ids_rutinas"] + 1, cont["ids_rutinas"] + m + 1),
            "user_id": ids[ru], "fecha": fechas, "nombre": nombre, "tipo_enfoque": tipo,
            "grupo_muscular": grupo, "duracion_min": dur, "num_ejercicios": nej, "intensidad": inten,
        })
        cont["ids_rutinas"] += m
        rutinas = duplicar(rng, rutinas, 0.005, cont, "duplicados_rutinas")
    else:
        rutinas = pd.DataFrame(columns=["rutina_id", "user_id", "fecha", "nombre", "tipo_enfoque",
                                        "grupo_muscular", "duracion_min", "num_ejercicios", "intensidad"])

    # ---------------- metas (se deciden mirando la trayectoria real) ----------------
    filas = []
    inicio_busq = reg_w + rng.integers(0, 3, n)
    posible = np.ones(n, dtype=bool)
    todos = np.arange(n)
    for k, p_k in enumerate([1.0, 0.45, 0.12]):
        quiere = posible & (rng.random(n) < p_k)
        r = rng.random(n)
        tipo_cod = np.select(
            [obj_cod == 0, obj_cod == 1, obj_cod == 2, obj_cod == 3],
            [np.where(r < 0.8, 0, 1), np.where(r < 0.5, 0, np.where(r < 0.8, 2, 3)),
             np.zeros(n, dtype=int), np.where(r < 0.5, 1, 0)])
        bajar = obj_cod != 1
        M = Mm[tipo_cod, todos]                                   # (n, T)
        valida = ~np.isnan(M) & (sem[None, :] >= inicio_busq[:, None])
        tiene = quiere & valida.any(axis=1)
        t0 = valida.argmax(axis=1)
        v0 = M[todos, t0]
        frac = np.where(tipo_cod == 0, rng.uniform(0.02, 0.08, n),
                        np.where(tipo_cod == 1, rng.uniform(0.02, 0.07, n), rng.uniform(0.015, 0.05, n)))
        frac = np.where(obj_cod == 2, rng.uniform(0.005, 0.02, n), frac)
        vobj = v0 * (1 + np.where(bajar, -1.0, 1.0) * frac)
        dur_sem = rng.integers(12, 35, n)
        t_lim = t0 + dur_sem
        ventana = ~np.isnan(M) & (sem[None, :] >= t0[:, None]) & (sem[None, :] <= t_lim[:, None])
        logrado = np.where(bajar[:, None], M <= vobj[:, None], M >= vobj[:, None]) & ventana
        cumplida = logrado.any(axis=1)
        t_cumple = logrado.argmax(axis=1)
        estado = np.where(cumplida, "cumplida",
                          np.where(t_lim >= T,
                                   np.where(drop_w < T, "abandonada", "activa"),
                                   np.where(drop_w <= t_lim, "abandonada", "vencida")))
        sel = np.nonzero(tiene)[0]
        if sel.size:
            f_cre = INICIO + (t0[sel] * 7 + rng.integers(0, 7, sel.size)).astype("timedelta64[D]")
            f_lim = f_cre + (dur_sem[sel] * 7).astype("timedelta64[D]")
            es_peso_lb = (tipo_cod[sel] == 0) & (unidad[sel] == "lb")
            factor = np.where(es_peso_lb, LB, 1.0)
            filas.append(pd.DataFrame({
                "user_id": ids[sel],
                "tipo_medida": np.array(MEDIDAS)[tipo_cod[sel]],
                "valor_inicial": (v0[sel] * factor).round(1),
                "valor_objetivo": (vobj[sel] * factor).round(1),
                "direccion": np.where(bajar[sel], "bajar", "subir"),
                "fecha_creacion": fecha_str(f_cre),
                "fecha_limite": fecha_str(f_lim),
                "estado": estado[sel],
            }))
        inicio_busq = np.where(cumplida, t_cumple, t_lim) + 1
        posible = tiene & (inicio_busq < drop_w) & (inicio_busq < T - 1)
    if filas:
        metas = pd.concat(filas, ignore_index=True)
        metas.insert(0, "meta_id", np.arange(cont["ids_metas"] + 1, cont["ids_metas"] + len(metas) + 1))
        cont["ids_metas"] += len(metas)
    else:
        metas = pd.DataFrame(columns=["meta_id", "user_id", "tipo_medida", "valor_inicial", "valor_objetivo",
                                      "direccion", "fecha_creacion", "fecha_limite", "estado"])

    oculto = pd.DataFrame({
        "user_id": ids,
        "constancia": c.round(4),
        "sensibilidad": sens.round(4),
        "abandono_temprano": temprano,
        "semana_primera_inactiva": np.where(drop_w < T, drop_w, -1),
        "peso_inicial_kg": peso0.round(1),
    })
    cont["usuarios_lb"] += int((unidad == "lb").sum())
    return usuarios, medidas, metas, rutinas, oculto


def escribir(df, ruta, primero):
    df.to_csv(ruta, mode="w" if primero else "a", header=primero, index=False)


def main():
    args = parsear()
    os.makedirs(os.path.join(args.salida, "clave_respuestas"), exist_ok=True)
    estacion, p_reg = calendario()
    cont = {k: 0 for k in [
        "ids_medidas", "ids_rutinas", "ids_metas", "usuarios_lb", "atipicos_peso",
        "nulos_cintura", "nulos_brazo", "nulos_pecho", "duplicados_medidas", "duplicados_rutinas",
        "fechas_otro_formato_medidas", "fechas_otro_formato_rutinas"]}
    filas = {"usuarios": 0, "medidas": 0, "metas": 0, "rutinas": 0}
    rutas = {
        "usuarios": os.path.join(args.salida, "usuarios.csv"),
        "medidas": os.path.join(args.salida, "medidas.csv"),
        "metas": os.path.join(args.salida, "metas.csv"),
        "rutinas": os.path.join(args.salida, "rutinas.csv"),
        "oculto": os.path.join(args.salida, "clave_respuestas", "usuarios_ocultos.csv"),
    }
    t_ini = time.time()
    for b, inicio in enumerate(range(0, args.usuarios, args.bloque)):
        n = min(args.bloque, args.usuarios - inicio)
        rng = np.random.default_rng([args.semilla, b])
        usuarios, medidas, metas, rutinas, oculto = generar_bloque(rng, n, inicio, estacion, p_reg, cont)
        for nombre, df in [("usuarios", usuarios), ("medidas", medidas), ("metas", metas), ("rutinas", rutinas)]:
            escribir(df, rutas[nombre], b == 0)
            filas[nombre] += len(df)
        escribir(oculto, rutas["oculto"], b == 0)
        print(f"  bloque {b + 1}: {inicio + n}/{args.usuarios} usuarios ({time.time() - t_ini:.0f} s)", flush=True)

    meta = {
        "nombre": "FitTrack-Synth", "semilla": args.semilla, "usuarios": args.usuarios,
        "semanas": SEMANAS, "desde": "2025-01-06", "hasta": "2026-07-05",
        "filas": filas, "filas_total": sum(filas.values()),
        "suciedad_inyectada": {k: v for k, v in cont.items() if not k.startswith("ids_")},
        "segundos": round(time.time() - t_ini, 1),
    }
    with open(os.path.join(args.salida, "clave_respuestas", "metadatos.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
