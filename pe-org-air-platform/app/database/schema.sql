-- =====================================================
-- PE Org-AI-R Platform - Snowflake Database Schema
- Database design and DDL
-- Case Study 1: Platform Foundation
-- =====================================================

-- Drop tables if they exist (for clean setup)
-- Order matters due to foreign key constraints
DROP TABLE IF EXISTS dimension_scores;
DROP TABLE IF EXISTS assessments;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS industries;

-- =====================================================
-- INDUSTRIES TABLE
-- Reference data for industry classifications
-- Used to categorize companies and apply industry-specific benchmarks
-- =====================================================

CREATE TABLE IF NOT EXISTS industries (
    -- Primary key
    id VARCHAR(36) PRIMARY KEY,
    
    -- Industry attributes
    name VARCHAR(255) NOT NULL UNIQUE,
    sector VARCHAR(100) NOT NULL,
    h_r_base DECIMAL(5,2) CHECK (h_r_base BETWEEN 0 AND 100),
    
    -- Metadata
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Comments for documentation
    COMMENT = 'Reference table for industry classifications and benchmarks'
);

COMMENT ON COLUMN industries.id IS 'Unique identifier (UUID)';
COMMENT ON COLUMN industries.name IS 'Industry name (e.g., Manufacturing, Healthcare Services)';
COMMENT ON COLUMN industries.sector IS 'Broader sector grouping (e.g., Industrials, Healthcare)';
COMMENT ON COLUMN industries.h_r_base IS 'Hurdle rate baseline for this industry (0-100%)';

-- =====================================================
-- COMPANIES TABLE
-- Portfolio companies and acquisition targets
-- Tracks companies being assessed for AI-readiness
-- =====================================================

CREATE TABLE IF NOT EXISTS companies (
    -- Primary key
    id VARCHAR(36) PRIMARY KEY,
    
    -- Company attributes
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(10),
    industry_id VARCHAR(36) REFERENCES industries(id),
    position_factor DECIMAL(4,3) DEFAULT 0.0 
        CHECK (position_factor BETWEEN -1.0 AND 1.0),
    
    -- Soft delete flag
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    COMMENT = 'Portfolio companies and acquisition targets'
);

COMMENT ON COLUMN companies.id IS 'Unique identifier (UUID)';
COMMENT ON COLUMN companies.name IS 'Company name';
COMMENT ON COLUMN companies.ticker IS 'Stock ticker symbol (optional, uppercase)';
COMMENT ON COLUMN companies.industry_id IS 'Foreign key to industries table';
COMMENT ON COLUMN companies.position_factor IS 'Strategic position indicator (-1=risk, 0=neutral, +1=opportunity)';
COMMENT ON COLUMN companies.is_deleted IS 'Soft delete flag (TRUE=deleted but retained for history)';

-- =====================================================
-- ASSESSMENTS TABLE
-- AI-readiness assessments of companies
-- Each assessment evaluates a company across 7 dimensions
-- =====================================================

CREATE TABLE IF NOT EXISTS assessments (
    -- Primary key
    id VARCHAR(36) PRIMARY KEY,
    
    -- Foreign key
    company_id VARCHAR(36) NOT NULL REFERENCES companies(id),
    
    -- Assessment attributes
    assessment_type VARCHAR(20) NOT NULL 
        CHECK (assessment_type IN 
            ('screening', 'due_diligence', 'quarterly', 'exit_prep')),
    assessment_date DATE NOT NULL,
    
    -- Workflow status
    status VARCHAR(20) DEFAULT 'draft'
        CHECK (status IN 
            ('draft', 'in_progress', 'submitted', 'approved', 'superseded')),
    
    -- Assessor tracking
    primary_assessor VARCHAR(255),
    secondary_assessor VARCHAR(255),
    
    -- Calculated scores (populated by scoring engine in CS3)
    v_r_score DECIMAL(5,2) CHECK (v_r_score BETWEEN 0 AND 100),
    confidence_lower DECIMAL(5,2),
    confidence_upper DECIMAL(5,2),
    
    -- Metadata
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    COMMENT = 'AI-readiness assessments of portfolio companies'
);

COMMENT ON COLUMN assessments.id IS 'Unique identifier (UUID)';
COMMENT ON COLUMN assessments.company_id IS 'Foreign key to companies table';
COMMENT ON COLUMN assessments.assessment_type IS 'Type of assessment (screening, due_diligence, quarterly, exit_prep)';
COMMENT ON COLUMN assessments.status IS 'Workflow status (draft → in_progress → submitted → approved)';
COMMENT ON COLUMN assessments.v_r_score IS 'Value-Readiness score (0-100), calculated in Case Study 3';
COMMENT ON COLUMN assessments.confidence_lower IS 'Lower bound of 95% confidence interval';
COMMENT ON COLUMN assessments.confidence_upper IS 'Upper bound of 95% confidence interval';

-- =====================================================
-- DIMENSION_SCORES TABLE
-- Individual dimension scores for each assessment
-- Each assessment should have exactly 7 dimension scores
-- =====================================================

CREATE TABLE IF NOT EXISTS dimension_scores (
    -- Primary key
    id VARCHAR(36) PRIMARY KEY,
    
    -- Foreign key
    assessment_id VARCHAR(36) NOT NULL REFERENCES assessments(id),
    
    -- Dimension being scored
    dimension VARCHAR(30) NOT NULL
        CHECK (dimension IN (
            'data_infrastructure',
            'ai_governance',
            'technology_stack',
            'talent_skills',
            'leadership_vision',
            'use_case_portfolio',
            'culture_change'
        )),
    
    -- Score attributes
    score DECIMAL(5,2) NOT NULL CHECK (score BETWEEN 0 AND 100),
    weight DECIMAL(4,3) CHECK (weight BETWEEN 0 AND 1),
    confidence DECIMAL(4,3) DEFAULT 0.8 CHECK (confidence BETWEEN 0 AND 1),
    evidence_count INT DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Business constraint: one score per dimension per assessment
    UNIQUE (assessment_id, dimension),
    
    COMMENT = 'Individual dimension scores for each assessment'
);

COMMENT ON COLUMN dimension_scores.id IS 'Unique identifier (UUID)';
COMMENT ON COLUMN dimension_scores.assessment_id IS 'Foreign key to assessments table';
COMMENT ON COLUMN dimension_scores.dimension IS 'Which dimension is being scored (one of 7 dimensions)';
COMMENT ON COLUMN dimension_scores.score IS 'Score for this dimension (0-100)';
COMMENT ON COLUMN dimension_scores.weight IS 'Weight for calculating VR score (0-1), defaults based on dimension';
COMMENT ON COLUMN dimension_scores.confidence IS 'Confidence in this score (0-1), default 0.8';
COMMENT ON COLUMN dimension_scores.evidence_count IS 'Number of evidence items supporting this score';

-- =====================================================
-- INDEXES
-- Optimize common query patterns
-- =====================================================

-- Companies indexes
CREATE INDEX IF NOT EXISTS idx_companies_industry 
    ON companies(industry_id)
    COMMENT = 'Optimize queries filtering by industry';

CREATE INDEX IF NOT EXISTS idx_companies_ticker 
    ON companies(ticker)
    COMMENT = 'Optimize ticker lookups';

CREATE INDEX IF NOT EXISTS idx_companies_deleted 
    ON companies(is_deleted)
    COMMENT = 'Optimize queries excluding deleted companies';

CREATE INDEX IF NOT EXISTS idx_companies_name
    ON companies(name)
    COMMENT = 'Optimize company name searches';

-- Assessments indexes
CREATE INDEX IF NOT EXISTS idx_assessments_company 
    ON assessments(company_id)
    COMMENT = 'Optimize queries for all assessments of a company';

CREATE INDEX IF NOT EXISTS idx_assessments_type 
    ON assessments(assessment_type)
    COMMENT = 'Optimize filtering by assessment type';

CREATE INDEX IF NOT EXISTS idx_assessments_status 
    ON assessments(status)
    COMMENT = 'Optimize filtering by workflow status';

CREATE INDEX IF NOT EXISTS idx_assessments_date
    ON assessments(assessment_date)
    COMMENT = 'Optimize date-based queries';

-- Dimension scores indexes
CREATE INDEX IF NOT EXISTS idx_dimension_scores_assessment 
    ON dimension_scores(assessment_id)
    COMMENT = 'Optimize queries for all scores of an assessment';

CREATE INDEX IF NOT EXISTS idx_dimension_scores_dimension 
    ON dimension_scores(dimension)
    COMMENT = 'Optimize filtering by specific dimension';

-- =====================================================
-- SEED DATA - Industries
-- Reference data for industry classifications
-- These are the 8 standard industries in the framework
-- =====================================================

INSERT INTO industries (id, name, sector, h_r_base) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'Manufacturing', 'Industrials', 72.00),
    ('550e8400-e29b-41d4-a716-446655440002', 'Healthcare Services', 'Healthcare', 78.00),
    ('550e8400-e29b-41d4-a716-446655440003', 'Business Services', 'Services', 75.00),
    ('550e8400-e29b-41d4-a716-446655440004', 'Retail', 'Consumer', 70.00),
    ('550e8400-e29b-41d4-a716-446655440005', 'Financial Services', 'Financial', 80.00),
    ('550e8400-e29b-41d4-a716-446655440006', 'Technology', 'Technology', 85.00),
    ('550e8400-e29b-41d4-a716-446655440007', 'Energy', 'Energy', 68.00),
    ('550e8400-e29b-41d4-a716-446655440008', 'Real Estate', 'Real Estate', 65.00);

-- =====================================================
-- VERIFICATION QUERIES
-- Run these to verify setup is correct
-- =====================================================

-- Check industries loaded
SELECT 'Industries loaded:' AS check_name, COUNT(*) AS count FROM industries;

-- Should return 8 industries
SELECT * FROM industries ORDER BY name;

-- Show all tables
SHOW TABLES;

-- Describe table structures
DESCRIBE TABLE industries;
DESCRIBE TABLE companies;
DESCRIBE TABLE assessments;
DESCRIBE TABLE dimension_scores;

-- Verify indexes were created
SHOW INDEXES IN companies;
SHOW INDEXES IN assessments;
SHOW INDEXES IN dimension_scores;

