-- =========================================================================
-- Warehouse, database, and schema setup
-- =========================================================================

CREATE WAREHOUSE IF NOT EXISTS PE_ORG_AIR_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;

CREATE DATABASE IF NOT EXISTS PE_ORG_AIR_DB;

CREATE SCHEMA IF NOT EXISTS PE_ORG_AIR_DB.PE_ORG_AIR_SCHEMA;

USE WAREHOUSE PE_ORG_AIR_WH;
USE DATABASE PE_ORG_AIR_DB;
USE SCHEMA PE_ORG_AIR_SCHEMA;

-- =========================================================================
-- Tables
-- =========================================================================

CREATE TABLE IF NOT EXISTS industry (
    id VARCHAR(36) PRIMARY KEY DEFAULT UUID_STRING(),
    name VARCHAR(255) NOT NULL,
    h_r_base FLOAT NOT NULL,
    sector VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS company (
    id VARCHAR(36) PRIMARY KEY DEFAULT UUID_STRING(),
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(10),
    industry_id VARCHAR(36) NOT NULL,
    position_factor FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (industry_id) REFERENCES industry(id)
);

CREATE TABLE IF NOT EXISTS assessment (
    id VARCHAR(36) PRIMARY KEY DEFAULT UUID_STRING(),
    company_id VARCHAR(36) NOT NULL,
    type VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    vr_score FLOAT,
    confidence_lower FLOAT,
    confidence_upper FLOAT,
    primary_assessor VARCHAR(255),
    secondary_assessor VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (company_id) REFERENCES company(id)
);

CREATE TABLE IF NOT EXISTS dimension_score (
    id VARCHAR(36) PRIMARY KEY DEFAULT UUID_STRING(),
    assessment_id VARCHAR(36) NOT NULL,
    dimension VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL,
    weight FLOAT,
    confidence FLOAT NOT NULL DEFAULT 0.8,
    evidence_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (assessment_id) REFERENCES assessment(id)
);

-- =========================================================================
-- Indexes for performance
-- =========================================================================

CREATE INDEX IF NOT EXISTS idx_companies_industry
ON company(industry_id);

CREATE INDEX IF NOT EXISTS idx_assessments_company
ON assessment(company_id);

CREATE INDEX IF NOT EXISTS idx_dimension_scores_assessment
ON dimension_score(assessment_id);

-- =========================================================================
-- Seed Data
-- =========================================================================

-- Insert industries
INSERT INTO industry (id, name, sector, h_r_base) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'Manufacturing', 'Industrials', 72),
('550e8400-e29b-41d4-a716-446655440002', 'Healthcare Services', 'Healthcare', 78),
('550e8400-e29b-41d4-a716-446655440003', 'Business Services', 'Services', 75),
('550e8400-e29b-41d4-a716-446655440004', 'Retail', 'Consumer', 70),
('550e8400-e29b-41d4-a716-446655440005', 'Financial Services', 'Financial', 80);
