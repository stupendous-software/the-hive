#! /usr/bin/bash
docker pull brianheston/the-hive:latest
# Create a temporary container to access the image’s files
docker create --name tmp_updater brianheston/the-hive:latest
# Copy updated entrypoint
docker cp tmp_updater:/a0/usr/scripts/docker-entrypoint.sh agent_zero:/a0/usr/scripts/docker-entrypoint.sh
# Copy auto_enable script (create missing directories if needed)
docker cp tmp_updater:/a0/usr/workdir/scripts/auto_enable_skills.py agent_zero:/a0/usr/workdir/scripts/auto_enable_skills.py
# Ensure permissions
docker exec agent_zero chmod +x /a0/usr/scripts/docker-entrypoint.sh /a0/usr/workdir/scripts/auto_enable_skills.py
docker rm tmp_updater
