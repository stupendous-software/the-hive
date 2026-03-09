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

# 3) Copy project files (grouped to minimize layers)
COPY . /a0/
COPY scripts/outer-entrypoint.sh /usr/local/bin/outer-entrypoint.sh

# 4) Permissions in a single RUN
RUN chmod +x /usr/local/bin/outer-entrypoint.sh \
    /a0/usr/scripts/docker-entrypoint.sh \
    /a0/usr/scripts/bootstrap_clone.py \
    /a0/usr/scripts/heartbeat_sender.py \
    /a0/usr/scripts/parent_clone_manager.py \
    \
    /a0/usr/common/bootstrap_common.py 

ENTRYPOINT ["/usr/local/bin/outer-entrypoint.sh"]
EXPOSE 22 80 9000-9009
EXPOSE 8080
