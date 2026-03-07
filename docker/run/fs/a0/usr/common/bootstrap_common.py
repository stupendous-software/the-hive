import os
import subprocess
import time

SHARED_POLICIES_MARKER = '/a0/usr/.policies_applied'


def apply_shared_policies():
    """Enforce shared policies: Git routing, resource usage, etc.
    Writes a marker file to indicate policies have been applied (with timestamp).
    """
    try:
        # Ensure we don't apply multiple times on same boot
        if os.path.exists(SHARED_POLICIES_MARKER):
            return
        # Here we could create an explicit policy manifest for the clone to read
        # For now, just create the marker with timestamp
        with open(SHARED_POLICIES_MARKER, 'w') as f:
            f.write(f'Policies applied at {time.asctime()}')
        # Additional actions could include writing /etc/hosts entries, setting up alerts, etc.
    except Exception as e:
        # Log but don't crash bootstrap
        print(f'[bootstrap_common] Warning: {e}')


def write_identity(name: str):
    """Write friendly name to /.identity for shell prompt."""
    try:
        with open('/.identity', 'w') as f:
            f.write(name)
    except Exception as e:
        print(f'[bootstrap_common] Failed to write identity: {e}')


def start_heartbeat():
    """Start the heartbeat sender daemon if not already running."""
    try:
        # Check if already running
        result = subprocess.run(['pgrep', '-f', 'heartbeat_sender.py'], capture_output=True)
        if result.returncode == 0:
            return
        # Start it in background
        subprocess.Popen(['python3', '/a0/usr/scripts/heartbeat_sender.py'])
    except Exception as e:
        print(f'[bootstrap_common] Failed to start heartbeat: {e}')

