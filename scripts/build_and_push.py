#!/usr/bin/env python3
import subprocess, os, sys, json

# Load Docker Hub credentials
secrets_path = '/a0/usr/.secrets'
creds = {}
with open(secrets_path, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            creds[k] = v

username = creds.get('DOCKERHUB_USERNAME')
token = creds.get('DOCKERHUB_TOKEN')
if not username or not token:
    print('ERROR: DOCKERHUB_USERNAME or DOCKERHUB_TOKEN missing in /a0/usr/.secrets', file=sys.stderr)
    sys.exit(1)

# Docker login
print('Logging into Docker Hub...')
login_cmd = ['docker', 'login', '-u', username, '--password-stdin']
proc = subprocess.run(login_cmd, input=token.encode(), capture_output=True)
if proc.returncode != 0:
    print('Docker login failed:', proc.stderr.decode(), file=sys.stderr)
    sys.exit(1)

# Build image with two tags
image_base = 'brianheston/the-hive'
tags = ['beta', 'latest']
build_cmd = ['docker', 'build', '-t', f'{image_base}:{tags[0]}', '-t', f'{image_base}:{tags[1]}', '-f', 'docker/run/Dockerfile', '.']
print('Building image...')
proc = subprocess.run(build_cmd, cwd='/a0')
if proc.returncode != 0:
    print('Docker build failed', file=sys.stderr)
    sys.exit(1)

# Push each tag
for tag in tags:
    full_tag = f'{image_base}:{tag}'
    print(f'Pushing {full_tag}...')
    push_cmd = ['docker', 'push', full_tag]
    proc = subprocess.run(push_cmd)
    if proc.returncode != 0:
        print(f'Push failed for {full_tag}', file=sys.stderr)
        sys.exit(1)

print('Build and push completed for tags:', tags)
