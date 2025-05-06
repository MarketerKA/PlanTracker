# Architecture

```
                       +---------------+
                       |               |
  Internet         +-->|    NGINX      |
  Requests         |   |  (Port 80,443)|
   +--------+      |   |               |
   |        |      |   +-------+-------+
   +--------v------+           |
                               |
                     +---------v----------+     +----------------+
                     |                    |     |                |
                     |     Frontend       +---->+    Backend     |
                     | (Internal Network) |     | (API Server)   |
                     |                    |     |                |
                     +--------------------+     +----------------+
```

## Network Architecture
- NGINX: Exposed to the internet (ports 80, 443)
- Frontend: Internal network, only accessible via NGINX
- Backend: Internal network, only accessible via Frontend

## Container Communication
- Frontend → Backend: API calls
- NGINX → Frontend: Proxied requests
- NGINX → Backend: Direct API requests via /api/ path

## Security
- Only NGINX is exposed to the internet
- Environment variables for secrets
- SSL termination at NGINX
- Internal Docker network for service communication 