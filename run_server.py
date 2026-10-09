import sys
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# Ensure backend directory is in sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("RAILWAY_PORT", 8080)))
    db_url = os.environ.get("DATABASE_URL", "")
    nvidia_key = os.environ.get("NVIDIA_API_KEY", "")
    nvidia_model = os.environ.get("NVIDIA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    if nvidia_key:
        ai_engine_str = f"NVIDIA NIM ({nvidia_model.split('/')[-1]}) [ACTIVE]"
    elif gemini_key:
        ai_engine_str = f"Google Gemini ({gemini_model}) [ACTIVE]"
    else:
        ai_engine_str = "Smart Grounded Analytics Engine (Offline)"

    print("=" * 60)
    print("  VendorSync AI — Platform Starting")
    print("=" * 60)
    print(f"  Port:       {port}")
    print(f"  Web App:    http://0.0.0.0:{port}")
    print(f"  Database:   {'PostgreSQL [OK]' if db_url else 'SQLite (local)'}")
    print(f"  AI Engine:  {ai_engine_str}")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
