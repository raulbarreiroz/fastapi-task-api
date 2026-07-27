import http from 'k6/http';
import { check, sleep } from 'k6';

// Configuration of the test (simulate 10 concurrent users for 30 seconds)
export const options = {
    stages: [
        { duration: '10s', target: 10}, // Goes from 0 to 10 users in 10 seconds
        { duration: '20s', target: 10}, // Maintains 10 users for 20 seconds
        { duration: '5s', target: 0}, // Goes from 10 to 0 users in 5 seconds
    ],
    thresholds: {
        'http_req_duration': ['p(95)<500'], // 95% of requests should be less than 500ms
        'http_req_failed': ['rate<0.01'], // Less than 1% of requests should fail
    },
}

export default function () {
    // 1. Authentication (using bearer token)
    const headers = {
        'Authorization': `Bearer ${__ENV.API_TOKEN}`,
        'Content-Type': 'application/json',
    }

    // 2. Simulate the task creation process
    const payload = JSON.stringify({
        title: `Load Test Task ${__VU}-${__ITER}`,
        description: `This is a load test task created by user ${__VU}`,
        completed: false,
    })

    const res = http.post('http://host.docker.internal:8000/api/v1/tasks', payload, { headers });

    // 3. Check the response (has to be 201 Created)
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

    // 4. Simulate time of user to complete the task
    sleep(0.2)
}

/*
test with docker:
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd)/tests:/tests" \
  -e API_TOKEN="valid-token" \
  -e K6_OUT=json=/tests/results.json \
  grafana/k6 run --summary-export=/tests/summary.json /tests/load-test.js
*/