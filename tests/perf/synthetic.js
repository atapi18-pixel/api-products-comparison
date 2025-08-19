import http from 'k6/http';
import { check, sleep } from 'k6';

/*
 Synthetic focado em gerar MAIS ciclos OK:
  - REMOVIDAS chamadas automáticas a /admin/mitigate (nenhuma ação de reset aqui).
  - Ciclo encurtado para 60s para o preditor ter mais amostras por unidade de tempo.
  - Fases:
      FAST   (0  - 45s): 100% sem X-Delay (30% SKIP para reduzir ainda mais latência / load) -> deve produzir P95 baixo.
      WARM   (45 - 55s): 10% das requisições com X-Delay=1s.
      STRESS (55 - 60s): 20% com X-Delay=2s e 5% (indep.) com X-Delay=3s.
  - Sem injeção global. Risco manual pode ser feito externamente quando desejar.
  - Ajustar percentuais se ainda faltar ciclos OK (ex: aumentar FAST para 50s ou reduzir probabilidades).
*/

export const options = {
  vus: 10,
  duration: '24h',
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<5000'],
  },
};

const THINK_TIME = 1; // intervalo entre requisições

export function setup() {
  sleep(15); // aguarda serviços subirem
  console.log('Synthetic ONLY-OK iniciado (sem delays)');
}

export default function () {



  const res = http.get('http://app:8000/v1/products', { timeout: '10s' });
  check(res, { 'status 200': r => r.status === 200 });

  try {
    let dur = 'na';
    if (res && res.timings && typeof res.timings.duration === 'number') {
      dur = res.timings.duration.toFixed(1);
    }
    console.log(`[synthetic] vu=${__VU} iter=${__ITER} status=${res.status} dur=${dur}ms`);
  } catch (e) {
    console.error(`[synthetic] log failure: ${e}`);
  }

  sleep(THINK_TIME);
}
