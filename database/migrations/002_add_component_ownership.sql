-- MIGRATION 002: Add Component Ownership Registry Table
-- Pre-check query: Checks if table does not exist
-- SELECT COUNT(*) FROM user_tables WHERE table_name = 'COMPONENT_REGISTRY';
-- Expected Pre-check Result: 0

-- Up Migration:
CREATE TABLE COMPONENT_REGISTRY (
    component_name   VARCHAR2(100) PRIMARY KEY,
    lead_engineer    VARCHAR2(100) NOT NULL,
    tier             VARCHAR2(20) DEFAULT 'CORE' NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_comp_tier CHECK (tier IN ('CORE', 'SUPPORTING', 'INTEGRATION', 'EXPERIMENTAL'))
);

-- Post-check query: Confirms table exists and is accessible
-- SELECT table_name FROM user_tables WHERE table_name = 'COMPONENT_REGISTRY';
-- Expected Post-check Result: 'COMPONENT_REGISTRY'

-- Rollback script:
-- DROP TABLE COMPONENT_REGISTRY;
