FROM node:20-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install --ignore-scripts

# Copy source code (be more specific than ". .")
COPY src/ ./src/
COPY public/ ./public/
COPY index.html tsconfig.json tsconfig.node.json vite.config.ts .eslintrc.cjs ./

# Build the application
RUN npm run build

# Production stage
FROM nginx:stable-alpine

# Create a non-root user for nginx
RUN addgroup -g 101 -S nginx \
    && adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx \
    && mkdir -p /var/cache/nginx /var/log/nginx \
    && chown -R nginx:nginx /var/cache/nginx /var/log/nginx

# Copy built files from build stage to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Create custom nginx configuration that runs as non-root
RUN mkdir -p /etc/nginx/conf.d
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf || echo 'server { \
    listen 8080; \
    root /usr/share/nginx/html; \
    index index.html; \
    server_name localhost; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Update permissions for nginx directories
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /etc/nginx && \
    chmod -R 755 /usr/share/nginx/html && \
    chmod -R 755 /etc/nginx

# Use a non-privileged port
EXPOSE 8080

# Set nginx to run as non-root
USER nginx

CMD ["nginx", "-g", "daemon off;"] 