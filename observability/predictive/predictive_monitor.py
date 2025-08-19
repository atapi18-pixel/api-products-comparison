#!/usr/bin/env python3
"""Predictive Monitor Service

Heurística simples para detectar tendência de violação de SLO (latência p95, erro %, memória)
com regressão linear e tomar ação de self-healing chamando endpoints admin.

Env vars:
  PROM_URL=http://prometheus:9090
  TARGET_SERVICE_BASE=http://app:8000
  ADMIN_TOKEN=secret
  SLO_P95_MS=300
  SLO_ERROR_RATE=0.02
  MEM_MAX_BYTES=300000000
  PREDICT_HORIZON_SECONDS=180
  QUERY_STEP=30s
  AUTO_HEAL=1
  WHATSAPP_WEBHOOK_URL=http://whatsapp-webhook:5000/webhook/whatsapp/critical
"""
import os, time, json, statistics, requests
from prometheus_client import Counter, Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime, timezone

PROM = os.getenv('PROM_URL','http://prometheus:9090')
BASE = os.getenv('TARGET_SERVICE_BASE','http://app:8000')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN','secret')
SLO_P95_MS = int(os.getenv('SLO_P95_MS','300'))
P95_TIMEOUT_MS = int(os.getenv('P95_TIMEOUT_MS','5000'))  # ponto em que timeout real ocorre
SLO_P95_EXIT_MS = int(os.getenv('SLO_P95_EXIT_MS', str(int(SLO_P95_MS * 0.9))))  # histerese: sair do estado de risco
SLO_ERROR = float(os.getenv('SLO_ERROR_RATE','0.02'))
MEM_MAX = int(os.getenv('MEM_MAX_BYTES','300000000'))
HORIZON = int(os.getenv('PREDICT_HORIZON_SECONDS','180'))
AUTO_HEAL = os.getenv('AUTO_HEAL','1') in ('1','true','True')
STEP = os.getenv('QUERY_STEP','30s')
# --- Novos parâmetros configuráveis para reagir mais rápido pós-mitigação ---
P95_TREND_RANGE = os.getenv('P95_TREND_RANGE','5m')              # janela longa usada na série para forecast
P95_FAST_WINDOW = os.getenv('P95_FAST_WINDOW','30s')              # janela curta para detecção rápida de recuperação (reduzido)
FAST_EXIT_CYCLES = int(os.getenv('FAST_EXIT_CYCLES','2'))         # ciclos consecutivos com fast p95 < EXIT para sair de risco
POST_MIT_FORCE_FAST_EXIT = os.getenv('POST_MIT_FORCE_FAST_EXIT','1') in ('1','true','True')
P95_SHORT_TREND_RANGE = os.getenv('P95_SHORT_TREND_RANGE','2m')   # janela curta adicional para forecast responsivo
POST_MIT_BLEND_SECONDS = int(os.getenv('POST_MIT_BLEND_SECONDS','120'))  # tempo para mesclar fast p95 no forecast
WHATSAPP_URL = os.getenv('WHATSAPP_WEBHOOK_URL')
GRAFANA_BASE = os.getenv('GRAFANA_BASE_URL', 'http://localhost:3000')
DASHBOARD_UID = os.getenv('DASHBOARD_UID', 'predictive-selfheal')
LOG_FILE_PATH = os.getenv('PREDICTIVE_LOG_FILE', '/logs/predictive-monitor.log')
GRAFANA_API_TOKEN = os.getenv('GRAFANA_API_TOKEN')
GRAFANA_USER = os.getenv('GRAFANA_USER')
GRAFANA_PASSWORD = os.getenv('GRAFANA_PASSWORD')
SESSION = requests.Session()
LAST_MIT_UNIX = None  # global state to compute age since last mitigation

# Versão do código para verificação rápida (atualize ao adicionar métricas novas)
VERSION = "2025-08-18-risk-metrics"

# Prometheus predictive-specific registry & metrics (isolated to avoid clashes)
REGISTRY = CollectorRegistry()
PREDICT_CYCLES = Counter('predict_cycles_total', 'Total de ciclos de previsão executados', registry=REGISTRY)
PREDICT_MITIGATIONS = Counter('predict_mitigations_total', 'Total de mitigações automáticas disparadas', registry=REGISTRY)
P95_FORECAST = Gauge('predict_forecast_p95_ms', 'Último forecast de latência p95 (ms)', registry=REGISTRY)
PREDICT_PROB = Gauge('predict_probability', 'Probabilidade heurística calculada para risco (0-1)', registry=REGISTRY)
PREDICT_R2 = Gauge('predict_r2', 'R2 simples da regressão de p95', registry=REGISTRY)
PREDICT_COOLDOWN = Gauge('predict_cooldown_active', 'Cooldown ativo (1=sim,0=não)', registry=REGISTRY)
PREDICT_SINCE_LAST = Gauge('predict_since_last_mitigation_seconds', 'Segundos desde a última mitigação', registry=REGISTRY)
PREDICT_RISK_CYCLES = Counter('predict_risk_cycles_total', 'Total de ciclos em estado de risco', registry=REGISTRY)
PREDICT_OK_CYCLES = Counter('predict_ok_cycles_total', 'Total de ciclos em estado OK', registry=REGISTRY)
PREDICT_RISK_STATE = Gauge('predict_in_risk_state', 'Estado atual de risco (1=risco,0=ok)', registry=REGISTRY)
PREDICT_BUILD_INFO = Gauge('predict_monitor_build_info', 'Info de build do predictive monitor', ['version'], registry=REGISTRY)
PREDICT_BUILD_INFO.labels(version=VERSION).set(1)

METRICS_PORT = int(os.getenv('PREDICT_METRICS_PORT','9105'))
COOLDOWN_SEC = int(os.getenv('PREDICT_COOLDOWN_SECONDS','600'))  # aumentado para evitar mitigacoes seguidas
PROB_STRONG = float(os.getenv('PREDICT_PROB_STRONG','0.6'))  # prob acima da qual mitiga direto
PROB_CONFIRM_MIN = float(os.getenv('PREDICT_PROB_CONFIRM_MIN','0.3'))  # faixa de confirmação dupla
MIN_R2 = float(os.getenv('PREDICT_MIN_R2','0.2'))
PRE_TIMEOUT_RATIO = float(os.getenv('PREDICT_PRE_TIMEOUT_RATIO','0.9'))  # mitigar se forecast alcançar 90% do timeout
# Parâmetros de recuperação pós-mitigação
POST_MIT_GRACE_CYCLES = int(os.getenv('POST_MIT_GRACE_CYCLES','3'))  # ciclos marcados como OK após mitigação
POST_MIT_RISK_REENTER_RATIO = float(os.getenv('POST_MIT_RISK_REENTER_RATIO','1.2'))  # exige forecast > SLO * ratio para reentrar em risco durante cooldown
_weak_prev_cycle = False  # estado para confirmação dupla
_in_risk_state = False    # estado de histerese
last_mitigation_time = None
_fast_ok_streak = 0       # contador de ciclos bons na janela rápida
_post_mit_grace = 0       # ciclos restantes em modo graça pós-mitigação

def log_json(obj: dict):
    """Print JSON to stdout and append to log file (best-effort)."""
    line = json.dumps(obj)
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def prom_query_range(expr, minutes=10):
    end = int(time.time())
    start = end - minutes*60
    params = {'query': expr, 'start': start, 'end': end, 'step': STEP}
    r = SESSION.get(f"{PROM}/api/v1/query_range", params=params, timeout=10)
    r.raise_for_status()
    data = r.json()['data']['result']
    if not data:
        return []
    # usar primeira série
    return [float(v[1]) for v in data[0]['values'] if v[1] is not None]

def prom_query_instant(expr):
    """Executa query instantânea e retorna primeiro valor (float) ou None."""
    try:
        r = SESSION.get(f"{PROM}/api/v1/query", params={'query': expr}, timeout=10)
        r.raise_for_status()
        data = r.json()['data']['result']
        if not data:
            return None
        v = data[0]['value'][1]
        return float(v) if v is not None else None
    except Exception:
        return None

def linear_forecast(series, horizon_s, step_s):
    # Accept even very small series; with <3 points fallback to last value forecast
    if len(series) == 0:
        return None, 0, 0
    if len(series) < 3:
        return series[-1], 0, 0
    n = len(series)
    xs = list(range(n))
    mean_x = statistics.mean(xs)
    mean_y = statistics.mean(series)
    num = sum((x-mean_x)*(y-mean_y) for x,y in zip(xs,series))
    den = sum((x-mean_x)**2 for x in xs) or 1e-6
    slope = num/den  # units per index
    intercept = mean_y - slope*mean_x
    # R2 calculation
    ss_tot = sum((y-mean_y)**2 for y in series) or 1e-6
    ss_res = sum((y - (intercept + slope*x))**2 for x,y in zip(xs,series))
    r2 = 1 - (ss_res/ss_tot)
    step_seconds = step_s
    horizon_idx = horizon_s/step_seconds
    forecast = series[-1] + slope * horizon_idx
    return forecast, slope * (1/step_seconds), r2  # slope per second & r2

def send_whatsapp(msg):
    if not WHATSAPP_URL:
        return
    try:
        SESSION.post(WHATSAPP_URL, json={'alerts':[{'annotations':{'summary':msg,'description':msg},'labels':{'severity':'critical'}}]}, timeout=5)
    except Exception:
        pass

def mitigate():
    try:
        SESSION.post(
            f"{BASE}/admin/mitigate",
            headers={'x-admin-token': ADMIN_TOKEN, 'x-predictive-automated': '1'},
            timeout=5
        )
        return True
    except Exception:
        return False

def grafana_annotate(text, tags):
    if not GRAFANA_BASE:
        return
    url = f"{GRAFANA_BASE}/api/annotations"
    payload = {"time": int(time.time()*1000), "tags": tags, "text": text}
    headers = {}
    auth = None
    if GRAFANA_API_TOKEN:
        headers['Authorization'] = f"Bearer {GRAFANA_API_TOKEN}"
    elif GRAFANA_USER and GRAFANA_PASSWORD:
        auth = (GRAFANA_USER, GRAFANA_PASSWORD)
    try:
        SESSION.post(url, json=payload, headers=headers, auth=auth, timeout=5)
    except Exception:
        pass

def predictive_cycle():
    step_seconds = int(STEP.strip('s'))
    # Queries
    # Janela longa para tendência / forecast (configurável)
    p95_expr = f"histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[{P95_TREND_RANGE}])) by (le)) * 1000"
    # Janela curta para detecção rápida de recuperação pós mitigação
    fast_p95_expr = f"histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[{P95_FAST_WINDOW}])) by (le)) * 1000"
    err_expr = "(sum(increase(http_request_errors_total[5m])))/(sum(increase(http_requests_total[5m]))+1e-9)"
    mem_expr = "process_resident_memory_bytes"
    p95_series = prom_query_range(p95_expr)
    err_series = prom_query_range(err_expr)
    mem_series = prom_query_range(mem_expr)

    results = []
    now = _now_iso()

    def evaluate(name, series, threshold, unit, kind):
        if not series:
            return
        forecast, slope_per_sec, r2 = linear_forecast(series, HORIZON, step_seconds)
        if forecast is None:
            return
        current = series[-1]
        breach = forecast > threshold
        results.append({
            'metric': name,
            'current': current,
            'forecast': forecast,
            'threshold': threshold,
            'unit': unit,
            'slope_per_sec': slope_per_sec,
            'breach_predicted': breach,
            'r2': r2
        })

    evaluate('latency_p95_ms', p95_series, SLO_P95_MS, 'ms', 'latency')
    evaluate('error_rate', err_series, SLO_ERROR, '', 'error')
    evaluate('memory_bytes', mem_series, MEM_MAX, 'bytes', 'memory')

    breach_any = any(r['breach_predicted'] for r in results)
    action_taken = None
    reason = None
    top = None
    global LAST_MIT_UNIX
    global last_mitigation_time

    # Compute effective forecast combining long & short windows + fast observed p95 post-mitigation
    latency_entry = next((r for r in results if r['metric']=='latency_p95_ms'), None)
    prob = None
    r2_val = None
    if latency_entry:
        long_forecast = latency_entry['forecast']
        # short trend series
        short_series = []
        if P95_SHORT_TREND_RANGE:
            try:
                short_expr = f"histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[{P95_SHORT_TREND_RANGE}])) by (le)) * 1000"
                short_series = prom_query_range(short_expr)
            except Exception:
                short_series = []
        short_forecast = None
        if short_series:
            try:
                sf,_,_ = linear_forecast(short_series, HORIZON, step_seconds)
                short_forecast = sf
            except Exception:
                pass
        effective = long_forecast
        if short_forecast is not None:
            effective = min(effective, short_forecast)
        # blend pós-mitigação usando fast p95 observado
        fast_obs = None
        try:
            fast_obs = prom_query_instant(f"histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[{P95_FAST_WINDOW}])) by (le)) * 1000")
        except Exception:
            pass
        if last_mitigation_time and (time.time() - last_mitigation_time) < POST_MIT_BLEND_SECONDS:
            if fast_obs is not None:
                effective = min(effective, fast_obs)
        latency_entry['effective_forecast'] = effective
        try:
            if effective <= SLO_P95_MS:
                prob = 0.0
            elif effective >= P95_TIMEOUT_MS:
                prob = 1.0
            else:
                prob = (effective - SLO_P95_MS) / max(1.0, (P95_TIMEOUT_MS - SLO_P95_MS))
        except Exception:
            prob = 0.0
        P95_FORECAST.set(effective)
        PREDICT_PROB.set(prob if prob is not None else 0.0)
        if 'r2' in latency_entry and latency_entry['r2'] is not None:
            r2_val = latency_entry['r2']
            PREDICT_R2.set(r2_val)

    # Cooldown state
    cooldown_active = 0
    if last_mitigation_time and (time.time() - last_mitigation_time) < COOLDOWN_SEC:
        cooldown_active = 1
    PREDICT_COOLDOWN.set(cooldown_active)
    # --- Nova lógica de decisão com histerese, confirmação dupla e pré-timeout ---
    global _weak_prev_cycle, _in_risk_state
    decision_detail = None
    latency_entry = next((r for r in results if r['metric']=='latency_p95_ms'), None)
    prob = None
    r2_val = None
    if latency_entry and 'effective_forecast' in latency_entry:
        eff_fc = latency_entry['effective_forecast']
    else:
        eff_fc = latency_entry['forecast'] if latency_entry else None
    if latency_entry and prob is None and eff_fc is not None:
        if eff_fc <= SLO_P95_MS:
            prob = 0.0
        elif eff_fc >= P95_TIMEOUT_MS:
            prob = 1.0
        else:
            prob = (eff_fc - SLO_P95_MS) / max(1.0,(P95_TIMEOUT_MS - SLO_P95_MS))
    if latency_entry and r2_val is None:
        r2_val = latency_entry.get('r2')

    # --- Atualizar estado de histerese com detecção acelerada + pós-mitigação ---
    global _fast_ok_streak, _post_mit_grace
    fast_current_p95 = prom_query_instant(fast_p95_expr)
    fast_exit_hit = False
    if fast_current_p95 is not None and fast_current_p95 < SLO_P95_EXIT_MS:
        _fast_ok_streak += 1
        if _fast_ok_streak >= FAST_EXIT_CYCLES:
            fast_exit_hit = True
    else:
        _fast_ok_streak = 0

    if _post_mit_grace > 0:
        # força estado OK independentemente de forecast para evitar re-mitigação precoce
        _in_risk_state = False
        _post_mit_grace -= 1
    else:
        if _in_risk_state:
            # Sair se forecast caiu abaixo EXIT ou janela rápida confirma
            if (latency_entry and eff_fc is not None and eff_fc < SLO_P95_EXIT_MS) or fast_exit_hit:
                _in_risk_state = False
                decision_detail = (decision_detail or '') + ' fast_exit'
                _fast_ok_streak = 0
        else:
            if latency_entry:
                # Reentrada mais difícil durante cooldown pós-mitigação
                enter_threshold = SLO_P95_MS
                if last_mitigation_time and (time.time() - last_mitigation_time) < COOLDOWN_SEC:
                    enter_threshold = SLO_P95_MS * POST_MIT_RISK_REENTER_RATIO
                if eff_fc is not None and eff_fc > enter_threshold:
                    _in_risk_state = True

    # contabilizar estado do ciclo atual
    # Expor série contínua do estado (gauge) e incrementar o counter apropriado
    if _in_risk_state:
        PREDICT_RISK_STATE.set(1)
        PREDICT_RISK_CYCLES.inc()
    else:
        PREDICT_RISK_STATE.set(0)
        PREDICT_OK_CYCLES.inc()

    can_act = AUTO_HEAL and cooldown_active == 0 and latency_entry and r2_val is not None and r2_val >= MIN_R2
    early_timeout = latency_entry and eff_fc is not None and eff_fc >= PRE_TIMEOUT_RATIO * P95_TIMEOUT_MS
    strong = prob is not None and prob >= PROB_STRONG
    weak_band = prob is not None and PROB_CONFIRM_MIN <= prob < PROB_STRONG

    trigger = False
    if can_act and latency_entry:
        if early_timeout:
            trigger = True
            decision_detail = f"early_timeout {prob:.2f} eff={eff_fc:.0f}"
        elif strong and _in_risk_state:
            trigger = True
            decision_detail = f"strong_prob {prob:.2f} r2={r2_val:.2f}"
        elif weak_band and _in_risk_state:
            if _weak_prev_cycle:
                trigger = True
                decision_detail = f"weak_confirmed {prob:.2f} r2={r2_val:.2f}"
            else:
                decision_detail = f"weak_first {prob:.2f} r2={r2_val:.2f}"
        else:
            decision_detail = f"no_trigger prob={prob if prob is not None else 'na'} r2={r2_val if r2_val is not None else 'na'}"
    else:
        if cooldown_active:
            decision_detail = "cooldown"
        elif not AUTO_HEAL:
            decision_detail = "auto_heal_disabled"
        elif latency_entry is None:
            decision_detail = "no_latency_entry"
        elif r2_val is not None and r2_val < MIN_R2:
            decision_detail = f"low_r2 {r2_val:.2f} < {MIN_R2}"

    if trigger and latency_entry:
        top = latency_entry
        try:
            eff_display = f"{eff_fc:.0f}" if eff_fc is not None else "na"
            reason = (f"Mitigating: p95_raw={top['forecast']:.0f}ms eff={eff_display}ms (prob={prob:.2f}) decision={decision_detail} slo={SLO_P95_MS} timeout={P95_TIMEOUT_MS}")
        except Exception:
            reason = "Mitigating (format error)"
        grafana_link = f"{GRAFANA_BASE}/d/{DASHBOARD_UID}?viewPanel=1"
        msg = f"PREDITIVO: {reason} | Dash: {grafana_link}"
        send_whatsapp(msg)
        grafana_annotate(msg, ["predictive", "mitigation_decision"])
        mitigate()
        action_taken = 'mitigation_called'
        mit_unix = int(time.time())
        mit_event = {
            'ts': _now_iso(),
            'unix_ts': mit_unix,
            'event': 'mitigation executed',
            'metric': 'latency_p95_ms',
            'forecast': top['forecast'],
            'threshold': SLO_P95_MS,
            'probability': prob,
            'r2': r2_val,
            'decision_detail': decision_detail,
            'source': 'predictive-monitor'
        }
        log_json(mit_event)
        LAST_MIT_UNIX = mit_unix
        last_mitigation_time = mit_unix
        PREDICT_MITIGATIONS.inc()
        _weak_prev_cycle = False
        # inicia modo graça
        _post_mit_grace = POST_MIT_GRACE_CYCLES
        _in_risk_state = False
    else:
        # atualizar flag de weak quando não houve trigger
        _weak_prev_cycle = bool(weak_band and can_act and not trigger and _in_risk_state)
    # compute since_last_mitigation if we just mitigated (0) or leave None
    since_last = None
    if LAST_MIT_UNIX is not None:
        since_last = int(time.time()) - LAST_MIT_UNIX
    payload = {
        'ts': now,
        'predictions': results,
        'breach_any': breach_any,
        'action_taken': action_taken,
        'reason': reason,
        'event': 'prediction cycle',
        'since_last_mitigation_sec': since_last,
        'source': 'predictive-monitor',
        'probability': prob,
        'r2': r2_val,
        'decision_detail': decision_detail,
        'in_risk_state': _in_risk_state,
        'cooldown_active': bool(cooldown_active),
    'fast_p95_ms': fast_current_p95,
    'fast_ok_streak': _fast_ok_streak,
    'effective_forecast_ms': eff_fc
    }
    # Ensure the phrase 'mitigation executed' is present in the same line when mitigation happened
    if action_taken == 'mitigation_called':
        payload['mitigation_event'] = 'mitigation executed'
    # Increment cycle counter & update since_last gauge
    PREDICT_CYCLES.inc()
    if since_last is not None:
        PREDICT_SINCE_LAST.set(since_last)
    log_json(payload)

def metrics_app(environ, start_response):
    if environ.get('PATH_INFO') == '/metrics':
        data = generate_latest(REGISTRY)
        start_response('200 OK', [('Content-Type', CONTENT_TYPE_LATEST), ('Content-Length', str(len(data)))])
        return [data]
    start_response('404 Not Found', [('Content-Type','text/plain')])
    return [b'not found']

if __name__ == '__main__':
    # Start simple metrics HTTP server (WSGI style)
    from wsgiref.simple_server import make_server
    metrics_port = METRICS_PORT
    httpd = make_server('', metrics_port, metrics_app)
    print(json.dumps({'ts':_now_iso(),'event':'metrics_server_started','port':metrics_port,'source':'predictive-monitor'}), flush=True)
    interval = int(os.getenv('CYCLE_INTERVAL_SECONDS','30'))
    # Run metrics server in background (basic, single thread) using non-blocking approach
    import threading
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    while True:
        try:
            predictive_cycle()
        except Exception as e:
            err_line = json.dumps({'ts':_now_iso(),'error':str(e),'source':'predictive-monitor'})
            print(err_line, flush=True)
            try:
                with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
                    f.write(err_line + '\n')
            except Exception:
                pass
        time.sleep(interval)
