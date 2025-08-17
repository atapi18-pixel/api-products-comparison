# Multi-stage build with Node 20
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy all source files
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config or create default
RUN echo 'events { worker_connections 1024; } \
http { \
  include /etc/nginx/mime.types; \
  server { \
    listen 80; \
    location / { \
      root /usr/share/nginx/html; \
      index index.html; \
      try_files $uri $uri/ /index.html; \
    } \
    location /api/ { \
      proxy_pass http://backend:5000; \
      proxy_set_header Host $host; \
    } \
    location /health { \
      return 200 "healthy"; \
      add_header Content-Type text/plain; \
    } \
  } \
}' > /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
