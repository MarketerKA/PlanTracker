import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 100 }, // Ramp-up to 100 users
    { duration: '30s', target: 300 }, // Ramp-up to 300 users
    { duration: '30s', target: 500 }, // Ramp-up to 500 users
    { duration: '2m', target: 500 },   // Hold at 500 users
    { duration: '30s', target: 0 },    // Ramp-down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s
    http_req_failed: ['rate<0.1'],     // Allow up to 10% failed requests
  },
  insecureSkipTLSVerify: true, // Ignore SSL certificate verification
};

const BASE_URL = 'https://158.160.23.164';
const USER_EMAIL = 'test.user@gmail.com';
const USER_PASSWORD = 'testpassword123';

// Generate a random string for unique activity titles
function randomString(length) {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

export default function () {
  // Step 1: Login and get token
  const loginPayload = JSON.stringify({
    email: USER_EMAIL,
    password: USER_PASSWORD,
  });
  const loginHeaders = { 'Content-Type': 'application/json' };
  const loginRes = http.post(`${BASE_URL}/api/users/login`, loginPayload, { headers: loginHeaders });
  check(loginRes, { 'login status is 200': (r) => r.status === 200 });
  const token = loginRes.json('access_token');

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };

  // Step 2: Test GET /api/activities/
  const activitiesResponse = http.get(`${BASE_URL}/api/activities/`, { headers });
  check(activitiesResponse, {
    'activities status is 200': (r) => r.status === 200,
  });
  sleep(0.5);

  // Step 3: Test GET /api/activities/{id}
  const activityId = 1; // Assumes there is an activity with ID 1
  const activityResponse = http.get(`${BASE_URL}/api/activities/${activityId}`, { headers });
  check(activityResponse, {
    'activity status is 200': (r) => r.status === 200,
  });
  sleep(0.5);

  // Step 4: Test POST /api/activities/
  const payload = JSON.stringify({
    title: 'Test Activity ' + randomString(8),
    description: 'Test Description',
    scheduled_time: new Date().toISOString(),
    tags: ['test'],
    timer_status: 'initial',
  });
  console.log('Sending POST request with payload:', payload);
  const createResponse = http.post(`${BASE_URL}/api/activities/`, payload, { headers });
  console.log('Create response status:', createResponse.status);
  console.log('Create response body:', createResponse.body);
  check(createResponse, {
    'create activity status is 201 or 200': (r) => r.status === 201 || r.status === 200,
  });
  sleep(0.5);
} 