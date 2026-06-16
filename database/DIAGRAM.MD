# Diagrama do Banco de Dados - LabGas Manager

## Visão Geral (ER Diagram)

```mermaid
erDiagram
    PERFIL ||--o{ CILINDRO : "possui"
    PERFIL ||--o{ ELEMENTO : "possui"
    PERFIL ||--o{ LEITURA : "possui"
    PERFIL ||--o{ AMOSTRA : "possui"
    PERFIL ||--o{ PRESSAO : "possui"
    PERFIL ||--o{ HISTORICO_LOG : "registra"
    
    CILINDRO ||--o{ LEITURA : "usado_em"
    CILINDRO ||--o{ PRESSAO : "medido_em"
    ELEMENTO ||--o{ LEITURA : "analisado_em"
    AMOSTRA ||--o{ AMOSTRA_ELEMENTO : "contem"
    ELEMENTO ||--o{ AMOSTRA_ELEMENTO : "selecionado_em"

    PERFIL {
        uuid id PK
        varchar role
        boolean ativo
        varchar nome
        varchar email
        jsonb habilitar_abas
        timestamptz criado_em
    }

    CILINDRO {
        int id PK
        varchar codigo
        date data_compra
        date data_inicio_consumo
        date data_fim
        decimal gas_kg
        decimal litros_equivalentes
        decimal custo
        varchar status
        uuid user_id FK
        timestamp created_at
    }

    ELEMENTO {
        int id PK
        varchar nome
        decimal consumo_lpm
        uuid user_id FK
        timestamp created_at
    }

    LEITURA {
        int id PK
        date data
        varchar tempo_chama
        int cilindro_id FK
        int elemento_id FK
        int quantidade
        uuid user_id FK
        timestamp created_at
    }

    AMOSTRA {
        int id PK
        numeric numero_amostra
        int lote
        uuid user_id FK
        timestamp created_at
    }

    AMOSTRA_ELEMENTO {
        int id PK
        int amostra_id FK
        int elemento_id FK
    }

    PRESSAO {
        int id PK
        int cilindro_id FK
        numeric pressao
        numeric temperatura
        date data
        time hora
        uuid user_id FK
        timestamp created_at
    }

    HISTORICO_LOG {
        int id PK
        varchar tipo
        varchar acao
        varchar nome
        uuid user_id FK
        timestamp created_at
    }
```

## Diagrama de Fluxo de Dados

```mermaid
flowchart TB
    subgraph auth["Auth (Supabase)"]
        auth_users["auth.users"]
    end
    
    subgraph app["Aplicação Flask"]
        frontend["Frontend<br/>Blueprints + Jinja2"]
    end
    
    subgraph db["Banco de Dados (Supabase)"]
        perfil["perfil"]
        cilindro["cilindro"]
        elemento["elemento"]
        leitura["leitura"]
        amostra["amostra"]
        amostra_elemento["amostra_elemento"]
        pressao["pressao"]
        historico["historico_log"]
    end
    
    auth_users -->|FK| perfil
    perfil -->|possui| cilindro
    perfil -->|possui| elemento
    perfil -->|possui| leitura
    perfil -->|possui| amostra
    perfil -->|possui| pressao
    perfil -->|registra| historico
    
    cilindro -->|usado_em| leitura
    elemento -->|analisado_em| leitura
    cilindro -->|medido_em| pressao
    amostra -->|contem| amostra_elemento
    elemento -->|selecionado_em| amostra_elemento
    
    frontend -->|CRUD| perfil
    frontend -->|CRUD| cilindro
    frontend -->|CRUD| elemento
    frontend -->|CRUD| leitura
    frontend -->|CRUD| amostra
    frontend -->|CRUD| pressao
    frontend -->|INSERT| historico
```

---

## Tabelas

### 1. perfil

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK - ID do usuário (ref auth.users) |
| role | VARCHAR(20) | 'admin' ou 'usuario' |
| ativo | BOOLEAN | Se o usuário está ativo |
| nome | VARCHAR(100) | Nome do usuário |
| email | VARCHAR(255) | Email do usuário |
| habilitar_abas | JSONB | Permissões de acesso às abas |
| criado_em | TIMESTAMP | Data de criação |

**Default:** `habilitar_abas = {"cilindro": false, "elemento": false, "leitura": false, "amostra": false, "pressao": false, "historico": false}`

---

### 2. cilindro

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | SERIAL | PK - ID automático |
| codigo | VARCHAR(50) | Código único (ex: CIL-001) |
| data_compra | DATE | Data de compra |
| data_inicio_consumo | DATE | Início de uso |
| data_fim | DATE | Fim de uso (opcional) |
| gas_kg | DECIMAL(5,2) | Quantidade de gás em kg |
| litros_equivalentes | DECIMAL(10,2) | Litros equivalentes (956 L/kg) |
| custo | DECIMAL(10,2) | Custo do cilindro |
| status | VARCHAR(20) | 'ativo' ou 'esgotado' |
| user_id | UUID | FK - Usuário dono |
| created_at | TIMESTAMP | Data de criação |

---

### 3. elemento

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | SERIAL | PK - ID automático |
| nome | VARCHAR(100) | Nome do elemento |
| consumo_lpm | DECIMAL(5,2) | Consumo em L/min |
| user_id | UUID | FK - Usuário dono |
| created_at | TIMESTAMP | Data de criação |

---

### 4. leitura

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | SERIAL | PK - ID automático |
| data | DATE | Data da análise |
| tempo_chama | VARCHAR(8) | Tempo de chama (HH:MM:SS) |
| cilindro_id | INTEGER | FK - Cilindro usado |
| elemento_id | INTEGER | FK - Elemento analisado |
| quantidade | INTEGER | Quantidade de leituras |
| user_id | UUID | FK - Usuário dono |
| created_at | TIMESTAMP | Data de criação |

---

### 5. amostra

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | SERIAL | PK - ID automático |
| numero_amostra | NUMERIC | Número da amostra (real positivo) |
| lote | INTEGER | Lote da amostra |
| user_id | UUID | FK - Usuário dono |
| created_at | TIMESTAMP | Data de criação |

**Índice único:** `UNIQUE(numero_amostra, user_id)`

---

### 6. amostra_elemento

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | SERIAL | PK - ID automático |
| amostra_id | INTEGER | FK - Amostra |
| elemento_id | INTEGER | FK - Elemento selecionado |

**Índice único:** `UNIQUE(amostra_id, elemento_id)`

---

### 5. pressao

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | SERIAL | PK - ID automático |
| cilindro_id | INTEGER | FK - Cilindro |
| pressao | NUMERIC | Pressão em bar |
| temperatura | NUMERIC | Temperatura em °C (opcional) |
| data | DATE | Data da medição |
| hora | TIME | Hora da medição |
| user_id | UUID | FK - Usuário dono |
| created_at | TIMESTAMP | Data de criação |

---

### 6. historico_log

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | SERIAL | PK - ID automático |
| tipo | VARCHAR(20) | Tipo: cilindro, elemento, leitura, amostra, pressao, perfil |
| acao | VARCHAR(20) | Ação: criado, atualizado, excluido |
| nome | VARCHAR(100) | Nome/identificação do item |
| user_id | UUID | FK - Usuário que executou |
| created_at | TIMESTAMP | Data/hora da ação |

---

## Relacionamentos

| De | Para | Tipo |
|----|------|------|
| cilindro.user_id | perfil.id | N:1 |
| elemento.user_id | perfil.id | N:1 |
| leitura.user_id | perfil.id | N:1 |
| leitura.cilindro_id | cilindro.id | N:1 |
| leitura.elemento_id | elemento.id | N:1 |
| amostra.user_id | perfil.id | N:1 |
| amostra_elemento.amostra_id | amostra.id | N:1 |
| amostra_elemento.elemento_id | elemento.id | N:1 |
| pressao.user_id | perfil.id | N:1 |
| pressao.cilindro_id | cilindro.id | N:1 |
| historico_log.user_id | perfil.id | N:1 |

---

## Políticas RLS

Todas as tabelas possuem Row Level Security (RLS) habilitado:

| Tabela | SELECT | INSERT | UPDATE | DELETE |
|--------|--------|--------|--------|--------|
| cilindro | Público | Próprio usuário | Próprio usuário | Próprio usuário |
| elemento | Público | Próprio usuário | Próprio usuário | Próprio usuário |
| leitura | Público | Próprio usuário | Próprio usuário | Próprio usuário |
| amostra | Público | Próprio usuário | Próprio usuário | Próprio usuário |
| amostra_elemento | Público | Próprio usuário | Próprio usuário | Próprio usuário |
| perfil | Próprio usuário | Próprio usuário | Próprio usuário | - |
| pressao | Público | Próprio usuário | Próprio usuário | Próprio usuário |
| historico_log | Público | Admin (service_role) | - | - |
