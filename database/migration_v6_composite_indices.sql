-- =====================================================
-- Migration v6: Índices compostos para queries do dashboard
-- =====================================================
-- As queries do dashboard filtram por user_id E ordenam por data.
-- Índices separados em cada coluna não são eficientes para isso.
-- =====================================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_leitura_user_data
    ON leitura(user_id, data DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pressao_user_data
    ON pressao(user_id, data);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_amostra_user_created
    ON amostra(user_id, created_at DESC);
