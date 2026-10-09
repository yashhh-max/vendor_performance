# Video Asset Manifest & Production Inventory
## Complete Catalog of Typography, Visual Assets, Audio Stems & Design Tokens

---

### 1. Typography Hierarchy & Font Tokens

The production film maintains strict editorial typographic discipline adhering to the repository design system guidelines:

| Role | Font Family / Fallback | Weight | Target Size (px) | Tracking / Spacing | Color Token | Usage |
|---|---|---|---|---|---|---|
| **Primary Display** | `Segoe UI Bold` / `Helvetica Neue` / `Arial Bold` | 700 / Bold | 52px – 64px | -1.0px tight | `#F8F9FA` | Main scene hero titles |
| **Section Header** | `Segoe UI Semibold` / `Arial Bold` | 600 / Semibold | 34px – 40px | -0.5px | `#FFFFFF` | Sub-titles, card headers |
| **Category Eyebrow**| `Segoe UI Bold` / `Arial Bold` | 700 / Bold | 16px – 18px | +2.0px uppercase | `#00E5FF` | Pillar categories, badge tags |
| **Body Narrative** | `Segoe UI Regular` / `Arial` | 400 / Normal | 22px – 26px | Normal | `#94A3B8` | Explanatory text, descriptions |
| **Monospace / Code**| `Consolas` / `Courier New` | 400 / Normal | 18px – 22px | Monospaced | `#38BDF8` | SQL snippets, repo paths, stats |
| **Numerical Metric**| `Segoe UI Black` / `Arial Black` | 900 / Black | 48px – 72px | +0.5px tabular | `#10B981` / `#EF4444` | Percentage scores, order counts |

---

### 2. Color Palette & Aesthetic Tokens

| Token Name | Hex Code | RGB | Aesthetic Purpose |
|---|---|---|---|
| `--color-canvas-dark` | `#0B0F19` | `11, 15, 25` | Deep cinematic background backdrop |
| `--color-card-surface` | `#111827` | `17, 24, 39` | High-contrast glassmorphic card fill |
| `--color-card-border` | `#1F2937` | `31, 41, 55` | Subtle technical bounding frame |
| `--color-accent-cyan` | `#00E5FF` | `0, 229, 255` | Electric focal accent & motion trails |
| `--color-accent-blue` | `#3B82F6` | `59, 130, 246` | Data connections & system nodes |
| `--color-nvidia-green` | `#76B900` | `118, 185, 0` | Official NVIDIA branding & NIM badge |
| `--color-success-emerald` | `#10B981` | `16, 185, 129` | High-performing vendor metrics (Northstar) |
| `--color-warning-amber` | `#F59E0B` | `245, 158, 11` | Moderate risk & delay notifications |
| `--color-danger-crimson` | `#EF4444` | `239, 68, 68` | Critical failure & high-risk tier (Pinnacle) |
| `--color-text-white` | `#F8F9FA` | `248, 249, 250` | Primary text readability |
| `--color-text-muted` | `#94A3B8` | `148, 163, 184` | Secondary text hierarchy |

---

### 3. Audio Tracks & Sound Effects Inventory

All audio assets are authentic, licensed, royalty-free stems sourced directly from the production environment:

#### 3.1 Primary Music Track
- **File**: `happy-beats-business-moves-vol-1-by-ende-dot-app.mp3`
- **Location**: `C:\Users\yashw\.gemini\config\skills\brag\assets\music\`
- **Original Duration**: 163.96 Seconds
- **BPM / Key**: ~120 BPM, Corporate Tech / Driving Ambient Groove
- **Editorial Treatment**: Trimmed to 112.00s with a 2.5s logarithmic intro fade-in and 3.0s exponential outro fade-out.

#### 3.2 UI & Motion Sound Effects (SFX)
| SFX File | Category | Duration | Playback Point | Sync Event |
|---|---|---|---|---|
| `impactSoft_heavy_000.ogg` | Impact / Bass | 0.8s | 00:00.20 | Opening dark title slam |
| `switch_001.ogg` | Interface | 0.3s | 00:10.00 | Kinetic title beam expansion |
| `click1.ogg` | UI Click | 0.1s | 00:15.00 | Feature badge 1 appear |
| `click2.ogg` | UI Click | 0.1s | 00:16.20 | Feature badge 2 appear |
| `click3.ogg` | UI Click | 0.1s | 00:17.40 | Feature badge 3 appear |
| `bong_001.ogg` | Interface | 0.5s | 00:20.50 | Relational architecture link |
| `impactPlate_medium_001.ogg`| Impact | 0.6s | 00:34.00 | 4-Pillar formula reveal |
| `rollover1.ogg` | UI Tone | 0.2s | 00:41.00 | Delivery 35% bar start |
| `rollover4.ogg` | UI Tone | 0.2s | 00:43.00 | Quality 35% bar start |
| `impactSoft_heavy_002.ogg` | Impact | 0.7s | 00:48.00 | Split benchmark card slam |
| `error_005.ogg` | UI Alert | 0.6s | 01:02.00 | Critical anomaly warning |
| `switch_004.ogg` | Interface | 0.4s | 01:09.00 | Trend line decay graph entry |
| `keypress-001.wav` | Keyboard | 0.1s | 01:17.00 – 01:21.00 | Chat query typing cadences |
| `switch_006.ogg` | Interface | 0.4s | 01:23.00 | Fact inspection drawer slide |
| `mouseclick1.ogg` | UI Click | 0.1s | 01:30.00 – 01:34.00 | Test suite passes tick |
| `switch15.ogg` | Interface | 0.5s | 01:36.00 | Security badge lock-in |

---

### 4. Real Data & UI Capture Sources

- **Database Reference**: `backend/vendor_sync.db` (SQLite 3 relational database)
- **Verified Suppliers**:
  - `Northstar Components` (`V-1048`): 92 score, 96% delivery, 94% quality, 148 orders, 6 delayed, 3 defects.
  - `Atlas Packaging` (`V-0977`): 86 score, 89% delivery, 91% quality, 121 orders, 9 delayed, 5 defects.
  - `Meridian Office Supply` (`V-1021`): 78 score, 81% delivery, 82% quality, 96 orders, 18 delayed, 8 defects.
  - `BluePeak Logistics` (`V-1132`): 73 score, 76% delivery, 79% quality, 88 orders, 19 delayed, 11 defects.
  - `Pinnacle Industrial` (`V-1103`): 61 score, 64% delivery, 68% quality, 74 orders, 27 delayed, 14 defects.
- **Frontend Code Reference**:
  - `frontend/public/index.html`
  - `frontend/public/static/css/ai-copilot.css`
  - `frontend/public/static/js/ai-copilot.js`
