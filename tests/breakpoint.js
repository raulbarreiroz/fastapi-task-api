import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    breakpoint: {
      executor: 'ramping-arrival-rate',
      startRate: 0,          // Comenzamos desde 0 peticiones/segundo
      timeUnit: '1s',        // La unidad de tiempo para 'rate' es 1 segundo
      preAllocatedVUs: 500,  // VUs reservados para evitar cuellos de botella
      maxVUs: 1000,          // VUs máximos que se pueden crear si es necesario
      stages: [
        { duration: '10m', target: 200 }, // Sube de 0 a 200 RPS en 10 minutos
        // Añade más stages si quieres seguir subiendo, por ejemplo:
        // { duration: '5m', target: 500 },
      ],
    },
  },
  thresholds: {
    http_req_duration: [
      {
        threshold: 'p(95)<2000', // El 95% de peticiones debe ser < 2000ms
        abortOnFail: true,       // ¡Para la prueba si no se cumple!
        delayAbortEval: '30s',   // Espera 30s para evaluar, evitando falsos positivos
      },
    ],
    http_req_failed: [
      {
        threshold: 'rate<0.01',  // La tasa de error debe ser menor al 1%
        abortOnFail: true,       // ¡Para la prueba si la tasa de error sube!
        delayAbortEval: '30s',
      },
    ],
  },
};

export default function () {
  // --- ¡AQUÍ VA TU CÓDIGO DE PRUEBA! ---
  // Copia y pega la lógica de tu script actual:
  const headers = {
    'Authorization': `Bearer ${__ENV.API_TOKEN}`,
    'Content-Type': 'application/json',
  };

  const payload = JSON.stringify({
    title: `Load Test Task ${__VU}-${__ITER}`,
    description: `This is a load test task created by user ${__VU}`,
    completed: false,
  });

  const res = http.post('http://host.docker.internal:8000/api/v1/tasks', payload, { headers });

  check(res, {
    'status is 201': (r) => r.status === 201,
    'response has id': (r) => {
      try {
        return r.body && JSON.parse(r.body).id !== undefined;
      } catch (e) {
        return false;
      }
    },
  });

  sleep(0.2);
}

/*
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd)/tests:/tests" \
  -e API_TOKEN="valid-token" \
  -e K6_OUT=json=/tests/results-breakpoint.json \
  grafana/k6 run --summary-export=/tests/summary-breakpoint.json /tests/breakpoint.js
  
*/
