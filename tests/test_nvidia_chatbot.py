"""
Comprehensive Test Suite for NVIDIA-Powered Vendor Performance Chatbot & Grounded Analytics
Covers:
1. Deterministic Analytics Engine & KPI Calculations
2. Intent Resolution & Metric Grounding
3. NVIDIA NIM Client Construction & Error Handling
4. Mocked Inference & Fallback Handling
5. FastApi Endpoints Validation & Auth Protection
6. Live Inference Verification (when NVIDIA_API_KEY is configured)
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ensure backend directory is in path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.analytics_engine import (
    calculate_order_spend_by_vendor,
    get_top_vendors,
    get_vendors_by_spend,
    compare_vendors_head_to_head,
    find_anomalies_and_risks,
    compute_portfolio_statistics,
    resolve_intent_and_facts,
    KPI_FORMULAS
)
from app.nvidia_service import (
    get_nvidia_config,
    is_nvidia_available,
    build_nvidia_messages,
    _clean_error_message
)

# Initialize database
init_db()
client = TestClient(app)

# Helper for authentication
def get_auth_client():
    c = TestClient(app)
    res = c.post("/api/auth/login", json={"email": "admin@vendorsync.ai", "password": "admin123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return c


# ==============================================================================
# 1. Deterministic Analytics Engine Tests
# ==============================================================================

def test_kpi_formulas_integrity():
    """Verify official KPI formula definitions are present and mathematically sound."""
    assert "score" in KPI_FORMULAS
    assert "risk_score" in KPI_FORMULAS
    weights = KPI_FORMULAS["score"]["weights"]
    assert weights["delivery"] == 0.35
    assert weights["quality"] == 0.35
    assert weights["cost"] == 0.15
    assert weights["reliability"] == 0.15
    assert sum(weights.values()) == 1.0


def test_compare_vendors_head_to_head():
    """Test deterministic comparative matrix between two suppliers."""
    v1 = {
        "id": "V-1", "name": "Vendor Alpha", "score": 92, "delivery": 95,
        "quality": 94, "cost": 85, "reliability": 90, "risk_score": 12, "contract_value": 150000.0
    }
    v2 = {
        "id": "V-2", "name": "Vendor Beta", "score": 75, "delivery": 80,
        "quality": 78, "cost": 88, "reliability": 72, "risk_score": 42, "contract_value": 80000.0
    }
    comp = compare_vendors_head_to_head(v1, v2)
    assert comp["vendor_1"] == "Vendor Alpha"
    assert comp["vendor_2"] == "Vendor Beta"
    assert comp["overall_winner"] == "Vendor Alpha"
    assert comp["vendor_1_wins"] > comp["vendor_2_wins"]


def test_find_anomalies_and_risks():
    """Test anomaly detection flags high delays and excessive defects."""
    vendors = [
        {
            "id": "V-HEALTHY", "name": "Healthy Co", "score": 90, "orders": 100,
            "delayed": 2, "complaints": 0, "defects": 1, "risk": "Low", "risk_score": 10,
            "trend": [88, 89, 90]
        },
        {
            "id": "V-RISKY", "name": "Bottleneck Inc", "score": 62, "orders": 50,
            "delayed": 15, "complaints": 5, "defects": 6, "risk": "High", "risk_score": 65,
            "trend": [72, 68, 62]
        }
    ]
    anomalies = find_anomalies_and_risks(vendors)
    assert len(anomalies) == 1
    assert anomalies[0]["vendor_id"] == "V-RISKY"
    assert any("delay rate" in r.lower() for r in anomalies[0]["reasons"])
    assert any("complaint" in r.lower() for r in anomalies[0]["reasons"])


def test_portfolio_statistics_calculation():
    """Test aggregated summary metrics computation."""
    vendors = [
        {"id": "V-1", "name": "V1", "category": "Electronics", "score": 90, "delivery": 90, "quality": 90, "cost": 90, "reliability": 90, "orders": 50, "delayed": 5, "complaints": 1, "defects": 1, "contract_value": 100000.0, "risk": "Low"},
        {"id": "V-2", "name": "V2", "category": "Packaging", "score": 80, "delivery": 80, "quality": 80, "cost": 80, "reliability": 80, "orders": 30, "delayed": 3, "complaints": 2, "defects": 2, "contract_value": 50000.0, "risk": "Medium"}
    ]
    orders = [{"vendor": "V1", "amount": 25000.0}]
    stats = compute_portfolio_statistics(vendors, orders)
    assert stats["total_vendors"] == 2
    assert stats["total_orders_count"] == 80
    assert stats["total_contract_value"] == 150000.0
    assert stats["total_recorded_order_spend"] == 25000.0
    assert stats["avg_score"] == 85.0


def test_intent_resolution_and_grounding():
    """Verify query intent classification properly routes queries and computes facts."""
    portfolio = {
        "vendors": [
            {"id": "V-1048", "name": "Northstar Components", "category": "Electronics", "score": 92, "delivery": 96, "quality": 94, "cost": 87, "reliability": 91, "orders": 100, "delayed": 4, "complaints": 1, "defects": 2, "contract_value": 200000.0, "risk": "Low", "risk_score": 12, "trend": [88, 90, 92]},
            {"id": "V-1021", "name": "Meridian Office", "category": "Stationery", "score": 75, "delivery": 78, "quality": 80, "cost": 85, "reliability": 70, "orders": 50, "delayed": 12, "complaints": 6, "defects": 5, "contract_value": 75000.0, "risk": "High", "risk_score": 58, "trend": [80, 78, 75]}
        ],
        "orders": [
            {"id": "O-1", "vendor": "Northstar Components", "amount": 50000.0}
        ]
    }

    # Comparison intent
    res_comp = resolve_intent_and_facts("Compare Northstar vs Meridian", portfolio)
    assert res_comp["intent"] == "comparison"
    assert "Northstar Components" in res_comp["factual_table_md"]

    # Revenue intent
    res_rev = resolve_intent_and_facts("Who has the highest contract spend?", portfolio)
    assert res_rev["intent"] == "revenue_spend"
    assert "$200,000.00" in res_rev["factual_table_md"]

    # Risk intent
    res_risk = resolve_intent_and_facts("Which suppliers have high delay bottlenecks?", portfolio)
    assert res_risk["intent"] == "risk_and_defects"

    # KPI formula intent
    res_kpi = resolve_intent_and_facts("How is the vendor score calculated?", portfolio)
    assert res_kpi["intent"] == "kpi_explanation"


# ==============================================================================
# 2. NVIDIA Service & Security Tests
# ==============================================================================

def test_nvidia_security_key_redaction():
    """Ensure error messages redact raw API credentials."""
    dummy_key = "nvapi-TESTSECRET1234567890"
    with patch.dict(os.environ, {"NVIDIA_API_KEY": dummy_key}):
        raw_error = f"Connection refused at https://integrate.api.nvidia.com with token {dummy_key}"
        clean_error = _clean_error_message(raw_error)
        assert dummy_key not in clean_error
        assert "nvapi-***REDACTED***" in clean_error


def test_build_nvidia_messages_grounding():
    """Ensure system prompt enforces strict factual adherence and injects verified data."""
    factual_table = "### [VERIFIED DATA]\n- Northstar: 96% delivery"
    messages = build_nvidia_messages("Tell me Northstar delivery", factual_table)
    assert len(messages) == 2
    assert "STRICT GROUNDING & ACCURACY CONTRACT" in messages[0]["content"]
    assert "[VERIFIED DATA]" in messages[1]["content"]
    assert "Northstar: 96% delivery" in messages[1]["content"]


# ==============================================================================
# 3. API Endpoints Security & Validation Tests
# ==============================================================================

def test_unauthenticated_chat_rejected():
    """Unauthenticated requests must be rejected with 401."""
    unauth_client = TestClient(app)
    res = unauth_client.post("/api/ai/chat", json={"message": "Hello"})
    assert res.status_code == 401


def test_empty_message_validation():
    """Empty or whitespace-only messages must be rejected with 400."""
    auth_client = get_auth_client()
    res1 = auth_client.post("/api/ai/chat", json={"message": ""})
    assert res1.status_code == 400
    res2 = auth_client.post("/api/ai/chat", json={"message": "   "})
    assert res2.status_code == 400


def test_excessive_message_length_validation():
    """Messages exceeding 4000 characters must be rejected with 400."""
    auth_client = get_auth_client()
    huge_message = "A" * 4500
    res = auth_client.post("/api/ai/chat", json={"message": huge_message})
    assert res.status_code == 400
    assert "exceeds maximum allowed length" in res.json()["detail"]


def test_grounding_audit_endpoint():
    """The /api/ai/grounding endpoint returns deterministic calculated facts."""
    auth_client = get_auth_client()
    res = auth_client.post("/api/ai/grounding", json={"message": "Compare top vendors"})
    assert res.status_code == 200
    data = res.json()
    assert "intent" in data
    assert "verified_metrics" in data
    assert "factual_table_md" in data


def test_ai_status_endpoint():
    """Verify /api/ai/status reports configured features and engine mode."""
    auth_client = get_auth_client()
    res = auth_client.get("/api/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert "provider" in data
    assert "model" in data
    assert "connected" in data
    assert "mode" in data


def test_ai_chat_end_to_end():
    """Verify /api/ai/chat returns a structured, grounded response."""
    auth_client = get_auth_client()
    res = auth_client.post("/api/ai/chat", json={
        "message": "Which vendor has the highest overall performance score?"
    })
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 20
    assert "provider" in data
    assert "verified_metrics" in data
    assert "intent" in data


def test_vendor_scoping_in_chat():
    """Verify specifying vendor_id scopes the grounding context to that supplier."""
    auth_client = get_auth_client()
    dash = auth_client.get("/api/dashboard").json()
    first_vendor = dash["vendors"][0]
    first_id = first_vendor["id"]

    res = auth_client.post("/api/ai/chat", json={
        "message": "Assess this vendor's on-time delivery",
        "vendor_id": first_id
    })
    assert res.status_code == 200
    data = res.json()
    assert data["verified_metrics"] is not None
    assert "scoped_vendor" in data["verified_metrics"]
    assert data["verified_metrics"]["scoped_vendor"]["id"] == first_id


def test_ai_deep_analysis_endpoint():
    """Verify /api/ai/analyze/{vendor_id} produces multi-factor risk diagnosis."""
    auth_client = get_auth_client()
    dash = auth_client.get("/api/dashboard").json()
    first_id = dash["vendors"][0]["id"]

    res = auth_client.post(f"/api/ai/analyze/{first_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["vendor_id"] == first_id
    assert "risk_level" in data
    assert "risk_score" in data
    assert "executive_summary" in data
    assert len(data["key_risk_drivers"]) > 0
    assert len(data["positive_indicators"]) > 0
    assert len(data["strategic_recommendations"]) > 0
    assert "contract_negotiation_advice" in data


# ==============================================================================
# 4. Mocked NVIDIA Inference & Failure Resilience Tests
# ==============================================================================

def test_mocked_nvidia_timeout_fallback():
    """Verify when NVIDIA API times out, the system gracefully falls back to deterministic engine."""
    with patch("app.ai_service.call_nvidia_api", return_value=None):
        auth_client = get_auth_client()
        res = auth_client.post("/api/ai/chat", json={
            "message": "Which vendor is best for high-value orders?"
        })
        assert res.status_code == 200
        data = res.json()
        assert len(data["reply"]) > 30
        assert "verified_metrics" in data
