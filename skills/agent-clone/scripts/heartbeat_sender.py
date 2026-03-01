#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime
import uuid
import sys

HEARTBEAT_DIR = '/a0/clone_heartbeat'
INTERVAL = 10

def get_container_id():
    try:
        with open('/proc/self/cgroup', 'r') as f:
            for line in f:
                parts = line.strip().split('/')
                if len(parts) > 2 and 'docker' in parts[1]:
                    cid = parts[-1]
                    if cid and cid != '.':
                        return cid[:12]
    except Exception:
        pass
    return str(uuid.getnode())[:12]

def get_port():
    return os.getenv('A0_CLONE_PORT', 'unknown')

def get_memory_subdir():
    return os.getenv('A0_CLONE_MEMORY_SUBDIR', 'clone')

def write_heartbeat():
    try:
        os.makedirs(HEARTBEAT_DIR, exist_ok=True)
        hb = {
            'container_id': get_container_id(),
            'port': get_port(),
            'memory_subdir': get_memory_subdir(),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': 'alive'
        }
        fp = os.path.join(HEARTBEAT_DIR, f'heartbeat_{hb["container_id"]}.json')
        with open(fp, 'w') as f:
            json.dump(hb, f, indent=2)
    except Exception as e:
        print(f'Heartbeat error: {e}', file=sys.stderr)

def main():
    while True:
        write_heartbeat()
        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
