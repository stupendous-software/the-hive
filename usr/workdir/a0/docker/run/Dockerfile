ARG CACHE_BUST=20260305T2100
FROM agent0ai/agent-zero:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl libgcc-s1 libstdc++6 openssl ca-certificates tzdata openssh-server \
    && rm -rf /var/lib/apt/lists/*

# Ensure our entrypoint is executable
RUN chmod +x /a0/usr/scripts/docker-entrypoint.sh || true

COPY ./a0/ /

# Branch environment for base image initialization
ENV BRANCH=beta

# Custom entrypoint to set hostname and identity based on A0_CLONE_NAME
ENTRYPOINT ["/a0/usr/scripts/docker-entrypoint.sh"]
CMD ["/exe/initialize.sh", "beta"]

EXPOSE 22 80 9000-9009
