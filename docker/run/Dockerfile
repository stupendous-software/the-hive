FROM agent0ai/agent-zero:latest

ARG BRANCH=beta
ENV BRANCH=$BRANCH

# Copy our custom entrypoint and any additional files
COPY ./fs/ /

# Ensure entrypoint is executable
RUN chmod +x /a0/usr/scripts/docker-entrypoint.sh
RUN chmod +x /exe/initialize.sh
RUN chmod +x /exe/initialize.sh

# Auto-bootstrap on first start
ENTRYPOINT ["/a0/usr/scripts/docker-entrypoint.sh"]
CMD ["/exe/initialize.sh"]
