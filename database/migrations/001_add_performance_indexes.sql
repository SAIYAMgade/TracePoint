-- MIGRATION 001: Add Component Performance Index
-- Pre-check query: Checks if index already exists
-- SELECT COUNT(*) FROM user_indexes WHERE index_name = 'IDX_DEFECTS_COMP';
-- Expected Pre-check Result: 0

-- Up Migration:
CREATE INDEX idx_defects_comp ON DEFECTS (affected_component);

-- Post-check query: Confirms index creation
-- SELECT status FROM user_indexes WHERE index_name = 'IDX_DEFECTS_COMP';
-- Expected Post-check Result: 'VALID'

-- Rollback script:
-- DROP INDEX idx_defects_comp;
