ARG CACHE_BUST=20260305T2245
FROM agent0ai/agent-zero:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl libgcc-s1 libstdc++6 openssl ca-certificates tzdata openssh-server \
    && rm -rf /var/lib/apt/lists/*

# Copy application tree (may be partially hidden by volumes at runtime but needed for base)
COPY ./a0/ /

# Copy our custom entrypoint to a location outside any potential volume
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV BRANCH=beta

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/exe/initialize.sh"]

EXPOSE 22 80 9000-9009
