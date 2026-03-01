#!/usr/bin/env python3
"""
Clone the current Agent Zero instance into a new Docker container.

Usage: clone.py <port> [memory_subdir]
"""
import sys, os, subprocess
from pathlib import Path

if len(sys.argv) < 2:
    print('Usage: clone.py <port> [memory_subdir]')
    sys.exit(1)

port = sys.argv[1]
memory_subdir = sys.argv[2] if len(sys.argv) > 2 else 'clone'

base_volume = 'agent_zero'
clone_volume = f'agent_zero_clone_{memory_subdir}'
clone_logs_volume = f'agent_zero_logs_{memory_subdir}'
clone_tmp_volume = f'agent_zero_tmp_{memory_subdir}'
container_name = f'agent-zero-clone-{memory_subdir}'
heartbeat_volume = 'agent_zero_heartbeat'

# Get parent's UUID (from current container or settings)
parent_uuid = 'unknown'
try:
    # Parent's settings.json might have an 'id'
    result = subprocess.run(['docker', 'exec', 'agent0', 'cat', '/a0/usr/settings.json'], capture_output=True, text=True)
    if result.returncode == 0:
        import json
        settings = json.loads(result.stdout)
        parent_uuid = settings.get('id', 'unknown')
except Exception:
    pass

# Create volumes
for vol in [clone_volume, clone_logs_volume, clone_tmp_volume]:
    print(f'Creating volume: {vol}')
    result = subprocess.run(['docker', 'volume', 'create', vol], capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Error creating volume {vol}:')
        print(result.stderr)
        sys.exit(1)

# Copy essential data from base volume's /usr to clone volume's root
copy_cmd = [
    'docker', 'run', '--rm',
    '-v', f'{base_volume}:/src:ro',
    '-v', f'{clone_volume}:/dst',
    'alpine',
    'sh', '-c',
    'mkdir -p /dst && '
    'cp -a /src/usr/settings.json /dst/ 2>/dev/null || echo "No settings.json"; '
    'if [ -f /src/usr/.env ]; then cp -a /src/usr/.env /dst/; fi; '
    'if [ -f /src/usr/secrets.env ]; then cp -a /src/usr/secrets.env /dst/; fi; '
    'if [ -d /src/usr/scripts ]; then cp -a /src/usr/scripts /dst/; fi; '
    'mkdir -p /dst/memory /dst/projects'
]
print('Copying base data to clone volume...')
result = subprocess.run(copy_cmd, capture_output=True, text=True)
if result.returncode != 0:
    print('Error copying data:')
    print(result.stderr)
    sys.exit(1)

# Run clone container with additional writable volumes
image = 'agent0ai/agent-zero:latest'
cmd = [
    'docker', 'run', '-d',
    '-p', f'{port}:80',
    '-v', f'{base_volume}:/a0:ro',
    '-v', f'{clone_volume}:/a0/usr',
    '-v', f'{clone_logs_volume}:/a0/logs',
    '-v', f'{clone_tmp_volume}:/a0/tmp',
    '-v', f'{heartbeat_volume}:/heartbeat',
    '-e', f'A0_SET_agent_memory_subdir={memory_subdir}',
    '-e', f'A0_CLONE_PORT={port}',
    '-e', f'A0_CLONE_MEMORY_SUBDIR={memory_subdir}',
    '-e', f'A0_PARENT_UUID={parent_uuid}',
    '--name', container_name,
    image
]

print('Running:', ' '.join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    container_id = result.stdout.strip()
    print(f'Clone container started: {container_id[:12]}\nConnect: http://localhost:{port}')
    # After container starts, run bootstrap inside it (via docker exec)
    bootstrap_cmd = ['docker', 'exec', '-d', container_id, 'python3', '/a0/usr/scripts/bootstrap_clone.py']
    subprocess.Popen(bootstrap_cmd)
    print('Bootstrap launched in clone.')
    # Also ensure heartbeat daemon is running (it may be launched by clone's entrypoint if present)
    # If not, launch manually
    # heartbeat_script = '/heartbeat/heartbeat_sender.py' (we should place it in shared scripts?)
    # For now, assume clone's entrypoint will check and launch heartbeat if present in /a0/usr/scripts
else:
    print('Error launching clone:')
    print(result.stderr)
    sys.exit(1)
