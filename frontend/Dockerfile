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

# Production stage with latest nginx alpine image
FROM nginx:1.27-alpine

# Create non-root user with a non-conflicting UID
RUN adduser -D -H -u 1001 -s /sbin/nologin nginx-user

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
        add_header Cache-Control "no-cache, no-store, must-revalidate"; \
        add_header Pragma "no-cache"; \
        add_header Expires "0"; \
    } \
    \
    location /assets/ { \
        try_files $uri =404; \
        expires 1y; \
        add_header Cache-Control "public, no-transform"; \
        add_header X-Content-Type-Options "nosniff"; \
        add_header X-Frame-Options "DENY"; \
        add_header X-XSS-Protection "1; mode=block"; \
    } \
    \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Update packages to fix vulnerabilities and remove unnecessary packages
RUN apk update && \
    apk upgrade --no-cache && \
    # Install only required curl version with minimal dependencies
    apk add --no-cache wget && \
    # Remove unnecessary packages that might have vulnerabilities
    apk del --no-cache curl && \
    rm -rf /var/cache/apk/*

# Copy healthcheck script
COPY healthcheck.sh /usr/local/bin/healthcheck.sh

# Create necessary directories with proper permissions
RUN mkdir -p /var/cache/nginx /var/run/nginx && \
    chown -R nginx-user:nginx-user /var/cache/nginx /var/run/nginx /var/log/nginx /usr/share/nginx/html && \
    chmod -R 755 /var/cache/nginx /var/run/nginx /var/log/nginx /usr/share/nginx/html && \
    # Remove default nginx.pid and create a new one with correct permissions
    rm -f /var/run/nginx.pid && \
    touch /var/run/nginx.pid && \
    chown nginx-user:nginx-user /var/run/nginx.pid && \
    chmod 644 /var/run/nginx.pid && \
    # Set permissions for healthcheck script
    chmod +x /usr/local/bin/healthcheck.sh && \
    chown nginx-user:nginx-user /usr/local/bin/healthcheck.sh

# Use a non-privileged port
EXPOSE 8080

# Add healthcheck using the script with exec form
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD ["/usr/local/bin/healthcheck.sh"]

# Switch to non-root user
USER nginx-user

# Command to run the application
CMD ["nginx", "-g", "daemon off;"] 