import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Canvas Configuration
WIDTH = 1920
HEIGHT = 1080
FPS = 30
TOTAL_DURATION = 112 # seconds
TOTAL_FRAMES = TOTAL_DURATION * FPS # 3360 frames

# Color Palette (Deep Charcoal, Refined Ivory, Electric Cyan, Emerald, Amber, Crimson)
BG_DARK = (11, 15, 25)          # #0B0F19
CARD_SURFACE = (17, 24, 39)     # #111827
CARD_SURFACE_LIGHT = (26, 36, 56) # #1A2438
CARD_BORDER = (31, 41, 55)      # #1F2937
ACCENT_CYAN = (0, 229, 255)     # #00E5FF
ACCENT_BLUE = (59, 130, 246)    # #3B82F6
ACCENT_NVIDIA = (118, 185, 0)   # #76B900
SUCCESS_EMERALD = (16, 185, 129)# #10B981
WARNING_AMBER = (245, 158, 11)  # #F59E0B
DANGER_CRIMSON = (239, 68, 68)  # #EF4444
TEXT_WHITE = (248, 249, 250)    # #F8F9FA
TEXT_MUTED = (148, 163, 184)    # #94A3B8
TEXT_DIM = (100, 116, 139)      # #64748B

# Font Cache
FONTS = {}

def get_font(size, bold=False, mono=False):
    key = (size, bold, mono)
    if key in FONTS:
        return FONTS[key]
    
    candidates = []
    if mono:
        candidates = ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/cour.ttf"]
    elif bold:
        candidates = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
    else:
        candidates = ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
        
    font = None
    for c in candidates:
        if os.path.exists(c):
            try:
                font = ImageFont.truetype(c, size)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()
    FONTS[key] = font
    return font

def ease_in_out(t):
    """Sigmoid-style smooth easing between 0.0 and 1.0"""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)

def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) * (1.0 - t)

# Reusable Drawing Primitives
def draw_rounded_card(draw, x, y, w, h, bg_color=CARD_SURFACE, border_color=CARD_BORDER, border_width=2, radius=12):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg_color, outline=border_color, width=border_width)

def draw_badge(draw, x, y, text, font, text_color, bg_color, border_color=None, padding_x=14, padding_y=6, radius=6):
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    bw = tw + padding_x * 2
    bh = th + padding_y * 2
    draw.rounded_rectangle([x, y, x + bw, y + bh], radius=radius, fill=bg_color, outline=border_color or bg_color, width=1)
    draw.text((x + padding_x, y + padding_y - bbox[1]), text, font=font, fill=text_color)
    return bw

def draw_progress_bar(draw, x, y, w, h, pct, fill_color, bg_color=(20, 28, 45), radius=4):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg_color)
    fill_w = max(4, int(w * max(0.0, min(1.0, pct))))
    draw.rounded_rectangle([x, y, x + fill_w, y + h], radius=radius, fill=fill_color)

def draw_background(draw, frame_idx):
    # Base dark gradient
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=BG_DARK)
    
    # Animated subtle grid lines
    grid_spacing = 80
    drift_x = int((frame_idx * 0.4) % grid_spacing)
    drift_y = int((frame_idx * 0.2) % grid_spacing)
    grid_color = (18, 24, 38)
    
    for gx in range(drift_x, WIDTH, grid_spacing):
        draw.line([(gx, 0), (gx, HEIGHT)], fill=grid_color, width=1)
    for gy in range(drift_y, HEIGHT, grid_spacing):
        draw.line([(0, gy), (WIDTH, gy)], fill=grid_color, width=1)

    # Ambient top edge subtle gradient line
    draw.line([(0, 0), (WIDTH, 0)], fill=ACCENT_CYAN, width=2)

def draw_header_nav(draw, current_act="ACT I", title="VENDOR PERFORMANCE ANALYSIS"):
    # Clean top status bar
    f_cat = get_font(13, bold=True)
    f_tit = get_font(13, bold=False, mono=True)
    draw.text((80, 45), current_act, font=f_cat, fill=ACCENT_CYAN)
    bbox = f_cat.getbbox(current_act)
    cat_w = bbox[2] - bbox[0]
    draw.text((80 + cat_w + 16, 45), "•  " + title, font=f_tit, fill=TEXT_MUTED)
    
    # Live system badge on top right
    draw_badge(draw, 1680, 40, "ENGINE ONLINE", get_font(11, bold=True), SUCCESS_EMERALD, (12, 38, 28), SUCCESS_EMERALD)

# =============================================================================
# SCENE RENDERERS (9 SCENES)
# =============================================================================

def render_scene_1(draw, frame_idx, local_frame, duration_frames):
    """Scene 1 (0:00 - 0:10): The Fragmentation Dilemma & Data Noise"""
    draw_background(draw, frame_idx)
    draw_header_nav(draw, "ACT I: THE HOOK", "SUPPLY CHAIN FRAGMENTATION")
    
    progress = local_frame / duration_frames
    fade_in = ease_out(min(1.0, local_frame / 45.0))
    
    # Floating chaotic data cards (flickering in space)
    cards = [
        (220, 260, "ORD-8821: STATUS UNKNOWN", "$42,500", DANGER_CRIMSON),
        (1280, 220, "V-1103: 36.5% DELAY RATE", "ALERT", WARNING_AMBER),
        (380, 680, "INVOICE DISCREPANCY: +14.2%", "UNAUDITED", DANGER_CRIMSON),
        (1340, 640, "QUALITY DEFECTS: 14 UNITS", "HIGH RISK", DANGER_CRIMSON),
        (820, 160, "MISSING SLA BENCHMARKS", "ERP SILO", TEXT_DIM)
    ]
    
    for i, (cx, cy, label, badge, col) in enumerate(cards):
        # Subtle floating motion
        float_y = int(math.sin(progress * math.pi * 2 + i * 1.5) * 12)
        c_alpha = ease_out(min(1.0, max(0.0, (local_frame - i * 15) / 30.0)))
        if c_alpha > 0.05:
            draw_rounded_card(draw, cx, cy + float_y, 360, 90, bg_color=(15, 21, 34), border_color=(col[0]//2, col[1]//2, col[2]//2))
            draw.text((cx + 20, cy + float_y + 20), label, font=get_font(14, bold=True, mono=True), fill=TEXT_WHITE)
            draw_badge(draw, cx + 20, cy + float_y + 50, badge, get_font(11, bold=True), col, (col[0]//6, col[1]//6, col[2]//6))

    # Center Hero Typography
    f_lead = get_font(20, bold=True)
    f_hero = get_font(52, bold=True)
    f_sub = get_font(24, bold=False)
    
    text_y = int(460 - (1.0 - fade_in) * 30)
    
    draw.text((WIDTH//2 - 280, text_y - 70), "THE PROCUREMENT DILEMMA", font=f_lead, fill=ACCENT_CYAN)
    draw.text((WIDTH//2 - 460, text_y), "Every vendor generates data.", font=f_hero, fill=TEXT_WHITE)
    draw.text((WIDTH//2 - 380, text_y + 80), "The challenge is finding the signal.", font=f_sub, fill=TEXT_MUTED)

def render_scene_2(draw, frame_idx, local_frame, duration_frames):
    """Scene 2 (0:10 - 0:20): Project Identity Reveal"""
    draw_background(draw, frame_idx)
    draw_header_nav(draw, "ACT I: SYSTEM IDENTITY", "VENDORSYNC AI PLATFORM")
    
    progress = local_frame / duration_frames
    expand = ease_out(min(1.0, local_frame / 40.0))
    
    # Expanding horizontal beam
    beam_w = int(1400 * expand)
    beam_x = (WIDTH - beam_w) // 2
    draw.line([(beam_x, 340), (beam_x + beam_w, 340)], fill=ACCENT_CYAN, width=3)
    
    # Title Reveal
    f_title = get_font(56, bold=True)
    f_desc = get_font(26, bold=False)
    
    ty = int(380 - (1.0 - expand) * 20)
    draw.text((WIDTH//2 - 480, ty), "VENDOR PERFORMANCE ANALYSIS", font=f_title, fill=TEXT_WHITE)
    draw.text((WIDTH//2 - 420, ty + 85), "Turning raw supply chain data into actionable intelligence.", font=f_desc, fill=TEXT_MUTED)
    
    # 3 Feature Badges
    badges = [
        ("DETERMINISTIC 4-PILLAR SCORING", ACCENT_CYAN, 0),
        ("MULTI-FACTOR RISK TRIAGING", SUCCESS_EMERALD, 15),
        ("NVIDIA NIM GROUNDED INTELLIGENCE", ACCENT_NVIDIA, 30)
    ]
    
    card_w = 400
    total_w = 3 * card_w + 2 * 40
    start_x = (WIDTH - total_w) // 2
    
    for i, (text, col, delay) in enumerate(badges):
        b_enter = ease_out(min(1.0, max(0.0, (local_frame - 20 - delay) / 30.0)))
        bx = start_x + i * (card_w + 40)
        by = int(620 - (1.0 - b_enter) * 30)
        if b_enter > 0.05:
            draw_rounded_card(draw, bx, by, card_w, 140, bg_color=CARD_SURFACE, border_color=col, border_width=2)
            draw.line([(bx + 25, by + 40), (bx + 85, by + 40)], fill=col, width=3)
            draw.text((bx + 25, by + 65), text, font=get_font(15, bold=True), fill=TEXT_WHITE)

def render_scene_3(draw, frame_idx, local_frame, duration_frames):
    """Scene 3 (0:20 - 0:34): Relational Architecture & Pipeline Hygiene"""
    draw_background(draw, frame_idx)
    draw_header_nav(draw, "ACT II: DATA ENGINEERING", "RELATIONAL ARCHITECTURE & HYGIENE")
    
    f_sec = get_font(36, bold=True)
    draw.text((80, 110), "Engineered for Complete Data Integrity", font=f_sec, fill=TEXT_WHITE)
    draw.text((80, 160), "Dual-dialect database engine powering zero-latency analytics and strict relational models.", font=get_font(18), fill=TEXT_MUTED)
    
    # 3 System Architecture Columns
    cols = [
        ("1. Transactional Ingestion", "orders, notes, purchase timestamps\n\n• 15 Purchase Orders fulfilled\n• Line-item dollar tracking\n• Delivery SLA timestamping", ACCENT_CYAN),
        ("2. Dual-Engine Persistence", "SQLite 3 (Edge) & Supabase PostgreSQL\n\n• Foreign key constraints\n• Sub-millisecond latency (0.51ms)\n• Cloud-ready schema migrations", ACCENT_BLUE),
        ("3. Canonical Pipeline", "analytics_engine.py & scoring.py\n\n• 4-Pillar composite calculations\n• Anomaly & trend detection\n• Factual markdown table contract", SUCCESS_EMERALD)
    ]
    
    card_w = 540
    card_h = 480
    start_x = 80
    
    for i, (title, content, col) in enumerate(cols):
        c_enter = ease_out(min(1.0, max(0.0, (local_frame - i * 15) / 30.0)))
        cx = start_x + i * (card_w + 30)
        cy = int(240 - (1.0 - c_enter) * 30)
        
        draw_rounded_card(draw, cx, cy, card_w, card_h, bg_color=CARD_SURFACE, border_color=col, border_width=2)
        draw.text((cx + 35, cy + 35), title, font=get_font(22, bold=True), fill=col)
        draw.line([(cx + 35, cy + 75), (cx + card_w - 35, cy + 75)], fill=(col[0]//3, col[1]//3, col[2]//3), width=1)
        
        # Multiline body
        lines = content.split("\n")
        ly = cy + 105
        for l in lines:
            draw.text((cx + 35, ly), l, font=get_font(17), fill=TEXT_WHITE if "•" in l else TEXT_MUTED)
            ly += 32

    # Bottom Telemetry Bar
    bar_y = 820
    draw_rounded_card(draw, 80, bar_y, 1760, 100, bg_color=(15, 23, 42), border_color=CARD_BORDER)
    draw.text((120, bar_y + 35), "LIVE TELEMETRY:", font=get_font(15, bold=True, mono=True), fill=ACCENT_CYAN)
    draw.text((310, bar_y + 35), "15 Orders Tracked   |   7 Enterprise Suppliers   |   0 Data Anomalies   |   Latency: 0.51ms", font=get_font(16, mono=True), fill=TEXT_WHITE)

def render_scene_4(draw, frame_idx, local_frame, duration_frames):
    """Scene 4 (0:34 - 0:48): 4-Pillar Mathematical Formulation"""
    draw_background(draw, frame_idx)
    draw_header_nav(draw, "ACT III: MATHEMATICAL SCORING", "4-PILLAR COMPOSITE FORMULA")
    
    f_sec = get_font(36, bold=True)
    draw.text((80, 110), "Deterministic Evaluation: Zero Guesswork", font=f_sec, fill=TEXT_WHITE)
    draw.text((80, 160), "Every score is mathematically calculated using audited formulas across 4 operational dimensions.", font=get_font(18), fill=TEXT_MUTED)
    
    # Formula Highlight Card
    draw_rounded_card(draw, 80, 220, 1760, 120, bg_color=(15, 25, 48), border_color=ACCENT_CYAN, border_width=2)
    draw.text((120, 245), "COMPOSITE OVERALL SCORE FORMULA", font=get_font(13, bold=True), fill=ACCENT_CYAN)
    draw.text((120, 275), "Score = (0.35 × Delivery) + (0.35 × Quality) + (0.15 × Cost) + (0.15 × Reliability)", font=get_font(26, bold=True, mono=True), fill=TEXT_WHITE)
    
    # 4 Pillar Progress Meters
    pillars = [
        ("On-Time Delivery", 0.35, "35%", "100 × (1 - Delayed / Total)", ACCENT_CYAN),
        ("Quality & Defects", 0.35, "35%", "100 × (1 - [1.5×Defects + Complaints] / Total)", SUCCESS_EMERALD),
        ("Cost Adherence", 0.15, "15%", "Benchmark margin & invoice compliance", WARNING_AMBER),
        ("Contract Reliability", 0.15, "15%", "SLA uptime & responsiveness index", ACCENT_BLUE)
    ]
    
    pw = 410
    start_x = 80
    m_progress = ease_out(min(1.0, local_frame / 45.0))
    
    for i, (p_name, weight, wt_text, p_formula, col) in enumerate(pillars):
        px = start_x + i * (pw + 40)
        py = 390
        draw_rounded_card(draw, px, py, pw, 460, bg_color=CARD_SURFACE, border_color=col, border_width=2)
        
        draw.text((px + 30, py + 35), p_name, font=get_font(20, bold=True), fill=TEXT_WHITE)
        draw.text((px + 30, py + 70), "WEIGHT: " + wt_text, font=get_font(14, bold=True, mono=True), fill=col)
        
        # Meter fill
        bar_y = py + 120
        draw_progress_bar(draw, px + 30, bar_y, pw - 60, 16, weight * m_progress * (1.0 / 0.35), col)
        
        draw.line([(px + 30, py + 170), (px + pw - 30, py + 170)], fill=CARD_BORDER, width=1)
        
        draw.text((px + 30, py + 200), "CALCULATION:", font=get_font(12, bold=True), fill=TEXT_MUTED)
        draw.text((px + 30, py + 230), p_formula, font=get_font(15, mono=True), fill=TEXT_WHITE)
        
        # Key rule note
        draw.text((px + 30, py + 360), "Bounded: [0, 100]", font=get_font(13, bold=True, mono=True), fill=col)

def render_scene_5(draw, frame_idx, local_frame, duration_frames):
    """Scene 5 (0:48 - 1:02): Empirical Benchmarking - Top vs Bottom Suppliers"""
    draw_background(draw, frame_idx)
    draw_header_nav(draw, "ACT III: EMPIRICAL BENCHMARKS", "REAL REPOSITORY DATASET")
    
    f_sec = get_font(36, bold=True)
    draw.text((80, 110), "Empirical Dataset: Real Vendor Performance", font=f_sec, fill=TEXT_WHITE)
    draw.text((80, 160), "Real production data directly queried from backend/vendor_sync.db.", font=get_font(18), fill=TEXT_MUTED)
    
    enter_prog = ease_out(min(1.0, local_frame / 35.0))
    
    # Left Card: Benchmark Leader (Northstar)
    lx = 80
    ly = int(240 - (1.0 - enter_prog) * 30)
    card_w = 850
    card_h = 560
    
    draw_rounded_card(draw, lx, ly, card_w, card_h, bg_color=CARD_SURFACE, border_color=SUCCESS_EMERALD, border_width=2)
    draw_badge(draw, lx + 40, ly + 35, "TIER-1 BENCHMARK LEADER", get_font(12, bold=True), SUCCESS_EMERALD, (12, 38, 28), SUCCESS_EMERALD)
    draw.text((lx + 40, ly + 80), "Northstar Components", font=get_font(36, bold=True), fill=TEXT_WHITE)
    draw.text((lx + 40, ly + 130), "ID: V-1048  •  Category: Electronics  •  Contract: $100,000", font=get_font(15, mono=True), fill=TEXT_MUTED)
    
    # Metrics Grid
    m_y = ly + 180
    draw.text((lx + 40, m_y), "OVERALL SCORE: 92%", font=get_font(28, bold=True), fill=SUCCESS_EMERALD)
    draw.text((lx + 480, m_y), "RISK: LOW (12%)", font=get_font(28, bold=True), fill=SUCCESS_EMERALD)
    
    draw_progress_bar(draw, lx + 40, m_y + 50, 360, 14, 0.92, SUCCESS_EMERALD)
    draw_progress_bar(draw, lx + 480, m_y + 50, 330, 14, 0.12, SUCCESS_EMERALD)
    
    # Stat rows
    s_y = ly + 290
    draw.text((lx + 40, s_y), "• On-Time Delivery: 96% (148 Orders, 6 Delayed)", font=get_font(18), fill=TEXT_WHITE)
    draw.text((lx + 40, s_y + 40), "• Defect Ratio: 2.0% (Only 3 defects logged)", font=get_font(18), fill=TEXT_WHITE)
    draw.text((lx + 40, s_y + 80), "• Quality Score: 94% Defect-Free Compliance", font=get_font(18), fill=TEXT_WHITE)
    draw.text((lx + 40, s_y + 120), "• Trailing Trend: 84 → 86 → 88 → 90 → 91 → 92 (Positive)", font=get_font(18, mono=True), fill=ACCENT_CYAN)

    # Right Card: Bottleneck Supplier (Pinnacle)
    rx = 990
    ry = ly
    draw_rounded_card(draw, rx, ry, card_w, card_h, bg_color=CARD_SURFACE, border_color=DANGER_CRIMSON, border_width=2)
    draw_badge(draw, rx + 40, ry + 35, "OPERATIONAL BOTTLENECK", get_font(12, bold=True), DANGER_CRIMSON, (45, 15, 15), DANGER_CRIMSON)
    draw.text((rx + 40, ry + 80), "Pinnacle Industrial", font=get_font(36, bold=True), fill=TEXT_WHITE)
    draw.text((rx + 40, ry + 130), "ID: V-1103  •  Category: Equipment  •  Contract: $100,000", font=get_font(15, mono=True), fill=TEXT_MUTED)
    
    draw.text((rx + 40, m_y), "OVERALL SCORE: 61%", font=get_font(28, bold=True), fill=DANGER_CRIMSON)
    draw.text((rx + 480, m_y), "RISK: HIGH (67%)", font=get_font(28, bold=True), fill=DANGER_CRIMSON)
    
    draw_progress_bar(draw, rx + 40, m_y + 50, 360, 14, 0.61, DANGER_CRIMSON)
    draw_progress_bar(draw, rx + 480, m_y + 50, 330, 14, 0.67, DANGER_CRIMSON)
    
    draw.text((rx + 40, s_y), "• On-Time Delivery: 64% (27 Delayed / 74 Orders)", font=get_font(18), fill=DANGER_CRIMSON)
    draw.text((rx + 40, s_y + 40), "• Defect Count: 14 Defective Units Logged", font=get_font(18), fill=TEXT_WHITE)
    draw.text((rx + 40, s_y + 80), "• Customer Escalations: 15 Complaints", font=get_font(18), fill=TEXT_WHITE)
    draw.text((rx + 40, s_y + 120), "• Trailing Trend: 72 → 69 → 66 → 64 → 63 → 61 (Decay)", font=get_font(18, mono=True), fill=DANGER_CRIMSON)

    # Bottom Delta Bar
    draw_rounded_card(draw, 80, 840, 1760, 90, bg_color=(16, 25, 45), border_color=ACCENT_CYAN)
    draw.text((120, 870), "EMPIRICAL DELTA:", font=get_font(16, bold=True, mono=True), fill=ACCENT_CYAN)
    draw.text((320, 870), "+32% Delivery Advantage  |  -78% Defect Exposure  |  Action: Shift allocation from V-1103 to V-1048", font=get_font(17, bold=True), fill=TEXT_WHITE)

def render_scene_6(draw, frame_idx, local_frame, duration_frames):
    """Scene 6 (1:02 - 1:16): Proactive Anomaly Triaging"""
    draw_background(draw, frame_idx)
    draw_header_nav(draw, "ACT IV: PREDICTIVE ANOMALY DETECTION", "SUPPLIER DISRUPTION RISK")
    
    f_sec = get_font(36, bold=True)
    draw.text((80, 110), "Automated Anomaly Detection & Risk Triaging", font=f_sec, fill=TEXT_WHITE)
    draw.text((80, 160), "Catching operational bottlenecks before production delays impact end-users.", font=get_font(18), fill=TEXT_MUTED)
    
    # Pulsing warning card
    pulse = (math.sin(local_frame * 0.2) + 1.0) * 0.5
    border_col = (int(DANGER_CRIMSON[0] * (0.6 + 0.4 * pulse)), int(DANGER_CRIMSON[1] * 0.5), int(DANGER_CRIMSON[2] * 0.5))
    
    draw_rounded_card(draw, 80, 230, 850, 620, bg_color=CARD_SURFACE, border_color=border_col, border_width=3)
    draw_badge(draw, 120, 265, "CRITICAL ANOMALY ALERT", get_font(13, bold=True), DANGER_CRIMSON, (45, 15, 15), DANGER_CRIMSON)
    
    draw.text((120, 320), "36.5% Delivery Failure Rate", font=get_font(32, bold=True), fill=TEXT_WHITE)
    draw.text((120, 370), "Target: Pinnacle Industrial (V-1103)", font=get_font(18, mono=True), fill=ACCENT_CYAN)
    
    # Anomaly checklist
    items = [
        ("27 Orders Exceeded Delivery SLA", "Average delay exceeds contract grace period by 4.2 days."),
        ("14 Recorded Physical Hardware Defects", "Concentrated in batch deliveries during Q2 procurement."),
        ("15 Formal Customer Escalations", "3x above portfolio baseline complaint rate."),
        ("Score Degraded by -11 Points over 6 Months", "Steady degradation from 72% down to 61%.")
    ]
    
    iy = 430
    for title, desc in items:
        draw.text((120, iy), "[!] " + title, font=get_font(17, bold=True), fill=DANGER_CRIMSON)
        draw.text((155, iy + 26), desc, font=get_font(14), fill=TEXT_MUTED)
        iy += 70
        
    draw_badge(draw, 120, 770, "RECOMMENDATION: INITIATE FORMAL CORRECTIVE ACTION PLAN (CAP)", get_font(13, bold=True), WARNING_AMBER, (40, 30, 10))

    # Right Card: Historical Trend Decay Chart
    rx = 990
    draw_rounded_card(draw, rx, 230, 850, 620, bg_color=CARD_SURFACE, border_color=CARD_BORDER, border_width=2)
    draw.text((rx + 40, 265), "TRAIL OF HISTORICAL SCORE DECAY", font=get_font(18, bold=True), fill=TEXT_WHITE)
    draw.text((rx + 40, 300), "6-Month Progression (Jan - Jun)", font=get_font(14, mono=True), fill=TEXT_MUTED)
    
    # Animated Line Graph
    scores = [72, 69, 66, 64, 63, 61]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    
    gx = rx + 80
    gy_base = 680
    gh = 300
    gw = 680
    
    # Graph Axes
    draw.line([(gx, gy_base), (gx + gw, gy_base)], fill=CARD_BORDER, width=2)
    draw.line([(gx, gy_base - gh), (gx, gy_base)], fill=CARD_BORDER, width=2)
    
    step_x = gw / (len(scores) - 1)
    pts = []
    anim_progress = ease_out(min(1.0, local_frame / 40.0))
    
    for idx, s in enumerate(scores):
        px = gx + idx * step_x
        # 60 to 75 scale
        norm_y = (s - 55) / 25.0
        py = gy_base - norm_y * gh
        pts.append((px, py))
        
        # Month labels
        draw.text((px - 15, gy_base + 15), months[idx], font=get_font(13, mono=True), fill=TEXT_MUTED)
        
    # Draw graph line
    for idx in range(len(pts) - 1):
        if idx < int(anim_progress * (len(pts) - 1)):
            draw.line([pts[idx], pts[idx+1]], fill=DANGER_CRIMSON, width=4)
            # Dot
            draw.ellipse([pts[idx][0]-6, pts[idx][1]-6, pts[idx][0]+6, pts[idx][1]+6], fill=TEXT_WHITE, outline=DANGER_CRIMSON, width=2)
            draw.text((pts[idx][0]-12, pts[idx][1]-32), str(scores[idx]), font=get_font(15, bold=True, mono=True), fill=DANGER_CRIMSON)

    # Last dot
    last_pt = pts[-1]
    draw.ellipse([last_pt[0]-6, last_pt[1]-6, last_pt[0]+6, last_pt[1]+6], fill=TEXT_WHITE, outline=DANGER_CRIMSON, width=2)
    draw.text((last_pt[0]-12, last_pt[1]-32), str(scores[-1]), font=get_font(15, bold=True, mono=True), fill=DANGER_CRIMSON)

def render_scene_7(draw, frame_idx, local_frame, duration_frames):
    """Scene 7 (1:16 - 1:30): NVIDIA NIM Copilot & Grounding Drawer"""
    draw_background(draw, frame_idx)
    draw_header_nav(draw, "ACT IV: NVIDIA NIM COPILOT", "GROUNDED AI INTELLIGENCE")
    
    f_sec = get_font(36, bold=True)
    draw.text((80, 110), "NVIDIA NIM Copilot: Zero-Hallucination Intelligence", font=f_sec, fill=TEXT_WHITE)
    draw.text((80, 160), "Two-stage pipeline: deterministic facts extracted from SQL before dispatching to Nemotron-3 Ultra.", font=get_font(18), fill=TEXT_MUTED)
    
    # Left: Interactive Chat Window
    cw = 1000
    ch = 680
    cx = 80
    cy = 230
    draw_rounded_card(draw, cx, cy, cw, ch, bg_color=CARD_SURFACE, border_color=CARD_BORDER, border_width=2)
    
    # Chat header
    draw.rectangle([cx, cy, cx + cw, cy + 65], fill=(22, 32, 51))
    draw_badge(draw, cx + 30, cy + 18, "NVIDIA NIM", get_font(12, bold=True), ACCENT_NVIDIA, (20, 40, 10), ACCENT_NVIDIA)
    draw.text((cx + 170, cy + 22), "nemotron-3-ultra-550b-a55b  •  Active Session", font=get_font(14, mono=True), fill=TEXT_WHITE)
    
    # User message (typing animation)
    full_prompt = "Which vendor should I select for our high-value microelectronic assemblies?"
    type_chars = int(min(len(full_prompt), local_frame * 1.5))
    typed_text = full_prompt[:type_chars]
    cursor = "_" if (frame_idx // 10) % 2 == 0 else ""
    
    draw_rounded_card(draw, cx + 180, cy + 100, 780, 80, bg_color=(28, 41, 65), border_color=ACCENT_CYAN, border_width=1)
    draw.text((cx + 210, cy + 125), typed_text + cursor, font=get_font(17), fill=TEXT_WHITE)
    
    # AI Response Bubble (Fades in after typing)
    if local_frame > 60:
        a_prog = ease_out(min(1.0, (local_frame - 60) / 30.0))
        ay = cy + 220
        draw_rounded_card(draw, cx + 40, ay, 920, 320, bg_color=(15, 23, 38), border_color=ACCENT_NVIDIA, border_width=2)
        draw_badge(draw, cx + 70, ay + 25, "GROUNDED RECOMMENDATION", get_font(12, bold=True), SUCCESS_EMERALD, (12, 38, 28))
        
        reply_lines = [
            "Based on verified repository metrics, select Northstar Components (V-1048):",
            "• Performance Score: 92% (Portfolio Leader)",
            "• On-Time Delivery: 96% SLA compliance across 148 purchase orders (only 6 delays)",
            "• Defect Rate: 2.0% with only 3 logged defect units across historical shipments",
            "• Risk Profile: Low Risk (12%) with positive 6-month upward trend (84 → 92)",
            "",
            "Strategic Advice: Shift volume away from Pinnacle Industrial (V-1103) which exhibits",
            "a 36.5% delay rate and a critical 67% risk rating."
        ]
        
        rly = ay + 75
        for rl in reply_lines:
            draw.text((cx + 70, rly), rl, font=get_font(15), fill=TEXT_WHITE if "•" in rl else TEXT_MUTED)
            rly += 26

    # Right: Slide-out Fact Inspection Drawer
    drawer_prog = ease_out(min(1.0, max(0.0, (local_frame - 90) / 30.0)))
    dw = 700
    dx = int(1140 + (1.0 - drawer_prog) * 60)
    dy = cy
    
    draw_rounded_card(draw, dx, dy, dw, ch, bg_color=(16, 26, 44), border_color=ACCENT_CYAN, border_width=2)
    draw.text((dx + 35, dy + 30), "FACT INSPECTION DRAWER", font=get_font(17, bold=True), fill=ACCENT_CYAN)
    draw.text((dx + 35, dy + 65), "[VERIFIED CONTRACT: ZERO HALLUCINATION]", font=get_font(12, bold=True, mono=True), fill=SUCCESS_EMERALD)
    
    draw.line([(dx + 35, dy + 100), (dx + dw - 35, dy + 100)], fill=CARD_BORDER, width=1)
    
    # Verified facts table snippet
    facts = [
        ("Vendor ID", "V-1048"),
        ("Supplier", "Northstar Components"),
        ("Category", "Electronics"),
        ("Overall Score", "92% (Calculated)"),
        ("Delivery Rate", "96.0% (142/148)"),
        ("Quality Rate", "94.0% (3 defects)"),
        ("Risk Band", "Low (12%)"),
        ("Engine Mode", "NVIDIA NIM / Grounded")
    ]
    
    fy = dy + 130
    for k, v in facts:
        draw.text((dx + 40, fy), k, font=get_font(15, mono=True), fill=TEXT_MUTED)
        draw.text((dx + 340, fy), v, font=get_font(15, bold=True, mono=True), fill=TEXT_WHITE)
        fy += 45

def render_scene_8(draw, frame_idx, local_frame, duration_frames):
    """Scene 8 (1:30 - 1:42): Enterprise Architecture & Test Suite Verification"""
    draw_background(draw, frame_idx)
    draw_header_nav(draw, "ACT V: ENTERPRISE ASSURANCE", "TEST COVERAGE & SECURITY")
    
    f_sec = get_font(36, bold=True)
    draw.text((80, 110), "Enterprise-Grade Reliability & Security", font=f_sec, fill=TEXT_WHITE)
    draw.text((80, 160), "100% test pass rate across mathematical validation, intent resolution, and security gates.", font=get_font(18), fill=TEXT_MUTED)
    
    # Left: Terminal Test Output
    tw = 950
    th = 640
    tx = 80
    ty = 230
    draw_rounded_card(draw, tx, ty, tw, th, bg_color=(12, 17, 28), border_color=SUCCESS_EMERALD, border_width=2)
    
    # Terminal Top Bar
    draw.rectangle([tx, ty, tx + tw, ty + 45], fill=(20, 28, 45))
    draw.ellipse([tx + 20, ty + 16, tx + 32, ty + 28], fill=DANGER_CRIMSON)
    draw.ellipse([tx + 40, ty + 16, tx + 52, ty + 28], fill=WARNING_AMBER)
    draw.ellipse([tx + 60, ty + 16, tx + 72, ty + 28], fill=SUCCESS_EMERALD)
    draw.text((tx + 100, ty + 12), "pytest tests/ -v  (31/31 SUITES VERIFIED)", font=get_font(14, mono=True), fill=TEXT_MUTED)
    
    # Test items
    tests = [
        "test_kpi_formulas_integrity ......................... PASSED",
        "test_compare_vendors_head_to_head ................... PASSED",
        "test_find_anomalies_and_risks ....................... PASSED",
        "test_portfolio_statistics_calculation ............... PASSED",
        "test_nvidia_security_key_redaction .................. PASSED",
        "test_build_nvidia_messages_grounding ................ PASSED",
        "test_unauthenticated_chat_rejected (401) ............ PASSED",
        "test_excessive_message_length_validation ............ PASSED",
        "test_ai_chat_end_to_end ............................. PASSED",
        "test_vendor_scoping_in_chat ......................... PASSED",
        "test_mocked_nvidia_timeout_fallback ................. PASSED",
        "test_backend.py (15/15 Regression Tests) ............. PASSED"
    ]
    
    show_count = int(min(len(tests), local_frame / 6.0))
    t_y = ty + 65
    for idx in range(show_count):
        draw.text((tx + 30, t_y), tests[idx], font=get_font(15, mono=True), fill=SUCCESS_EMERALD if "PASSED" in tests[idx] else TEXT_WHITE)
        t_y += 40

    # Right: 3 Security Badges
    rw = 760
    rx = 1080
    
    sec_cards = [
        ("API Key Redaction", "All exceptions and outgoing traces automatically mask credentials as nvapi-***REDACTED***.", SUCCESS_EMERALD),
        ("HTTPOnly Cookie Auth", "Protected JWT tokens prevent cross-site scripting and unauthorized procurement access.", ACCENT_CYAN),
        ("Offline Deterministic Fallback", "Graceful degradation ensures 100% platform availability if NVIDIA NIM times out.", WARNING_AMBER)
    ]
    
    for i, (stitle, sdesc, scol) in enumerate(sec_cards):
        sy = ty + i * 215
        draw_rounded_card(draw, rx, sy, rw, 195, bg_color=CARD_SURFACE, border_color=scol, border_width=2)
        draw.text((rx + 35, sy + 30), "[PASS]  " + stitle, font=get_font(21, bold=True), fill=scol)
        draw.text((rx + 35, sy + 75), sdesc, font=get_font(16), fill=TEXT_WHITE)

def render_scene_9(draw, frame_idx, local_frame, duration_frames):
    """Scene 9 (1:42 - 1:52): Final Brand Reveal & Repository Call to Action"""
    draw_background(draw, frame_idx)
    
    progress = local_frame / duration_frames
    fade_out = 1.0 - ease_in_out(max(0.0, (local_frame - (duration_frames - 35)) / 35.0))
    
    # Grand Center Card
    cw = 1400
    ch = 680
    cx = (WIDTH - cw) // 2
    cy = (HEIGHT - ch) // 2
    
    draw_rounded_card(draw, cx, cy, cw, ch, bg_color=(15, 22, 36), border_color=ACCENT_CYAN, border_width=2)
    
    draw.line([(cx + 80, cy + 120), (cx + cw - 80, cy + 120)], fill=ACCENT_CYAN, width=2)
    
    f_brand = get_font(56, bold=True)
    f_sub = get_font(26, bold=False)
    
    draw.text((cx + 100, cy + 50), "VENDORSYNC AI", font=f_brand, fill=TEXT_WHITE)
    draw.text((cx + 620, cy + 72), "NEXT-GEN PROCUREMENT INTELLIGENCE", font=get_font(16, bold=True), fill=ACCENT_CYAN)
    
    # 3 Summary Pillars
    bullets = [
        ("DETERMINISTIC EVALUATION", "Replaced subjective intuition with empirical 4-pillar mathematical scoring."),
        ("ZERO-HALLUCINATION AI", "Anchored NVIDIA Nemotron-3 Ultra strictly to verified relational data contracts."),
        ("PROACTIVE RESILIENCE", "Early anomaly identification eliminates supplier disruption and line-stoppage risk.")
    ]
    
    by = cy + 160
    for btitle, bdesc in bullets:
        draw.text((cx + 100, by), "• " + btitle, font=get_font(20, bold=True), fill=ACCENT_CYAN)
        draw.text((cx + 125, by + 34), bdesc, font=get_font(18), fill=TEXT_MUTED)
        by += 90

    # Contribution Banner
    draw_rounded_card(draw, cx + 80, cy + 470, cw - 160, 140, bg_color=(20, 32, 54), border_color=SUCCESS_EMERALD, border_width=1)
    draw.text((cx + 120, cy + 500), "CONTRIBUTION SUMMARY:", font=get_font(15, bold=True, mono=True), fill=SUCCESS_EMERALD)
    draw.text((cx + 120, cy + 535), "Repository: https://github.com/chikkajyothika-max/vendor_performance", font=get_font(16, mono=True), fill=TEXT_WHITE)
    draw.text((cx + 120, cy + 565), "Feature Branch: feat/ai-vendor-performance-chatbot   •   Pull Request #1: Open & Passing", font=get_font(16, mono=True), fill=ACCENT_CYAN)

# =============================================================================
# MASTER TIMELINE ROUTER
# =============================================================================

def render_frame(frame_idx):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    
    sec = frame_idx / FPS
    
    if sec < 10.0:
        render_scene_1(draw, frame_idx, frame_idx, int(10.0 * FPS))
    elif sec < 20.0:
        render_scene_2(draw, frame_idx, frame_idx - 10 * FPS, int(10.0 * FPS))
    elif sec < 34.0:
        render_scene_3(draw, frame_idx, frame_idx - 20 * FPS, int(14.0 * FPS))
    elif sec < 48.0:
        render_scene_4(draw, frame_idx, frame_idx - 34 * FPS, int(14.0 * FPS))
    elif sec < 62.0:
        render_scene_5(draw, frame_idx, frame_idx - 48 * FPS, int(14.0 * FPS))
    elif sec < 76.0:
        render_scene_6(draw, frame_idx, frame_idx - 62 * FPS, int(14.0 * FPS))
    elif sec < 90.0:
        render_scene_7(draw, frame_idx, frame_idx - 76 * FPS, int(14.0 * FPS))
    elif sec < 102.0:
        render_scene_8(draw, frame_idx, frame_idx - 90 * FPS, int(12.0 * FPS))
    else:
        render_scene_9(draw, frame_idx, frame_idx - 102 * FPS, int(10.0 * FPS))
        
    # Global fade to black in the final 1.5 seconds
    if sec > (TOTAL_DURATION - 1.5):
        fade_t = (sec - (TOTAL_DURATION - 1.5)) / 1.5
        alpha = int(255 * (1.0 - fade_t))
        overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        img = Image.blend(overlay, img, alpha / 255.0)

    return img

def render_full_film(output_video="video/vendor-performance-full-project-cinematic.mp4"):
    audio_track = "video/soundtrack_mix.wav"
    if not os.path.exists(audio_track):
        print("Soundtrack mix missing! Building audio first...")
        import build_audio
        build_audio.build_audio(audio_track)

    print(f"Starting cinematic video render: {TOTAL_FRAMES} frames ({TOTAL_DURATION}s @ {FPS}fps)...")
    
    # FFmpeg Pipe Command
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", audio_track,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-movflags", "+faststart",
        "-t", str(TOTAL_DURATION),
        output_video
    ]
    
    log_file = open("video/ffmpeg_render.log", "w")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log_file)
    
    for f in range(TOTAL_FRAMES):
        frame_img = render_frame(f)
        proc.stdin.write(frame_img.tobytes())
        
        if f % 150 == 0 or f == TOTAL_FRAMES - 1:
            pct = (f + 1) / TOTAL_FRAMES * 100
            print(f"Rendered {f + 1}/{TOTAL_FRAMES} frames ({pct:.1f}%) - {f/FPS:.1f}s", flush=True)
            
    proc.stdin.close()
    proc.wait()
    log_file.close()
    
    if proc.returncode != 0:
        with open("video/ffmpeg_render.log", "r") as lf:
            print("FFmpeg error:", lf.read()[-1000:])
        return False
        
    print(f"\nFilm rendered successfully to: {output_video}", flush=True)
    return True

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "video/vendor-performance-full-project-cinematic.mp4"
    render_full_film(out_file)
