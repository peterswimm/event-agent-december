# Multi-stage build for Event Kit Agent
# Stage 1: Builder - install dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - minimal image with nginx reverse proxy
FROM python:3.11-slim AS runtime

# Install nginx only
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Set working directory
WORKDIR /app

# Copy application files
COPY agent.py agent.json telemetry.py errors.py core.py settings.py ./
COPY assets/ ./assets/
COPY deploy/nginx.conf /etc/nginx/nginx.conf

# Create directories for logs and exports
RUN mkdir -p /app/logs /app/exports /app/data

# Non-root user for security
RUN useradd -m -u 1000 eventkit && \
    chown -R eventkit:eventkit /app /var/log/nginx /var/lib/nginx

USER eventkit

# Run agent on internal 8011 (not exposed) and nginx on 8010
ENV PORT=8011
EXPOSE 8010

# Health check on nginx endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8010/health')" || exit 1

CMD ["bash", "-c", "python agent.py serve --port ${PORT} --card & nginx -g 'daemon off;'"]
