ARG CACHE_BUST=20260305T1955
FROM brianheston/the-hive:beta
RUN echo "Cache bust: $CACHE_BUST"
USER root

# System setup + Node.js removal in one RUN
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-pip && \
    apt-get purge -y nodejs npm && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Python: install nest-asyncio (required by status agent)
RUN /opt/venv-a0/bin/pip install --no-cache-dir nest-asyncio

# Upgrade vulnerable dependencies to patched versions (CVE fixes)
RUN /opt/venv-a0/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /opt/venv-a0/bin/pip install --no-cache-dir \
      'nltk>=3.9.3' \
      'unstructured[all-docs]>=0.18.18' \
      'langchain>=0.2.16,<0.3.0' \
      'langchain-core>=0.2.40,<0.3.0' \
      'langchain-community>=0.2.0,<0.3.0 \
      'langchain-unstructured[all-docs]>=0.1.8' \
      'lxml_html_clean>=0.4.0' \
      'pillow>=12.1.1' \
      'cryptography>=46.0.5' \
      'codecarbon' && \
    /opt/venv-a0/bin/pip uninstall -y torch torchvision transformers sentence-transformers && \
    /opt/venv-a0/bin/pip install --no-cache-dir \
      'torch==2.6.0' \
      'torchvision==0.21.0' \
      'transformers==4.40.0' \
      'sentence-transformers==3.2.1' \
      -f https://download.pytorch.org/whl/torch_stable.html

# Copy project files
COPY . /a0/
COPY scripts/outer-entrypoint.sh /usr/local/bin/outer-entrypoint.sh

# Permissions - only chmod files that exist
RUN set -e; for f in /usr/local/bin/outer-entrypoint.sh /a0/usr/scripts/docker-entrypoint.sh /a0/usr/scripts/bootstrap_clone.py /a0/usr/scripts/heartbeat_sender.py /a0/usr/scripts/parent_clone_manager.py; do if [ -f "$f" ]; then chmod +x "$f"; fi; done

ENTRYPOINT ["/usr/local/bin/outer-entrypoint.sh"]
EXPOSE 22 80 9000-9009
EXPOSE 8080
