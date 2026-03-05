FROM agent0ai/agent-zero:latest

# Add custom entrypoint that sets clone name without touching base /a0
COPY scripts/outer-entrypoint.sh /usr/local/bin/outer-entrypoint.sh
RUN chmod +x /usr/local/bin/outer-entrypoint.sh

# Set BRANCH as environment for initialize.sh
ENV BRANCH=beta

# Use our outer entrypoint; it will exec the base command (initialize.sh)
ENTRYPOINT ["/usr/local/bin/outer-entrypoint.sh"]
CMD ["/exe/initialize.sh"]

EXPOSE 22 80 9000-9009
