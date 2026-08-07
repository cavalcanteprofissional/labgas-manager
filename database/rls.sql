-- =====================================================
-- POLÍTICAS RLS (Row Level Security) - LabGas Manager
-- =====================================================
-- Fonte única e executável: habilita RLS em todas as tabelas,
-- define a função is_dev() e recria todas as policies de forma
-- idempotente (DROP POLICY IF EXISTS + CREATE POLICY).
--
-- As policies SELECT restringem leitura ao dono do registro
-- (auth.uid() = user_id); usuários com role 'dev' enxergam tudo
-- via public.is_dev() (SECURITY DEFINER).

-- =====================================================
-- Função is_dev() — SECURITY DEFINER para evitar recursão RLS
-- (migration 20260806_cilindro_numero.sql)
-- =====================================================
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

-- =====================================================
-- Tabela: perfil
-- =====================================================
ALTER TABLE perfil ENABLE ROW LEVEL SECURITY;

-- SELECT: Apenas próprio usuário ou dev
DROP POLICY IF EXISTS "Users can view own perfil" ON perfil;
CREATE POLICY "Users can view own perfil" ON perfil
    FOR SELECT USING (auth.uid() = id OR public.is_dev());

-- INSERT: Apenas próprio usuário pode inserir (seu próprio perfil)
DROP POLICY IF EXISTS "Users can insert own perfil" ON perfil;
CREATE POLICY "Users can insert own perfil" ON perfil
    FOR INSERT WITH CHECK (auth.uid() = id);

-- UPDATE: Apenas próprio usuário pode atualizar
DROP POLICY IF EXISTS "Users can update own perfil" ON perfil;
CREATE POLICY "Users can update own perfil" ON perfil
    FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

-- =====================================================
-- Tabela: cilindro
-- =====================================================
ALTER TABLE cilindro ENABLE ROW LEVEL SECURITY;

-- SELECT: próprio usuário ou dev
DROP POLICY IF EXISTS "Users can view own cilindro" ON cilindro;
CREATE POLICY "Users can view own cilindro" ON cilindro
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- INSERT: Apenas próprio usuário pode inserir
DROP POLICY IF EXISTS "Users can insert cilindro" ON cilindro;
CREATE POLICY "Users can insert cilindro" ON cilindro
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- UPDATE: Apenas próprio usuário pode atualizar
DROP POLICY IF EXISTS "Users can update cilindro" ON cilindro;
CREATE POLICY "Users can update cilindro" ON cilindro
    FOR UPDATE USING (auth.uid() = user_id);

-- DELETE: Apenas próprio usuário pode excluir
DROP POLICY IF EXISTS "Users can delete cilindro" ON cilindro;
CREATE POLICY "Users can delete cilindro" ON cilindro
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: elemento
-- =====================================================
ALTER TABLE elemento ENABLE ROW LEVEL SECURITY;

-- SELECT: próprio usuário ou dev
DROP POLICY IF EXISTS "Users can view own elemento" ON elemento;
CREATE POLICY "Users can view own elemento" ON elemento
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- INSERT: Apenas próprio usuário pode inserir
DROP POLICY IF EXISTS "Users can insert elemento" ON elemento;
CREATE POLICY "Users can insert elemento" ON elemento
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- UPDATE: Apenas próprio usuário pode atualizar
DROP POLICY IF EXISTS "Users can update elemento" ON elemento;
CREATE POLICY "Users can update elemento" ON elemento
    FOR UPDATE USING (auth.uid() = user_id);

-- DELETE: Apenas próprio usuário pode excluir
DROP POLICY IF EXISTS "Users can delete elemento" ON elemento;
CREATE POLICY "Users can delete elemento" ON elemento
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: leitura
-- =====================================================
ALTER TABLE leitura ENABLE ROW LEVEL SECURITY;

-- SELECT: próprio usuário ou dev
DROP POLICY IF EXISTS "Users can view own leitura" ON leitura;
CREATE POLICY "Users can view own leitura" ON leitura
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- INSERT: Apenas próprio usuário pode inserir
DROP POLICY IF EXISTS "Users can insert leitura" ON leitura;
CREATE POLICY "Users can insert leitura" ON leitura
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- UPDATE: Apenas próprio usuário pode atualizar
DROP POLICY IF EXISTS "Users can update leitura" ON leitura;
CREATE POLICY "Users can update leitura" ON leitura
    FOR UPDATE USING (auth.uid() = user_id);

-- DELETE: Apenas próprio usuário pode excluir
DROP POLICY IF EXISTS "Users can delete leitura" ON leitura;
CREATE POLICY "Users can delete leitura" ON leitura
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: pressao
-- =====================================================
ALTER TABLE pressao ENABLE ROW LEVEL SECURITY;

-- SELECT: próprio usuário ou dev
DROP POLICY IF EXISTS "Users can view own pressao" ON pressao;
CREATE POLICY "Users can view own pressao" ON pressao
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- INSERT: Apenas próprio usuário pode inserir
DROP POLICY IF EXISTS "Users can insert pressao" ON pressao;
CREATE POLICY "Users can insert pressao" ON pressao
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- UPDATE: Apenas próprio usuário pode atualizar
DROP POLICY IF EXISTS "Users can update pressao" ON pressao;
CREATE POLICY "Users can update pressao" ON pressao
    FOR UPDATE USING (auth.uid() = user_id);

-- DELETE: Apenas próprio usuário pode excluir
DROP POLICY IF EXISTS "Users can delete pressao" ON pressao;
CREATE POLICY "Users can delete pressao" ON pressao
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: amostra
-- =====================================================
ALTER TABLE amostra ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own amostra" ON amostra;
CREATE POLICY "Users can view own amostra" ON amostra
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

DROP POLICY IF EXISTS "Users can insert amostra" ON amostra;
CREATE POLICY "Users can insert amostra" ON amostra
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update amostra" ON amostra;
CREATE POLICY "Users can update amostra" ON amostra
    FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete amostra" ON amostra;
CREATE POLICY "Users can delete amostra" ON amostra
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: amostra_elemento
-- =====================================================
ALTER TABLE amostra_elemento ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own amostra_elemento" ON amostra_elemento;
CREATE POLICY "Users can view own amostra_elemento" ON amostra_elemento
    FOR SELECT USING (
        auth.uid() IN (SELECT user_id FROM amostra WHERE id = amostra_elemento.amostra_id)
        OR public.is_dev()
    );

DROP POLICY IF EXISTS "Users can insert amostra_elemento" ON amostra_elemento;
CREATE POLICY "Users can insert amostra_elemento" ON amostra_elemento
    FOR INSERT WITH CHECK (auth.uid() IN (
        SELECT user_id FROM amostra WHERE id = amostra_id
    ));

DROP POLICY IF EXISTS "Users can delete amostra_elemento" ON amostra_elemento;
CREATE POLICY "Users can delete amostra_elemento" ON amostra_elemento
    FOR DELETE USING (auth.uid() IN (
        SELECT user_id FROM amostra WHERE id = amostra_id
    ));

DROP POLICY IF EXISTS "Users can update amostra_elemento" ON amostra_elemento;
CREATE POLICY "Users can update amostra_elemento" ON amostra_elemento
    FOR UPDATE USING (auth.uid() IN (
        SELECT user_id FROM amostra WHERE id = amostra_id
    ));

-- =====================================================
-- Tabela: historico_auditoria
-- =====================================================
ALTER TABLE historico_auditoria ENABLE ROW LEVEL SECURITY;

-- SELECT: próprio usuário ou dev
DROP POLICY IF EXISTS "Users can view own historico_auditoria" ON historico_auditoria;
CREATE POLICY "Users can view own historico_auditoria" ON historico_auditoria
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- Nota: INSERT/UPDATE/DELETE são feitos via service_role (admin)
-- para permitir registro de histórico de qualquer usuário

-- =====================================================
-- Tabela: historico_login
-- =====================================================
ALTER TABLE historico_login ENABLE ROW LEVEL SECURITY;

-- SELECT: admins e devs apenas (migration 20260620_add_login_history.sql)
DROP POLICY IF EXISTS "admins_select_historico_login" ON historico_login;
CREATE POLICY "admins_select_historico_login"
    ON historico_login FOR SELECT
    USING (
        auth.uid() IN (
            SELECT id FROM public.perfil WHERE role IN ('admin', 'dev')
        )
    );
