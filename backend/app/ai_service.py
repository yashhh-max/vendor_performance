"""
VendorSync AI — AI Orchestration & RAG Grounding Service
Routes queries to NVIDIA NIM as primary provider, with graceful fallbacks
to Gemini, OpenAI, or the offline deterministic grounded analytics engine.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import httpx

from .nvidia_service import (
    call_nvidia_api,
    stream_nvidia_api,
    is_nvidia_available,
    get_nvidia_config
)
from .analytics_engine import (
    resolve_intent_and_facts,
    KPI_FORMULAS
)

logger = logging.getLogger("ai_service")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def get_ai_status() -> Dict[str, Any]:
    """Returns the operational status of the AI integration hierarchy."""
    nvidia_cfg = get_nvidia_config()
    has_nvidia = nvidia_cfg["configured"]
    has_gemini = bool(os.getenv("GEMINI_API_KEY", "").strip())
    has_openai = bool(os.getenv("OPENAI_API_KEY", "").strip())

    if has_nvidia:
        return {
            "provider": "nvidia",
            "model": nvidia_cfg["model"],
            "connected": True,
            "mode": f"NVIDIA NIM ({nvidia_cfg['model'].split('/')[-1]})",
            "message": f"Connected to NVIDIA NIM API at {nvidia_cfg['base_url']}",
            "features": ["Grounded RAG", "Streaming", "Reasoning Content", "Multi-Vendor Matrix"]
        }
    elif has_gemini:
        return {
            "provider": "google_gemini",
            "model": GEMINI_MODEL,
            "connected": True,
            "mode": "Live Google Gemini AI",
            "message": "Connected to Google Gemini API",
            "features": ["Grounded RAG", "Multi-Vendor Matrix"]
        }
    elif has_openai:
        return {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "connected": True,
            "mode": "Live OpenAI GPT",
            "message": "Connected to OpenAI API",
            "features": ["Grounded RAG", "Multi-Vendor Matrix"]
        }
    else:
        return {
            "provider": "grounded_analytics_engine",
            "model": "VendorSync-Deterministic-v2",
            "connected": False,
            "mode": "Smart Grounded Analytics Engine (Offline)",
            "message": "Configure NVIDIA_API_KEY in .env to activate live NVIDIA NIM reasoning.",
            "features": ["Deterministic Analytics", "Rule-Based KPI Verification", "Offline Matrix"]
        }


async def call_gemini_api(prompt: str, system_instruction: str = "") -> Optional[str]:
    """Direct HTTPS call to Google Gemini Flash API using httpx."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "topP": 0.8, "maxOutputTokens": 2048}
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
    return None


async def call_openai_api(messages: List[Dict[str, str]]) -> Optional[str]:
    """Call OpenAI compatible API if OPENAI_API_KEY is configured."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.2
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
    return None


def _local_fallback_risk_analysis(vendor: Dict[str, Any], notes: List[Any], orders: List[Any]) -> Dict[str, Any]:
    """Deterministic, explainable heuristic fallback when no external API key is active."""
    score = vendor.get("score", 75)
    delivery = vendor.get("delivery", 80)
    quality = vendor.get("quality", 80)
    cost = vendor.get("cost", 75)
    orders_cnt = vendor.get("orders", 10)
    delayed_cnt = vendor.get("delayed", 0)
    complaints_cnt = vendor.get("complaints", 0)
    defects_cnt = vendor.get("defects", 0)
    delay_ratio = delayed_cnt / max(orders_cnt, 1)

    drivers = []
    positives = []

    if delivery >= 90:
        positives.append(f"Superior on-time dispatch rate ({delivery}%)")
    elif delivery < 78:
        drivers.append(f"Sub-par fulfillment schedule ({delivery}% on-time, {delayed_cnt} delayed orders)")
    else:
        positives.append(f"Acceptable delivery cadence ({delivery}%)")

    if quality >= 90:
        positives.append(f"Industry-leading manufacturing consistency ({quality}% score)")
    elif quality < 78:
        drivers.append(f"Quality defect frequency above threshold ({defects_cnt} recorded defect batches)")
    else:
        positives.append(f"Moderate quality adherence ({quality}%)")

    if complaints_cnt > 1:
        drivers.append(f"Elevated stakeholder friction ({complaints_cnt} open escalations)")
    else:
        positives.append("Clean stakeholder resolution history with low complaint volume")

    if cost >= 85:
        positives.append(f"Competitive unit rate efficiency ({cost}% rating)")
    elif cost < 70:
        drivers.append(f"Higher contract margin variance ({cost}% rating)")

    if score >= 85 and delay_ratio <= 0.08:
        risk_level = "Low"
        risk_score = vendor.get("risk_score", 12)
        summary = (
            f"{vendor.get('name')} demonstrates exemplary operational reliability across {orders_cnt} tracked cycles. "
            f"Fulfillment consistency sits at {delivery}% with negligible warranty disputes."
        )
        recommendations = [
            "Maintain Tier-1 preferred vendor status for future high-volume procurement.",
            "Consider negotiating multi-year volume tier discounts.",
            "Schedule standard bi-annual business reviews."
        ]
        negotiation = "Leverage prompt payment terms to negotiate an additional 3-5% rebate on bulk purchase orders."
    elif score >= 70:
        risk_level = "Medium"
        risk_score = max(vendor.get("risk_score", 35), 32)
        summary = (
            f"{vendor.get('name')} maintains viable baseline throughput ({score}%), but exhibits moderate vulnerability "
            f"in delivery schedule buffers ({delayed_cnt} delayed dispatches)."
        )
        recommendations = [
            "Retain as secondary or split-award supplier rather than single-source.",
            "Institute strict milestone tracking with weekly delivery checkpoints.",
            "Establish penalty clauses for delays exceeding 48 hours."
        ]
        negotiation = "Tie progress billing to verified on-time delivery milestones rather than advance disbursements."
    else:
        risk_level = "High"
        risk_score = max(vendor.get("risk_score", 72), 65)
        summary = (
            f"{vendor.get('name')} presents acute procurement exposure. Multiple performance bottlenecks detected "
            f"including {delayed_cnt} delayed orders and {complaints_cnt} service grievances."
        )
        recommendations = [
            "Freeze new capital purchase orders pending a mandatory supplier audit.",
            "Demand a 30-day root-cause Corrective Action Plan (CAPA).",
            "Qualify pre-approved backup vendors to avoid supply-chain disruption."
        ]
        negotiation = "Withhold 15% warranty retainage on active deliveries until zero-defect verification."

    return {
        "vendor_id": vendor.get("id"),
        "vendor_name": vendor.get("name"),
        "risk_level": risk_level,
        "risk_score": risk_score,
        "confidence_score": 92,
        "executive_summary": summary,
        "key_risk_drivers": drivers if drivers else ["No adverse risk drivers detected."],
        "positive_indicators": positives,
        "strategic_recommendations": recommendations,
        "contract_negotiation_advice": negotiation,
        "engine": "VendorSync Smart Local AI Reasoning (Offline)",
        "gemini_connected": False,
        "nvidia_connected": False
    }


async def analyze_vendor_risk_ai(
    vendor: Dict[str, Any],
    notes: Optional[List[Dict[str, Any]]] = None,
    orders: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Performs AI-powered risk diagnosis using NVIDIA NIM (with Gemini, OpenAI, or local fallback).
    """
    notes = notes or []
    orders = orders or []
    notes_summary = "; ".join([f"{n.get('author')}: {n.get('note')}" for n in notes[:5]]) if notes else "No notes recorded."
    recent_orders = [
        f"Order {o.get('id')}: ${o.get('amount')} ({o.get('status')})" for o in orders[:5]
    ]

    prompt = f"""
Analyze the following supplier data and output a structured JSON procurement risk analysis.

SUPPLIER PROFILE:
- ID: {vendor.get('id')}
- Name: {vendor.get('name')}
- Category: {vendor.get('category')}
- Location: {vendor.get('location')}
- Contract Value: ${vendor.get('contract_value', 100000)}
- Overall Score: {vendor.get('score')}%
- Delivery Reliability: {vendor.get('delivery')}%
- Product Quality: {vendor.get('quality')}%
- Cost Efficiency: {vendor.get('cost')}%
- Relationship Health: {vendor.get('reliability')}%
- Total Orders: {vendor.get('orders')}
- Delayed Orders: {vendor.get('delayed')}
- Customer Complaints: {vendor.get('complaints')}
- Defective Batches: {vendor.get('defects')}
- Recent Notes: {notes_summary}
- Recent Orders: {', '.join(recent_orders) if recent_orders else 'None'}

INSTRUCTIONS:
Return strictly a valid JSON object matching this schema without any markdown formatting or code fences:
{{
  "vendor_id": "{vendor.get('id')}",
  "vendor_name": "{vendor.get('name')}",
  "risk_level": "Low" | "Medium" | "High",
  "risk_score": <integer 1 to 100>,
  "confidence_score": <integer 80 to 99>,
  "executive_summary": "<concise 2-3 sentence executive briefing>",
  "key_risk_drivers": ["<specific driver 1>", "<specific driver 2>"],
  "positive_indicators": ["<positive 1>", "<positive 2>"],
  "strategic_recommendations": ["<actionable recommendation 1>", "<actionable recommendation 2>"],
  "contract_negotiation_advice": "<specific negotiation strategy>"
}}
"""
    system_instruction = (
        "You are an enterprise procurement risk analyst and AI auditor. "
        "Provide factual, grounded, analytical risk evaluations. Return only raw JSON."
    )

    # 1. Try NVIDIA NIM first
    if is_nvidia_available():
        res = await call_nvidia_api(
            prompt,
            f"### [AUDIT DATA] {vendor.get('name')}",
            max_tokens=1024,
            temperature=0.2
        )
        if res and res.get("reply"):
            try:
                cleaned = res["reply"].strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                data = json.loads(cleaned.strip())
                data["engine"] = f"NVIDIA NIM ({res['model']})"
                data["nvidia_connected"] = True
                data["gemini_connected"] = False
                return data
            except Exception as e:
                logger.warning(f"Failed to parse NVIDIA JSON response: {e}")

    # 2. Try Gemini
    raw_response = await call_gemini_api(prompt, system_instruction)

    # 3. Try OpenAI if Gemini not set
    if not raw_response and os.getenv("OPENAI_API_KEY", "").strip():
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
        raw_response = await call_openai_api(messages)

    if raw_response:
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            data["engine"] = f"Google Gemini Flash ({GEMINI_MODEL})"
            data["gemini_connected"] = True
            data["nvidia_connected"] = False
            return data
        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON: {e}")

    # 4. Fallback to deterministic local reasoning
    return _local_fallback_risk_analysis(vendor, notes, orders)


async def chat_with_procurement_ai(
    user_message: str,
    portfolio: Dict[str, Any],
    chat_history: Optional[List[Dict[str, str]]] = None,
    scoped_vendor_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    RAG-grounded AI Copilot for procurement managers.
    Pipeline:
    1. Deterministic Intent & Fact Resolution
    2. NVIDIA NIM inference (grounded in verified facts)
    3. Fallbacks to Gemini, OpenAI, or local deterministic generator
    """
    chat_history = chat_history or []

    # 1. Deterministic Grounding
    grounding = resolve_intent_and_facts(user_message, portfolio, scoped_vendor_id)
    intent = grounding["intent"]
    verified_metrics = grounding["verified_metrics"]
    factual_table_md = grounding["factual_table_md"]

    scoped_vendor_name = None
    if scoped_vendor_id:
        v = next((x for x in portfolio.get("vendors", []) if x.get("id") == scoped_vendor_id), None)
        if v:
            scoped_vendor_name = v.get("name")

    # 2. Try NVIDIA NIM
    if is_nvidia_available():
        res = await call_nvidia_api(
            user_message=user_message,
            factual_table_md=factual_table_md,
            chat_history=chat_history,
            scoped_vendor_name=scoped_vendor_name
        )
        if res and res.get("reply"):
            return {
                "reply": res["reply"],
                "reasoning": res.get("reasoning"),
                "provider": "NVIDIA NIM",
                "model": res["model"],
                "connected": True,
                "intent": intent,
                "verified_metrics": verified_metrics,
                "supporting_data": verified_metrics
            }

    # 3. Try Gemini Fallback
    system_instruction = (
        "You are VendorSync Copilot, an expert AI procurement intelligence assistant. "
        "Ground all answers strictly on the supplied verified data. Be concise, professional, and actionable."
    )
    prompt = f"{factual_table_md}\n\nUSER QUERY:\n{user_message}"
    raw_gemini = await call_gemini_api(prompt, system_instruction)
    if raw_gemini:
        return {
            "reply": raw_gemini.strip(),
            "provider": "Google Gemini",
            "model": GEMINI_MODEL,
            "connected": True,
            "intent": intent,
            "verified_metrics": verified_metrics,
            "supporting_data": verified_metrics
        }

    # 4. Try OpenAI Fallback
    if os.getenv("OPENAI_API_KEY", "").strip():
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
        raw_openai = await call_openai_api(messages)
        if raw_openai:
            return {
                "reply": raw_openai.strip(),
                "provider": "OpenAI",
                "model": "gpt-4o-mini",
                "connected": True,
                "intent": intent,
                "verified_metrics": verified_metrics,
                "supporting_data": verified_metrics
            }

    # 5. Deterministic Grounded Engine Fallback
    vendors = portfolio.get("vendors", [])
    stats = verified_metrics.get("stats", {})

    if intent == "comparison" and "comparison" in verified_metrics:
        comp = verified_metrics["comparison"]
        reply = (
            f"### 📊 Comparative Analysis: {comp['vendor_1']} vs {comp['vendor_2']}\n\n"
            f"{factual_table_md}\n\n"
            f"**Strategic Assessment:**\n"
            f"- **Leader**: **{comp['overall_winner']}** demonstrates superior operational stability across {max(comp['vendor_1_wins'], comp['vendor_2_wins'])} evaluated dimensions.\n"
            f"- **Procurement Recommendation**: For high-volume contracts, prioritize {comp['overall_winner']} to reduce operational delay exposure."
        )
    elif intent == "revenue_spend" and "top_financial_vendors" in verified_metrics:
        top_v = verified_metrics["top_financial_vendors"][0]
        reply = (
            f"### 💰 Financial Commitment & Spend Analysis\n\n"
            f"{factual_table_md}\n\n"
            f"**Key Financial Takeaways:**\n"
            f"- The largest active supplier by contract allocation is **{top_v['name']}** at **${top_v['contract_value']:,.2f}**.\n"
            f"- Total capital committed across all {stats.get('total_vendors', len(vendors))} suppliers is **${stats.get('total_contract_value', 0):,.2f}**.\n"
            f"- Recommendation: Conduct quarterly margin audits on top 3 suppliers to negotiate bulk purchase rebates."
        )
    elif intent == "risk_and_defects":
        reply = (
            f"### 🚨 Risk & Quality Bottleneck Analysis\n\n"
            f"{factual_table_md}\n\n"
            f"**Actionable Risk Mitigation Plan:**\n"
            f"1. **Contract Hold**: Pause expansion on High-Risk suppliers with delay rates exceeding 15%.\n"
            f"2. **Corrective Action**: Issue 30-day remediation plans for suppliers with more than 3 customer complaints.\n"
            f"3. **Dual-Sourcing**: Qualify secondary backup vendors for single-source suppliers."
        )
    elif intent == "kpi_explanation":
        reply = (
            f"### 📐 Procurement KPI Methodology & Formula Guide\n\n"
            f"{factual_table_md}\n\n"
            f"**Weighting Rationale:**\n"
            f"- **Delivery (35%) & Quality (35%)**: Form 70% of the core score because on-time defect-free supply directly impacts end-customer fulfillment.\n"
            f"- **Cost (15%) & Reliability (15%)**: Balance competitive unit economics with relationship responsiveness."
        )
    elif intent == "trends" and "trends" in verified_metrics:
        reply = (
            f"### 📈 6-Month Vendor Trajectory Analysis\n\n"
            f"{factual_table_md}\n\n"
            f"**Trend Interpretation:**\n"
            f"- Suppliers showing positive trajectory (↗) are expanding manufacturing consistency.\n"
            f"- Suppliers with negative trajectory (↘) warrant an operational check-in before contract renewal."
        )
    else:
        top_supplier = sorted(vendors, key=lambda x: x.get("score", 0), reverse=True)[0] if vendors else None
        reply = (
            f"### 🏢 Vendor Portfolio Overview\n\n"
            f"{factual_table_md}\n\n"
            f"**Portfolio Health:**\n"
            f"- Network average performance score is **{stats.get('avg_score', 84)}%**.\n"
            f"- Top performing supplier: **{top_supplier['name'] if top_supplier else 'N/A'}** (`{top_supplier['score'] if top_supplier else 0}%` score).\n"
            f"- Active Risk Distribution: {stats.get('risk_distribution', {}).get('Low', 0)} Low, {stats.get('risk_distribution', {}).get('Medium', 0)} Medium, {stats.get('risk_distribution', {}).get('High', 0)} High."
        )

    return {
        "reply": reply,
        "provider": "VendorSync Grounded Analytics Engine (Offline)",
        "model": "VendorSync-Deterministic-v2",
        "connected": False,
        "intent": intent,
        "verified_metrics": verified_metrics,
        "supporting_data": verified_metrics
    }
