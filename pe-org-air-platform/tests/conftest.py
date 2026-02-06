import pytest
import uuid
from datetime import datetime
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.snowflake import get_db


# =============================================================================
# Constants
# =============================================================================

FAKE_ID = str(uuid.uuid4())
FAKE_INDUSTRY_ID = str(uuid.uuid4())
NOW = datetime(2025, 1, 1, 0, 0, 0)


# =============================================================================
# Database Fixtures
# =============================================================================

def _fake_db():
    """Yield a mocked database session."""
    db = MagicMock()
    yield db


@pytest.fixture()
def client():
    """Provide a TestClient with mocked database dependency."""
    app.dependency_overrides[get_db] = _fake_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# =============================================================================
# Mock Data Generators
# =============================================================================

def _industry_row(**overrides):
    """Create a mock industry row."""
    defaults = dict(
        id=FAKE_ID,
        name="Technology",
        sector="IT",
        h_r_base=85.0,
        created_at=NOW,
    )
    defaults.update(overrides)
    row = MagicMock()
    row.configure_mock(**defaults)
    return row


def _company_row(**overrides):
    """Create a mock company row."""
    defaults = dict(
        id=FAKE_ID,
        name="Acme Corp",
        ticker="ACME",
        industry_id=FAKE_INDUSTRY_ID,
        position_factor=0.5,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    row = MagicMock()
    row.configure_mock(**defaults)
    return row


def _assessment_row(**overrides):
    """Create a mock assessment row."""
    defaults = dict(
        id=FAKE_ID,
        company_id=FAKE_INDUSTRY_ID,
        type="screening",
        assessment_date=datetime(2025, 6, 1),
        status="draft",
        vr_score=None,
        confidence_lower=None,
        confidence_upper=None,
        primary_assessor=None,
        secondary_assessor=None,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    return MagicMock(**defaults)


def _score_row(**overrides):
    """Create a mock dimension score row."""
    defaults = dict(
        id=FAKE_ID,
        assessment_id=FAKE_ID,
        dimension="data_infrastructure",
        score=80.0,
        weight=0.25,
        confidence=0.9,
        evidence_count=5,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    return MagicMock(**defaults)


# =============================================================================
# Pytest Fixtures for Mock Data
# =============================================================================

@pytest.fixture
def industry_row():
    """Return a mock industry row."""
    return _industry_row()


@pytest.fixture
def company_row():
    """Return a mock company row."""
    return _company_row()


@pytest.fixture
def assessment_row():
    """Return a mock assessment row."""
    return _assessment_row()


@pytest.fixture
def score_row():
    """Return a mock dimension score row."""
    return _score_row()
