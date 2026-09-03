-- =====================================================
-- MIGRAÇÃO: Flag de dados retroativos - LabGas Manager
-- Data: 2026-09-03
-- =====================================================

-- MELHORIA-03: Adicionar coluna retroativo em leitura
ALTER TABLE public.leitura ADD COLUMN IF NOT EXISTS retroativo BOOLEAN DEFAULT false;

-- Marcar leituras retroativas (created_at - data > 7 dias)
UPDATE public.leitura
SET retroativo = true
WHERE created_at::date - data > 7;

-- Verificar quantas foram marcadas
-- SELECT retroativo, COUNT(*) FROM public.leitura GROUP BY retroativo;
