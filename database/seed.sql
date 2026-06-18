-- =====================================================
-- SEED (SQL) — LabGas Manager
-- Apenas upsert do perfil (seguro para versionar).
-- O auth.user deve ser criado primeiro via:
--   python scripts/seed.py
-- =====================================================

DO $$
DECLARE
    v_user_id UUID;
BEGIN
    SELECT id INTO v_user_id FROM auth.users WHERE email = 'teste@labgas.com';

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'Usuário auth.users não encontrado. Execute "python scripts/seed.py" primeiro.';
    END IF;

    INSERT INTO perfil (id, role, ativo, nome, email, habilitar_abas)
    VALUES (
        v_user_id,
        'dev',
        true,
        'Usuário Teste',
        'teste@labgas.com',
        '{"cilindro":true,"pressao":true,"elemento":true,"leitura":true,"amostra":true,"historico":true}'
    )
    ON CONFLICT (id) DO UPDATE
    SET role = 'dev',
        ativo = true,
        nome = 'Usuário Teste',
        email = 'teste@labgas.com',
        habilitar_abas = '{"cilindro":true,"pressao":true,"elemento":true,"leitura":true,"amostra":true,"historico":true}';

    RAISE NOTICE 'Perfil do usuário teste@labgas.com atualizado com sucesso.';
END;
$$;
