from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import subprocess, os, json, uuid, time

router = APIRouter(prefix="/api/clone", tags=["clone"])  # type: ignore

# Simple auth placeholder: in real app, use session or token
def get_current_user(request: Request):
    # For now, allow any; later integrate with clone auth system
    return "admin"

class LLMOverride(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None

class ResourceSpec(BaseModel):
    cpu: Optional[float] = 1.0
    memory: Optional[float] = 2.0  # in GB
    pids: Optional[int] = 100

class CreateClonePayload(BaseModel):
    parent_uuid: str
    port: Optional[int] = None
    memory_subdir: Optional[str] = None
    name: str
    project: str = "default"
    tags: List[str] = []
    llm_override: Optional[LLMOverride] = None
    resources: Optional[ResourceSpec] = ResourceSpec()
    tool_whitelist: List[str] = []
    network_policy: str = "none"
    heartbeat_interval: int = 10
    auto_update: bool = True
    log_level: str = "INFO"

    @validator('port')
    def port_range(cls, v):
        if v is not None and not (1024 <= v <= 65535):
            raise ValueError("Port must be between 1024 and 65535")
        return v

@router.get("/parents")
def list_parents(user: str = Depends(get_current_user)):
    """Return list of parent agents with their clone counts and child details.
    Reads the heartbeat registry (via parent manager) and clone stats.
    """
    # In production, this could query the parent_clone_manager registry file.
    # For MoC, return a single parent (Number One) if known.
    registry_path = "/a0/usr/clone_registry.json"
    parent_uuid = os.getenv('A0_PARENT_UUID')
    max_clones = int(os.getenv('A0_MAX_CLONES', '5'))
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        active_clones = [info for info in registry.values() if info.get('status') == 'active']
        current = len(active_clones)
        children = [{
            "name": info.get('name', info['container_id'][:12]),
            "port": info.get('port'),
            "status": info.get('status', 'active')
        } for info in active_clones]
        # Find parent name? maybe from A0_PARENT_NAME or registry entry
        parent_name = os.getenv('A0_PARENT_NAME', 'Number One')
        return [{
            "uuid": parent_uuid,
            "name": parent_name,
            "port": int(os.getenv('A0_PARENT_PORT', '42437')),
            "current_clones": current,
            "max_clones": max_clones,
            "clones": children
        }]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read registry: {e}")

@router.post("/create")
def create_clone(payload: CreateClonePayload, user: str = Depends(get_current_user)):
    """Create a new clone with the given configuration under the specified parent."""
    # Validate parent exists and has capacity (use same logic as list_parents)
    registry_path = "/a0/usr/clone_registry.json"
    max_clones = int(os.getenv('A0_MAX_CLONES', '5'))
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        active = [info for info in registry.values() if info.get('status') == 'active']
        if len(active) >= max_clones:
            raise HTTPException(status_code=400, detail="Parent has reached maximum clone capacity")
    except FileNotFoundError:
        pass  # no registry yet, ok

    # Prepare environment / args for clone.py
    # Memory subdir: generate if missing
    memory_subdir = payload.memory_subdir or f"clone-{uuid.uuid4().hex[:8]}"
    # Port: if not provided, find a free one (simple heuristic)
    port = payload.port
    if port is None:
        # Use a simple range from 50000 upwards; check not in use by scanning registry ports
        used_ports = {info.get('port') for info in registry.values() if info.get('port')}
        port = 50000
        while port in used_ports:
            port += 1
    # Build command to run clone.py inside the parent container? Here we assume we are inside the parent container and clone.py is available under /a0/skills/agent-clone/scripts/clone.py
    clone_script = "/a0/skills/agent-clone/scripts/clone.py"
    if not os.path.exists(clone_script):
        # Maybe we are in the main container and need to call docker exec into parent? Not implemented for PoC.
        raise HTTPException(status_code=500, detail="Clone script not found; ensure agent-clone skill is installed.")

    # Execute clone creation
    cmd = ["python", clone_script, str(port), memory_subdir]
    # Optional: pass JSON config via stdin or temp file; for now, assume clone.py copies base settings; later we will add flags for overrides.
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"clone.py failed: {result.stderr}")
        container_id = result.stdout.strip().split()[-1] if result.stdout.strip() else None
        # Update registry manually? In real system, parent manager will detect it via heartbeat. For immediate feedback, we can add an entry now.
        try:
            with open(registry_path, 'r+') as f:
                reg = json.load(f)
                reg[container_id] = {
                    "name": payload.name,
                    "port": port,
                    "memory_subdir": memory_subdir,
                    "status": "active",
                    "last_seen": time.time(),
                    "container_id": container_id,
                    "parent_uuid": payload.parent_uuid,
                    "project": payload.project,
                }
                f.seek(0); json.dump(reg, f, indent=2); f.truncate()
        except Exception as e:
            # Not critical; heartbeat will populate later
            pass
        return {
            "success": True,
            "uuid": str(uuid.uuid4()),
            "port": port,
            "container_id": container_id,
            "memory_subdir": memory_subdir
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Clone creation timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To include in main app, import this module and do: app.include_router(clone_api.router)
