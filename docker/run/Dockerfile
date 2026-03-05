# Multi-stage optimized build for Agent Zero (patched for beta)
# ============================================

# STAGE 1: Builder
FROM python:3.11 AS builder

WORKDIR /build

# Build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make cmake pkg-config libffi-dev libssl-dev git gfortran \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv-a0

# Copy requirements from project root within fs/a0
COPY ./fs/a0/requirements.txt .

# Install dependencies into the virtualenv
RUN /opt/venv-a0/bin/pip install --no-cache-dir -r requirements.txt

# STAGE 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Runtime dependencies (Debian package names)
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl libgcc-s1 libstdc++6 openssl ca-certificates tzdata openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 agent

# Copy virtualenv from builder
COPY --from=builder /opt/venv-a0 /opt/venv-a0
ENV PATH=/opt/venv-a0/bin:$PATH

# Copy application files
COPY ./fs/ /

# Ensure entrypoint and scripts are executable
RUN chmod +x /a0/usr/scripts/docker-entrypoint.sh /exe/run_A0.sh /exe/initialize.sh /exe/run_searxng.sh /exe/run_tunnel_api.sh

EXPOSE 22 80 9000-9009

RUN chown -R agent:agent /app
USER agent

CMD ["/a0/usr/scripts/docker-entrypoint.sh", "local"]
