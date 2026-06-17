-- =====================================================
-- SCHEMA DO BANCO DE DADOS - LabGas Manager
-- Supabase (PostgreSQL)
-- =====================================================

-- Tabela: perfil (criar primeiro - dependencias de outras tabelas)
CREATE TABLE perfil (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'usuario' CHECK (role IN ('admin', 'usuario')),
    ativo BOOLEAN DEFAULT true,
    nome VARCHAR(100),
    email VARCHAR(255),
    habilitar_abas JSONB DEFAULT '{"cilindro": false, "elemento": false, "leitura": false, "amostra": false, "historico": false}',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela: cilindro
CREATE TABLE cilindro (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL,
    data_compra DATE NOT NULL,
    data_inicio_consumo DATE,
    data_fim DATE,
    gas_kg NUMERIC(6,2) DEFAULT 1.0,
    litros_equivalentes NUMERIC(10,3) DEFAULT 956.0,
    custo NUMERIC(10,2) DEFAULT 290.00,
    status VARCHAR(20) DEFAULT 'ativo',
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: elemento
CREATE TABLE elemento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    consumo_lpm NUMERIC(5,2) NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: pressao
CREATE TABLE pressao (
    id SERIAL PRIMARY KEY,
    cilindro_id INTEGER REFERENCES cilindro(id) ON DELETE CASCADE,
    pressao NUMERIC(5,2) NOT NULL,
    temperatura NUMERIC(5,2),
    data DATE NOT NULL,
    hora TIME NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: leitura
CREATE TABLE leitura (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    tempo_chama VARCHAR(8) NOT NULL,
    cilindro_id INTEGER REFERENCES cilindro(id) ON DELETE CASCADE,
    elemento_id INTEGER REFERENCES elemento(id) ON DELETE CASCADE,
    quantidade INTEGER DEFAULT 1,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: historico_log
CREATE TABLE historico_log (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    acao VARCHAR(20) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela: amostra
CREATE TABLE amostra (
    id SERIAL PRIMARY KEY,
    numero_amostra INTEGER NOT NULL,
    lote INTEGER NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(numero_amostra, user_id)
);

-- Tabela: amostra_elemento (relação N:N)
CREATE TABLE amostra_elemento (
    id SERIAL PRIMARY KEY,
    amostra_id INTEGER REFERENCES amostra(id) ON DELETE CASCADE,
    elemento_id INTEGER REFERENCES elemento(id) ON DELETE CASCADE,
    UNIQUE(amostra_id, elemento_id)
);

-- =====================================================
-- ÍNDICES
-- =====================================================

CREATE INDEX idx_cilindro_user_id ON cilindro(user_id);
CREATE INDEX idx_cilindro_codigo ON cilindro(codigo);
CREATE INDEX idx_elemento_user_id ON elemento(user_id);
CREATE INDEX idx_elemento_nome ON elemento(nome);
CREATE INDEX idx_leitura_user_id ON leitura(user_id);
CREATE INDEX idx_leitura_cilindro_id ON leitura(cilindro_id);
CREATE INDEX idx_leitura_elemento_id ON leitura(elemento_id);
CREATE INDEX idx_leitura_data ON leitura(data);
CREATE INDEX idx_perfil_id ON perfil(id);
CREATE INDEX idx_perfil_role ON perfil(role);
CREATE INDEX idx_perfil_role_ativo ON perfil(role, ativo);
CREATE INDEX idx_pressao_user_id ON pressao(user_id);
CREATE INDEX idx_pressao_cilindro_id ON pressao(cilindro_id);
CREATE INDEX idx_pressao_data ON pressao(data);
CREATE INDEX idx_historico_log_user_id ON historico_log(user_id);
CREATE INDEX idx_historico_log_tipo ON historico_log(tipo);
CREATE INDEX idx_historico_log_created_at ON historico_log(created_at);
CREATE INDEX idx_amostra_user_id ON amostra(user_id);
CREATE INDEX idx_amostra_lote ON amostra(lote);
CREATE INDEX idx_amostra_elemento_amostra_id ON amostra_elemento(amostra_id);
CREATE INDEX idx_amostra_elemento_elemento_id ON amostra_elemento(elemento_id);
