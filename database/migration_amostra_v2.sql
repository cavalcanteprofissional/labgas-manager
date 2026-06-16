-- =====================================================
-- MIGRATION: Criar tabelas amostra + amostra_elemento
-- Executar no SQL Editor do Supabase
-- =====================================================

CREATE TABLE amostra (
    id SERIAL PRIMARY KEY,
    numero_amostra INTEGER NOT NULL,
    lote INTEGER NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(numero_amostra, user_id)
);

CREATE TABLE amostra_elemento (
    id SERIAL PRIMARY KEY,
    amostra_id INTEGER REFERENCES amostra(id) ON DELETE CASCADE,
    elemento_id INTEGER REFERENCES elemento(id) ON DELETE CASCADE,
    UNIQUE(amostra_id, elemento_id)
);

CREATE INDEX idx_amostra_user_id ON amostra(user_id);
CREATE INDEX idx_amostra_lote ON amostra(lote);
CREATE INDEX idx_amostra_elemento_amostra_id ON amostra_elemento(amostra_id);
CREATE INDEX idx_amostra_elemento_elemento_id ON amostra_elemento(elemento_id);

ALTER TABLE amostra ENABLE ROW LEVEL SECURITY;
ALTER TABLE amostra_elemento ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view amostra" ON amostra FOR SELECT USING (true);
CREATE POLICY "Users can insert amostra" ON amostra FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update amostra" ON amostra FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete amostra" ON amostra FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Anyone can view amostra_elemento" ON amostra_elemento FOR SELECT USING (true);
CREATE POLICY "Users can insert amostra_elemento" ON amostra_elemento
    FOR INSERT WITH CHECK (auth.uid() IN (SELECT user_id FROM amostra WHERE id = amostra_id));
CREATE POLICY "Users can delete amostra_elemento" ON amostra_elemento
    FOR DELETE USING (auth.uid() IN (SELECT user_id FROM amostra WHERE id = amostra_id));
