#!/usr/bin/env python3
import sys, subprocess, json, os
import requests
import datetime

port = int(sys.argv[1])
mem = sys.argv[2]
parent_obs_url = sys.argv[3] if len(sys.argv) > 3 else None
trace_id = sys.argv[4] if len(sys.argv) > 4 else None

base_vol = 'hive_data'
clone_vol = f'hive_clone_{mem}'
log_vol = f'hive_logs_{mem}'
tmp_vol = f'hive_tmp_{mem}'
heartbeat_vol = 'hive_heartbeat'
name = f'hive-clone-{mem}'
image = 'brianheston/the-hive:beta'


def get_management_key():
    """Load OpenRouter management key from secrets file."""
    secrets_path = '/a0/usr/.secrets'
    try:
        with open(secrets_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, val = line.split('=', 1)
                    if key == 'OPENROUTER_MANAGEMENT_KEY':
                        return val
    except Exception as e:
        print(f'ERROR: Could not load OPENROUTER_MANAGEMENT_KEY: {e}')
        return None


def create_openrouter_key(clone_name):
    """Create an OpenRouter API key for this clone.
    Returns tuple (key_string, key_id) or (None, None).
    """
    management_key = get_management_key()
    if not management_key:
        print('ERROR: OPENROUTER_MANAGEMENT_KEY not available')
        return None, None
    url = 'https://openrouter.ai/api/v1/keys'
    payload = {
        'name': clone_name,
        'limit': 0,
        'limit_reset': None
    }
    try:
        resp = requests.post(url, headers={
            'Authorization': f'Bearer {management_key}',
            'Content-Type': 'application/json'
        }, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        key = data.get('key')
        key_id = data.get('id')  # Store the key ID for revocation
        if key:
            print(f'[OpenRouter] Created key for {clone_name}')
            return key, key_id
        else:
            print(f'[OpenRouter] Response missing key: {data}')
            return None, None
    except Exception as e:
        print(f'[OpenRouter] Failed to create key: {e}')
        return None, None


def store_clone_key_in_registry(clone_name, key_id):
    """Store the clone's OpenRouter key ID in the registry for later revocation."""
    registry_path = '/a0/usr/clone_registry.json'
    try:
        if os.path.exists(registry_path):
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        else:
            registry = {}
        registry[clone_name] = {
            'openrouter_key_id': key_id,
            'created_at': datetime.datetime.utcnow().isoformat() + 'Z'
        }
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        print(f'[Registry] Stored OpenRouter key ID for {clone_name}')
    except Exception as e:
        print(f'[Registry] Failed to store key: {e}')


def get_parent_network():
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
        result = subprocess.run(['docker', 'inspect', container_id],
                              capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        if not info or not info[0].get('NetworkSettings', {}).get('Networks'):
            print('WARNING: No network information found for container')
            return None
        networks = list(info[0]['NetworkSettings']['Networks'].keys())
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
            print('WARNING: No suitable network found')
            return None
    except subprocess.CalledProcessError as e:
        print(f'WARNING: Docker command failed: {e.stderr if e.stderr else e}')
        return None
    except Exception as e:
        print(f'WARNING: Network detection error: {e}')
        return None


# Create Docker volumes
subprocess.run(['docker', 'volume', 'create', clone_vol], capture_output=True)
subprocess.run(['docker', 'volume', 'create', log_vol], capture_output=True)
subprocess.run(['docker', 'volume', 'create', tmp_vol], capture_output=True)

# Copy base data from parent
print('Copying base data from parent...')
copy_cmd = (
    'cp -a /src/usr/settings.json /dst/ 2>/dev/null || echo "No settings.json"; '
    'if [ -f /src/usr/.env ]; then cp -a /src/usr/.env /dst/; fi; '
    'if [ -f /src/usr/secrets.env ]; then cp -a /src/usr/secrets.env /dst/; fi; '
    'if [ -d /src/usr/scripts ]; then cp -a /src/usr/scripts /dst/; fi; '
    'mkdir -p /dst/memory /dst/projects'
)
try:
    import docker
    client = docker.from_env()
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

# Build docker run command
cmd = [
    'docker', 'run', '-d',
    '-v', '/var/run/docker.sock:/var/run/docker.sock',
    '-p', f'{port}:80',
    '-v', f'{base_vol}:/a0:ro',
    '-v', f'{clone_vol}:/a0/usr',
    '-v', f'{log_vol}:/a0/logs',
    '-v', f'{tmp_vol}:/a0/tmp',
    '-v', f'{heartbeat_vol}:/heartbeat',
    '-v', 'hive_secrets:/a0/usr/.secrets',
    '-e', f'A0_SET_agent_memory_subdir={mem}',
    '-e', f'A0_CLONE_NAME={mem}',
    '-e', f'A0_CLONE_PORT={port}',
    '-e', f'A0_CLONE_MEMORY_SUBDIR={mem}',
    '-e', 'A0_PARENT_UUID=unknown',
    '--name', name,
    image
]

# Inject OpenRouter API key for this clone
print('Generating OpenRouter API key...')
new_key, key_id = create_openrouter_key(name)
if new_key and key_id:
    cmd.extend(['-e', f'OPENROUTER_API_KEY={new_key}'])
    store_clone_key_in_registry(name, key_id)
else:
    print('WARNING: Failed to generate OpenRouter API key; clone will use parent key if available')

# Inject observability environment
if parent_obs_url:
    cmd.extend(['-e', f'A0_PARENT_OBS_URL={parent_obs_url}'])
if trace_id:
    cmd.extend(['-e', f'A0_TRACE_ID={trace_id}'])

network = get_parent_network()
if network:
    cmd.insert(3, '--network')
    cmd.insert(4, network)

# Inject A2A server configuration
try:
    with open('/a0/usr/settings.json') as f:
        parent_settings = json.load(f)
    a2a_secret = parent_settings.get('a2a_secret')
    if a2a_secret:
        cmd.extend(['-e', 'A0_SET_a2a_server_enabled=true'])
        cmd.extend(['-e', 'A0_SET_a2a_http_url=http://0.0.0.0:8000/a2a'])
        cmd.extend(['-e', f'A0_SET_a2a_secret={a2a_secret}'])
    else:
        print('WARNING: a2a_secret not found in parent settings; A2A will not be enabled on clone')
except Exception as e:
    print(f'WARNING: Could not load parent A2A settings: {e}')

print('Running:', ' '.join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print('Launch failed:', res.stderr)
    sys.exit(1)
print(f'Clone started: {res.stdout.strip()}')
print(f'Connect: http://localhost:{port}')
print('Bootstrap launched.')
