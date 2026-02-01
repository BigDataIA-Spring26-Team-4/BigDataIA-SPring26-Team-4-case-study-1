CREATE TABLE industry (
    id VARCHAR(36) PRIMARY KEY DEFAULT UUID_STRING(),
    name VARCHAR(255) NOT NULL,
    h_r_base FLOAT NOT NULL,
    sector: VARCHAR(255) NOT NULL
);

CREATE TABLE company (
    id VARCHAR(36) PRIMARY KEY DEFAULT UUID_STRING(),
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    industry_id VARCHAR(36) NOT NULL,
    position FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (industry_id) REFERENCES industry(id)
);

CREATE TABLE IF NOT EXISTS assessment (
    id VARCHAR(36) PRIMARY KEY DEFAULT UUID_STRING(),
    company_id VARCHAR(36) NOT NULL,
    type VARCHAR(50) NOT NULL,
    assessment_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    vr_score float,
    lower_bound float,
    upper_bound float,

    FOREIGN KEY (company_id) REFERENCES company(id)
);