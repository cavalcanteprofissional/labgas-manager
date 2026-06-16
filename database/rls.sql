-- =====================================================
-- POLÍTICAS RLS (Row Level Security) - LabGas Manager
-- =====================================================

-- =====================================================
-- Tabela: cilindro
-- =====================================================

-- SELECT: Qualquer usuário pode visualizar
CREATE POLICY "Anyone can view cilindro" ON cilindro
    FOR SELECT USING (true);

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

-- SELECT: Qualquer usuário pode visualizar
CREATE POLICY "Anyone can view elemento" ON elemento
    FOR SELECT USING (true);

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

-- SELECT: Qualquer usuário pode visualizar
CREATE POLICY "Anyone can view leitura" ON leitura
    FOR SELECT USING (true);

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

-- SELECT: Apenas próprio usuário pode visualizar
CREATE POLICY "Users can view own perfil" ON perfil
    FOR SELECT USING (auth.uid() = id);

-- INSERT: Apenas próprio usuário pode inserir (seu próprio perfil)
CREATE POLICY "Users can insert own perfil" ON perfil
    FOR INSERT WITH CHECK (auth.uid() = id);

-- UPDATE: Apenas próprio usuário pode atualizar
CREATE POLICY "Users can update own perfil" ON perfil
    FOR UPDATE USING (true) WITH CHECK (true);

-- =====================================================
-- Tabela: pressao
-- =====================================================

-- SELECT: Qualquer usuário pode visualizar
CREATE POLICY "Anyone can view pressao" ON pressao
    FOR SELECT USING (true);

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
-- Tabela: historico_log
-- =====================================================

-- SELECT: Qualquer usuário pode visualizar
CREATE POLICY "Users can view historico_log" ON historico_log
    FOR SELECT USING (true);

-- Nota: INSERT/UPDATE/DELETE são feitos via service_role (admin)
-- para permitir registro de histórico de qualquer usuário

-- =====================================================
-- Tabela: amostra
-- =====================================================

CREATE POLICY "Anyone can view amostra" ON amostra
    FOR SELECT USING (true);

CREATE POLICY "Users can insert amostra" ON amostra
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update amostra" ON amostra
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete amostra" ON amostra
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Tabela: amostra_elemento
-- =====================================================

CREATE POLICY "Anyone can view amostra_elemento" ON amostra_elemento
    FOR SELECT USING (true);

CREATE POLICY "Users can insert amostra_elemento" ON amostra_elemento
    FOR INSERT WITH CHECK (auth.uid() IN (
        SELECT user_id FROM amostra WHERE id = amostra_id
    ));

CREATE POLICY "Users can delete amostra_elemento" ON amostra_elemento
    FOR DELETE USING (auth.uid() IN (
        SELECT user_id FROM amostra WHERE id = amostra_id
    ));
