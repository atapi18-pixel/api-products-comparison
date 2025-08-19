import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  vus: 3,
  duration: '1m',
  thresholds: {
    http_req_duration: ['p(99)<1000'], // 99% das requisições devem ser < 1s (exceto timeouts intencionais)
  },
};

// Executado uma única vez antes dos VUs iniciarem
export function setup() {
  const injectResp = http.post('http://app:8000/admin/fault?mode=latency&inc=50', null, {
    headers: { 'x-admin-token': 'secret' }
  });
  if (injectResp.status !== 200) {
    console.error(`Falha ao injetar latência artificial: status=${injectResp.status} body=${injectResp.body}`);
  } else {
    console.log(`✅ Latência artificial injetada: +50ms -> ${injectResp.body}`);
  }
}

export default function () {
  // Chamadas normais da API (maioria do tráfego)
  const normalResponse = http.get('http://app:8000/v1/products');
  check(normalResponse, {
    'status is 200': (r) => r.status === 200,
  });
  
  // A cada 20 iterações, fazer chamadas que geram erro
  if (__ITER % 20 === 0) {
    console.log('🚨 Testando endpoint que gera erro...');
    const errorResponse = http.get('http://app:8000/v1/products/nonexistent');
    check(errorResponse, {
      'error status is 404': (r) => r.status === 404,
    });
  }
  
  // A cada 10 iterações, fazer chamada com timeout (delay de 4 segundos)
  if (__ITER % 10 === 0) {
    console.log('⏱️  Testando endpoint com timeout (4s delay) usando X-Delay header...');
    const timeoutResponse = http.get('http://app:8000/v1/products', {
      headers: {
        'X-Delay': '4', // 4 segundos de delay
      },
      timeout: '5s', // timeout de 5s para não falhar o teste
    });
    check(timeoutResponse, {
      'timeout request completed': (r) => r.status === 200,
      'timeout request duration > 5s': (r) => r.timings.duration > 5000,
    });
  }
  
  sleep(1);
}
