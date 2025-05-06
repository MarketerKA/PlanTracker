FROM node:20-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

# Copy source code
COPY src/ ./src/
COPY public/ ./public/
COPY index.html tsconfig.json tsconfig.node.json tsconfig.app.json vite.config.ts eslint.config.js ./

# Build the application
RUN npm run build

# Production stage with specific NGINX version
FROM nginx:1.25-alpine

# Copy built files from build stage to nginx 
COPY --from=build /app/dist /usr/share/nginx/html

# Create custom nginx config with health check 
RUN echo 'server { \
    listen 8080; \
    root /usr/share/nginx/html; \
    index index.html; \
    server_name localhost; \
    \
    # Security headers \
    add_header X-Content-Type-Options "nosniff"; \
    add_header X-Frame-Options "DENY"; \
    add_header X-XSS-Protection "1; mode=block"; \
    add_header Content-Security-Policy "default-src '\''self'\''; script-src '\''self'\''; object-src '\''none'\''"; \
    \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Use a non-privileged port
EXPOSE 8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Command to run the application
CMD ["nginx", "-g", "daemon off;"] 