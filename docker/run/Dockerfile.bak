ARG CACHE_BUST=20260305T1955
FROM brianheston/the-hive:beta
USER root

# System setup + Node.js removal in one RUN
RUN apt-get update &&     apt-get install -y --no-install-recommends python3-pip &&     apt-get purge -y nodejs npm &&     apt-get autoremove -y &&     rm -rf /var/lib/apt/lists/*

# Python: install nest-asyncio (required by status agent)
RUN /opt/venv-a0/bin/pip install --no-cache-dir nest-asyncio

# Copy project files
COPY . /a0/
COPY scripts/outer-entrypoint.sh /usr/local/bin/outer-entrypoint.sh

# Permissions
RUN chmod +x /usr/local/bin/outer-entrypoint.sh     /a0/usr/scripts/docker-entrypoint.sh     /a0/usr/scripts/bootstrap_clone.py     /a0/usr/scripts/heartbeat_sender.py     /a0/usr/scripts/parent_clone_manager.py     /a0/usr/common/bootstrap_common.py

ENTRYPOINT ["/usr/local/bin/outer-entrypoint.sh"]
EXPOSE 22 80 9000-9009
EXPOSE 8080
