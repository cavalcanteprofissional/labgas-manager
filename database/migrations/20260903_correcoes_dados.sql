-- =====================================================
-- CORREÇÕES DE DADOS - LabGas Manager (Fase 1)
-- Backup: labgas_backup_2026-08-31_20-55-22.json
-- Execute apenas após fazer um backup!
-- =====================================================

-- ==========================================
-- BUG-01: Cilindro #1 (id=33) com data_fim invertida
-- ==========================================
UPDATE public.cilindro
SET data_fim = '2025-09-16'
WHERE id = 33;

-- Validação: deve retornar 0 registros
-- SELECT * FROM public.cilindro WHERE data_fim < data_inicio_consumo;

-- ==========================================
-- BUG-02: Mercúrio (id=69) com consumo_lpm = 0
-- Ajustar conforme manual do espectrômetro
-- ==========================================
UPDATE public.elemento
SET consumo_lpm = 0.5
WHERE id = 69;

-- ==========================================
-- BUG-03: Remover 4 duplicatas exatas
-- ==========================================
DELETE FROM public.leitura WHERE id IN (112, 121, 154, 159);

-- ==========================================
-- BUG-04: Leituras fora do período do cilindro
-- ==========================================

-- Cil #5 (id=37): ajustar data_fim para incluir a leitura de 2025-12-23
UPDATE public.cilindro SET data_fim = '2025-12-23' WHERE id = 37;

-- Cil #9 (id=41): mover leitura id=194 para Cil #8 (id=40)
-- que estava ativo em 2026-02-12
UPDATE public.leitura SET cilindro_id = 40 WHERE id = 194;

-- Cil #13 (id=151): ajustar data_fim para incluir leituras de 2026-07-16
UPDATE public.cilindro SET data_fim = '2026-07-16' WHERE id = 151;

-- ==========================================
-- BUG-05: Thiago (admin) com menos permissões
-- ==========================================
UPDATE public.perfil
SET habilitar_abas = '{"amostra": true, "leitura": true, "pressao": true, "cilindro": true, "elemento": true, "historico": true}'::jsonb
WHERE id = 'a908e61d-ac27-4ba1-af2a-698836aab07b';

-- ==========================================
-- BUG-07: registros de auditoria órfãos permanecem
-- (soft-delete recomendado - sem ação necessária agora)
-- ==========================================

-- ==========================================
-- VALIDAÇÕES PÓS-CORREÇÃO
-- ==========================================

-- 1. Cilindros com data_fim < data_inicio (deve ser 0)
-- SELECT COUNT(*) FROM public.cilindro WHERE data_fim < data_inicio_consumo;

-- 2. Elementos com consumo_lpm <= 0 (deve ser 0)
-- SELECT COUNT(*) FROM public.elemento WHERE consumo_lpm <= 0;

-- 3. Leituras duplicadas (deve ser 0 pares exatos)
-- SELECT l1.id AS id_a, l2.id AS id_b, l1.data, l1.cilindro_id, l1.elemento_id
-- FROM public.leitura l1
-- JOIN public.leitura l2
--   ON l1.data = l2.data
--   AND l1.cilindro_id = l2.cilindro_id
--   AND l1.elemento_id = l2.elemento_id
--   AND l1.id < l2.id;

-- 4. Leituras fora do período do cilindro (deve ser 0)
-- SELECT l.id, l.data, l.cilindro_id, c.data_inicio_consumo, c.data_fim
-- FROM public.leitura l
-- JOIN public.cilindro c ON c.id = l.cilindro_id
-- WHERE (c.data_inicio_consumo IS NOT NULL AND l.data < c.data_inicio_consumo)
--    OR (c.data_fim IS NOT NULL AND l.data > c.data_fim);
