ARG CACHE_BUST=20260305T2010
ARG BRANCH=beta
FROM agent0ai/agent-zero:latest
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl libgcc-s1 libstdc++6 openssl ca-certificates tzdata openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 agent

COPY ./a0/ /

# Ensure critical scripts are executable (shell chmod)
RUN chmod 0755 /a0/usr/scripts/docker-entrypoint.sh \
 && chmod +x /a0/usr/scripts/bootstrap_clone.py \
 && chmod +x /a0/usr/scripts/heartbeat_sender.py \
 && chmod +x /a0/usr/scripts/parent_clone_manager.py \
 && chmod +x /a0/usr/common/bootstrap_common.py \
 && if [ -d /exe ]; then \
      chmod +x /exe/initialize.sh \
      chmod +x /exe/run_A0.sh \
      chmod +x /exe/run_searxng.sh \
      chmod +x /exe/run_tunnel_api.sh; \
    fi

EXPOSE 22 80 9000-9009
RUN chown -R agent:agent /app
USER agent
CMD ["/exe/initialize.sh"]
