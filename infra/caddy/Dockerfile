# syntax=docker/dockerfile:1
# Edge image: builds the React SPA and bakes it into a Caddy server that also
# reverse-proxies the API. Build context is the repo root.

FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM caddy:2-alpine
COPY infra/caddy/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
