#!/usr/bin/env python3
"""Prueba de carga minima para FitTrack, sin dependencias externas.

Usa solo la libreria estandar. Sirve para comparar 1 vs N replicas:
  1. login (o registro si la cuenta no existe),
  2. calentamiento,
  3. N peticiones GET concurrentes,
  4. resumen de RPS, latencias (p50/p90/p95/p99) y errores.

Ejemplo:
  python tests/load/load_test.py --base http://192.168.100.2:8080 \
    --email audit20261105@gmail.com --password Password123 \
    --requests 500 --concurrency 20 --path /api/measurements/
"""
import argparse
import json
import statistics
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


def http_json(method, url, payload=None, token=None, timeout=10):
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, (json.loads(body) if body else None)


def login_or_register(base, email, password, full_name):
    try:
        status, body = http_json("POST", base + "/api/users/login",
                                 {"email": email, "password": password})
        if status == 200 and body and body.get("access_token"):
            return body["access_token"]
    except urllib.error.HTTPError:
        pass
    try:
        http_json("POST", base + "/api/users/register",
                  {"full_name": full_name, "email": email, "password": password})
    except urllib.error.HTTPError as exc:
        if exc.code not in (400, 409):
            raise
    status, body = http_json("POST", base + "/api/users/login",
                             {"email": email, "password": password})
    return body["access_token"]


def one_request(url, token, timeout):
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
            return True, resp.status, (time.perf_counter() - start) * 1000.0
    except urllib.error.HTTPError as exc:
        return False, exc.code, (time.perf_counter() - start) * 1000.0
    except Exception:
        return False, 0, (time.perf_counter() - start) * 1000.0


def percentile(values, p):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((p / 100.0) * (len(ordered) - 1))))
    return ordered[index]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://192.168.100.2:8080")
    parser.add_argument("--email", default="audit20261105@gmail.com")
    parser.add_argument("--password", default="Password123")
    parser.add_argument("--full-name", default="Load Test User")
    parser.add_argument("--path", default="/api/measurements/")
    parser.add_argument("--requests", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    base = args.base.rstrip("/")
    token = login_or_register(base, args.email, args.password, args.full_name)
    url = base + args.path

    # Calentamiento: evita medir el arranque de conexiones y JIT.
    for _ in range(5):
        one_request(url, token, args.timeout)

    latencies = []
    errors = 0
    status_counts = {}
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(one_request, url, token, args.timeout)
                   for _ in range(args.requests)]
        for future in as_completed(futures):
            ok, status, ms = future.result()
            status_counts[status] = status_counts.get(status, 0) + 1
            if ok:
                latencies.append(ms)
            else:
                errors += 1
    wall = time.perf_counter() - start

    result = {
        "base": base,
        "path": args.path,
        "requests": args.requests,
        "concurrency": args.concurrency,
        "ok": len(latencies),
        "errors": errors,
        "status_counts": status_counts,
        "wall_seconds": round(wall, 3),
        "rps": round(len(latencies) / wall, 2) if wall else 0.0,
        "latency_ms": {
            "min": round(min(latencies), 2) if latencies else 0.0,
            "mean": round(statistics.mean(latencies), 2) if latencies else 0.0,
            "p50": round(percentile(latencies, 50), 2),
            "p90": round(percentile(latencies, 90), 2),
            "p95": round(percentile(latencies, 95), 2),
            "p99": round(percentile(latencies, 99), 2),
            "max": round(max(latencies), 2) if latencies else 0.0,
        },
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
