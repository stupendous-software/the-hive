#!/usr/bin/env python3
import sys, subprocess

port = int(sys.argv[1])
mem = sys.argv[2]

base_vol = 'agent_zero'
clone_vol = f'agent_zero_clone_{mem}'
log_vol = f'agent_zero_logs_{mem}'
tmp_vol = f'agent_zero_tmp_{mem}'
heartbeat_vol = 'agent_zero_heartbeat'
name = f'agent-zero-clone-{mem}'
image = 'agent0ai/agent-zero:latest'

# Ensure volumes exist
subprocess.run(['docker','volume','create',clone_vol], capture_output=True)
subprocess.run(['docker','volume','create',log_vol], capture_output=True)
subprocess.run(['docker','volume','create',tmp_vol], capture_output=True)

<<<<<<< Updated upstream
# Copy base data from parent
copy_cmd = [
    'docker','run','--rm',
    '-v',f'{base_vol}:/src:ro',
    '-v',f'{clone_vol}:/dst',
    'alpine','sh','-c',
    'cp -a /src/usr/settings.json /dst/ 2>/dev/null || echo "No settings.json"; '
    'if [ -f /src/usr/.env ]; then cp -a /src/usr/.env /dst/; fi; '
    'if [ -f /src/usr/secrets.env ]; then cp -a /src/usr/secrets.env /dst/; fi; '
    'if [ -d /src/usr/scripts ]; then cp -a /src/usr/scripts /dst/; fi; '
    'mkdir -p /dst/memory /dst/projects'
]
res = subprocess.run(copy_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print('Copy failed:', res.stderr)
=======
# Copy base data from parent using a temporary Alpine container
print('Copying base data from parent...')
# Copy base data from parent using a temporary Alpine container
print('Copying base data from parent...')
copy_cmd = (
        'cp -a /src/usr/settings.json /dst/ 2>/dev/null || echo "No settings.json"; '
        'if [ -f /src/usr/.env ]; then cp -a /src/usr/.env /dst/; fi; '
        'if [ -f /src/usr/secrets.env ]; then cp -a /src/usr/secrets.env /dst/; fi; '
        'if [ -d /src/usr/scripts ]; then cp -a /src/usr/scripts /dst/; fi; '
        'mkdir -p /dst/memory /dst/projects'
    )
'if [ -f /src/usr/.env ]; then cp -a /src/usr/.env /dst/; fi; '
'if [ -f /src/usr/secrets.env ]; then cp -a /src/usr/secrets.env /dst/; fi; '
'if [ -d /src/usr/scripts ]; then cp -a /src/usr/scripts /dst/; fi; '
'mkdir -p /dst/memory /dst/projects'

try:
    copy_container = client.containers.run(
        image='alpine',
        command=['sh', '-c', copy_cmd],
        volumes={
            base_vol: {'bind': '/src', 'mode': 'ro'},
            clone_vol: {'bind': '/dst', 'mode': 'rw'}
        },
        remove=True,
        detach=False
    )
except Exception as e:
    print('Copy failed:', e)
>>>>>>> Stashed changes
    sys.exit(1)

# Launch clone container
cmd = [
    'docker','run','-d',
    '-v','/var/run/docker.sock:/var/run/docker.sock',
    '-p',f'{port}:80',
    '-v',f'{base_vol}:/a0:ro',
    '-v',f'{clone_vol}:/a0/usr',
    '-v',f'{log_vol}:/a0/logs',
    '-v',f'{tmp_vol}:/a0/tmp',
    '-v',f'{heartbeat_vol}:/heartbeat',
    '-e',f'A0_SET_agent_memory_subdir={mem}',
    '-e',f'A0_CLONE_PORT={port}',
    '-e',f'A0_CLONE_MEMORY_SUBDIR={mem}',
    '-e','A0_PARENT_UUID=unknown',
    '--name',name,
    image
]
print('Running:',' '.join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print('Launch failed:', res.stderr)
    sys.exit(1)
print(f'Clone started: {res.stdout.strip()}')
print(f'Connect: http://localhost:{port}')
print('Bootstrap launched.')
