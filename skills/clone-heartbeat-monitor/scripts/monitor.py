#!/usr/bin/env python3
import subprocess
import json
import sys
import time


def get_clones():
    """Return list of clone containers with name starting with 'agent-'"""
    cmd = [
        'docker', 'ps', '-a',
        '--filter', 'name=agent-',
        '--format', 'json'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error listing containers: {result.stderr}", file=sys.stderr)
        return []
    containers = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        try:
            c = json.loads(line)
            containers.append(c)
        except json.JSONDecodeError:
            continue
    return containers


def get_port_mapping(container_name: str) -> int:
    """Get the host port mapped to container port 80.
    Example: '0.0.0.0:50011->80/tcp' -> 50011
    """
    cmd = ['docker', 'inspect', '--format', '{{json .NetworkSettings.Ports}}', container_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        ports = json.loads(result.stdout.strip())
        # ports is a dict like {"80/tcp": [{"HostIp":"0.0.0.0","HostPort":"50011"}]}
        port_list = ports.get('80/tcp', [])
        if port_list:
            return int(port_list[0].get('HostPort'))
    except Exception:
        pass
    return None


def health_check(port: int, timeout=5) -> bool:
    """Check if http://localhost:<port>/health returns 200."""
    import urllib.request
    try:
        with urllib.request.urlopen(f'http://localhost:{port}/health', timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def get_logs(container_name: str, tail=50) -> str:
    cmd = ['docker', 'logs', '--tail', str(tail), container_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else result.stderr


def main():
    clones = get_clones()
    report = []
    alerts = []

    for c in clones:
        name = c.get('Names', '').lstrip('/')
        status = c.get('Status', '')
        running = 'Up' in status
        port = get_port_mapping(name)

        entry = {
            'name': name,
            'status': status,
            'port': port,
            'healthy': None,
        }

        if not running:
            entry['healthy'] = False
            logs = get_logs(name, tail=100)
            entry['logs_sample'] = logs[-2000:] if len(logs) > 2000 else logs
            alerts.append(f"Clone {name} is NOT running. Status: {status}")
        elif port is None:
            entry['healthy'] = False
            alerts.append(f"Clone {name} is running but port mapping missing.")
        else:
            healthy = health_check(port)
            entry['healthy'] = healthy
            if not healthy:
                logs = get_logs(name, tail=100)
                entry['logs_sample'] = logs[-2000:] if len(logs) > 2000 else logs
                alerts.append(f"Clone {name} health check failed on port {port}.")

        report.append(entry)

    # Output summary
    print('Clone Heartbeat Report:')
    print(json.dumps(report, indent=2))

    if alerts:
        print('\nAlerts:')
        for a in alerts:
            print(f'- {a}')
        # Exit code 1 indicates issues
        sys.exit(1)
    else:
        print('\nAll clones healthy.')
        sys.exit(0)


if __name__ == '__main__':
    main()
