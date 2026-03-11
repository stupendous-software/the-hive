import asyncio
import json
import logging
from datetime import datetime, timezone
from collections import defaultdict
from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
import nest_asyncio
from observability import get_agent_status, get_system_metrics, get_logs, StructuredLogger

nest_asyncio.apply()

app = FastAPI(title="Hive Status API", version="1.0")
logger = StructuredLogger(agent_id='status_api')

@app.get('/health')
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get('/status')
def status():
    try:
        data = get_agent_status()
        # Ensure dashboard_url and health_url use localhost (host-reachable)
        data['dashboard_url'] = 'http://localhost:8080'
        data['health_url'] = 'http://localhost:8080/health'
        return data
    except Exception as e:
        logger.error('Failed to get agent status', error=str(e))
        return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get('/metrics')
def metrics():
    try:
        data = get_system_metrics()
        # Convert to Prometheus text format including counters and gauges
        lines = []
        # Add metric type definitions
        for key in data.get('gauges', {}):
            lines.append(f'# TYPE {key} gauge')
        for key in data.get('counters', {}):
            lines.append(f'# TYPE {key} counter')
        # Add metric values
        for key, value in data.get('gauges', {}).items():
            lines.append(f'{key} {value}')
        for key, value in data.get('counters', {}).items():
            lines.append(f'{key} {value}')
        # Add histogram summaries if present
        for name, values in data.get('histograms', {}).items():
            if values:
                count = len(values)
                total = sum(values)
                lines.append(f'# TYPE {name} histogram')
                lines.append(f'{name}_count {count}')
                lines.append(f'{name}_sum {total}')
                lines.append(f'{name}_bucket {{le="{max(values)}"}} {count}')
        return PlainTextResponse('\n'.join(lines))
    except Exception as e:
        logger.error('Failed to get metrics', error=str(e))
        return PlainTextResponse(f'# Error: {e}\n', status_code=500)

@app.get('/logs')
def logs(limit: int = 100):
    try:
        entries = get_logs(limit=limit)
        return {
            "count": len(entries),
            "entries": entries,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error('Failed to get logs', error=str(e))
        return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}

@app.websocket('/ws/logs')
async def ws_logs(websocket):
    await websocket.accept()
    try:
        while True:
            # Send heartbeat and optionally recent logs
            payload = {
                'heartbeat': datetime.now(timezone.utc).isoformat()
            }
            # Optionally include recent log entries
            try:
                recent = get_logs(limit=5)
                payload['logs'] = recent
            except Exception:
                pass
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(2)
    except Exception as e:
        logger.error('WebSocket error', error=str(e))
    finally:
        await websocket.close()

if __name__ == '__main__':
    import uvicorn
    logger.info('Starting Hive Status API', host='0.0.0.0', port=8080)
    uvicorn.run(app, host='0.0.0.0', port=8080)
