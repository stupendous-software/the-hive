ARG CACHE_BUST=20260305T2055
FROM agent0ai/agent-zero:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl libgcc-s1 libstdc++6 openssl ca-certificates tzdata openssh-server \
    && rm -rf /var/lib/apt/lists/*

COPY ./a0/ /

EXPOSE 22 80 9000-9009
