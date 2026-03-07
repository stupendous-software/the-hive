#!/usr/bin/env python3
import sys, json, docker

port = int(sys.argv[1])
mem = sys.argv[2]

client = docker.from_env()

base_vol = 'hive_data'
clone_vol = f'hive_clone_{mem}'
log_vol = f'hive_logs_{mem}'
tmp_vol = f'hive_tmp_{mem}'
heartbeat_vol = 'hive_heartbeat'
name = f'hive-clone-{mem}'
image = 'brianheston/the-hive:beta'

# ==================== NETWORK DETECTION ====================
def get_parent_network():
    """Detect the Docker network the parent container is on using Docker SDK."""
    try:
        container_id = None
        with open('/proc/self/cgroup', 'r') as f:
            for line in f:
                if 'docker' in line:
                    parts = line.strip().split('/')
                    if len(parts) >= 3:
                        container_id = parts[-1][:12]
                        break
        if not container_id:
            print('WARNING: Could not determine container ID from /proc/self/cgroup')
            return None
        
        # Use SDK to inspect container
        container = client.containers.get(container_id)
        networks = list(container.attrs['NetworkSettings']['Networks'].keys())
        print(f'INFO: Parent connected to networks: {networks}')
        
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
    except docker.errors.NotFound:
        print('WARNING: Parent container not found via Docker SDK')
        return None
    except Exception as e:
        print(f'WARNING: Network detection error: {e}')
        return None
# ============================================================

# Ensure volumes exist
print(f'Creating volumes: {clone_vol}, {log_vol}, {tmp_vol}')
client.volumes.create(name=clone_vol)
client.volumes.create(name=log_vol)
client.volumes.create(name=tmp_vol)

# Copy base data from parent using a temporary Alpine container
print('Copying base data from parent...')
copy_cmd = 'cp -a /src/usr/settings.json /dst/ 2>/dev/null || echo "No settings.json"; '
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
    sys.exit(1)

# Detect network
network = get_parent_network()

# Prepare run configuration
run_kwargs = {
    'image': image,
    'name': name,
    'ports': {'80/tcp': port},
    'volumes': {
        '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
        base_vol: {'bind': '/a0', 'mode': 'ro'},
        clone_vol: {'bind': '/a0/usr', 'mode': 'rw'},
        log_vol: {'bind': '/a0/logs', 'mode': 'rw'},
        tmp_vol: {'bind': '/a0/tmp', 'mode': 'rw'},
        heartbeat_vol: {'bind': '/heartbeat', 'mode': 'rw'},
        'hive_secrets': {'bind': '/a0/usr/.secrets', 'mode': 'ro'}
    },
    'environment': {
        'A0_SET_agent_memory_subdir': mem,
        'A0_CLONE_NAME': mem,
        'A0_CLONE_PORT': str(port),
        'A0_CLONE_MEMORY_SUBDIR': mem,
        'A0_PARENT_UUID': 'unknown'
    },
    'detach': True
}

if network:
    run_kwargs['network'] = network

print(f'Running clone container with config: {run_kwargs}')
try:
    container = client.containers.run(**run_kwargs)
    print(f'Clone started: {container.id[:12]}')
    print(f'Connect: http://localhost:{port}')
    print('Bootstrap launched.')
except Exception as e:
    print('Launch failed:', e)
    sys.exit(1)
