ARG CACHE_BUST=20260305T2035
FROM agent0ai/agent-zero:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl libgcc-s1 libstdc++6 openssl ca-certificates tzdata openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 agent || true

COPY ./a0/ /

ENTRYPOINT ["/a0/usr/scripts/docker-entrypoint.sh"]

EXPOSE 22 80 9000-9009
RUN chown -R agent:agent /app 2>/dev/null || true
USER agent
# No CMD defined; inherit from base image
