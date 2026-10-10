import sys
import os
from urllib.parse import parse_qs, urlencode

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import Request
from app.main import app
from app.database import init_db

try:
    init_db()
except Exception:
    pass

@app.middleware("http")
async def vercel_path_rewrite_middleware(request: Request, call_next):
    # Check if Vercel passed the path via _path query param
    path_param = request.query_params.get("_path")
    if path_param is not None:
        clean_path = "/" + path_param.lstrip("/")
        if not clean_path.startswith("/api"):
            clean_path = "/api" + clean_path
        
        request.scope["path"] = clean_path
        request.scope["raw_path"] = clean_path.encode("ascii")
        
        # Clean up _path from query_string so it does not interfere with endpoint logic
        raw_qs = request.scope.get("query_string", b"").decode("latin-1")
        if raw_qs:
            qs = parse_qs(raw_qs)
            qs.pop("_path", None)
            flat_qs = {k: v[0] if len(v) == 1 else v for k, v in qs.items()}
            request.scope["query_string"] = urlencode(flat_qs).encode("latin-1")

    return await call_next(request)
