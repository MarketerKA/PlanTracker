FROM node:20-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install --ignore-scripts

# Copy source code (be more specific than ". .")
COPY src/ ./src/
COPY public/ ./public/
COPY index.html tsconfig.json tsconfig.node.json tsconfig.app.json vite.config.ts eslint.config.js ./

# Build the application
RUN npm run build

# Create a default nginx configuration
RUN echo 'server { \
    listen 8080; \
    root /usr/share/nginx/html; \
    index index.html; \
    server_name localhost; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
    } \
}' > nginx.conf

# Production stage
FROM nginx:stable-alpine

# Create non-root user
RUN adduser -D -H -u 101 -s /sbin/nologin nginx-user

# Copy built files from build stage to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration 
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf

# Create necessary directories with proper permissions
RUN mkdir -p /var/cache/nginx /var/run/nginx && \
    chown -R nginx-user:nginx-user /var/cache/nginx /var/run/nginx /var/log/nginx /usr/share/nginx/html && \
    chmod -R 755 /var/cache/nginx /var/run/nginx /var/log/nginx /usr/share/nginx/html

# Use a non-privileged port
EXPOSE 8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Switch to non-root user
USER nginx-user

# Command to run the application
CMD ["nginx", "-g", "daemon off;"] 