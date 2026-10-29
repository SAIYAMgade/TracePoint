import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup():
    init_db()

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert "database" in data
    assert data["database"]["connection_status"] == "ONLINE"

def test_dashboard_metrics():
    res = client.get("/api/reports/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "open_defects_by_severity" in data
    assert "releases_blocked" in data
    assert data["total_active_defects"] >= 4

def test_list_defects_with_pagination():
    res = client.get("/api/defects?skip=0&limit=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 5

def test_create_and_transition_defect():
    # 1. Create defect
    payload = {
        "title": "API Integration Test Defect",
        "description": "Validation test created via automated API test suite",
        "severity": "MEDIUM",
        "priority": "P3",
        "affected_component": "api-gateway",
        "environment": "TEST",
        "assigned_owner": "api.tester"
    }
    create_res = client.post("/api/defects", json=payload)
    assert create_res.status_code == 201
    defect = create_res.json()
    defect_id = defect["defect_id"]
    assert defect["status"] == "OPEN"

    # 2. Transition to REPRODUCED
    trans_res = client.post(
        f"/api/defects/{defect_id}/transition",
        json={
            "target_status": "REPRODUCED",
            "actor": "api.tester",
            "reason": "Successfully confirmed failure via synthetic curl"
        }
    )
    assert trans_res.status_code == 200
    assert trans_res.json()["status"] == "REPRODUCED"

def test_test_runner_allowlist_security():
    # Non-allowlisted command must be rejected with 400
    res = client.post(
        "/api/testing/runs/execute",
        json={"command": "rm -rf /", "triggered_by": "attacker"}
    )
    assert res.status_code == 400
    assert "Security restriction" in res.json()["message"]

def test_test_runner_executes_allowlisted_suite():
    # Allowlisted test execution
    res = client.post(
        "/api/testing/runs/execute",
        json={
            "command": "pytest demo_lab/tests/test_scenario_a_date_boundary.py -v",
            "related_defect_id": "DEF-101",
            "triggered_by": "api.tester"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["outcome"] == "PASSED"
    assert data["passed_count"] == 2
    assert "PASSED" in data["output_summary"]

def test_database_change_execution():
    res = client.post("/api/database-changes/CHG-001/execute")
    assert res.status_code == 200
    data = res.json()
    assert data["change_id"] == "CHG-001"
    assert "Pre-check" in data["execution_log"]
