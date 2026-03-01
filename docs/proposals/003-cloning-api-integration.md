# Integration Instructions for Clone API

1. Open your main API file (likely `python/api/main.py` or `python/api/server.py`).
2. Add: `from . import clone_api` (adjust if needed).
3. Include the router: `app.include_router(clone_api.router)`.
4. Ensure the endpoint prefix matches your app's base path (currently `/api/clone`).
5. Restart the API server.
6. The frontend page `/webui/pages/cloning.html` will work once the APIs are available under the same origin.
