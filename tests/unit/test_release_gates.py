import pytest
from backend.app.services.release_service import ReleaseService
from backend.app.repositories.release_repository import ReleaseRepository
from backend.app.core.database import init_db

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_release_blocked_by_failed_checks_and_open_blockers():
    # REL-2026.1.0 has failed mandatory checks and open blockers
    eval_res = ReleaseService.evaluate_readiness("REL-2026.1.0")
    assert eval_res["is_ready"] is False
    assert eval_res["status"] == "BLOCKED"
    assert len(eval_res["blocking_reasons"]) > 0

def test_ready_release_passes():
    # REL-2026.0.9 has no open blockers and 100% checks
    rel = ReleaseRepository.get_by_id("REL-2026.0.9")
    assert rel is not None
    assert rel["is_ready"] is True
    assert rel["readiness_score"] == 100
