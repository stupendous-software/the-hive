ARG CACHE_BUST=20260305T2025
ARG BRANCH=beta
FROM agent0ai/agent-zero:latest

# Combine runtime setup in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl libgcc-s1 libstdc++6 openssl ca-certificates tzdata openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 agent || true

# Copy our a0 directory over base
COPY ./a0/ /

# The base image likely already sets correct permissions. Avoid chmod that may fail.

EXPOSE 22 80 9000-9009
RUN chown -R agent:agent /app 2>/dev/null || true
USER agent
CMD ["/exe/initialize.sh"]
