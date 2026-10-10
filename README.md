# VendorSync AI — Enterprise Vendor Performance Platform
### Featuring Grounded AI Copilot powered by NVIDIA NIM (`nvidia/nemotron-3-ultra-550b-a55b`)

[![Live Public Deployment](https://img.shields.io/badge/Live%20Demo-HTTPS%20Online-success?logo=cloudflare)](https://eyes-reaches-scheme-legends.trycloudflare.com)
[![Backend Integration Tests](https://img.shields.io/badge/Backend%20Tests-15%2F15%20Passing-success)](test_backend.py)
[![NVIDIA AI Pytest Suite](https://img.shields.io/badge/Pytest%20Suite-16%2F16%20Passing-success)](tests/test_nvidia_chatbot.py)
[![NVIDIA NIM](https://img.shields.io/badge/AI%20Engine-NVIDIA%20NIM%20Active-76b900?logo=nvidia)](https://build.nvidia.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🌐 Live Public Deployment

The full-stack application is deployed live on the public internet:
- **Direct Public URL (Zero-Password):** [https://eyes-reaches-scheme-legends.trycloudflare.com](https://eyes-reaches-scheme-legends.trycloudflare.com)
- **Branded Subdomain URL:** [https://vendorsync-ai.loca.lt](https://vendorsync-ai.loca.lt) *(Tunnel Password: `27.6.169.89`)*
- **Demo Account:** `admin@vendorsync.ai` / `admin123`
- **Architecture:** Cloudflare Edge Anycast SSL → Zero-Trust Tunnel → FastAPI ASGI Core + Static SPA + SQLite/Postgres + NVIDIA NIM (`nemotron-3-ultra-550b-a55b`)
- **Detailed Deployment Guide:** See [DEPLOY.md](DEPLOY.md)

---

## 🚀 Overview

**VendorSync AI** is an enterprise-grade vendor intelligence and risk evaluation platform. This contribution introduces a **Grounded AI Chatbot for Vendor Performance Analysis**, allowing procurement managers, supply-chain analysts, and directors to query live supplier performance, evaluate delivery risks, perform head-to-head supplier comparisons, and inspect mathematical calculations in real time.

All AI responses are strictly grounded in deterministic calculations executed against the live database, eliminating LLM hallucinations and ensuring auditability.

---

## 🏛️ Architecture & Grounded Analytics Pipeline

The assistant enforces a strict separation of concerns between deterministic mathematics and LLM explanation:

```
┌────────────────────────┐
│     User Inquiry       │  (e.g., "Compare Northstar vs Meridian", "Highest spend")
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  Intent Classification │  (Ranking, Comparison, Risk/Defects, Spend, KPI Formula)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Deterministic Analytics│  • Aggregates live purchase order volume
│     Engine (Python)    │  • Evaluates delay rates, complaints, defects
└───────────┬────────────┘  • Computes 4-pillar score & risk penalty
            │
            ▼
┌────────────────────────┐
│ Verified Facts Payload │  Structured tabular context + mathematical ground truth
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│   NVIDIA NIM Client    │  `nvidia/nemotron-3-ultra-550b-a55b` via OpenAI SDK
│  (Strict Grounding)    │  Enforces factual adherence & strategic procurement advice
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Streamed / REST Reply  │  Includes "Inspect Grounded Data" audit drawer & copy action
└────────────────────────┘
```

---

## 📐 Mathematical KPI Framework

The deterministic engine evaluates suppliers according to clear mathematical contracts:

### 1. Overall Performance Score (0–100%)
A weighted composite balancing fulfillment consistency and commercial competitiveness:
$$\text{Score} = (\text{Delivery} \times 0.35) + (\text{Quality} \times 0.35) + (\text{Cost} \times 0.15) + (\text{Reliability} \times 0.15)$$

- **Delivery (35%)**: On-time shipment rate across all tracked purchase orders.
- **Quality (35%)**: Defect-adjusted batch inspection acceptance index.
- **Cost Efficiency (15%)**: Unit pricing competitiveness against market benchmarks.
- **Operational Reliability (15%)**: SLA adherence and response cadence.

### 2. Risk Score & Penalty Calculation
$$\text{Penalty} = \left(\frac{\text{Delayed Orders}}{\text{Total Orders}} \times 30\right) + (\text{Complaints} \times 4) + (\text{Defective Batches} \times 3)$$
$$\text{Risk Score} = \text{clamp}\Big(100 - \text{Score} + \text{Penalty},\, 5,\, 95\Big)$$

### 3. Exposure Classification
- **Low Risk**: $\text{Score} \ge 85$ and $\text{Risk Score} \le 20$
- **Medium Risk**: $\text{Score} \ge 68$ and $\text{Risk Score} \le 50$
- **High Risk**: $\text{Score} < 68$ or $\text{Risk Score} > 50$

---

## ⚡ NVIDIA NIM Integration & Configuration

The platform connects to NVIDIA NIM's API endpoints using the OpenAI-compatible SDK with automatic transient retry, exponential backoff, and secret key redaction.

### Environment Setup (`.env`)

Copy `.env.example` to `.env` and configure your credentials:

```bash
# --- NVIDIA AI / NIM (Primary Enterprise Provider) ---
# Obtain from https://build.nvidia.com/
NVIDIA_API_KEY=nvapi-your-secret-api-key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=nvidia/nemotron-3-ultra-550b-a55b

# --- Fallbacks (Optional) ---
GEMINI_API_KEY=
OPENAI_API_KEY=

# --- App Settings ---
PORT=8000
JWT_SECRET_KEY=your-production-secret-key
DATABASE_URL=
```

> **Security Note:** Secrets are strictly loaded from environment variables and `.env`. The `.env` file is protected by `.gitignore` and must never be committed to Git. All diagnostic output automatically redacts API keys.

---

## 🛠️ API Endpoints Reference

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/ai/status` | `GET` | Required | Returns active provider (`nvidia`), connected model, and dialect latency |
| `/api/ai/chat` | `POST` | Required | Grounded analytical conversation endpoint with verified figures payload |
| `/api/ai/chat/stream` | `POST` | Required | Real-time Server-Sent Events (SSE) token streaming from NVIDIA NIM |
| `/api/ai/grounding` | `POST` | Required | Returns pure deterministic mathematical facts without LLM invocation |
| `/api/ai/analyze/{vendor_id}` | `POST` | Required | Deep multi-factor risk diagnosis with drivers, positives & negotiation tips |
| `/api/risk/predict` | `POST` | Required | Hybrid deterministic + AI augmented risk evaluation for a supplier |
| `/api/health` | `GET` | Public | System and database latency health check |

---

## 🎨 UI/UX Design & Copilot Features

The AI Copilot has been crafted according to modern design principles (OLED Dark Mode, Inter typography, anti-slop standards):

- **Floating Docked & Maximize Mode**: Toggle between compact 500px drawer and expansive 860px analytical workbench.
- **Live Grounding Indicator**: Displays database dialect and query latency in milliseconds.
- **Supplier Scoping**: Scope prompts to the entire network or a single vendor (e.g. `Northstar Components`).
- **Prompt Suggestion Chips**: One-click shortcuts for high-spend suppliers, head-to-head comparisons, delay bottlenecks, and KPI formula breakdowns.
- **"Inspect Grounded Data" Accordion**: Transparency drawer under each response showing the raw calculation matrix.
- **Markdown Tables & Code Spans**: Responsive tables comparing suppliers side-by-side.
- **Deep AI Risk Audit Tab**: Multi-factor supplier evaluations with executive briefings and contract renegotiation advice.
- **KPI Methodology Tab**: Interactive formula guide explaining score weighting and penalty math.
- **One-Click Export**: Export conversation history to Markdown transcript.

---

## 🧪 Testing and Verification

Run the comprehensive automated test suites locally:

### 1. Pytest Suite (NVIDIA Integration & Analytics Engine)
```bash
pytest tests/test_nvidia_chatbot.py -v
```
**Results: 16 / 16 PASSED**
- Grounded analytics KPI mathematical integrity
- Comparative head-to-head matrix generator
- Anomaly & bottleneck detection
- Intent resolution & prompt construction
- API key redaction & security protection
- Input validation (empty inputs, 4000-char limits)
- Authenticated endpoint security
- Mocked NVIDIA timeout resilience & offline fallback

### 2. Original Backend Integration Tests
```bash
python test_backend.py
```
**Results: 15 / 15 PASSED**
- Unauthenticated access prevention (401)
- Admin login & JWT session cookies
- Dashboard stats & profile retrieval
- Vendor creation, notes, and deletion
- AI status & live Copilot chat
- Deep AI supplier risk analysis

---

## 💻 Running Locally

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python run_server.py
   ```

3. **Open the application:**
   Navigate to [http://localhost:8000](http://localhost:8000).
   - Default admin credentials: `admin@vendorsync.ai` / `admin123`
   - Click the **NV AI Copilot** button in the bottom right corner to interact with the assistant.