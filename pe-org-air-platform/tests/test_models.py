"""
Model Tests for PE Org-AI-R Platform
Test all Pydantic model validations

This test suite validates:
- Field constraints (min/max lengths, ranges)
- Custom validators (ticker uppercase, confidence intervals)
- Model relationships (required fields, optionals)
- Business logic (dimension weights, position factors)
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

# Import all models
from app.models import (
    # Assessment models
    AssessmentType,
    AssessmentStatus,
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse,
    
    # Company models
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    IndustryResponse,
    
    # Dimension models
    Dimension,
    DIMENSION_WEIGHTS,
    DimensionScoreCreate,
    DimensionScoreUpdate,
    DimensionScoreResponse,
    validate_dimension_coverage,
    calculate_weighted_score,
    
    # Common models
    PaginatedResponse,
    HealthResponse,
    ErrorResponse,
)


# =====================================================
# COMPANY MODEL TESTS
# =====================================================

class TestCompanyModels:
    """Test suite for Company models"""
    
    def test_company_create_valid(self):
        """Test creating a valid company"""
        company = CompanyCreate(
            name="TechCorp Industries",
            ticker="TECH",
            industry_id=uuid4(),
            position_factor=0.5
        )
        assert company.name == "TechCorp Industries"
        assert company.ticker == "TECH"
        assert company.position_factor == 0.5
    
    def test_company_ticker_uppercase(self):
        """Test that ticker is automatically converted to uppercase"""
        company = CompanyCreate(
            name="TechCorp",
            ticker="tech",
            industry_id=uuid4()
        )
        assert company.ticker == "TECH"
    
    def test_company_ticker_optional(self):
        """Test that ticker is optional"""
        company = CompanyCreate(
            name="Private Company",
            industry_id=uuid4()
        )
        assert company.ticker is None
    
    def test_company_position_factor_default(self):
        """Test that position_factor defaults to 0.0"""
        company = CompanyCreate(
            name="TechCorp",
            industry_id=uuid4()
        )
        assert company.position_factor == 0.0
    
    def test_company_position_factor_range(self):
        """Test that position_factor must be between -1.0 and 1.0"""
        # Valid values
        CompanyCreate(name="Test", industry_id=uuid4(), position_factor=-1.0)
        CompanyCreate(name="Test", industry_id=uuid4(), position_factor=0.0)
        CompanyCreate(name="Test", industry_id=uuid4(), position_factor=1.0)
        
        # Invalid values
        with pytest.raises(ValidationError):
            CompanyCreate(name="Test", industry_id=uuid4(), position_factor=-1.5)
        
        with pytest.raises(ValidationError):
            CompanyCreate(name="Test", industry_id=uuid4(), position_factor=1.5)
    
    def test_company_name_required(self):
        """Test that company name is required"""
        with pytest.raises(ValidationError):
            CompanyCreate(industry_id=uuid4())
    
    def test_company_name_not_empty(self):
        """Test that company name cannot be empty or whitespace"""
        with pytest.raises(ValidationError):
            CompanyCreate(name="", industry_id=uuid4())
        
        with pytest.raises(ValidationError):
            CompanyCreate(name="   ", industry_id=uuid4())
    
    def test_company_name_stripped(self):
        """Test that company name is stripped of whitespace"""
        company = CompanyCreate(
            name="  TechCorp  ",
            industry_id=uuid4()
        )
        assert company.name == "TechCorp"
    
    def test_company_name_length(self):
        """Test company name length constraints"""
        # Valid: 255 characters
        long_name = "A" * 255
        company = CompanyCreate(name=long_name, industry_id=uuid4())
        assert len(company.name) == 255
        
        # Invalid: 256 characters
        with pytest.raises(ValidationError):
            CompanyCreate(name="A" * 256, industry_id=uuid4())
    
    def test_company_update_partial(self):
        """Test that company update allows partial updates"""
        update = CompanyUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.ticker is None
        assert update.industry_id is None
        assert update.position_factor is None


# =====================================================
# ASSESSMENT MODEL TESTS
# =====================================================

class TestAssessmentModels:
    """Test suite for Assessment models"""
    
    def test_assessment_create_valid(self):
        """Test creating a valid assessment"""
        assessment = AssessmentCreate(
            company_id=uuid4(),
            assessment_type=AssessmentType.DUE_DILIGENCE,
            primary_assessor="John Smith"
        )
        assert assessment.assessment_type == AssessmentType.DUE_DILIGENCE
        assert assessment.primary_assessor == "John Smith"
    
    def test_assessment_date_default(self):
        """Test that assessment_date defaults to current time"""
        assessment = AssessmentCreate(
            company_id=uuid4(),
            assessment_type=AssessmentType.SCREENING
        )
        assert assessment.assessment_date is not None
        # Check it's recent (within last minute)
        now = datetime.now(timezone.utc)
        assert (now - assessment.assessment_date).total_seconds() < 60
    
    def test_assessment_assessors_optional(self):
        """Test that assessors are optional"""
        assessment = AssessmentCreate(
            company_id=uuid4(),
            assessment_type=AssessmentType.QUARTERLY
        )
        assert assessment.primary_assessor is None
        assert assessment.secondary_assessor is None
    
    def test_assessment_type_enum(self):
        """Test that assessment_type must be valid enum"""
        # Valid
        AssessmentCreate(
            company_id=uuid4(),
            assessment_type=AssessmentType.SCREENING
        )
        
        # Invalid
        with pytest.raises(ValidationError):
            AssessmentCreate(
                company_id=uuid4(),
                assessment_type="invalid_type"
            )
    
    def test_assessment_status_enum(self):
        """Test that status must be valid enum"""
        # Valid
        update = AssessmentUpdate(status=AssessmentStatus.IN_PROGRESS)
        assert update.status == AssessmentStatus.IN_PROGRESS
        
        # Invalid
        with pytest.raises(ValidationError):
            AssessmentUpdate(status="invalid_status")
    
    def test_assessment_confidence_interval_valid(self):
        """Test valid confidence intervals"""
        assessment = AssessmentResponse(
            id=uuid4(),
            company_id=uuid4(),
            assessment_type=AssessmentType.DUE_DILIGENCE,
            assessment_date=datetime.now(timezone.utc),
            status=AssessmentStatus.APPROVED,
            v_r_score=75.0,
            confidence_lower=70.0,
            confidence_upper=80.0,
            created_at=datetime.now(timezone.utc)
        )
        assert assessment.confidence_lower == 70.0
        assert assessment.confidence_upper == 80.0
    
    def test_assessment_confidence_interval_invalid(self):
        """Test that upper bound must be >= lower bound"""
        with pytest.raises(ValidationError) as exc_info:
            AssessmentResponse(
                id=uuid4(),
                company_id=uuid4(),
                assessment_type=AssessmentType.DUE_DILIGENCE,
                assessment_date=datetime.now(timezone.utc),
                status=AssessmentStatus.APPROVED,
                v_r_score=75.0,
                confidence_lower=80.0,  # Higher than upper!
                confidence_upper=70.0,
                created_at=datetime.now(timezone.utc)
            )
        assert "confidence_upper must be >= confidence_lower" in str(exc_info.value)
    
    def test_assessment_vr_score_range(self):
        """Test that VR score must be 0-100"""
        # Valid
        AssessmentResponse(
            id=uuid4(),
            company_id=uuid4(),
            assessment_type=AssessmentType.SCREENING,
            assessment_date=datetime.now(timezone.utc),
            status=AssessmentStatus.DRAFT,
            v_r_score=50.0,
            created_at=datetime.now(timezone.utc)
        )
        
        # Invalid: negative
        with pytest.raises(ValidationError):
            AssessmentResponse(
                id=uuid4(),
                company_id=uuid4(),
                assessment_type=AssessmentType.SCREENING,
                assessment_date=datetime.now(timezone.utc),
                status=AssessmentStatus.DRAFT,
                v_r_score=-10.0,
                created_at=datetime.now(timezone.utc)
            )
        
        # Invalid: over 100
        with pytest.raises(ValidationError):
            AssessmentResponse(
                id=uuid4(),
                company_id=uuid4(),
                assessment_type=AssessmentType.SCREENING,
                assessment_date=datetime.now(timezone.utc),
                status=AssessmentStatus.DRAFT,
                v_r_score=110.0,
                created_at=datetime.now(timezone.utc)
            )


# =====================================================
# DIMENSION SCORE MODEL TESTS
# =====================================================

class TestDimensionScoreModels:
    """Test suite for Dimension Score models"""
    
    def test_dimension_score_create_valid(self):
        """Test creating a valid dimension score"""
        score = DimensionScoreCreate(
            assessment_id=uuid4(),
            dimension=Dimension.DATA_INFRASTRUCTURE,
            score=75.0,
            confidence=0.85,
            evidence_count=10
        )
        assert score.dimension == Dimension.DATA_INFRASTRUCTURE
        assert score.score == 75.0
        assert score.confidence == 0.85
        assert score.evidence_count == 10
    
    def test_dimension_weight_auto_set(self):
        """Test that weight is automatically set based on dimension"""
        score = DimensionScoreCreate(
            assessment_id=uuid4(),
            dimension=Dimension.DATA_INFRASTRUCTURE,
            score=75.0
        )
        # DATA_INFRASTRUCTURE should get weight 0.25
        assert score.weight == 0.25
        
        score2 = DimensionScoreCreate(
            assessment_id=uuid4(),
            dimension=Dimension.CULTURE_CHANGE,
            score=60.0
        )
        # CULTURE_CHANGE should get weight 0.05
        assert score2.weight == 0.05
    
    def test_dimension_weight_manual_override(self):
        """Test that weight can be manually overridden"""
        score = DimensionScoreCreate(
            assessment_id=uuid4(),
            dimension=Dimension.DATA_INFRASTRUCTURE,
            score=75.0,
            weight=0.30  # Override default 0.25
        )
        assert score.weight == 0.30
    
    def test_dimension_score_range(self):
        """Test that score must be 0-100"""
        # Valid
        DimensionScoreCreate(
            assessment_id=uuid4(),
            dimension=Dimension.AI_GOVERNANCE,
            score=0.0
        )
        DimensionScoreCreate(
            assessment_id=uuid4(),
            dimension=Dimension.AI_GOVERNANCE,
            score=100.0
        )
        
        # Invalid
        with pytest.raises(ValidationError):
            DimensionScoreCreate(
                assessment_id=uuid4(),
                dimension=Dimension.AI_GOVERNANCE,
                score=-5.0
            )
        
        with pytest.raises(ValidationError):
            DimensionScoreCreate(
                assessment_id=uuid4(),
                dimension=Dimension.AI_GOVERNANCE,
                score=105.0
            )
    
    def test_dimension_confidence_range(self):
        """Test that confidence must be 0-1"""
        # Valid
        DimensionScoreCreate(
            assessment_id=uuid4(),
            dimension=Dimension.TALENT_SKILLS,
            score=80.0,
            confidence=0.0
        )
        DimensionScoreCreate(
            assessment_id=uuid4(),
            dimension=Dimension.TALENT_SKILLS,
            score=80.0,
            confidence=1.0
        )
        
        # Invalid
        with pytest.raises(ValidationError):
            DimensionScoreCreate(
                assessment_id=uuid4(),
                dimension=Dimension.TALENT_SKILLS,
                score=80.0,
                confidence=-0.1
            )
        
        with pytest.raises(ValidationError):
            DimensionScoreCreate(
                assessment_id=uuid4(),
                dimension=Dimension.TALENT_SKILLS,
                score=80.0,
                confidence=1.5
            )
    
    def test_dimension_confidence_default(self):
        """Test that confidence defaults to 0.8"""
        score = DimensionScoreCreate(
            assessment_id=uuid4(),
            dimension=Dimension.LEADERSHIP_VISION,
            score=70.0
        )
        assert score.confidence == 0.8
    
    def test_dimension_evidence_count_default(self):
        """Test that evidence_count defaults to 0"""
        score = DimensionScoreCreate(
            assessment_id=uuid4(),
            dimension=Dimension.USE_CASE_PORTFOLIO,
            score=65.0
        )
        assert score.evidence_count == 0
    
    def test_dimension_enum_all_values(self):
        """Test that all 7 dimensions are defined"""
        assert len(Dimension) == 7
        assert Dimension.DATA_INFRASTRUCTURE in Dimension
        assert Dimension.AI_GOVERNANCE in Dimension
        assert Dimension.TECHNOLOGY_STACK in Dimension
        assert Dimension.TALENT_SKILLS in Dimension
        assert Dimension.LEADERSHIP_VISION in Dimension
        assert Dimension.USE_CASE_PORTFOLIO in Dimension
        assert Dimension.CULTURE_CHANGE in Dimension
    
    def test_dimension_weights_sum(self):
        """Test that all dimension weights sum to 1.0"""
        total_weight = sum(DIMENSION_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.01  # Allow for floating point precision
    
    def test_validate_dimension_coverage_complete(self):
        """Test validate_dimension_coverage with all dimensions"""
        assessment_id = uuid4()
        scores = [
            DimensionScoreCreate(
                assessment_id=assessment_id,
                dimension=dim,
                score=70.0
            )
            for dim in Dimension
        ]
        assert validate_dimension_coverage(scores) is True
    
    def test_validate_dimension_coverage_incomplete(self):
        """Test validate_dimension_coverage with missing dimensions"""
        assessment_id = uuid4()
        scores = [
            DimensionScoreCreate(
                assessment_id=assessment_id,
                dimension=Dimension.DATA_INFRASTRUCTURE,
                score=75.0
            ),
            DimensionScoreCreate(
                assessment_id=assessment_id,
                dimension=Dimension.AI_GOVERNANCE,
                score=80.0
            )
        ]
        assert validate_dimension_coverage(scores) is False
    
    def test_calculate_weighted_score(self):
        """Test weighted score calculation"""
        assessment_id = uuid4()
        scores = [
            DimensionScoreResponse(
                id=uuid4(),
                assessment_id=assessment_id,
                dimension=Dimension.DATA_INFRASTRUCTURE,
                score=80.0,
                weight=0.25,
                confidence=0.8,
                evidence_count=10,
                created_at=datetime.now(timezone.utc)
            ),
            DimensionScoreResponse(
                id=uuid4(),
                assessment_id=assessment_id,
                dimension=Dimension.AI_GOVERNANCE,
                score=70.0,
                weight=0.20,
                confidence=0.8,
                evidence_count=8,
                created_at=datetime.now(timezone.utc)
            ),
        ]
        
        # Expected: (80 * 0.25 + 70 * 0.20) / (0.25 + 0.20)
        # = (20 + 14) / 0.45 = 34 / 0.45 = 75.56
        weighted_score = calculate_weighted_score(scores)
        assert abs(weighted_score - 75.56) < 0.01


# =====================================================
# COMMON MODEL TESTS
# =====================================================

class TestCommonModels:
    """Test suite for Common models"""
    
    def test_paginated_response(self):
        """Test PaginatedResponse structure"""
        response = PaginatedResponse[CompanyResponse](
            items=[],
            total=50,
            page=2,
            page_size=20,
            total_pages=3
        )
        assert response.total == 50
        assert response.page == 2
        assert response.page_size == 20
        assert response.total_pages == 3
    
    def test_paginated_response_has_next(self):
        """Test has_next property"""
        response = PaginatedResponse[CompanyResponse](
            items=[],
            total=50,
            page=2,
            page_size=20,
            total_pages=3
        )
        assert response.has_next is True
        
        last_page = PaginatedResponse[CompanyResponse](
            items=[],
            total=50,
            page=3,
            page_size=20,
            total_pages=3
        )
        assert last_page.has_next is False
    
    def test_paginated_response_has_prev(self):
        """Test has_prev property"""
        response = PaginatedResponse[CompanyResponse](
            items=[],
            total=50,
            page=2,
            page_size=20,
            total_pages=3
        )
        assert response.has_prev is True
        
        first_page = PaginatedResponse[CompanyResponse](
            items=[],
            total=50,
            page=1,
            page_size=20,
            total_pages=3
        )
        assert first_page.has_prev is False
    
    def test_health_response(self):
        """Test HealthResponse structure"""
        response = HealthResponse(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            version="1.0.0",
            dependencies={
                "snowflake": "healthy",
                "redis": "healthy",
                "s3": "healthy"
            }
        )
        assert response.status == "healthy"
        assert response.is_healthy is True
        assert len(response.failed_dependencies) == 0
    
    def test_health_response_degraded(self):
        """Test HealthResponse with failed dependency"""
        response = HealthResponse(
            status="degraded",
            timestamp=datetime.now(timezone.utc),
            version="1.0.0",
            dependencies={
                "snowflake": "healthy",
                "redis": "unhealthy",
                "s3": "healthy"
            }
        )
        assert response.is_healthy is False
        assert "redis" in response.failed_dependencies
        assert len(response.failed_dependencies) == 1
    
    def test_error_response(self):
        """Test ErrorResponse structure"""
        response = ErrorResponse(
            detail="Company not found",
            error_code="COMPANY_NOT_FOUND"
        )
        assert response.detail == "Company not found"
        assert response.error_code == "COMPANY_NOT_FOUND"
        assert response.timestamp is not None


# =====================================================
# RUN TESTS
# =====================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.models", "--cov-report=html"])