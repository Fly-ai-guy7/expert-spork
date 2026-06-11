# Static single-file deploy for AISE Rooms (Fly.io / any static host).
# Serves the shared app + a per-deployment brand.js (white-label override).
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
COPY brand.js   /usr/share/nginx/html/brand.js
EXPOSE 80
