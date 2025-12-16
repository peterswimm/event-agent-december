# Minimal container exposing only 8010 via NGINX reverse proxy
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app/eventkit
COPY agent.py /app/eventkit/agent.py
COPY agent.json /app/eventkit/agent.json
COPY telemetry.py /app/eventkit/telemetry.py
COPY deploy/nginx.conf /etc/nginx/nginx.conf

# Run agent on internal 8011 (not exposed) and nginx on 8010
ENV PORT=8011
EXPOSE 8010

CMD ["bash", "-lc", "python agent.py serve --port ${PORT} --card & nginx -g 'daemon off;' "]
