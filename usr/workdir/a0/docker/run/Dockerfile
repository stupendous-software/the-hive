ARG CACHE_BUST=20260305T1955
ARG BRANCH=beta
FROM agent0ai/agent-zero:latest

# Ensure we run as root so entrypoint can set identity
USER root

# Add custom outer entrypoint
COPY scripts/outer-entrypoint.sh /usr/local/bin/outer-entrypoint.sh
RUN chmod +x /usr/local/bin/outer-entrypoint.sh

# Copy our custom bootstrap and entrypoint scripts into the image
COPY a0/usr/scripts/docker-entrypoint.sh /a0/usr/scripts/docker-entrypoint.sh
COPY a0/usr/scripts/bootstrap_clone.py /a0/usr/scripts/bootstrap_clone.py
COPY a0/usr/scripts/heartbeat_sender.py /a0/usr/scripts/heartbeat_sender.py
COPY a0/usr/common/bootstrap_common.py /a0/usr/common/bootstrap_common.py

# Ensure executability
RUN chmod +x /a0/usr/scripts/docker-entrypoint.sh \
    /a0/usr/scripts/bootstrap_clone.py \
    /a0/usr/scripts/heartbeat_sender.py \
    /a0/usr/common/bootstrap_common.py \
    /exe/initialize.sh 2>/dev/null || true

# Copy supervisor overrides
COPY a0/docker/run/fs/etc/supervisor/conf.d/ /etc/supervisor/conf.d/

# Outer entrypoint sets identity then calls docker-entrypoint with BRANCH
ENTRYPOINT ["/usr/local/bin/outer-entrypoint.sh"]
# No CMD arguments; outer-entrypoint handles BRANCH

EXPOSE 22 80 9000-9009
