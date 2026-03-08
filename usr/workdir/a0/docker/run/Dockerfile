ARG CACHE_BUST=20260305T1955
ARG BRANCH=beta
FROM agent0ai/agent-zero:latest
USER root

# 1) System setup + Node.js removal in one RUN
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-pip && \
    apt-get purge -y nodejs npm && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# 2) Python dependency
RUN /opt/venv-a0/bin/pip install --no-cache-dir fasta2a==0.5.0

# 3) Copy updated telemetry files (overwrite specific)
COPY token_telemetry/ /a0/token_telemetry/
COPY observability_extension.py a0/observability_extension.py
COPY status_api.py a0/status_api.py
COPY docs/ a0/docs/

# 4) Ensure outer-entrypoint.sh is executable
COPY scripts/outer-entrypoint.sh /usr/local/bin/outer-entrypoint.sh
RUN chmod +x /usr/local/bin/outer-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/outer-entrypoint.sh"]
EXPOSE 22 80 9000-9009
