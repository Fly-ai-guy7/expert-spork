# RxEgypt frontend — static file server.
# At startup, docker-entrypoint.sh writes config.js from $RXEGYPT_API_URL so the
# image can point at any backend without editing source.
FROM python:3.11-slim

WORKDIR /app
COPY . .

EXPOSE 3000
CMD ["sh", "/app/docker-entrypoint.sh"]
