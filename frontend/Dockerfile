# Luxor Guest House frontend — static build served by nginx (Cloud Run-ready).
# VITE_API_URL is baked at build time (Vite inlines env vars), so pass it as a
# build arg:  docker build --build-arg VITE_API_URL=https://api.example.com .

# --- build stage ---
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# --- serve stage ---
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
# Cloud Run expects the container to listen on 8080.
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
