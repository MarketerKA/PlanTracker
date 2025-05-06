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
}' > nginx.conf

# Production stage
FROM nginx:stable-alpine

# Set up Nginx to run as root (only for testing)
# This is not recommended for production
ENV NGINX_USER=root

# Copy built files from build stage to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration 
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf

# Create necessary directories with proper permissions
RUN mkdir -p /var/cache/nginx /var/run/nginx && \
    chmod -R 777 /var/cache/nginx /var/run/nginx /var/log/nginx

# Use a non-privileged port
EXPOSE 8080

# Command to run the application
CMD ["nginx", "-g", "daemon off;"] 