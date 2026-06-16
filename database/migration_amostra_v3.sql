-- =====================================================
-- MIGRATION v3: numero_amostra INTEGER → NUMERIC
-- Permite que o usuário insira números reais positivos
-- =====================================================

ALTER TABLE amostra ALTER COLUMN numero_amostra TYPE NUMERIC;
