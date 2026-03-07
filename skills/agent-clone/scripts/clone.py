#!/usr/bin/env python3
import sys, subprocess, json

port = int(sys.argv[1])
mem = sys.argv[2]

base_vol = 'hive_data'
clone_vol = f'hive_clone_{mem}'
log_vol = f'hive_logs_{mem}'
tmp_vol = f'hive_tmp_{mem}'
heartbeat_vol = 'hive_heartbeat'
name = f'hive-clone-{mem}'
image = 'brianheston/the-hive:beta'

# ==================== NETWORK DETECTION FIX ====================
# NEW: Function to detect the Docker network the parent container is on
def get_parent_network():
    """Detect the Docker network the parent container is connected to.
    Returns network name or None if detection fails."""
    try:
        # Get container ID from /proc/self/cgroup
        container_id = None
        with open('/proc/self/cgroup', 'r') as f:
            for line in f:
                if 'docker' in line:
                    parts = line.strip().split('/')
                    if len(parts) >= 3:
                        # Last part is the full container ID, take first 12 chars
                        container_id = parts[-1][:12]
                        break

        if not container_id:
            print('WARNING: Could not determine container ID from /proc/self/cgroup')
            return None

        # Inspect container to get its connected networks
        result = subprocess.run(['docker', 'inspect', container_id],
                              capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)

        if not info or not info[0].get('NetworkSettings', {}).get('Networks'):
            print('WARNING: No network information found for container')
            return None

        networks = list(info[0]['NetworkSettings']['Networks'].keys())
        print(f'INFO: Parent connected to networks: {networks}')

        # Prefer custom bridge networks (exclude default bridge, host, none)
        custom_networks = [n for n in networks if n not in ['bridge', 'host', 'none']]

        if custom_networks:
            selected = custom_networks[0]
            print(f'INFO: Selected custom network: {selected}')
            return selected
        elif 'bridge' in networks:
            print('WARNING: Only default bridge network available, using it')
            return 'bridge'
        else:
            print('WARNING: No suitable network found for inter-container communication')
            return None

    except subprocess.CalledProcessError as e:
        print(f'WARNING: Docker command failed: {e.stderr if e.stderr else e}')
        return None
    except Exception as e:
        print(f'WARNING: Network detection error: {e}')
        return None
# ==================================================================

# Ensure volumes exist
subprocess.run(['docker','volume','create',clone_vol], capture_output=True)
subprocess.run(['docker','volume','create',log_vol], capture_output=True)
subprocess.run(['docker','volume','create',tmp_vol], capture_output=True)

# Copy base data from parent
copy_cmd = [
    'docker','run','--rm',
    '-v',f'{base_vol}:/src:ro',
    '-v',f'{clone_vol}:/dst',
    'alpine','sh','-c',
    'cp -a /src/usr/settings.json /dst/ 2>/dev/null || echo \"No settings.json\"; '
    'if [ -f /src/usr/.env ]; then cp -a /src/usr/.env /dst/; fi; '
    'if [ -f /src/usr/secrets.env ]; then cp -a /src/usr/secrets.env /dst/; fi; '
    'if [ -d /src/usr/scripts ]; then cp -a /src/usr/scripts /dst/; fi; '
    'mkdir -p /dst/memory /dst/projects'
]
res = subprocess.run(copy_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print('Copy failed:', res.stderr)
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
    '-v','hive_secrets:/a0/usr/.secrets',
    '-e',f'A0_SET_agent_memory_subdir={mem}',
    '-e',f'A0_CLONE_NAME={mem}',
    '-e',f'A0_CLONE_PORT={port}',
    '-e',f'A0_CLONE_MEMORY_SUBDIR={mem}',
    '-e','A0_PARENT_UUID=unknown',
    '--name',name,
    image
]

# ==================== NETWORK FLAG INJECTION ====================
# NEW: Detect parent network and add --network flag if available
network = get_parent_network()
if network:
    # Insert --network flag after 'docker run -d' to maintain proper order
    cmd.insert(3, '--network')
    cmd.insert(4, network)
# ==================================================================

print('Running:',' '.join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print('Launch failed:', res.stderr)
    sys.exit(1)
print(f'Clone started: {res.stdout.strip()}')
print(f'Connect: http://localhost:{port}')
print('Bootstrap launched.')
