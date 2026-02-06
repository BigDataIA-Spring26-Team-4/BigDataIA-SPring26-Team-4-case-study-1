import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime, timezone, date

from app.models.industry import IndustryCreate, IndustryResponse
from app.models.company import CompanyCreate, CompanyUpdate
from app.models.assessment import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentType,
    AssessmentStatus,
)
from app.models.dimension import (
    DimensionScoreCreate,
    Dimension,
    DIMENSION_WEIGHTS,
)


# =============================================================================
# Industry Model Tests
# =============================================================================


class TestIndustryModel:
    def test_valid_industry_creation(self):
        """Test creating a valid industry."""
        industry = IndustryCreate(
            name="Technology",
            sector="IT",
            h_r_base=85.0
        )
        assert industry.name == "Technology"
        assert industry.sector == "IT"
        assert industry.h_r_base == 85.0

    def test_h_r_base_range_validation(self):
        """Test h_r_base must be between 0 and 100."""
        # Valid range
        IndustryCreate(name="Test", sector="Test", h_r_base=0.0)
        IndustryCreate(name="Test", sector="Test", h_r_base=50.0)
        IndustryCreate(name="Test", sector="Test", h_r_base=100.0)

        # Invalid - below range
        with pytest.raises(ValidationError) as exc:
            IndustryCreate(name="Test", sector="Test", h_r_base=-1.0)
        assert "greater than or equal to 0" in str(exc.value).lower()

        # Invalid - above range
        with pytest.raises(ValidationError) as exc:
            IndustryCreate(name="Test", sector="Test", h_r_base=101.0)
        assert "less than or equal to 100" in str(exc.value).lower()

    def test_industry_name_required(self):
        """Test industry name is required."""
        with pytest.raises(ValidationError):
            IndustryCreate(sector="Test", h_r_base=50.0)

    def test_industry_name_length_constraints(self):
        """Test industry name length constraints."""
        # Too short
        with pytest.raises(ValidationError):
            IndustryCreate(name="", sector="Test", h_r_base=50.0)

        # Too long (>255 chars)
        with pytest.raises(ValidationError):
            IndustryCreate(name="x" * 256, sector="Test", h_r_base=50.0)


# =============================================================================
# Company Model Tests
# =============================================================================


class TestCompanyModel:
    def test_valid_company_creation(self):
        """Test creating a valid company."""
        industry_id = uuid4()
        company = CompanyCreate(
            name="Acme Corp",
            ticker="ACME",
            industry_id=industry_id,
            position_factor=0.5
        )
        assert company.name == "Acme Corp"
        assert company.ticker == "ACME"
        assert company.industry_id == industry_id
        assert company.position_factor == 0.5

    def test_ticker_uppercase_conversion(self):
        """Test field_validator converts lowercase ticker to uppercase."""
        industry_id = uuid4()

        # Lowercase input
        company = CompanyCreate(
            name="Test",
            ticker="aapl",
            industry_id=industry_id
        )
        assert company.ticker == "AAPL"

        # Mixed case
        company = CompanyCreate(
            name="Test",
            ticker="TeSt",
            industry_id=industry_id
        )
        assert company.ticker == "TEST"

        # None should remain None
        company = CompanyCreate(
            name="Test",
            industry_id=industry_id
        )
        assert company.ticker is None

    def test_position_factor_range_validation(self):
        """Test position_factor must be between -1.0 and 1.0."""
        industry_id = uuid4()

        # Valid range
        CompanyCreate(name="Test", industry_id=industry_id, position_factor=-1.0)
        CompanyCreate(name="Test", industry_id=industry_id, position_factor=0.0)
        CompanyCreate(name="Test", industry_id=industry_id, position_factor=1.0)

        # Invalid - below range
        with pytest.raises(ValidationError) as exc:
            CompanyCreate(name="Test", industry_id=industry_id, position_factor=-1.1)
        assert "greater than or equal to -1" in str(exc.value).lower()

        # Invalid - above range
        with pytest.raises(ValidationError) as exc:
            CompanyCreate(name="Test", industry_id=industry_id, position_factor=1.1)
        assert "less than or equal to 1" in str(exc.value).lower()

    def test_company_name_required(self):
        """Test company name is required."""
        industry_id = uuid4()
        with pytest.raises(ValidationError):
            CompanyCreate(industry_id=industry_id)

    def test_ticker_length_validation(self):
        """Test ticker maximum length is 10 characters."""
        industry_id = uuid4()

        # Valid
        CompanyCreate(name="Test", ticker="A", industry_id=industry_id)
        CompanyCreate(name="Test", ticker="ABCDEFGHIJ", industry_id=industry_id)

        # Invalid - too long
        with pytest.raises(ValidationError):
            CompanyCreate(name="Test", ticker="ABCDEFGHIJK", industry_id=industry_id)


# =============================================================================
# Assessment Model Tests
# =============================================================================


class TestAssessmentModel:
    def test_valid_assessment_creation(self):
        """Test creating a valid assessment."""
        company_id = uuid4()
        assessment = AssessmentCreate(
            company_id=company_id,
            type=AssessmentType.SCREENING,
            assessment_date=datetime.now(timezone.utc),
            status=AssessmentStatus.DRAFT
        )
        assert assessment.company_id == company_id
        assert assessment.type == AssessmentType.SCREENING
        assert assessment.status == AssessmentStatus.DRAFT

    def test_assessment_date_default_factory(self):
        """Test assessment_date gets default value from factory."""
        company_id = uuid4()
        before = datetime.now(timezone.utc)
        assessment = AssessmentCreate(
            company_id=company_id,
            type=AssessmentType.SCREENING
        )
        after = datetime.now(timezone.utc)

        # Check it got a timestamp
        assert before <= assessment.assessment_date <= after

    def test_confidence_interval_validation(self):
        """Test model_validator ensures confidence_upper >= confidence_lower."""
        company_id = uuid4()
        assessment_id = uuid4()

        # Valid intervals
        AssessmentResponse(
            id=assessment_id,
            company_id=company_id,
            type=AssessmentType.SCREENING,
            assessment_date=datetime.now(timezone.utc),
            status=AssessmentStatus.DRAFT,
            confidence_lower=10.0,
            confidence_upper=20.0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # Invalid - upper < lower
        with pytest.raises(ValidationError) as exc:
            AssessmentResponse(
                id=assessment_id,
                company_id=company_id,
                type=AssessmentType.SCREENING,
                assessment_date=datetime.now(timezone.utc),
                status=AssessmentStatus.DRAFT,
                confidence_lower=20.0,
                confidence_upper=10.0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        assert "confidence_upper must be >= confidence_lower" in str(exc.value)

    def test_vr_score_range_validation(self):
        """Test vr_score must be between 0 and 100."""
        company_id = uuid4()

        # Valid
        AssessmentCreate(
            company_id=company_id,
            type=AssessmentType.SCREENING,
            vr_score=0.0
        )
        AssessmentCreate(
            company_id=company_id,
            type=AssessmentType.SCREENING,
            vr_score=50.0
        )
        AssessmentCreate(
            company_id=company_id,
            type=AssessmentType.SCREENING,
            vr_score=100.0
        )

        # Invalid - below range
        with pytest.raises(ValidationError):
            AssessmentCreate(
                company_id=company_id,
                type=AssessmentType.SCREENING,
                vr_score=-1.0
            )

        # Invalid - above range
        with pytest.raises(ValidationError):
            AssessmentCreate(
                company_id=company_id,
                type=AssessmentType.SCREENING,
                vr_score=101.0
            )

    def test_assessment_type_enum(self):
        """Test AssessmentType enum values."""
        assert AssessmentType.SCREENING.value == "screening"
        assert AssessmentType.DUE_DILIGENCE.value == "due_diligence"
        assert AssessmentType.QUARTERLY.value == "quarterly"
        assert AssessmentType.EXIT_PREP.value == "exit_prep"

    def test_assessment_status_enum(self):
        """Test AssessmentStatus enum values."""
        assert AssessmentStatus.DRAFT.value == "draft"
        assert AssessmentStatus.IN_PROGRESS.value == "in_progress"
        assert AssessmentStatus.SUBMITTED.value == "submitted"
        assert AssessmentStatus.APPROVED.value == "approved"
        assert AssessmentStatus.SUPERSEDED.value == "superseded"


# =============================================================================
# Dimension Score Model Tests
# =============================================================================


class TestDimensionScoreModel:
    def test_valid_dimension_score_creation(self):
        """Test creating a valid dimension score."""
        assessment_id = uuid4()
        score = DimensionScoreCreate(
            assessment_id=assessment_id,
            dimension=Dimension.DATA_INFRASTRUCTURE,
            score=80.0
        )
        assert score.assessment_id == assessment_id
        assert score.dimension == Dimension.DATA_INFRASTRUCTURE
        assert score.score == 80.0

    def test_default_weight_assignment(self):
        """Test model_validator auto-assigns weight based on dimension."""
        assessment_id = uuid4()

        # Test each dimension gets its correct weight
        for dimension, expected_weight in DIMENSION_WEIGHTS.items():
            score = DimensionScoreCreate(
                assessment_id=assessment_id,
                dimension=dimension,
                score=50.0
            )
            assert score.weight == expected_weight

    def test_weight_can_be_manually_set(self):
        """Test weight can be manually overridden."""
        assessment_id = uuid4()
        score = DimensionScoreCreate(
            assessment_id=assessment_id,
            dimension=Dimension.DATA_INFRASTRUCTURE,
            score=50.0,
            weight=0.5  # Override default
        )
        assert score.weight == 0.5

    def test_dimension_weights_match_spec(self):
        """Verify DIMENSION_WEIGHTS values match specification."""
        assert DIMENSION_WEIGHTS[Dimension.DATA_INFRASTRUCTURE] == 0.25
        assert DIMENSION_WEIGHTS[Dimension.AI_GOVERNANCE] == 0.20
        assert DIMENSION_WEIGHTS[Dimension.TECHNOLOGY_STACK] == 0.15
        assert DIMENSION_WEIGHTS[Dimension.TALENT_SKILLS] == 0.15
        assert DIMENSION_WEIGHTS[Dimension.LEADERSHIP_VISION] == 0.10
        assert DIMENSION_WEIGHTS[Dimension.USE_CASE_PORTFOLIO] == 0.10
        assert DIMENSION_WEIGHTS[Dimension.CULTURE_CHANGE] == 0.05

    def test_score_range_validation(self):
        """Test score must be between 0 and 100."""
        assessment_id = uuid4()

        # Valid
        DimensionScoreCreate(
            assessment_id=assessment_id,
            dimension=Dimension.DATA_INFRASTRUCTURE,
            score=0.0
        )
        DimensionScoreCreate(
            assessment_id=assessment_id,
            dimension=Dimension.DATA_INFRASTRUCTURE,
            score=50.0
        )
        DimensionScoreCreate(
            assessment_id=assessment_id,
            dimension=Dimension.DATA_INFRASTRUCTURE,
            score=100.0
        )

        # Invalid - below range
        with pytest.raises(ValidationError):
            DimensionScoreCreate(
                assessment_id=assessment_id,
                dimension=Dimension.DATA_INFRASTRUCTURE,
                score=-1.0
            )

        # Invalid - above range
        with pytest.raises(ValidationError):
            DimensionScoreCreate(
                assessment_id=assessment_id,
                dimension=Dimension.DATA_INFRASTRUCTURE,
                score=101.0
            )

    def test_confidence_default_value(self):
        """Test confidence has default value of 0.8."""
        assessment_id = uuid4()
        score = DimensionScoreCreate(
            assessment_id=assessment_id,
            dimension=Dimension.DATA_INFRASTRUCTURE,
            score=50.0
        )
        assert score.confidence == 0.8

    def test_evidence_count_default_value(self):
        """Test evidence_count has default value of 0."""
        assessment_id = uuid4()
        score = DimensionScoreCreate(
            assessment_id=assessment_id,
            dimension=Dimension.DATA_INFRASTRUCTURE,
            score=50.0
        )
        assert score.evidence_count == 0

    def test_dimension_enum_values(self):
        """Test Dimension enum has all 7 dimensions."""
        assert Dimension.DATA_INFRASTRUCTURE.value == "data_infrastructure"
        assert Dimension.AI_GOVERNANCE.value == "ai_governance"
        assert Dimension.TECHNOLOGY_STACK.value == "technology_stack"
        assert Dimension.TALENT_SKILLS.value == "talent_skills"
        assert Dimension.LEADERSHIP_VISION.value == "leadership_vision"
        assert Dimension.USE_CASE_PORTFOLIO.value == "use_case_portfolio"
        assert Dimension.CULTURE_CHANGE.value == "culture_change"
