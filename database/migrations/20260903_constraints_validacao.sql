-- =====================================================
-- MIGRAÇÃO: Constraints de Validação - LabGas Manager
-- Data: 2026-09-03
-- Descrição: Adiciona constraints para validar integridade dos dados
-- =====================================================

-- VAL-01: data_fim >= data_inicio_consumo (cilindro)
-- Impede que data_fim seja anterior à data de início do consumo
ALTER TABLE public.cilindro
ADD CONSTRAINT chk_cilindro_datas
CHECK (data_fim IS NULL OR data_fim >= data_inicio_consumo);

-- VAL-02: consumo_lpm > 0 (elemento)
-- Impede que elementos tenham consumo zero ou negativo
-- NOTA: Corrigir elemento Mercúrio (id=69) ANTES de aplicar esta constraint
-- UPDATE public.elemento SET consumo_lpm = 0.5 WHERE id = 69;
ALTER TABLE public.elemento
ADD CONSTRAINT chk_elemento_consumo
CHECK (consumo_lpm > 0);

-- VAL-03: UNIQUE em leitura (data + cilindro + elemento)
-- Impede duplicatas de leitura no mesmo dia para o mesmo cilindro e elemento
-- NOTA: Remover duplicatas existentes ANTES de criar o índice
-- DELETE FROM public.leitura WHERE id IN (112, 121, 154, 159);
CREATE UNIQUE INDEX IF NOT EXISTS idx_leitura_unique
ON public.leitura (data, cilindro_id, elemento_id);

-- =====================================================
-- CONSTRAINTS ADICIONAIS (Melhorias)
-- =====================================================

-- Pressão positiva
ALTER TABLE public.pressao
ADD CONSTRAINT chk_pressao_positiva
CHECK (pressao > 0);

-- Temperatura em range razoável (-20 a 100°C)
ALTER TABLE public.pressao
ADD CONSTRAINT chk_pressao_temperatura
CHECK (temperatura IS NULL OR (temperatura >= -20 AND temperatura <= 100));

-- Quantidade de leitura positiva
ALTER TABLE public.leitura
ADD CONSTRAINT chk_leitura_quantidade
CHECK (quantidade > 0);
