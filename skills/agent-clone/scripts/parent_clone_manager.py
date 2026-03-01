#!/usr/bin/env python3
"""Parent Clone Manager

Monitors clone heartbeats via the shared volume.
- Shuts down clones idle > IDLE_TIMEOUT_MINUTES.
- Enforces maximum concurrent clones (MAX_CLONES).
- Maintains clone_registry.json for visibility.
"""

import json
import os
import time
import subprocess
from datetime import datetime, timezone, timedelta

# Configuration
MAX_CLONES = 5
IDLE_TIMEOUT_MINUTES = 15
REGISTRY_PATH = '/a0/usr/clone_registry.json'
HEARTBEAT_VOLUME = 'agent_zero_heartbeat'
HEARTBEAT_DIR = '/hb'

CLONE_REGISTRY = {}


def list_heartbeat_files():
    """Return list of heartbeat file names from the shared volume."""
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
    """Read a single heartbeat JSON file from the volume and return data dict."""
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
    """Return list of container IDs idle longer than IDLE_TIMEOUT_MINUTES."""
    idle = []
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=IDLE_TIMEOUT_MINUTES)
    for cid, info in CLONE_REGISTRY.items():
        ts_str = info.get('last_seen')
        if not ts_str:
            continue
        try:
            # Handle ISO format with trailing Z
            if ts_str.endswith('Z'):
                ts_str = ts_str[:-1] + '+00:00'
            last_dt = datetime.fromisoformat(ts_str)
            if last_dt < cutoff:
                idle.append(cid)
        except Exception:
            continue
    return idle


def get_over_limit_clones():
    """Return list of container IDs to remove if over MAX_CLONES (oldest first)."""
    if len(CLONE_REGISTRY) <= MAX_CLONES:
        return []
    sorted_ids = sorted(
        CLONE_REGISTRY.keys(),
        key=lambda cid: CLONE_REGISTRY[cid].get('last_seen', '')
    )
    excess = len(CLONE_REGISTRY) - MAX_CLONES
    return sorted_ids[:excess]


def shutdown_clone(container_id: str, reason: str):
    """Stop and remove the clone container."""
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
    while True:
        try:
            update_registry_from_heartbeats()
            for cid in get_idle_clones():
                shutdown_clone(cid, f'idle > {IDLE_TIMEOUT_MINUTES} minutes')
            for cid in get_over_limit_clones():
                shutdown_clone(cid, f'exceeded max clones ({MAX_CLONES})')
            persist_registry()
        except Exception as e:
            print(f'[ParentManager] Loop error: {e}')
        time.sleep(60)


if __name__ == '__main__':
    main_loop()
