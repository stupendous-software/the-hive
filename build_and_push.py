import os, sys, subprocess

# Ensure docker SDK is installed and up-to-date
subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', '--upgrade', 'docker'], check=False)

import docker
print('Docker SDK version:', getattr(docker, '__version__', 'unknown'))

# Get client (prefer high-level from_env; fallback to old Client)
if hasattr(docker, 'from_env'):
    client = docker.from_env()
else:
    client = docker.Client(version='auto')

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

# Login if credentials present
if username and token:
    try:
        client.login(username=username, password=token, registry='https://index.docker.io/v1/')
        print('Docker Hub login succeeded')
    except Exception as e:
        print('Docker Hub login failed, proceeding with existing auth:', e)
else:
    print('No explicit Docker Hub credentials found; proceeding without login')

# Build image
build_path = '/a0'
dockerfile = 'docker/run/Dockerfile'
tag_beta = 'brianheston/the-hive:beta'
tag_latest = 'brianheston/the-hive:latest'
print(f'Building image from {dockerfile} in {build_path}...')
try:
    image, build_log = client.images.build(path=build_path, dockerfile=dockerfile, tag=tag_beta, rm=True)
    for line in build_log:
        if isinstance(line, dict):
            msg = line.get('status') or line.get('stream') or ''
            if msg:
                print(msg.strip())
            if line.get('error'):
                raise Exception(line['error'])
        else:
            print(line)
except Exception as e:
    print('Build failed:', e)
    sys.exit(1)

# Tag latest
image.tag(tag_latest)
print(f'Tagged {tag_latest}')

# Push both tags
for tag in (tag_beta, tag_latest):
    print(f'Pushing {tag}...')
    try:
        push_log = client.images.push(tag, stream=True, decode=True)
        for line in push_log:
            if isinstance(line, dict):
                msg = line.get('status') or line.get('error') or ''
                if msg:
                    print(msg.strip())
            else:
                print(line)
        print(f'Pushed {tag}')
    except Exception as e:
        print(f'Push failed for {tag}: {e}')
        sys.exit(1)

print('✅ Docker image build and push complete.')
