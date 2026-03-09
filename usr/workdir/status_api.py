import sys
sys.path.insert(0, '/a0')
sys.path.insert(0, '/a0/usr/workdir')
import os
import json
from pathlib import Path
import threading
import time
from datetime import datetime, timezone
from collections import deque
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, PlainTextResponse
import psutil
from observability import get_agent_status, MetricsCollector
from token_telemetry import token_counter


def get_public_url():
    try:
        settings_path = Path('/a0/usr/settings.json')
        if settings_path.exists():
            settings = json.loads(settings_path.read_text())
            return settings.get('public_url', 'http://localhost')
    except Exception:
        pass
    return 'http://localhost'

app = FastAPI()
clone_metrics: Dict[str, Dict[str, Any]] = {}
clone_token_metrics: Dict[str, Dict[str, Any]] = {}  # stores {'counters': {...}, 'costs': {...}}
traces_store: Dict[str, List[Dict[str, Any]]] = {}
trace_ttl_seconds = 300
log_buffer: deque = deque(maxlen=1000)
log_websockets: List[WebSocket] = []
clone_metrics_lock = threading.Lock()
traces_lock = threading.Lock()
clone_token_lock = threading.Lock()

@app.get('/health')
def health():
    return JSONResponse({'status': 'ok', 'timestamp': datetime.now(timezone.utc).isoformat()})

@app.get('/status')
def status():
    try:
        base = get_agent_status()
    except Exception as e:
        base = {'error': str(e)}
    with clone_metrics_lock:
        clones_snapshot = dict(clone_metrics)
    base['clones'] = clones_snapshot
    with traces_lock:
        base['traces'] = {
            'active_count': len(traces_store),
            'trace_ids': list(traces_store.keys())[:10]
        }
    base['dashboard_url'] = f"{get_public_url()}/status"
    base['health_url'] = f"{get_public_url()}/health"
    return JSONResponse(base)

@app.get('/metrics')
def metrics():
    mc = MetricsCollector()
    lines = []
    data = mc.to_dict()
    for name, val in data.get('counters', {}).items():
        lines.append(f'# TYPE a0_{name} counter')
        lines.append(f'a0_{name} {val}')
    for name, val in data.get('gauges', {}).items():
        lines.append(f'# TYPE a0_{name} gauge')
        lines.append(f'a0_{name} {val}')
    for name, values in data.get('histograms', {}).items():
        lines.append(f'# TYPE a0_{name} histogram')
        for v in values:
            lines.append(f'a0_{name} {v}')
    # Clone resource metrics
    with clone_metrics_lock:
        for clone_name, metrics in clone_metrics.items():
            cpu = metrics.get('cpu_percent')
            mem = metrics.get('memory_usage')
            if cpu is not None:
                lines.append(f'# TYPE a0_clone_cpu_percent gauge')
                lines.append(f'a0_clone_cpu_percent{{a0_clone="{clone_name}"}} {cpu}')
            if mem is not None:
                lines.append(f'# TYPE a0_clone_memory_bytes gauge')
                lines.append(f'a0_clone_memory_bytes{{a0_clone="{clone_name}"}} {mem}')
    # Token telemetry: aggregate leader + clones
    # First, collect leader's own token data
    leader_token_data = token_counter.get_metrics()
    # Prepare combined counters and costs
    combined_counters = {}
    combined_costs = {}
    # Add leader
    for cid, models in leader_token_data.get('counters', {}).items():
        combined_counters[cid] = models
    for cid, models in leader_token_data.get('costs', {}).items():
        combined_costs[cid] = models
    # Add clones
    with clone_token_lock:
        for clone_name, tdata in clone_token_metrics.items():
            counters = tdata.get('counters', {})
            costs = tdata.get('costs', {})
            # For each clone, counters keyed by model -> {input, output}
            for model, dirs in counters.items():
                if clone_name not in combined_counters:
                    combined_counters[clone_name] = {}
                if model not in combined_counters[clone_name]:
                    combined_counters[clone_name][model] = {'input': 0, 'output': 0}
                # Merge into existing (should be just this clone's own)
                combined_counters[clone_name][model]['input'] += dirs.get('input', 0)
                combined_counters[clone_name][model]['output'] += dirs.get('output', 0)
            for model, cost_val in costs.items():
                if clone_name not in combined_costs:
                    combined_costs[clone_name] = {}
                if model not in combined_costs[clone_name]:
                    combined_costs[clone_name][model] = 0.0
                combined_costs[clone_name][model] += cost_val
    # Emit token count metrics (counter)
    # TYPE a0_tokens_total counter (emit once)
    # We'll emit TYPE first time we encounter any token metric, but need exactly one TYPE line. We'll emit before series.
    emitted_token_type = False
    for clone_id, models in combined_counters.items():
        for model, dirs in models.items():
            inp = dirs.get('input', 0)
            out = dirs.get('output', 0)
            if inp > 0:
                if not emitted_token_type:
                    lines.append('# TYPE a0_tokens_total counter')
                    emitted_token_type = True
                lines.append(f'a0_tokens_total{{a0_clone="{clone_id}",a0_model="{model}",direction="input"}} {inp}')
            if out > 0:
                if not emitted_token_type:
                    lines.append('# TYPE a0_tokens_total counter')
                    emitted_token_type = True
                lines.append(f'a0_tokens_total{{a0_clone="{clone_id}",a0_model="{model}",direction="output"}} {out}')
    # Emit cost metrics (gauge)
    emitted_cost_type = False
    for clone_id, models in combined_costs.items():
        for model, cost in models.items():
            if cost > 0:
                if not emitted_cost_type:
                    lines.append('# TYPE a0_cost_total gauge')
                    emitted_cost_type = True
                lines.append(f'a0_cost_total{{a0_clone="{clone_id}",a0_model="{model}",currency="USD"}} {cost:.6f}')
    return PlainTextResponse('\n'.join(lines))

@app.post('/metrics/containers')
async def receive_container_metrics(request: Dict[str, Any]):
    clone_name = request.get('clone_name', 'unknown')
    payload = {
        'cpu_percent': request.get('cpu_percent'),
        'memory_usage': request.get('memory_usage'),
        'memory_limit': request.get('memory_limit'),
        'timestamp': request.get('timestamp', datetime.now(timezone.utc).isoformat())
    }
    with clone_metrics_lock:
        clone_metrics[clone_name] = payload
    # Store token metrics if present
    token_metrics = request.get('token_metrics')
    if token_metrics:
        with clone_token_lock:
            clone_token_metrics[clone_name] = token_metrics
    log_buffer.append(f"[Metrics] {clone_name}: CPU {payload['cpu_percent']}%, Memory {payload['memory_usage']} bytes")
    for ws in list(log_websockets):
        try:
            await ws.send_json({'type': 'metrics', 'data': payload})
        except Exception:
            if ws in log_websockets:
                log_websockets.remove(ws)
    return JSONResponse({'ok': True})

@app.post('/traces')
async def receive_traces(request: List[Dict[str, Any]]):
    now = time.time()
    with traces_lock:
        for span in request:
            trace_id = span.get('trace_id')
            if not trace_id:
                continue
            if trace_id not in traces_store:
                traces_store[trace_id] = []
            traces_store[trace_id].append(span)
        expired = [tid for tid, spans in traces_store.items() if now - spans[-1].get('start_time', now) > trace_ttl_seconds]
        for tid in expired:
            del traces_store[tid]
    return JSONResponse({'ok': True, 'stored_traces': len(request)})

@app.get('/traces/{trace_id}')
def get_trace(trace_id: str):
    with traces_lock:
        spans = traces_store.get(trace_id, [])
    return JSONResponse({'trace_id': trace_id, 'spans': spans})

@app.post('/logs')
async def receive_logs(logs: List[Dict[str, Any]]):
    for entry in logs:
        try:
            line = json.dumps(entry)
            log_buffer.append(line)
            for ws in list(log_websockets):
                try:
                    await ws.send_json(entry)
                except Exception:
                    if ws in log_websockets:
                        log_websockets.remove(ws)
        except Exception:
            continue
    return JSONResponse({'ok': True, 'received': len(logs)})

@app.websocket('/ws/logs')
async def ws_logs(websocket: WebSocket):
    await websocket.accept()
    log_websockets.append(websocket)
    try:
        while True:
            for line in list(log_buffer):
                try:
                    data = json.loads(line)
                    await websocket.send_json(data)
                except Exception:
                    await websocket.send_text(line)
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in log_websockets:
            log_websockets.remove(websocket)
    except Exception:
        if websocket in log_websockets:
            log_websockets.remove(websocket)

@app.get('/token_metrics')
def token_metrics():
    # Return aggregated token metrics JSON
    leader_data = token_counter.get_metrics()
    combined = {'leader': leader_data}
    with clone_token_lock:
        for clone_name, tdata in clone_token_metrics.items():
            combined[clone_name] = tdata
    return JSONResponse(combined)

def run(port=None):
    import uvicorn
    if port is None:
        port = int(os.getenv('A0_OBSERVABILITY_PORT', '8080'))
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='warning')
