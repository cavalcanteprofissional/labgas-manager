-- =====================================================
-- Migration v5: Índices faltantes no historico_log
-- =====================================================
-- Os índices abaixo existem no schema.sql mas nunca
-- foram aplicados ao banco via migration.
-- =====================================================
-- NOTA (Fase 76/77): LEGADO — a tabela `historico_log` foi substituída por
-- `historico_auditoria` e dropada em 2026-08-05. Os índices correspondentes
-- agora vivem no schema.sql como idx_historico_aud_*. Este arquivo é mantido
-- apenas como registro histórico; não deve ser executado contra o schema atual.
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_historico_log_user_id ON historico_log(user_id);
CREATE INDEX IF NOT EXISTS idx_historico_log_tipo ON historico_log(tipo);
CREATE INDEX IF NOT EXISTS idx_historico_log_created_at ON historico_log(created_at);

-- Índice composto para a query de lotes (amostra.py):
-- SELECT lote, created_at FROM amostra ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_amostra_lote_created ON amostra(lote, created_at DESC);
