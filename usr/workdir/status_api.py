import sys
sys.path.insert(0, '/a0')
import os
import json
import threading
import time
from datetime import datetime, timezone
from collections import deque
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, PlainTextResponse
import psutil
from observability import get_agent_status, MetricsCollector

app = FastAPI()
clone_metrics: Dict[str, Dict[str, Any]] = {}
traces_store: Dict[str, List[Dict[str, Any]]] = {}
trace_ttl_seconds = 300
log_buffer: deque = deque(maxlen=1000)
log_websockets: List[WebSocket] = []
clone_metrics_lock = threading.Lock()
traces_lock = threading.Lock()

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

def run(port=None):
    import uvicorn
    if port is None:
        port = int(os.getenv('A0_OBSERVABILITY_PORT', '8080'))
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='warning')
