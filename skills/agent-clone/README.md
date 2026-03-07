# Agent Clone Skill for The Hive

This skill allows the Hive parent agent to spawn new clone sub-agents. It uses the custom Hive Docker image and follows the volume naming conventions (`hive_data`, `hive_heartbeat`, `hive_logs`, `hive_tmp`).

## Usage
```bash
python scripts/clone.py <port> <memory_subdir>
```
- `<port>`: Port on which the clone's web UI will be available on the host (e.g., 50081).
- `<memory_subdir>`: Name of the clone (used for memory isolation and container name).

The script creates a new Docker container running `brianheston/the-hive:beta`, sets appropriate environment variables, and starts the clone. The heartbeat sender inside the clone registers it with the parent manager.

## Notes
- The parent manager (`parent_clone_manager.py`) monitors clones via the shared `hive_heartbeat` volume.
- Clones are automatically terminated if idle for 15 minutes or if the parent exceeds the maximum of 5 active clones.
