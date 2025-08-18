import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  vus: 3,
  duration: '2m',
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% das requisições devem ser < 1s (exceto timeouts intencionais)
  },
};

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
  
  // A cada 10 iterações, fazer chamada com timeout (delay de 5 segundos)
  if (__ITER % 10 === 0) {
    console.log('⏱️  Testando endpoint com timeout (5s delay) usando X-Delay header...');
    const timeoutResponse = http.get('http://app:8000/v1/products', {
      headers: {
        'X-Delay': '5', // 5 segundos de delay
      },
      timeout: '10s', // timeout de 10s para não falhar o teste
    });
    check(timeoutResponse, {
      'timeout request completed': (r) => r.status === 200,
      'timeout request duration > 5s': (r) => r.timings.duration > 5000,
    });
  }
  
  sleep(1);
}
