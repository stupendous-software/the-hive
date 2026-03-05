FROM agent0ai/agent-zero:latest

ARG BRANCH=beta
ENV BRANCH=$BRANCH

# Copy our Agent Zero tree into the container under /a0/
COPY ./a0/ /a0/

# Ensure entrypoint and init script are executable
RUN chmod +x /a0/usr/scripts/docker-entrypoint.sh \
 && chmod +x /exe/initialize.sh

# Auto-bootstrap on first start
ENTRYPOINT ["/a0/usr/scripts/docker-entrypoint.sh"]
CMD ["/exe/initialize.sh"]

EXPOSE 22 80 9000-9009
