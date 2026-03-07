#!/usr/bin/env python3
import subprocess
import sys
import time
import os

VENV_PIP = '/opt/venv-a0/bin/pip'
VENV_PYTHON = '/opt/venv-a0/bin/python'
REQUIREMENTS = '/a0/requirements.txt'

# Import bootstrap_common from shared volume
BOOTSTRAP_COMMON_PATH = '/a0/usr/common/bootstrap_common.py'

import importlib.util

spec = importlib.util.spec_from_file_location('bootstrap_common', BOOTSTRAP_COMMON_PATH)
if spec and spec.loader:
    bootstrap_common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bootstrap_common)
else:
    bootstrap_common = None


def run_cmd(cmd, check=True):
    print(f'[bootstrap] {" ".join(cmd)}')
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print('[bootstrap] ERROR:', result.stderr)
        sys.exit(result.returncode)
    return result


def main():
    print('[bootstrap] Starting enhanced clone bootstrap')
    
    # Validate venv
    if not os.path.exists(VENV_PIP):
        print('[bootstrap] ERROR: venv pip not found at', VENV_PIP)
        sys.exit(1)

    # Install ALL Hive dependencies
    if os.path.exists(REQUIREMENTS):
        run_cmd([VENV_PIP, 'install', '--no-cache-dir', '-r', REQUIREMENTS], check=False)
    else:
        print('[bootstrap] WARNING: requirements.txt not found')

    # Ensure FastAPI/Uvicorn explicitly
    run_cmd([VENV_PIP, 'install', '--no-cache-dir', 'fastapi', 'uvicorn[standard]'], check=False)
    # Install Docker Python package for host docker access
    run_cmd([VENV_PIP, 'install', '--no-cache-dir', 'docker'], check=False)

    # Ensure Docker CLI is installed
    try:
        run_cmd([VENV_PIP, 'install', '--no-cache-dir', 'docker'], check=False)
    except Exception as e:
        print(f'[bootstrap] Docker Python package install note: {e}')

    # Apply shared policies, identity, and start heartbeat via bootstrap_common
    if bootstrap_common:
        try:
            clone_name = os.getenv('A0_CLONE_NAME', 'clone')
            bootstrap_common.apply_shared_policies()
            bootstrap_common.write_identity(clone_name)
            bootstrap_common.start_heartbeat()
            print('[bootstrap] Shared policies applied, identity set, heartbeat started')
        except Exception as e:
            print(f'[bootstrap] Warning: bootstrap_common failed: {e}')
    else:
        print('[bootstrap] bootstrap_common not available, skipping policies/heartbeat')

    # Restart run_ui
    try:
        run_cmd(['supervisorctl', 'restart', 'run_ui'], check=False)
        time.sleep(3)
        status = subprocess.run(['supervisorctl', 'status', 'run_ui'], capture_output=True, text=True)
        print('[bootstrap] run_ui status:', status.stdout)
    except Exception as e:
        print(f'[bootstrap] Failed to restart run_ui: {e}')

    print('[bootstrap] Complete')

if __name__ == '__main__':
    main()
