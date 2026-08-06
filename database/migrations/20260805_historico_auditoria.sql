-- =====================================================
-- MIGRATION: historico_log → historico_auditoria
-- Data: 2026-08-05
-- Motivo: a coluna `nome` de historico_log armazenava dados
-- heterogêneos (identificadores, strings compostas como
-- "CIL-013 - 150 bar" e mensagens livres), sem FK para o
-- registro de origem e com risco de truncamento (VARCHAR(100)).
-- A nova tabela separa a semântica em:
--   * label   — texto legível (era a coluna nome)
--   * ref_id  — id do registro de origem na tabela definida por `tipo`
--               (polimórfico; sem FK rígida, pois a tabela varia por tipo)
--   * detalhe — payload estruturado JSONB (pressao, temperatura,
--               quantidade, lote, role, aba, alvo, etc.)
--
-- FLUXO (executar nesta ordem):
--   1) CREATE TABLE historico_auditoria + índices
--   2) Migrar dados (INSERT ... SELECT) preservando created_at/user_id
--   3) Verificar contagens (devem bater)
--   4) Após o código/backend atualizado e validado: DROP TABLE historico_log
-- =====================================================

-- -----------------------------------------------------
-- 1) Tabela nova
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS historico_auditoria (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,               -- cilindro|pressao|elemento|leitura|amostra|perfil
    acao VARCHAR(20) NOT NULL CHECK (acao IN ('criado', 'atualizado', 'excluido')),
    ref_id INTEGER,                          -- id do registro de origem (conforme `tipo`);
                                             -- NULL para perfil/auth/ações em lote
    label VARCHAR(150),                      -- texto legível (antiga coluna nome)
    detalhe JSONB,                           -- payload estruturado (opcional)
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_historico_aud_tipo ON historico_auditoria(tipo);
CREATE INDEX IF NOT EXISTS idx_historico_aud_user_id ON historico_auditoria(user_id);
CREATE INDEX IF NOT EXISTS idx_historico_aud_created_at ON historico_auditoria(created_at);
CREATE INDEX IF NOT EXISTS idx_historico_aud_ref ON historico_auditoria(tipo, ref_id);

ALTER TABLE historico_auditoria ENABLE ROW LEVEL SECURITY;

-- SELECT: mesmo comportamento de historico_log — qualquer usuário autenticado
-- pode visualizar (a UI já filtra por papel; INSERT é feito via service_role)
CREATE POLICY "Anyone can view historico_auditoria" ON historico_auditoria
    FOR SELECT USING (true);

-- -----------------------------------------------------
-- 2) Migração dos dados
-- -----------------------------------------------------
-- ref_id é resolvido por backfill apenas onde é inequívoco:
--   * cilindro → join por (codigo, user_id)
--   * elemento → join por (nome, user_id)  (último registro se houver duplicata)
--   * amostra  → join por ('A/' || numero_amostra || ' L' || lote, user_id)
--   * pressao / leitura / perfil → ref_id = NULL:
--       - pressao/leitura gravavam strings compostas cuja reconstrução
--         exata do registro seria frágil (possibilidade de ref errado).
--         Os novos registros já passam ref_id + detalhe corretos.
--       - perfil é registro de usuário (user_id é UUID) — não cabe em ref_id.
--   O `label` preserva integralmente o texto legível original.
INSERT INTO historico_auditoria (tipo, acao, ref_id, label, detalhe, user_id, created_at)
SELECT
    h.tipo,
    h.acao,
    CASE h.tipo
        WHEN 'cilindro' THEN (
            SELECT c.id FROM cilindro c
            WHERE c.codigo = h.nome AND c.user_id = h.user_id
            LIMIT 1
        )
        WHEN 'elemento' THEN (
            SELECT e.id FROM elemento e
            WHERE e.nome = h.nome AND e.user_id = h.user_id
            ORDER BY e.id DESC
            LIMIT 1
        )
        WHEN 'amostra' THEN (
            SELECT a.id FROM amostra a
            WHERE a.user_id = h.user_id
              AND 'A/' || a.numero_amostra || ' L' || a.lote = h.nome
            LIMIT 1
        )
        ELSE NULL
    END AS ref_id,
    h.nome AS label,
    NULL::jsonb AS detalhe,
    h.user_id,
    h.created_at
FROM historico_log h;

-- -----------------------------------------------------
-- 3) Verificação
-- -----------------------------------------------------
-- SELECT
--   (SELECT count(*) FROM historico_log) AS legados,
--   (SELECT count(*) FROM historico_auditoria) AS migrados;
-- SELECT tipo, acao, count(*) FROM historico_auditoria GROUP BY tipo, acao ORDER BY tipo, acao;
-- SELECT count(*) AS sem_ref FROM historico_auditoria WHERE ref_id IS NULL;

-- -----------------------------------------------------
-- 4) Descarte da tabela legada (apenas após backend validado)
-- -----------------------------------------------------
-- EXECUTADO em 2026-08-05 (Fase 77), após:
--   * contagens validadas (351/351)
--   * snapshot de segurança historico_log_bkp_20260805 criado e, após
--     smoke test + backup --no-upload + suíte test_backup (33 verdes),
--     também descartado
-- DROP TABLE historico_log;
-- DROP TABLE historico_log_bkp_20260805;
