-- =====================================================
-- MIGRATION: cilindro.codigo (VARCHAR 'CIL-XXX') → cilindro.numero (INTEGER)
-- Data: 2026-08-06
-- Motivo (Fase 80): o identificador de cilindro passa a ser um número
-- inteiro (1, 2, 3...) em vez do código textual 'CIL-001'. A UI passa a
-- exibir somente números em tudo (tabela, exports CSV/Markdown/Excel,
-- labels do histórico). Em paralelo, esta migration fecha lacunas de
-- integridade/segurança do schema:
--   * UNIQUE(numero, user_id) no cilindro (replica idx_cilindro_codigo_user
--     que era criado só via aplicação)
--   * UNIQUE(nome, user_id) no elemento (idem, hoje só via app)
--   * CHECK tipo em historico_auditoria (alinhado ao app)
--   * RLS: policies SELECT passam de USING(true) (qualquer um lê tudo)
--     para auth.uid() = user_id OR public.is_dev()
--
-- FLUXO (transação única):
--   1) Função SECURITY DEFINER public.is_dev() para uso em políticas RLS
--   2) ADD COLUMN numero → backfill a partir do sufixo numérico do codigo
--   3) Verificar 0 NULLs → SET NOT NULL → UNIQUE(numero, user_id)
--   4) DROP COLUMN codigo (arrasta idx_cilindro_codigo_user junto)
--   5) UNIQUE(nome, user_id) em elemento; CHECK tipo em historico_auditoria
--   6) Substituir policies SELECT de leitura por políticas dev-aware
-- =====================================================

BEGIN;

-- -----------------------------------------------------
-- 1) Função is_dev() — SECURITY DEFINER para evitar recursão RLS
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION public.is_dev()
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.perfil p
        WHERE p.id = auth.uid() AND p.role = 'dev'
    );
$$;

-- -----------------------------------------------------
-- 2) Nova coluna numero + backfill
-- -----------------------------------------------------
ALTER TABLE cilindro ADD COLUMN IF NOT EXISTS numero INTEGER;

UPDATE cilindro
SET numero = (regexp_match(codigo, '(\d+)\s*$'))[1]::integer
WHERE numero IS NULL;

-- -----------------------------------------------------
-- 3) Garantir backfill completo antes de SET NOT NULL
-- -----------------------------------------------------
DO $$
DECLARE v_sem_numero INTEGER;
BEGIN
    SELECT count(*) INTO v_sem_numero FROM cilindro WHERE numero IS NULL;
    IF v_sem_numero > 0 THEN
        RAISE EXCEPTION 'Backfill incompleto: % cilindro(s) sem numero', v_sem_numero;
    END IF;
END $$;

ALTER TABLE cilindro ALTER COLUMN numero SET NOT NULL;

-- Substitui o único (user_id, codigo) que existia via aplicação
ALTER TABLE cilindro ADD CONSTRAINT uq_cilindro_numero_user UNIQUE (numero, user_id);

CREATE INDEX IF NOT EXISTS idx_cilindro_numero ON cilindro(numero);

-- -----------------------------------------------------
-- 4) Remove a coluna legada (o índice idx_cilindro_codigo_user
--    é derrubado automaticamente junto com a coluna)
-- -----------------------------------------------------
ALTER TABLE cilindro DROP COLUMN codigo;

-- -----------------------------------------------------
-- 5) Integridade: elemento UNIQUE + CHECK tipo do histórico
-- -----------------------------------------------------
ALTER TABLE elemento ADD CONSTRAINT uq_elemento_nome_user UNIQUE (nome, user_id);

ALTER TABLE historico_auditoria ADD CONSTRAINT chk_historico_tipo
    CHECK (tipo IN ('cilindro', 'pressao', 'elemento', 'leitura', 'amostra', 'perfil'));

-- -----------------------------------------------------
-- 6) RLS — políticas SELECT dev-aware (fim do USING(true))
-- -----------------------------------------------------

-- cilindro
DROP POLICY IF EXISTS "Anyone can view cilindro" ON cilindro;
CREATE POLICY "Users can view own cilindro" ON cilindro
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- elemento
DROP POLICY IF EXISTS "Anyone can view elemento" ON elemento;
CREATE POLICY "Users can view own elemento" ON elemento
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- leitura
DROP POLICY IF EXISTS "Anyone can view leitura" ON leitura;
CREATE POLICY "Users can view own leitura" ON leitura
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- pressao
DROP POLICY IF EXISTS "Anyone can view pressao" ON pressao;
CREATE POLICY "Users can view own pressao" ON pressao
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- amostra
DROP POLICY IF EXISTS "Anyone can view amostra" ON amostra;
CREATE POLICY "Users can view own amostra" ON amostra
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- historico_auditoria
DROP POLICY IF EXISTS "Anyone can view historico_auditoria" ON historico_auditoria;
CREATE POLICY "Users can view own historico_auditoria" ON historico_auditoria
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- amostra_elemento (sem user_id: herda do dono da amostra)
DROP POLICY IF EXISTS "Anyone can view amostra_elemento" ON amostra_elemento;
CREATE POLICY "Users can view own amostra_elemento" ON amostra_elemento
    FOR SELECT USING (
        auth.uid() IN (SELECT user_id FROM amostra WHERE id = amostra_elemento.amostra_id)
        OR public.is_dev()
    );

-- perfil
DROP POLICY IF EXISTS "Users can view own perfil" ON perfil;
CREATE POLICY "Users can view own perfil" ON perfil
    FOR SELECT USING (auth.uid() = id OR public.is_dev());

COMMIT;

-- -----------------------------------------------------
-- Verificação pós-migração (executar manualmente)
-- -----------------------------------------------------
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'cilindro';
-- SELECT count(*) FROM cilindro WHERE numero IS NULL;
-- SELECT numero, status, user_id FROM cilindro ORDER BY numero;
-- SELECT relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname IN ('cilindro','elemento','leitura','pressao','amostra','perfil','historico_auditoria','amostra_elemento');
-- SELECT polname, pg_get_expr(polqual, polrelid) FROM pg_policy WHERE polrelid IN ('cilindro'::regclass, 'elemento'::regclass);
