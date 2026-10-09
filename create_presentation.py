import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_presentation(output_path="vendor_performance_presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    BG_DARK = RGBColor(11, 19, 43)        # #0B132B
    CARD_BG = RGBColor(28, 37, 65)        # #1C2541
    CARD_BORDER = RGBColor(58, 80, 107)   # #3A506F
    TEXT_WHITE = RGBColor(248, 249, 250)  # #F8F9FA
    TEXT_MUTED = RGBColor(180, 190, 205)  # #B4BECD
    ACCENT_CYAN = RGBColor(0, 229, 255)   # #00E5FF
    ACCENT_BLUE = RGBColor(72, 202, 228)  # #48CAE4
    SUCCESS_GREEN = RGBColor(16, 185, 129)# #10B981
    WARNING_AMBER = RGBColor(245, 158, 11)# #F59E0B
    DANGER_RED = RGBColor(239, 68, 68)    # #EF4444

    def add_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.color.rgb = BG_DARK
        return bg

    def add_header(slide, title_text, category="VENDORSYNC AI | ENTERPRISE PLATFORM"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, title="", border_color=CARD_BORDER, bg_color=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        if title:
            tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(0.5))
            tf = tb.text_frame
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(15)
            p.font.bold = True
            p.font.color.rgb = ACCENT_CYAN
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1)

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.15), Inches(3.8))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_CYAN
    bar.line.color.rgb = ACCENT_CYAN

    tb = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "NEXT-GENERATION SUPPLY CHAIN GOVERNANCE"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_CYAN

    p1 = tf.add_paragraph()
    p1.text = "Vendor Performance Analysis\n& AI Procurement Copilot"
    p1.font.size = Pt(38)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_before = Pt(12)
    p1.space_after = Pt(16)

    p2 = tf.add_paragraph()
    p2.text = "Deterministic 4-Pillar Scoring  |  Multi-Factor Risk Triaging  |  NVIDIA NIM Grounded Intelligence"
    p2.font.size = Pt(16)
    p2.font.color.rgb = TEXT_MUTED

    # Bottom badge card
    add_card(s1, 0.8, 6.0, 11.7, 0.85, bg_color=RGBColor(18, 26, 48))
    tb_badge = s1.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.6))
    tf_badge = tb_badge.text_frame
    p_b = tf_badge.paragraphs[0]
    p_b.text = "Repository: chikkajyothika-max/vendor_performance  •  Contributor: yashhh-max  •  Engine: NVIDIA Nemotron-3"
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = ACCENT_BLUE

    # =========================================================================
    # SLIDE 2: THE BUSINESS PROBLEM
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2)
    add_header(s2, "The Procurement Blind Spot: Why Supplier Data Fails")

    # 3 Stat Cards
    c1 = add_card(s2, 0.8, 1.8, 3.7, 4.8, "Data Fragmentation")
    tb = s2.shapes.add_textbox(Inches(1.05), Inches(2.5), Inches(3.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ERP SILOS & NOISE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = DANGER_RED
    p2 = tf.add_paragraph()
    p2.text = "• Fulfillment logs, quality inspection sheets, and invoices live in disconnected silos.\n• Procurement managers spend 15+ hours/month manually aggregating Excel sheets for vendor reviews.\n• Lack of real-time visibility prevents proactive escalation."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(12)

    c2 = add_card(s2, 4.8, 1.8, 3.7, 4.8, "Hidden Defect Rates")
    tb = s2.shapes.add_textbox(Inches(5.05), Inches(2.5), Inches(3.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "36.5% DELAY SURPRISE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = WARNING_AMBER
    p2 = tf.add_paragraph()
    p2.text = "• Suppliers with catastrophic delivery failures (e.g. Pinnacle Industrial: 27/74 orders delayed) continue receiving PO renewals.\n• Hidden quality defects (14 logged units) slip through without automated score penalties.\n• Subjective relationship bias clouds empirical vendor risk."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(12)

    c3 = add_card(s2, 8.8, 1.8, 3.7, 4.8, "Hallucination Trap")
    tb = s2.shapes.add_textbox(Inches(9.05), Inches(2.5), Inches(3.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "AI RELIABILITY CRISIS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p2 = tf.add_paragraph()
    p2.text = "• Generic LLMs invent delivery percentages and hallucinate non-existent supplier contracts.\n• Mission-critical supply decisions demand 100% mathematical certainty.\n• Enterprise compliance requires audit-ready source attribution and strict key protection."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(12)

    # =========================================================================
    # SLIDE 3: THE VENDORSYNC AI SOLUTION
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3)
    add_header(s3, "The VendorSync AI Solution: 3-Tier Enterprise Architecture")

    # 3 Horizontal Cards
    tier1 = add_card(s3, 0.8, 1.8, 11.7, 1.4, "1. Deterministic Data Layer (SQLite / Supabase PostgreSQL)")
    tb = s3.shapes.add_textbox(Inches(1.05), Inches(2.4), Inches(11.2), Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Structured storage of vendors, purchase orders, qualitative relationship notes, and trailing 6-month historical metrics with relational integrity and low-latency indexed queries."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MUTED

    tier2 = add_card(s3, 0.8, 3.5, 11.7, 1.4, "2. Analytical Intelligence & Scoring Engine (FastAPI + Python)")
    tb = s3.shapes.add_textbox(Inches(1.05), Inches(4.1), Inches(11.2), Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Automated 4-pillar composite scoring (35% Delivery, 35% Quality, 15% Cost, 15% Reliability), multi-factor risk categorization (Low/Medium/High), and automated anomaly detection."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MUTED

    tier3 = add_card(s3, 0.8, 5.2, 11.7, 1.4, "3. NVIDIA NIM AI Copilot & Grounded Context Gateway")
    tb = s3.shapes.add_textbox(Inches(1.05), Inches(5.8), Inches(11.2), Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Strict zero-hallucination prompt contract powered by NVIDIA Nemotron-3 Ultra (550B), live fact-verification inspection drawer, credential redaction, and offline deterministic fallback."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: 4-PILLAR KPI MATHEMATICAL FORMULATION
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4)
    add_header(s4, "Rigorous Mathematical Foundation: 4-Pillar Scoring Model")

    # Formula highlight card
    f_card = add_card(s4, 0.8, 1.8, 11.7, 1.2, "Composite Overall Score Formulation", border_color=ACCENT_CYAN)
    tb = s4.shapes.add_textbox(Inches(1.05), Inches(2.4), Inches(11.2), Inches(0.5))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Overall Score = (0.35 × Delivery) + (0.35 × Quality) + (0.15 × Cost) + (0.15 × Reliability)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    # 4 Pillar Cards
    pillars = [
        ("On-Time Delivery (35%)", "Delivery = 100 × (1 - Delayed / Total)\nMeasures shipment SLA compliance and lead time consistency.", ACCENT_CYAN),
        ("Quality & Defects (35%)", "Quality = 100 × (1 - [1.5×Defects + 1.0×Complaints] / Total)\nPenalizes physical defects and customer escalations.", SUCCESS_GREEN),
        ("Cost Adherence (15%)", "Cost = Margin adherence score (0-100)\nEvaluates invoice accuracy, price stability, and contract discount tiers.", WARNING_AMBER),
        ("Reliability (15%)", "Reliability = Responsiveness index (0-100)\nTracks SLA uptime, speed of issue resolution, and support responsiveness.", ACCENT_BLUE)
    ]

    for i, (p_title, p_desc, color) in enumerate(pillars):
        left = 0.8 + (i * 2.95)
        add_card(s4, left, 3.2, 2.85, 3.5, p_title, border_color=color)
        tb = s4.shapes.add_textbox(Inches(left + 0.15), Inches(3.9), Inches(2.55), Inches(2.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = p_desc
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5: EMPIRICAL BENCHMARK: REAL DATASET
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5)
    add_header(s5, "Empirical Dataset Benchmark: Real Supplier Performance Data")

    # Table of real vendors
    rows = 6
    cols = 7
    table_shape = s5.shapes.add_table(rows, cols, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
    table = table_shape.table

    headers = ["Vendor ID", "Supplier Name", "Category", "Score", "Risk Level", "Delivery Rate", "Quality Rate"]
    col_widths = [Inches(1.2), Inches(3.2), Inches(1.8), Inches(1.2), Inches(1.5), Inches(1.4), Inches(1.4)]
    for idx, width in enumerate(col_widths):
        table.columns[idx].width = width

    for col_idx, h_text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(18, 26, 48)
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = ACCENT_CYAN

    data = [
        ("V-1048", "Northstar Components", "Electronics", "92%", "Low (12%)", "96%", "94%"),
        ("V-0977", "Atlas Packaging", "Packaging", "86%", "Low (18%)", "89%", "91%"),
        ("V-1021", "Meridian Office Supply", "Stationery", "78%", "Medium (38%)", "81%", "82%"),
        ("V-1132", "BluePeak Logistics", "Logistics", "73%", "Medium (44%)", "76%", "79%"),
        ("V-1103", "Pinnacle Industrial", "Equipment", "61%", "High (67%)", "64%", "68%"),
    ]

    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, text in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 1 else RGBColor(22, 30, 52)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(13)
            if col_idx == 3: # Score
                p.font.bold = True
                p.font.color.rgb = SUCCESS_GREEN if int(text.replace("%","")) >= 80 else (WARNING_AMBER if int(text.replace("%","")) >= 70 else DANGER_RED)
            elif col_idx == 4: # Risk
                p.font.color.rgb = SUCCESS_GREEN if "Low" in text else (WARNING_AMBER if "Medium" in text else DANGER_RED)
            else:
                p.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 6: CRITICAL RISK EXPOSURE & ANOMALY DETECTION
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6)
    add_header(s6, "Automated Anomaly Detection & Operational Bottlenecks")

    # Left: High Risk Deep Dive
    add_card(s6, 0.8, 1.8, 5.7, 4.8, "High-Risk Case: Pinnacle Industrial (V-1103)", border_color=DANGER_RED)
    tb = s6.shapes.add_textbox(Inches(1.05), Inches(2.5), Inches(5.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CRITICAL METRIC BREAKDOWN"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DANGER_RED
    p2 = tf.add_paragraph()
    p2.text = "• Delay Rate: 36.5% (27 of 74 orders failed SLA)\n• Defect Count: 14 defective units logged\n• Escalated Complaints: 15 customer incident tickets\n• Trailing Trend: Consistent downward drop across 6 months (72 → 69 → 66 → 64 → 63 → 61)\n• Action: Corrective Action Plan (CAP) triggered; secondary sourcing initiated."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(12)

    # Right: High Performer Case
    add_card(s6, 6.8, 1.8, 5.7, 4.8, "Benchmark Leader: Northstar Components (V-1048)", border_color=SUCCESS_GREEN)
    tb = s6.shapes.add_textbox(Inches(7.05), Inches(2.5), Inches(5.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "TIER-1 SUPPLIER METRICS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = SUCCESS_GREEN
    p2 = tf.add_paragraph()
    p2.text = "• On-Time Delivery: 96% across 148 fulfilled purchase orders\n• Defect Ratio: Only 3 defects across 148 orders (2.0% defect rate)\n• Quality Rating: 94% defect-free compliance\n• Trailing Trend: Continuous upward expansion (84 → 86 → 88 → 90 → 91 → 92)\n• Action: Recommended for annual volume rebate discount & long-term commitment."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(12)

    # =========================================================================
    # SLIDE 7: NVIDIA NIM COPILOT ARCHITECTURE
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7)
    add_header(s7, "NVIDIA NIM Integration: Two-Stage Grounding Pipeline")

    add_card(s7, 0.8, 1.8, 5.7, 4.8, "Stage 1: Intent & Data Extraction Engine")
    tb = s7.shapes.add_textbox(Inches(1.05), Inches(2.5), Inches(5.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "100% DETERMINISTIC CALCULATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p2 = tf.add_paragraph()
    p2.text = "• Parses user intent: Top Vendor, Head-to-Head Comparison, Anomaly Discovery, Portfolio Aggregates.\n• Direct query to SQLite / PostgreSQL database for real records.\n• Pre-computes exact rankings, averages, and deltas in Python.\n• Assembles the strict Markdown Grounding Contract table."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(10)

    add_card(s7, 6.8, 1.8, 5.7, 4.8, "Stage 2: NVIDIA NIM Cognitive Synthesis")
    tb = s7.shapes.add_textbox(Inches(7.05), Inches(2.5), Inches(5.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "STRICT ZERO-HALLUCINATION PROMPT"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = SUCCESS_GREEN
    p2 = tf.add_paragraph()
    p2.text = "• Model: nvidia/nemotron-3-ultra-550b-a55b via NVIDIA NIM API.\n• Enforces Grounding Contract: LLM forbidden from inventing any metrics or suppliers outside the table.\n• Synthesizes executive briefings with actionable next steps.\n• Returns verified metadata payload for frontend inspection drawer."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(10)

    # =========================================================================
    # SLIDE 8: CHATBOT IN ACTION: SAMPLE GROUNDED RESPONSES
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8)
    add_header(s8, "Grounded Natural Language Queries in Production")

    q_cards = [
        ("Query: 'Which vendor has the highest delivery rate?'",
         "Grounded Answer: Northstar Components (V-1048) leads the portfolio with an outstanding 96% on-time delivery rate across 148 purchase orders (only 6 delays).\nVerified Delta: +7% higher than second-place Atlas Packaging (89%) and +32% above Pinnacle Industrial (64%).",
         ACCENT_CYAN),
        ("Query: 'Compare Northstar and Pinnacle head-to-head'",
         "Grounded Answer: Northstar Components outscores Pinnacle Industrial by +31 overall points (92 vs 61).\nDelivery: 96% vs 64% (+32%) | Quality: 94% vs 68% (+26%) | Reliability: 91% vs 59% (+32%).\nStrategic Action: Transition critical orders from Pinnacle to Northstar.",
         ACCENT_BLUE),
        ("Query: 'What are the largest risks in our supply chain?'",
         "Grounded Answer: Pinnacle Industrial (V-1103) represents the primary risk with 36.5% delay rate and 14 defects (Risk Score: 67%).\nSecondary Risk: BluePeak Logistics (V-1132) has 19 delayed shipments (21.6% delay rate, 44% risk index).",
         WARNING_AMBER)
    ]

    for idx, (title, content, color) in enumerate(q_cards):
        top = 1.8 + (idx * 1.65)
        add_card(s8, 0.8, top, 11.7, 1.45, title, border_color=color)
        tb = s8.shapes.add_textbox(Inches(1.05), Inches(top + 0.45), Inches(11.2), Inches(0.85))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = content
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 9: ENTERPRISE SECURITY & RESILIENCE
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9)
    add_header(s9, "Enterprise Security, Credential Safety & Fallback Modes")

    add_card(s9, 0.8, 1.8, 3.7, 4.8, "API Key Redaction")
    tb = s9.shapes.add_textbox(Inches(1.05), Inches(2.5), Inches(3.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "REGEX SANITIZATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = SUCCESS_GREEN
    p2 = tf.add_paragraph()
    p2.text = "• All outgoing logs, exceptions, and API error strings pass through _clean_error_message().\n• Patterns matching nvapi-* are instantly masked as nvapi-***REDACTED***.\n• Zero credential exposure in HTTP responses or browser consoles."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(10)

    add_card(s9, 4.8, 1.8, 3.7, 4.8, "Session Authentication")
    tb = s9.shapes.add_textbox(Inches(5.05), Inches(2.5), Inches(3.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "HTTPONLY COOKIES"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p2 = tf.add_paragraph()
    p2.text = "• Strict JWT session verification on /api/ai/chat and /api/ai/grounding.\n• Unauthenticated access immediately returns 401 Unauthorized.\n• Prevents cross-site script hijacking and protects sensitive vendor scorecards."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(10)

    add_card(s9, 8.8, 1.8, 3.7, 4.8, "Offline Fallback Engine")
    tb = s9.shapes.add_textbox(Inches(9.05), Inches(2.5), Inches(3.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "100% SERVICE AVAILABILITY"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = WARNING_AMBER
    p2 = tf.add_paragraph()
    p2.text = "• When NVIDIA NIM times out or network disruptions occur, the system seamlessly shifts to the VendorSync Offline Engine.\n• Generates mathematically identical executive answers without API dependency.\n• High-reliability SLA guarantee."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(10)

    # =========================================================================
    # SLIDE 10: AUTOMATED TEST SUITE & VERIFICATION
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_background(s10)
    add_header(s10, "Verification & Quality Assurance: 31/31 Tests Passing")

    # Big stat box
    stat_card = add_card(s10, 0.8, 1.8, 11.7, 1.4, "Automated Test Coverage: 100% Passing", border_color=SUCCESS_GREEN)
    tb = s10.shapes.add_textbox(Inches(1.05), Inches(2.35), Inches(11.2), Inches(0.7))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "16 Pytest AI & Grounding Unit/Integration Tests  +  15 Backend Regression Tests = 31 / 31 PASSED"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = SUCCESS_GREEN

    # 2 Sub-breakdowns
    add_card(s10, 0.8, 3.5, 5.7, 3.2, "AI & Grounding Suite (16 Tests)")
    tb = s10.shapes.add_textbox(Inches(1.05), Inches(4.1), Inches(5.2), Inches(2.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "✔ Mathematical KPI formula bounds (0-100)\n✔ Head-to-head comparison calculation\n✔ Statistical anomaly detection\n✔ Credential redaction in error messages\n✔ Authentication rejection (401)\n✔ Payload flood rejection (4000+ chars)\n✔ Offline fallback upon upstream timeout"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    add_card(s10, 6.8, 3.5, 5.7, 3.2, "Core Backend Suite (15 Tests)")
    tb = s10.shapes.add_textbox(Inches(7.05), Inches(4.1), Inches(5.2), Inches(2.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "✔ Cookie session authentication lifecycle\n✔ Multi-vendor dashboard data aggregation\n✔ Machine learning risk prediction endpoint\n✔ CRUD operations for qualitative vendor notes\n✔ Dynamic vendor registration & deletion\n✔ Database health & latency check (<1ms)\n✔ Deep AI vendor profile risk diagnosis"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 11: DEPLOYMENT & PRODUCTION RUNBOOK
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_background(s11)
    add_header(s11, "Deployment Runbook & Cloud Readiness")

    deploy_modes = [
        ("Local Development", "Quick 1-command startup:\npython run_server.py\nRuns on port 8000 with local SQLite database & instant reload.", ACCENT_CYAN),
        ("Docker Container", "Standardized containerization:\ndocker build -t vendorsync .\ndocker run -p 8000:8000 vendorsync\nRuns in isolated Linux environment.", ACCENT_BLUE),
        ("Cloud PaaS (Railway / Render)", "Production-ready configs:\nIncludes Procfile & railway.toml.\nAutomatic TLS certificates, health monitoring, and scaling.", SUCCESS_GREEN),
        ("Supabase Cloud Database", "Enterprise persistence:\nSet DATABASE_URL=postgresql://...\nAutomatic schema migration & multi-region database replication.", WARNING_AMBER)
    ]

    for idx, (d_title, d_desc, color) in enumerate(deploy_modes):
        left = 0.8 + (idx * 2.95)
        add_card(s11, left, 1.8, 2.85, 4.8, d_title, border_color=color)
        tb = s11.shapes.add_textbox(Inches(left + 0.15), Inches(2.5), Inches(2.55), Inches(3.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = d_desc
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 12: CONCLUSION & CONTRIBUTION CALL TO ACTION
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_background(s12)
    add_header(s12, "VendorSync AI: Smarter Decisions, Resilient Supply Chains")

    add_card(s12, 0.8, 1.8, 11.7, 3.8, "Enterprise Value Delivered", border_color=ACCENT_CYAN)
    tb = s12.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(11.1), Inches(2.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. OBJECTIVE SUPPLIER EVALUATION: Replaced gut feeling and subjective reviews with deterministic 4-pillar mathematical scoring."
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p2 = tf.add_paragraph()
    p2.text = "2. ZERO-HALLUCINATION AI: Delivered enterprise-safe AI with NVIDIA NIM Nemotron-3 Ultra, strictly anchored to factual data contracts."
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(10)
    p3 = tf.add_paragraph()
    p3.text = "3. PROACTIVE RISK MITIGATION: Early detection of supply chain bottlenecks (36.5% delay detection) prevents costly factory halts."
    p3.font.size = Pt(14)
    p3.font.bold = True
    p3.font.color.rgb = TEXT_WHITE
    p3.space_before = Pt(10)

    # Bottom links card
    add_card(s12, 0.8, 5.8, 11.7, 1.0, bg_color=RGBColor(18, 26, 48))
    tb_end = s12.shapes.add_textbox(Inches(1.0), Inches(5.95), Inches(11.3), Inches(0.7))
    tf_end = tb_end.text_frame
    p_end = tf_end.paragraphs[0]
    p_end.text = "Repository: https://github.com/chikkajyothika-max/vendor_performance  •  Pull Request #1: Live on GitHub"
    p_end.font.size = Pt(13)
    p_end.font.color.rgb = ACCENT_CYAN

    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path} ({len(prs.slides)} slides)")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "vendor_performance_presentation.pptx"
    build_presentation(out)
