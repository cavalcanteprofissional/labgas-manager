-- =====================================================
-- MIGRATION v4: numero_amostra NUMERIC → INTEGER
-- Apenas valores inteiros positivos são permitidos
-- =====================================================

ALTER TABLE amostra ALTER COLUMN numero_amostra TYPE INTEGER USING FLOOR(numero_amostra)::INTEGER;
