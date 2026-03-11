ARG CACHE_BUST=20260305T1955
FROM brianheston/the-hive:beta
USER root

# System setup + Node.js removal in one RUN
RUN apt-get update &&     apt-get install -y --no-install-recommends python3-pip &&     apt-get purge -y nodejs npm &&     apt-get autoremove -y &&     rm -rf /var/lib/apt/lists/*

# Python: install nest-asyncio (required by status agent)
RUN /opt/venv-a0/bin/pip install --no-cache-dir nest-asyncio

# Upgrade vulnerable dependencies to patched versions (CVE fixes)
RUN /opt/venv-a0/bin/pip install --no-cache-dir \
  'nltk>=3.9.3' \
  'unstructured[all-docs]>=0.18.18' \
  'langchain-core>=0.3.81' \
  'langchain-unstructured[all-docs]>=0.1.8' \
  'lxml_html_clean>=0.4.0' \
  'pillow>=12.1.1' \
  'cryptography>=46.0.5' \
  && /opt/venv-a0/bin/pip install --no-cache-dir 'torch>=2.6.0' -f https://download.pytorch.org/whl/torch_stable.html


# Copy project files
COPY . /a0/
COPY scripts/outer-entrypoint.sh /usr/local/bin/outer-entrypoint.sh

# Permissions
RUN chmod +x /usr/local/bin/outer-entrypoint.sh     /a0/usr/scripts/docker-entrypoint.sh     /a0/usr/scripts/bootstrap_clone.py     /a0/usr/scripts/heartbeat_sender.py     /a0/usr/scripts/parent_clone_manager.py     /a0/usr/scripts/auto_enable_prompts.py /a0/common/bootstrap_common.py

ENTRYPOINT ["/usr/local/bin/outer-entrypoint.sh"]
EXPOSE 22 80 9000-9009
EXPOSE 8080
