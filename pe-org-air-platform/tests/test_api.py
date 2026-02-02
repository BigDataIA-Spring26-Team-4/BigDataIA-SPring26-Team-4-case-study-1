import uuid
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.services.snowflake import get_db

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FAKE_ID = str(uuid.uuid4())
FAKE_INDUSTRY_ID = str(uuid.uuid4())
NOW = datetime(2025, 1, 1, 0, 0, 0)


def _fake_db():
    db = MagicMock()
    yield db


@pytest.fixture()
def client():
    app.dependency_overrides[get_db] = _fake_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _company_row(**overrides):
    defaults = dict(
        id=FAKE_ID,
        name="Acme Corp",
        ticker="ACME",
        industry_id=FAKE_INDUSTRY_ID,
        position=0.5,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    row = MagicMock()
    row.configure_mock(**defaults)
    return row


def _assessment_row(**overrides):
    defaults = dict(
        id=FAKE_ID,
        company_id=FAKE_INDUSTRY_ID,
        type="initial",
        assessment_date=date(2025, 6, 1),
        status="pending",
        vr_score=None,
        lower_bound=None,
        upper_bound=None,
        assessor_name=None,
        assessor_email=None,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    return MagicMock(**defaults)


def _score_row(**overrides):
    defaults = dict(
        id=FAKE_ID,
        assessment_id=FAKE_ID,
        dimension="data_infrastructure",
        score=80.0,
        weight=0.2,
        confidence=0.9,
        evidence_count=5,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    return MagicMock(**defaults)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------

COMPANIES_URL = "/api/v1/companies"


class TestCreateCompany:
    @patch("app.routers.companies.snowflake")
    @patch("app.routers.companies.invalidate")
    def test_success(self, _inv, mock_sf, client):
        mock_sf.create_company.return_value = _company_row()
        payload = {
            "name": "Acme Corp",
            "ticker": "ACME",
            "industry_id": FAKE_INDUSTRY_ID,
            "position": 0.5,
        }
        resp = client.post(COMPANIES_URL, json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Acme Corp"
        assert body["id"] == FAKE_ID
        mock_sf.create_company.assert_called_once()

    def test_invalid_ticker(self, client):
        payload = {
            "name": "Acme",
            "ticker": "bad",
            "industry_id": FAKE_INDUSTRY_ID,
            "position": 0.0,
        }
        resp = client.post(COMPANIES_URL, json=payload)
        assert resp.status_code == 422

    def test_missing_name(self, client):
        payload = {"industry_id": FAKE_INDUSTRY_ID}
        resp = client.post(COMPANIES_URL, json=payload)
        assert resp.status_code == 422

    def test_position_out_of_range(self, client):
        payload = {
            "name": "Acme",
            "industry_id": FAKE_INDUSTRY_ID,
            "position": 5.0,
        }
        resp = client.post(COMPANIES_URL, json=payload)
        assert resp.status_code == 422


class TestListCompanies:
    @patch("app.routers.companies.snowflake")
    def test_success(self, mock_sf, client):
        mock_sf.list_companies.return_value = [_company_row()]
        resp = client.get(COMPANIES_URL)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @patch("app.routers.companies.snowflake")
    def test_empty(self, mock_sf, client):
        mock_sf.list_companies.return_value = []
        resp = client.get(COMPANIES_URL)
        assert resp.status_code == 200
        assert resp.json() == []


class TestGetCompany:
    @patch("app.routers.companies.snowflake")
    def test_success(self, mock_sf, client):
        mock_sf.get_company.return_value = _company_row()
        resp = client.get(f"{COMPANIES_URL}/{FAKE_ID}")
        assert resp.status_code == 200
        assert resp.json()["id"] == FAKE_ID

    @patch("app.routers.companies.snowflake")
    def test_not_found(self, mock_sf, client):
        mock_sf.get_company.side_effect = HTTPException(status_code=404, detail="Company not found")
        resp = client.get(f"{COMPANIES_URL}/{FAKE_ID}")
        assert resp.status_code == 404


class TestUpdateCompany:
    @patch("app.routers.companies.snowflake")
    @patch("app.routers.companies.invalidate")
    def test_success(self, _inv, mock_sf, client):
        mock_sf.update_company.return_value = _company_row(name="Updated")
        resp = client.put(f"{COMPANIES_URL}/{FAKE_ID}", json={"name": "Updated"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"

    @patch("app.routers.companies.snowflake")
    @patch("app.routers.companies.invalidate")
    def test_not_found(self, _inv, mock_sf, client):
        mock_sf.update_company.side_effect = HTTPException(status_code=404, detail="Company not found")
        resp = client.put(f"{COMPANIES_URL}/{FAKE_ID}", json={"name": "X"})
        assert resp.status_code == 404


class TestDeleteCompany:
    @patch("app.routers.companies.snowflake")
    @patch("app.routers.companies.invalidate")
    def test_success(self, _inv, mock_sf, client):
        mock_sf.delete_company.return_value = None
        resp = client.delete(f"{COMPANIES_URL}/{FAKE_ID}")
        assert resp.status_code == 200
        assert resp.json() == {"detail": "deleted"}

    @patch("app.routers.companies.snowflake")
    @patch("app.routers.companies.invalidate")
    def test_not_found(self, _inv, mock_sf, client):
        mock_sf.delete_company.side_effect = HTTPException(status_code=404, detail="Company not found")
        resp = client.delete(f"{COMPANIES_URL}/{FAKE_ID}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Assessments
# ---------------------------------------------------------------------------

ASSESSMENTS_URL = "/api/v1/assessments"


class TestCreateAssessment:
    @patch("app.routers.assessments.snowflake")
    @patch("app.routers.assessments.invalidate")
    def test_success(self, _inv, mock_sf, client):
        mock_sf.create_assessment.return_value = _assessment_row()
        payload = {
            "company_id": FAKE_INDUSTRY_ID,
            "type": "initial",
            "assessment_date": "2025-06-01",
        }
        resp = client.post(ASSESSMENTS_URL, json=payload)
        assert resp.status_code == 200
        assert resp.json()["type"] == "initial"

    def test_invalid_type(self, client):
        payload = {
            "company_id": FAKE_INDUSTRY_ID,
            "type": "invalid_type",
            "assessment_date": "2025-06-01",
        }
        resp = client.post(ASSESSMENTS_URL, json=payload)
        assert resp.status_code == 422

    def test_vr_score_out_of_range(self, client):
        payload = {
            "company_id": FAKE_INDUSTRY_ID,
            "type": "initial",
            "assessment_date": "2025-06-01",
            "vr_score": 200.0,
        }
        resp = client.post(ASSESSMENTS_URL, json=payload)
        assert resp.status_code == 422


class TestListAssessments:
    @patch("app.routers.assessments.snowflake")
    def test_success(self, mock_sf, client):
        mock_sf.list_assessments.return_value = [_assessment_row()]
        resp = client.get(ASSESSMENTS_URL)
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestGetAssessment:
    @patch("app.routers.assessments.snowflake")
    def test_success(self, mock_sf, client):
        mock_sf.get_assessment.return_value = _assessment_row()
        resp = client.get(f"{ASSESSMENTS_URL}/{FAKE_ID}")
        assert resp.status_code == 200

    @patch("app.routers.assessments.snowflake")
    def test_not_found(self, mock_sf, client):
        mock_sf.get_assessment.side_effect = HTTPException(status_code=404, detail="Assessment not found")
        resp = client.get(f"{ASSESSMENTS_URL}/{FAKE_ID}")
        assert resp.status_code == 404


class TestUpdateAssessment:
    @patch("app.routers.assessments.snowflake")
    @patch("app.routers.assessments.invalidate")
    def test_success(self, _inv, mock_sf, client):
        mock_sf.update_assessment.return_value = _assessment_row(status="in_progress")
        resp = client.patch(f"{ASSESSMENTS_URL}/{FAKE_ID}", json={"status": "in_progress"})
        assert resp.status_code == 200

    @patch("app.routers.assessments.snowflake")
    @patch("app.routers.assessments.invalidate")
    def test_invalid_transition(self, _inv, mock_sf, client):
        mock_sf.update_assessment.side_effect = HTTPException(
            status_code=400,
            detail="Invalid status transition from 'completed' to 'pending'",
        )
        resp = client.patch(f"{ASSESSMENTS_URL}/{FAKE_ID}", json={"status": "pending"})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Dimension Scores
# ---------------------------------------------------------------------------


def _score_payload(assessment_id=FAKE_ID):
    return {
        "assessment_id": assessment_id,
        "dimension": "data_infrastructure",
        "score": 80.0,
        "weight": 0.2,
        "confidence": 0.9,
        "evidence_count": 5,
    }


class TestAddScores:
    @patch("app.routers.assessments.snowflake")
    @patch("app.routers.assessments.invalidate")
    def test_success(self, _inv, mock_sf, client):
        mock_sf.add_scores.return_value = [_score_row()]
        resp = client.post(f"{ASSESSMENTS_URL}/{FAKE_ID}/scores", json=[_score_payload()])
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @patch("app.routers.assessments.snowflake")
    @patch("app.routers.assessments.invalidate")
    def test_assessment_not_found(self, _inv, mock_sf, client):
        mock_sf.add_scores.side_effect = HTTPException(status_code=404, detail="Assessment not found")
        resp = client.post(f"{ASSESSMENTS_URL}/{FAKE_ID}/scores", json=[_score_payload()])
        assert resp.status_code == 404

    def test_invalid_dimension(self, client):
        payload = _score_payload()
        payload["dimension"] = "nonexistent"
        resp = client.post(f"{ASSESSMENTS_URL}/{FAKE_ID}/scores", json=[payload])
        assert resp.status_code == 422

    def test_score_out_of_range(self, client):
        payload = _score_payload()
        payload["score"] = 150.0
        resp = client.post(f"{ASSESSMENTS_URL}/{FAKE_ID}/scores", json=[payload])
        assert resp.status_code == 422


class TestGetScores:
    @patch("app.routers.assessments.snowflake")
    def test_success(self, mock_sf, client):
        mock_sf.get_scores.return_value = [_score_row()]
        resp = client.get(f"{ASSESSMENTS_URL}/{FAKE_ID}/scores")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestUpdateScores:
    @patch("app.routers.assessments.snowflake")
    @patch("app.routers.assessments.invalidate")
    def test_success(self, _inv, mock_sf, client):
        mock_sf.update_scores.return_value = [_score_row(score=90.0)]
        resp = client.put(
            f"{ASSESSMENTS_URL}/{FAKE_ID}/scores",
            json=[{"score": 90.0}],
        )
        assert resp.status_code == 200

    @patch("app.routers.assessments.snowflake")
    @patch("app.routers.assessments.invalidate")
    def test_count_mismatch(self, _inv, mock_sf, client):
        mock_sf.update_scores.side_effect = HTTPException(
            status_code=400, detail="Expected 2 scores, got 1"
        )
        resp = client.put(
            f"{ASSESSMENTS_URL}/{FAKE_ID}/scores",
            json=[{"score": 90.0}],
        )
        assert resp.status_code == 400
