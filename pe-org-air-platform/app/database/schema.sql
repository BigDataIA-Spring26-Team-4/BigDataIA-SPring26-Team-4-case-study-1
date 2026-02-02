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
    sector VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS company (
    id VARCHAR(36) PRIMARY KEY DEFAULT UUID_STRING(),
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(10),
    industry_id VARCHAR(36) NOT NULL,
    position FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (industry_id) REFERENCES industry(id)
);

CREATE TABLE IF NOT EXISTS assessment (
    id VARCHAR(36) PRIMARY KEY DEFAULT UUID_STRING(),
    company_id VARCHAR(36) NOT NULL,
    type VARCHAR(50) NOT NULL,
    assessment_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    vr_score FLOAT,
    lower_bound FLOAT,
    upper_bound FLOAT,
    assessor_name VARCHAR(255),
    assessor_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (company_id) REFERENCES company(id)
);

CREATE TABLE IF NOT EXISTS dimension_score (
    id VARCHAR(36) PRIMARY KEY DEFAULT UUID_STRING(),
    assessment_id VARCHAR(36) NOT NULL,
    dimension VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL,
    weight FLOAT NOT NULL,
    confidence FLOAT NOT NULL,
    evidence_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    FOREIGN KEY (assessment_id) REFERENCES assessment(id)
);
