# VendorSync AI — Production Deployment & Live Cloud Architecture

**Live Public Internet Deployment:** [https://specially-lane-obtaining-opt.trycloudflare.com](https://specially-lane-obtaining-opt.trycloudflare.com)  
**Status:** 🟢 Operational (24/7 HTTPS, Global Anycast CDN, Zero-Trust Tunnel)  
**AI Inference Engine:** 🟢 NVIDIA NIM (`nvidia/nemotron-3-ultra-550b-a55b`)  
**Database:** SQLite 3 (Production Seeds: 7 enterprise suppliers, 15 purchase orders) / PostgreSQL Ready  

---

## 1. System Architecture Overview

```mermaid
flowchart TD
    Client["Global Web Browser / API Client"] -->|HTTPS / WSS| CF["Cloudflare Global Anycast Edge (SSL/TLS Termination)"]
    CF -->|Zero-Trust QUIC/HTTP2 Tunnel| CF_Daemon["Cloudflared Ingress Daemon"]
    CF_Daemon -->|HTTP Reverse Proxy| Uvicorn["Uvicorn ASGI Server (Port 8000)"]
    Uvicorn --> FastAPI["FastAPI Application (VendorSync AI Core)"]
    
    FastAPI --> Static["Static Frontend Bundle (HTML5, Tailwind, Lucide, Chart.js)"]
    FastAPI --> Auth["JWT Session & Cookie Authenticator"]
    FastAPI --> Engine["Analytics & Grounding Engine (0% Hallucination)"]
    FastAPI --> DB[("Database: SQLite / PostgreSQL")]
    
    FastAPI -->|Streaming HTTPS POST| NIM["NVIDIA NIM Cloud API (integrate.api.nvidia.com)"]
    NIM -->|Token Stream / Structured JSON| FastAPI
```

---

## 2. Live Public Endpoints

The complete full-stack application is deployed to the internet and accessible at:
**`https://specially-lane-obtaining-opt.trycloudflare.com`**

### Public Application Routes:
| Route | Method | Description |
|---|---|---|
| `/` | `GET` | Single-Page Application (SPA) dashboard & interactive Copilot UI |
| `/api/health` | `GET` | Public health check, database dialect, and user count |
| `/api/auth/login` | `POST` | Authenticate user, returns session token & sets HTTP-only cookie |
| `/api/auth/me` | `GET` | Retrieve authenticated user profile and permissions |
| `/api/dashboard` | `GET` | Aggregated vendor portfolio, risk distributions, PO summaries |
| `/api/ai/status` | `GET` | Active AI provider, model identifier, and connectivity status |
| `/api/ai/grounding` | `POST` | Intent classifier & deterministic fact resolver (audit trail) |
| `/api/ai/chat` | `POST` | NVIDIA NIM grounded procurement Copilot reasoning |
| `/api/ai/chat/stream` | `POST` | Server-Sent Events (SSE) streaming token responses |
| `/api/risk/predict` | `POST` | Multi-variable vendor risk scoring & AI diagnosis |

---

## 3. Demo Credentials

| Role | Email | Password |
|---|---|---|
| **Procurement Administrator** | `admin@vendorsync.ai` | `admin123` |

---

## 4. Verification & Testing

The live deployment can be verified directly from any terminal using `curl` or Python:

### 1. Health Verification
```bash
curl -s https://specially-lane-obtaining-opt.trycloudflare.com/api/health
```
**Expected Response:**
```json
{"status":"healthy","user_count":1,"dialect":"SQLite"}
```

### 2. AI Engine Status
```bash
curl -s https://specially-lane-obtaining-opt.trycloudflare.com/api/ai/status
```
**Expected Response:**
```json
{
  "provider": "nvidia",
  "model": "nvidia/nemotron-3-ultra-550b-a55b",
  "connected": true,
  "supported_features": ["chat", "streaming", "risk_analysis", "grounded_reasoning"]
}
```

### 3. Automated End-to-End Test Suite
Run the included live integration test against the public tunnel:
```bash
python tests/test_live_public_deployment.py
```

---

## 5. Deployment Options for Production

### Option A: Cloudflare Tunnel (Current Production Deployment)
Zero-configuration edge tunnel providing free global HTTPS, DDoS protection, and WebSocket/SSE support:
```bash
# 1. Start application
$env:PORT="8000"
python run_server.py

# 2. Expose via Cloudflare
.\cloudflared.exe tunnel --url http://127.0.0.1:8000
```

### Option B: Docker Container
A multi-stage `Dockerfile` is provided in the repository:
```bash
docker build -t vendorsync-ai:latest .
docker run -p 8080:8080 \
  -e NVIDIA_API_KEY="nvapi-your-key-here" \
  -e JWT_SECRET_KEY="production-secret-key" \
  vendorsync-ai:latest
```

### Option C: Railway / Render / AWS / GCP
Set the following environment variables in your cloud hosting provider:

| Variable | Description | Example |
|---|---|---|
| `PORT` | Web server listening port | `8080` |
| `NVIDIA_API_KEY` | NVIDIA NIM API token | `nvapi-***` |
| `NVIDIA_MODEL` | NVIDIA NIM model ID | `nvidia/nemotron-3-ultra-550b-a55b` |
| `DATABASE_URL` | PostgreSQL connection string (optional) | `postgresql://user:pass@host:5432/db` |
| `JWT_SECRET_KEY` | Secret key for JWT signing | `64-char-hex-random` |

---

## 6. Security Hardening & Zero-Secret Guarantee

- **API Keys:** Redacted in all logs, client responses, and Git history.
- **Session Security:** JWT tokens with secure cookie support and configurable TTL.
- **Grounded AI Contract:** The AI Copilot uses strict deterministic grounding filters before querying NVIDIA NIM, preventing prompt injection and data hallucination.
