# Multi-stage build for the-hive:beta
FROM python:3.11 AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make cmake pkg-config libffi-dev libssl-dev git gfortran libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/venv-a0
COPY a0/requirements.txt .
ENV PIP_ONLY_BINARY=:all:
RUN /opt/venv-a0/bin/pip install --no-cache-dir --upgrade pip setuptools wheel
RUN /opt/venv-a0/bin/pip install --no-cache-dir "scikit-learn>=1.3.0"
RUN /opt/venv-a0/bin/pip install --no-cache-dir -r requirements.txt

FROM agent0ai/agent-zero:latest
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl libgcc-s1 libstdc++6 openssl ca-certificates tzdata openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 agent
COPY --from=builder /opt/venv-a0 /opt/venv-a0
ENV PATH=/opt/venv-a0/bin:$PATH

# Copy entire a0 tree
COPY ./a0/ /

# Ensure script line endings are Unix (in case of CRLF)
RUN sed -i 's/\r$//' /a0/usr/scripts/docker-entrypoint.sh || true

# Ensure critical scripts are executable (use binary chmod)
RUN [/bin/chmod, 0755, /a0/usr/scripts/docker-entrypoint.sh] \
 && [/bin/chmod, +x, /a0/usr/scripts/bootstrap_clone.py] \
 && [/bin/chmod, +x, /a0/usr/scripts/heartbeat_sender.py] \
 && [/bin/chmod, +x, /a0/usr/scripts/parent_clone_manager.py] \
 && [/bin/chmod, +x, /a0/usr/common/bootstrap_common.py] \
 && if [ -d /exe ]; then [/bin/chmod, +x, /exe/initialize.sh] \
      [/bin/chmod, +x, /exe/run_A0.sh] \
      [/bin/chmod, +x, /exe/run_searxng.sh] \
      [/bin/chmod, +x, /exe/run_tunnel_api.sh] 2>/dev/null || true; fi

EXPOSE 22 80 9000-9009
RUN chown -R agent:agent /app
USER agent
CMD ["/exe/initialize.sh"]
