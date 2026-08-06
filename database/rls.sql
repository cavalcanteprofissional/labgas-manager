-- =====================================================
-- POLÍTICAS RLS (Row Level Security) - LabGas Manager
-- =====================================================
-- As policies SELECT restringem leitura ao dono do registro
-- (auth.uid() = user_id); usuários com role 'dev' enxergam tudo
-- via public.is_dev() (SECURITY DEFINER, ver migration
-- 20260806_cilindro_numero.sql).

-- =====================================================
-- Tabela: cilindro
-- =====================================================

-- SELECT: próprio usuário ou dev
CREATE POLICY "Users can view own cilindro" ON cilindro
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- INSERT: Apenas próprio usuário pode inserir
CREATE POLICY "Users can insert cilindro" ON cilindro
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- UPDATE: Apenas próprio usuário pode atualizar
CREATE POLICY "Users can update cilindro" ON cilindro
    FOR UPDATE USING (auth.uid() = user_id);

-- DELETE: Apenas próprio usuário pode excluir
CREATE POLICY "Users can delete cilindro" ON cilindro
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: elemento
-- =====================================================

-- SELECT: próprio usuário ou dev
CREATE POLICY "Users can view own elemento" ON elemento
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- INSERT: Apenas próprio usuário pode inserir
CREATE POLICY "Users can insert elemento" ON elemento
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- UPDATE: Apenas próprio usuário pode atualizar
CREATE POLICY "Users can update elemento" ON elemento
    FOR UPDATE USING (auth.uid() = user_id);

-- DELETE: Apenas próprio usuário pode excluir
CREATE POLICY "Users can delete elemento" ON elemento
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: leitura
-- =====================================================

-- SELECT: próprio usuário ou dev
CREATE POLICY "Users can view own leitura" ON leitura
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- INSERT: Apenas próprio usuário pode inserir
CREATE POLICY "Users can insert leitura" ON leitura
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- UPDATE: Apenas próprio usuário pode atualizar
CREATE POLICY "Users can update leitura" ON leitura
    FOR UPDATE USING (auth.uid() = user_id);

-- DELETE: Apenas próprio usuário pode excluir
CREATE POLICY "Users can delete leitura" ON leitura
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: perfil
-- =====================================================

-- SELECT: Apenas próprio usuário ou dev
CREATE POLICY "Users can view own perfil" ON perfil
    FOR SELECT USING (auth.uid() = id OR public.is_dev());

-- INSERT: Apenas próprio usuário pode inserir (seu próprio perfil)
CREATE POLICY "Users can insert own perfil" ON perfil
    FOR INSERT WITH CHECK (auth.uid() = id);

-- UPDATE: Apenas próprio usuário pode atualizar
CREATE POLICY "Users can update own perfil" ON perfil
    FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

-- =====================================================
-- Tabela: pressao
-- =====================================================

-- SELECT: próprio usuário ou dev
CREATE POLICY "Users can view own pressao" ON pressao
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- INSERT: Apenas próprio usuário pode inserir
CREATE POLICY "Users can insert pressao" ON pressao
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- UPDATE: Apenas próprio usuário pode atualizar
CREATE POLICY "Users can update pressao" ON pressao
    FOR UPDATE USING (auth.uid() = user_id);

-- DELETE: Apenas próprio usuário pode excluir
CREATE POLICY "Users can delete pressao" ON pressao
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: historico_auditoria
-- =====================================================

-- SELECT: próprio usuário ou dev
CREATE POLICY "Users can view own historico_auditoria" ON historico_auditoria
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

-- Nota: INSERT/UPDATE/DELETE são feitos via service_role (admin)
-- para permitir registro de histórico de qualquer usuário

-- =====================================================
-- Tabela: amostra
-- =====================================================

CREATE POLICY "Users can view own amostra" ON amostra
    FOR SELECT USING (auth.uid() = user_id OR public.is_dev());

CREATE POLICY "Users can insert amostra" ON amostra
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update amostra" ON amostra
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete amostra" ON amostra
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: amostra_elemento
-- =====================================================

CREATE POLICY "Users can view own amostra_elemento" ON amostra_elemento
    FOR SELECT USING (
        auth.uid() IN (SELECT user_id FROM amostra WHERE id = amostra_elemento.amostra_id)
        OR public.is_dev()
    );

CREATE POLICY "Users can insert amostra_elemento" ON amostra_elemento
    FOR INSERT WITH CHECK (auth.uid() IN (
        SELECT user_id FROM amostra WHERE id = amostra_id
    ));

CREATE POLICY "Users can delete amostra_elemento" ON amostra_elemento
    FOR DELETE USING (auth.uid() IN (
        SELECT user_id FROM amostra WHERE id = amostra_id
    ));

CREATE POLICY "Users can update amostra_elemento" ON amostra_elemento
    FOR UPDATE USING (auth.uid() IN (
        SELECT user_id FROM amostra WHERE id = amostra_id
    ));
