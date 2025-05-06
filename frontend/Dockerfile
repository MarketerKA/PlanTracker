FROM node:20-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install --ignore-scripts

# Copy source code
COPY src/ ./src/
COPY public/ ./public/
COPY index.html tsconfig.json tsconfig.node.json tsconfig.app.json vite.config.ts eslint.config.js ./

# Build the application
RUN npm run build

# Production stage
FROM nginx:stable-alpine

# Copy built files from build stage to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Configure nginx
RUN echo 'server { \
    listen 8080; \
    root /usr/share/nginx/html; \
    index index.html; \
    server_name localhost; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Use non-privileged port
EXPOSE 8080

# Use non-root user
USER nginx

CMD ["nginx", "-g", "daemon off;"] 