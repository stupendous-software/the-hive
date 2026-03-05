ARG CACHE_BUST=20260305T2300
FROM agent0ai/agent-zero:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl libgcc-s1 libstdc++6 openssl ca-certificates tzdata openssh-server \
    && rm -rf /var/lib/apt/lists/*

COPY ./a0/ /
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV BRANCH=beta

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/exe/initialize.sh", "beta"]

EXPOSE 22 80 9000-9009
