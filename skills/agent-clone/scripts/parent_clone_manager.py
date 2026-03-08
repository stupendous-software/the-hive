#!/usr/bin/env python3
import json
import os
import time
import subprocess
import socket
import uuid
from datetime import datetime, timezone, timedelta

MAX_CLONES = 5
IDLE_TIMEOUT_MINUTES = 15
REGISTRY_PATH = '/a0/usr/clone_registry.json'
HEARTBEAT_VOLUME = 'agent_zero_heartbeat'
HEARTBEAT_DIR = '/hb'

CLONE_REGISTRY = {}

POLICY_FILES = ['/a0/usr/git_policy.md', '/a0/usr/handbook/CLONE_HANDBOOK.md']
policy_mtimes = {}
for _f in POLICY_FILES:
    if os.path.exists(_f):
        try:
            policy_mtimes[_f] = os.path.getmtime(_f)
        except Exception:
            pass

def load_rfc_token():
    try:
        with open('/a0/usr/settings.json') as sf:
            settings = json.load(sf)
        return settings.get('rfc_password')
    except Exception:
        return None

def broadcast_policy_alert(changed_files):
    token = load_rfc_token()
    if not token:
        return
    for cid, info in CLONE_REGISTRY.items():
        port = info.get('port')
        if not port:
            continue
        url = f'http://localhost:{port}/a2a'
        payload = {'type': 'policy_alert', 'changed_files': changed_files}
        try:
            subprocess.run(
                ['curl', '-s', '-X', 'POST',
                 '-H', f'Authorization: Bearer {token}',
                 '-H', 'Content-Type: application/json',
                 '-d', json.dumps(payload),
                 url],
                timeout=5, capture_output=True
            )
        except Exception:
            pass

def list_heartbeat_files():
    try:
        result = subprocess.run(
            ['docker', 'run', '--rm', '-v', f'{HEARTBEAT_VOLUME}:{HEARTBEAT_DIR}', 'alpine', 'ls', '-1', f'{HEARTBEAT_DIR}/heartbeat_*.json'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.strip().splitlines() if f]
    except Exception:
        return []


def read_heartbeat_file(fname: str):
    try:
        result = subprocess.run(
            ['docker', 'run', '--rm', '-v', f'{HEARTBEAT_VOLUME}:{HEARTBEAT_DIR}', 'alpine', 'cat', f'{HEARTBEAT_DIR}/{fname}'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except Exception:
        return None


def update_registry_from_heartbeats():
    global CLONE_REGISTRY
    now = datetime.now(timezone.utc)
    files = list_heartbeat_files()
    for f in files:
        data = read_heartbeat_file(f)
        if not data:
            continue
        cid = data.get('container_id')
        if not cid:
            continue
        CLONE_REGISTRY[cid] = {
            'name': data.get('memory_subdir', cid),
            'port': data.get('port'),
            'last_seen': data.get('timestamp'),
            'container_id': cid,
        }


def get_idle_clones():
    idle = []
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=IDLE_TIMEOUT_MINUTES)
    for cid, info in CLONE_REGISTRY.items():
        ts_str = info.get('last_seen')
        if not ts_str:
            continue
        try:
            if ts_str.endswith('Z'):
                ts_str = ts_str[:-1] + '+00:00'
            last_dt = datetime.fromisoformat(ts_str)
            if last_dt < cutoff:
                idle.append(cid)
        except Exception:
            continue
    return idle


def get_over_limit_clones():
    if len(CLONE_REGISTRY) <= MAX_CLONES:
        return []
    sorted_ids = sorted(
        CLONE_REGISTRY.keys(),
        key=lambda cid: CLONE_REGISTRY[cid].get('last_seen', '')
    )
    excess = len(CLONE_REGISTRY) - MAX_CLONES
    return sorted_ids[:excess]


def shutdown_clone(container_id: str, reason: str):
    try:
        name = CLONE_REGISTRY.get(container_id, {}).get('name', container_id)
        print(f'[ParentManager] Shutting down clone {name} ({container_id[:12]}): {reason}')
        subprocess.run(['docker', 'rm', '-f', container_id], capture_output=True, timeout=30)
        CLONE_REGISTRY.pop(container_id, None)
    except Exception as e:
        print(f'[ParentManager] Error shutting down {container_id}: {e}')


def persist_registry():
    try:
        with open(REGISTRY_PATH, 'w') as f:
            json.dump(CLONE_REGISTRY, f, indent=2, default=str)
    except Exception as e:
        print(f'[ParentManager] Failed to persist registry: {e}')


def main_loop():
    print('[ParentManager] Starting clone monitoring (60s interval)')
    first_run = True
    while True:
        try:
            update_registry_from_heartbeats()
            for cid in get_idle_clones():
                shutdown_clone(cid, f'idle > {IDLE_TIMEOUT_MINUTES} minutes')
            for cid in get_over_limit_clones():
                shutdown_clone(cid, f'exceeded max clones ({MAX_CLONES})')
            persist_registry()
            changed = []
            for f in POLICY_FILES:
                if os.path.exists(f):
                    try:
                        mtime = os.path.getmtime(f)
                        if first_run or mtime != policy_mtimes.get(f):
                            changed.append(f)
                            policy_mtimes[f] = mtime
                    except Exception:
                        pass
            if changed:
                broadcast_policy_alert(changed)
                print(f'[ParentManager] Policy change detected: {changed}. Broadcast sent.')
            first_run = False
        except Exception as e:
            print(f'[ParentManager] Loop error: {e}')
        time.sleep(60)


if __name__ == '__main__':
    main_loop()
