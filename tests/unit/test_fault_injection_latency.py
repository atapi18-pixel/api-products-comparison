#!/usr/bin/env python3
"""Tests relacionados à injeção de latência artificial e sua composição com X-Delay.

Cenários:
1. Injeta latência artificial e verifica impacto em request sem X-Delay.
2. Composição: X-Delay + latência artificial => tempo >= soma aproximada.
3. Mitigate reseta latência artificial reduzindo tempo subsequente.

Notas:
- Usamos margens de tolerância porque a execução local pode variar.
- Não testamos exatamente igualdade e sim faixas mínimas.
"""

import time
from fastapi.testclient import TestClient
from app.main import app


ADMIN_TOKEN = "secret"  # default conforme main.py


def _inject_latency(ms: int):
    client = TestClient(app)
    r = client.post(f"/admin/fault?mode=latency&inc={ms}", headers={"x-admin-token": ADMIN_TOKEN})
    assert r.status_code == 200, r.text
    return r.json()


def _mitigate():
    client = TestClient(app)
    r = client.post("/admin/mitigate", headers={"x-admin-token": ADMIN_TOKEN})
    assert r.status_code == 200, r.text
    return r.json()


def test_artificial_latency_injection_affects_requests():
    client = TestClient(app)
    _mitigate()  # garante estado limpo

    # baseline sem latência artificial
    start = time.time()
    r = client.get("/v1/products")
    base_duration = time.time() - start
    assert r.status_code == 200

    # injeta 200ms
    _inject_latency(200)

    start = time.time()
    r2 = client.get("/v1/products")
    dur_with_latency = time.time() - start
    assert r2.status_code == 200

    # Deve ser pelo menos ~0.18s maior (tolerância de 20ms)
    assert dur_with_latency >= base_duration + 0.18


def test_composed_latency_with_x_delay():
    client = TestClient(app)
    _mitigate()
    _inject_latency(150)  # 150ms = 0.15s

    start = time.time()
    r = client.get("/v1/products", headers={"X-Delay": "1"})  # 1s + 0.15s
    elapsed = time.time() - start
    assert r.status_code == 200

    # Esperado >= 1.10s (tolerância para jitter)
    assert elapsed >= 1.10


def test_mitigate_resets_latency():
    client = TestClient(app)
    _mitigate()
    _inject_latency(300)  # 0.3s

    # Request com latência
    t1 = time.time(); client.get("/v1/products"); d1 = time.time() - t1
    assert d1 >= 0.25  # tolerância ~50ms

    # Mitiga
    _mitigate()

    t2 = time.time(); client.get("/v1/products"); d2 = time.time() - t2

    # Após mitigação deve reduzir substancialmente (>120ms de diferença)
    assert (d1 - d2) >= 0.12
