CREATE TABLE IF NOT EXISTS historico_login (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    ip_address INET,
    user_agent TEXT,
    sucesso BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_historico_login_user_id ON historico_login(user_id);
CREATE INDEX IF NOT EXISTS idx_historico_login_created_at ON historico_login(created_at DESC);

ALTER TABLE historico_login ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admins_select_historico_login"
    ON historico_login FOR SELECT
    USING (
        auth.uid() IN (
            SELECT id FROM public.perfil WHERE role IN ('admin', 'dev')
        )
    );
