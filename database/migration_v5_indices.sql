-- =====================================================
-- Migration v5: Índices faltantes no historico_log
-- =====================================================
-- Os índices abaixo existem no schema.sql mas nunca
-- foram aplicados ao banco via migration.
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_historico_log_user_id ON historico_log(user_id);
CREATE INDEX IF NOT EXISTS idx_historico_log_tipo ON historico_log(tipo);
CREATE INDEX IF NOT EXISTS idx_historico_log_created_at ON historico_log(created_at);

-- Índice composto para a query de lotes (amostra.py):
-- SELECT lote, created_at FROM amostra ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_amostra_lote_created ON amostra(lote, created_at DESC);
