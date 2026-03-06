ARG CACHE_BUST=20260305T1955
ARG BRANCH=beta
FROM agent0ai/agent-zero:latest
USER root
COPY scripts/outer-entrypoint.sh /usr/local/bin/outer-entrypoint.sh
RUN chmod +x /usr/local/bin/outer-entrypoint.sh
COPY a0/usr/scripts/docker-entrypoint.sh /a0/usr/scripts/docker-entrypoint.sh
COPY a0/usr/scripts/bootstrap_clone.py /a0/usr/scripts/bootstrap_clone.py
COPY a0/usr/scripts/heartbeat_sender.py /a0/usr/scripts/heartbeat_sender.py
COPY a0/usr/scripts/parent_clone_manager.py /a0/usr/scripts/parent_clone_manager.py
COPY a0/usr/common/bootstrap_common.py /a0/usr/common/bootstrap_common.py
RUN chmod +x /a0/usr/scripts/docker-entrypoint.sh /a0/usr/scripts/bootstrap_clone.py /a0/usr/scripts/heartbeat_sender.py /a0/usr/scripts/parent_clone_manager.py /a0/usr/common/bootstrap_common.py /exe/initialize.sh 2>/dev/null || true
COPY a0/usr/settings.json /a0/usr/settings.json
COPY hive-product-page /a0/hive-product-page/
ENTRYPOINT ["/usr/local/bin/outer-entrypoint.sh"]
EXPOSE 22 80 9000-9009
