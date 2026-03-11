import sys, os, subprocess

# Remove the script's directory from sys.path to avoid shadowing the docker SDK
if sys.path and sys.path[0] == os.path.dirname(os.path.abspath(__file__)):
    sys.path.pop(0)

# Ensure docker SDK is available
try:
    import docker
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', 'docker'], check=True)
    import docker

# Load Docker Hub credentials
secrets_dir = '/a0/usr/.secrets'
username = os.getenv('DOCKERHUB_USERNAME')
token = os.getenv('DOCKERHUB_TOKEN')
if not (username and token):
    up = os.path.join(secrets_dir, 'dockerhub_username')
    tk = os.path.join(secrets_dir, 'dockerhub_token')
    if os.path.isfile(up) and os.path.isfile(tk):
        with open(up) as f: username = f.read().strip()
        with open(tk) as f: token = f.read().strip()

# Connect to Docker daemon via Unix socket
client = docker.APIClient(base_url='unix:///var/run/docker.sock')

# Log in to Docker Hub if credentials present
if username and token:
    try:
        client.login(username=username, password=token, registry='https://index.docker.io/v1/')
        print('Docker Hub login succeeded')
    except Exception as e:
        print('Docker Hub login failed, proceeding with existing auth:', e)
else:
    print('No explicit Docker Hub credentials; proceeding without login')

# Build image
build_path = '/a0'
dockerfile = 'docker/run/Dockerfile'
tag_beta = 'brianheston/the-hive:beta'
tag_latest = 'brianheston/the-hive:latest'
print(f'Building image from {dockerfile} in {build_path}...')
try:
    build_log = client.build(path=build_path, dockerfile=dockerfile, tag=tag_beta, rm=True, decode=True)
    for line in build_log:
        if isinstance(line, dict):
            msg = line.get('status') or line.get('stream') or ''
            if msg: print(msg)
            if line.get('error'): raise Exception(line['error'])
        else:
            print(line)
except Exception as e:
    print('Build failed:', e)
    sys.exit(1)

# Tag latest
client.tag(tag_beta, tag_latest)
print(f'Tagged {tag_latest}')

# Push both tags
for tag in (tag_beta, tag_latest):
    print(f'Pushing {tag}...')
    try:
        push_log = client.push(tag, stream=True, decode=True)
        for line in push_log:
            msg = line.get('status') or line.get('error') or ''
            if msg: print(msg)
        print(f'Pushed {tag}')
    except Exception as e:
        print(f'Push failed for {tag}: {e}')
        sys.exit(1)

print('✅ Docker image build and push complete.')
