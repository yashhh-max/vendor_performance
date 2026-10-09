import httpx
import json

base_url = "https://specially-lane-obtaining-opt.trycloudflare.com"

def run_live_tests():
    print(f"Connecting to live public URL: {base_url}\n")
    with httpx.Client(base_url=base_url, timeout=60.0) as client:
        # 1. Health check
        print("--- 1. Testing Public Health Endpoint ---")
        r_health = client.get("/api/health")
        assert r_health.status_code == 200, f"Expected 200, got {r_health.status_code}"
        h_data = r_health.json()
        print(f"PASS: /api/health returned status: {h_data['status']} (Dialect: {h_data['dialect']}, Users: {h_data['user_count']})")

        # 2. Homepage HTML & Static Assets
        print("\n--- 2. Testing Public Single-Page Application & Assets ---")
        r_home = client.get("/")
        assert r_home.status_code == 200
        assert "VendorSync AI" in r_home.text
        print("PASS: Public root / serves index.html with VendorSync AI")

        r_css = client.get("/static/css/ai-copilot.css")
        assert r_css.status_code == 200
        print(f"PASS: /static/css/ai-copilot.css loaded successfully ({len(r_css.text)} bytes)")

        r_js = client.get("/static/js/ai-copilot.js")
        assert r_js.status_code == 200
        print(f"PASS: /static/js/ai-copilot.js loaded successfully ({len(r_js.text)} bytes)")

        # 3. Authentication
        print("\n--- 3. Testing Public Authentication Lifecycle ---")
        r_unauth = client.get("/api/auth/me")
        assert r_unauth.status_code == 401
        print("PASS: Unauthenticated access rejected with 401 Unauthorized")

        r_login = client.post("/api/auth/login", json={"email": "admin@vendorsync.ai", "password": "admin123"})
        assert r_login.status_code == 200, f"Login failed: {r_login.text}"
        user = r_login.json()
        print(f"PASS: Logged in successfully as {user['name']} ({user['email']}, Role: {user['role']})")

        r_me = client.get("/api/auth/me")
        assert r_me.status_code == 200
        assert r_me.json()["id"] == user["id"]
        print("PASS: Verified session cookie with /api/auth/me")

        # 4. Vendor Analytics Dashboard
        print("\n--- 4. Testing Public Vendor Analytics Dashboard ---")
        r_dash = client.get("/api/dashboard")
        assert r_dash.status_code == 200
        dash = r_dash.json()
        stats = dash["stats"]
        vendors = dash["vendors"]
        print(f"PASS: Dashboard returned {stats['vendors']} vendors, {stats['orders']} purchase orders")
        print(f"      Risk breakdown: Low: {stats['low']}, Medium: {stats['medium']}, High: {stats['high']}")
        for v in vendors[:4]:
            print(f"      • {v['name']} ({v['id']}): Overall {v['score']}% | Risk: {v['risk']} ({v['risk_score']}%) | Delivery: {v['delivery']}% | Quality: {v['quality']}%")

        # 5. AI Engine Status
        print("\n--- 5. Testing Public AI Engine Status ---")
        r_status = client.get("/api/ai/status")
        assert r_status.status_code == 200
        status_data = r_status.json()
        print(f"PASS: AI Status -> Provider: {status_data['provider']}, Model: {status_data['model']}, Connected: {status_data['connected']}")

        # 6. AI Grounding Audit
        print("\n--- 6. Testing Public Grounding Audit Endpoint ---")
        r_ground = client.post("/api/ai/grounding", json={"message": "Which vendor has highest delivery rate?"})
        assert r_ground.status_code == 200
        g_data = r_ground.json()
        top_v = g_data["verified_metrics"]["top_delivery"][0]
        print(f"PASS: Grounding Intent: {g_data['intent']} -> Top Delivery Vendor: {top_v['name']} ({top_v['delivery']}% delivery, {top_v['score']}% score)")

        # 7. AI Copilot Chat (Live Inference)
        print("\n--- 7. Testing Public AI Copilot Chat (End-to-End Inference) ---")
        r_chat = client.post("/api/ai/chat", json={"message": "Which vendor has the highest delivery rate and what is their risk profile?"})
        assert r_chat.status_code == 200
        chat_data = r_chat.json()
        assert len(chat_data["reply"]) > 30
        print(f"PASS: AI Chat response received via public URL!")
        print(f"      Engine Provider: {chat_data.get('provider')}")
        print(f"      Reply excerpt: {chat_data['reply'][:200]}...")

        # 8. Vendor Risk Prediction
        print("\n--- 8. Testing Public Risk Prediction Endpoint ---")
        r_pred = client.post("/api/risk/predict", json={"vendor_id": "V-1048"})
        assert r_pred.status_code == 200
        pred_data = r_pred.json()
        print(f"PASS: Risk Prediction for V-1048: {pred_data['risk']} (Risk Score: {pred_data['risk_score']}%, Performance: {pred_data['performance']}%)")
        print(f"      Recommendation: {pred_data['recommendation']}")

        print("\n=======================================================")
        print("ALL 8 PUBLIC LIVE INTEGRATION TESTS PASSED SUCCESSFULLY!")
        print(f"PUBLIC DEPLOYMENT URL IS 100% OPERATIONAL: {base_url}")
        print("=======================================================")

if __name__ == "__main__":
    run_live_tests()
