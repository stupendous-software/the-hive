ARG CACHE_BUST=20260305T1940
ARG BRANCH=beta
FROM agent0ai/agent-zero:latest
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl libgcc-s1 libstdc++6 openssl ca-certificates tzdata openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 agent

COPY ./a0/ /

# Ensure critical scripts are executable (binary chmod)
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
