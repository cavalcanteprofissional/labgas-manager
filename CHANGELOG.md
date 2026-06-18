# Changelog

Todas as alterações notáveis no LabGas Manager serão documentadas neste arquivo.

## [2.6.15] - 2026-06-17

### Padronização

- **Header da tabela de histórico** 🎨: removido gradiente escuro (`linear-gradient(135deg, #002a47, #003a5e)`) do `card-header` — agora usa `bg-light` igual cilindro, elemento, leitura, pressão e amostra. Filtros foram separados em um card próprio (com `mb-4`), e a tabela ficou em um segundo card, seguindo exatamente o padrão das demais abas. O `<thead>` permanece `class="table-light"`, idêntico a todos os outros templates.

### Segurança

- **Seed com senha no .env.local** 🔐: `database/seed.sql` não contém mais senhas (só upsert do `perfil`). Novo `scripts/seed.py` lê `TEST_PASSWORD` do `frontend/.env.local` e cria/reseta o auth user via Admin API, sem expor credenciais no repositório.

## [2.6.14] - 2026-06-17

### Features

- **Autocomplete de horário com colons** ⌨️: nova função JS `autoFormatTime()` inserida nos templates `leitura.html` e `pressao.html`. Ao digitar apenas números nos campos de tempo, os dois-pontos são inseridos automaticamente:
  - `tempo_chama` (Leitura): `HH:MM:SS` — 6 dígitos → `14:30:05`
  - `hora` (Pressão): `HH:MM` — 4 dígitos → `14:30`
  - Funciona tanto no formulário de criação quanto nos modais de edição
  - JS puro, sem dependências — só redefine o value se houve mudança real, evitando loop infinito

## [2.6.13] - 2026-06-17

### Segurança dos Cleanups 🛡️

- **`.neq("id", 0)` removido de todos os 6 cleanups** em `conftest.py` — esse filtro casava com todo registro (todos têm `id >= 1`), não protegia nada e criava falsa sensação de segurança. Se alguém removesse o `.eq("user_id", ...)` por engano, o resultado seria um `DELETE ALL` via admin_client (bypass RLS).
- **`amostra_elemento` cleanup reforçado**: filtro adicional `if a.get("id")` garante que só IDs válidos sejam passados ao `in_()`, e a SELECT de amostras já é escopada por `user_id` antes do delete
- **`test_user_id = None`**: todos os cleanups já possuem guard `if test_user_id:`, pulando execução quando o usuário de teste não existe

### Alterações

- `frontend/tests/conftest.py`: linhas 171, 178, 185, 192, 203, 210 — `.neq("id", 0)` removidos; linha 200 — filtro `if a.get("id")` adicionado

## [2.6.12] - 2026-06-17

### Bugfixes

- **Registro de Leitura quebrava com erro 500**: `formatar_tempo_chama()` em `validators.py` esperava 3 argumentos (`hora, minuto, segundo`), mas era chamada com 1 string `"HH:MM:SS"` em `leitura.py:50` — TypeError não capturado pelo `except ValueError`, gerando Internal Server Error ao tentar registrar qualquer leitura
- **formatar_tempo_chama refatorada**: função agora aceita string `"HH:MM:SS"` (ou `"HH:MM"`), faz o parsing internamente e retorna `"HH:MM:SS"` formatado

### Testes

- **test_create_leitura**: antes era falso positivo (não selecionava cilindro nem elemento, campos obrigatórios) — refatorado para criar cilindro+elemento via admin_client, preencher todos os campos do formulário e verificar persistência no banco (`assert result.data[0]["quantidade"] == 3`)
- **test_create_leitura_with_existing_cilindro_elemento removido**: funcionalidade incorporada ao `test_create_leitura` reformulado (que sempre cria dados frescos em vez de depender de registros existentes)

## [2.6.11] - 2026-06-17

### Testes em Modais (Fase 39) 🧪

- **18 testes modais** (Playwright) com flag `--run-modais`:
  - Amostra: 6 testes (edit preenche, valida JS, submit, delete confirma, cancela, bulk)
  - Cilindro: 3 testes (edit preenche, delete, bulk)
  - Elemento: 3 testes (edit preenche, delete, bulk)
  - Leitura: 3 testes (edit preenche, delete, bulk)
  - Pressão: 3 testes (edit preenche, delete, bulk)
- **Marker pytest** `modais`: opt-in via `pytest --run-modais`, skipados por padrão
- **conftest.py**: `pytest_addoption` + `pytest_collection_modifyitems` para skip automático
- **pytest.ini**: marker `modais` registrado
- **Total**: 47 testes (29 normais + 18 modais), 2 skips condicionais

### Bugfixes

- **Paginação escondendo registros de teste**: páginas cilindro/elemento/leitura/pressao usam `SELECT USING (true)` sem filtro de `user_id`, então registros de outros usuários ocupavam página 1 — navegações nos testes modais usam `?per_page=1000`
- **Float formatting nas asserções**: `<input type="number" step="0.1">` renderiza `42.0` em vez de `42` — asserções corrigidas para `"42.0"`, `"150.0"`, `"25.0"`

## [2.6.10] - 2026-06-17

### Features

- **Paginação padronizada na aba Amostra** (Fase 38): agora usa o mesmo padrão da aba Leitura — per_page dropdown (10/25/50/100), max_pages=10, `...` para N>10, Anterior/Próxima com estado disabled
- **`--run-modais`**: opção pytest adicionada ao conftest.py para executar testes de modal (skipados por padrão)

## [2.6.9] - 2026-06-17

### Bugfixes

- **HTML inválido — modais dentro de `<tbody>`**: browsers fecham `<tbody>` automaticamente ao encontrar `<div>`, movendo os modais para fora da tabela e quebrando o JS do Bootstrap — modais editModal + deleteModal movidos para depois de `</table>` em amostra.html (Fase 37)

## [2.6.8] - 2026-06-17

### Bugfixes

- **Amostra sem elementos após registro**: batch insert `client.table("amostra_elemento").insert(ae_records)` (lista de dicts) não persistia registros — substituído por loop individual com `insert({...})`, comprovadamente funcional
- **cleanup_amostras deletava todos os amostra_elemento**: cleanup removia registros de **todos os usuários** (`neq("id", 0)` sem filtro de `user_id`) — corrigido para deletar apenas `amostra_elemento` vinculado às amostras do usuário de teste

### Testes

- **test_create_amostra**: agora cria um elemento de teste, marca seu checkbox no formulário, e verifica se o badge do elemento aparece na listagem — garante que o fluxo amostra→amostra_elemento funciona de ponta a ponta (antes o teste não selecionava checkbox algum, era um falso positivo)

## [2.6.7] - 2026-06-17

### SQL Optimization (Fase 35)

- **Índices no banco**: 4 índices adicionados via migration v5 (`idx_historico_log_user_id`, `idx_historico_log_tipo`, `idx_historico_log_created_at`, `idx_amostra_lote_created`) — `historico_log` tinha apenas PK, agora usa os 3 índices do schema.sql; `amostra` ganhou índice composto `(lote, created_at DESC)` para consulta de lotes
- **Batch INSERT em amostra_elemento** (create + update): laço de N inserts substituído por único `insert([dict,...])` — 1 query independente do número de elementos
- **Batch DELETE com `in_()` em amostra.py**: `delete_multiple` reduziu de N×3 queries para 3 queries fixas (1 SELECT + 2 DELETE batch)
- **Batch DELETE com `in_()` em cilindro.py + elemento.py**: cada um reduziu de N×4 queries para 3 queries fixas (2 SELECT + 1 DELETE batch, com verificação de FK em lote)
- **Batch DELETE com `in_()` em leitura.py + pressao.py**: cada um reduziu de N×3+N queries para 3-4 queries fixas (1 SELECT + lookup batch + 1 DELETE)
- **Consulta de lotes eliminada**: `SELECT lote, created_at` redundante removido — lotes extraídos do resultado principal de amostras
- **histórico: 2 queries fundidas em 1**: paginação + contagem agora feitas numa única chamada com `count="exact"` + `.range()` — 1 round-trip em vez de 2

## [2.6.6] - 2026-06-17

### Bugfixes

- **test_admin.py**: seletor com `ç` em `text=Administração` causava encoding mismatch — substituído por `text=Admin` (estável)
- **Warning de elementos na aba Amostra**: `alert()` do navegador substituído por `<div class="alert alert-warning">` inline (padrão flash do Bootstrap), some ao marcar um checkbox

## [2.6.5] - 2026-06-17

### Features

- **Formato amostra no histórico**: nomes de amostra (`h.nome`) alterados de `#5603 Lote 13070` para `A/5603 L13070` — mais scannable
- **Layout column-major nos seletores de elementos (aba Amostra)**: checkboxes agora preenchem de cima para baixo, depois para a próxima coluna, via CSS `column-count` (2/3/4 colunas responsivas)
- **Padronização dos botões de ação (Editar/Excluir)**: cilindro, elemento, leitura e pressão agora usam o mesmo design da aba Amostra — botões `btn-outline-primary`/`btn-outline-danger` com ícones puros, layout horizontal
- **Feedback visual na pipeline de testes**: logs de progresso durante startup do Flask (`"Waiting for Flask... (5s)"`, `"Flask ready after 2.0s"`)
- **Validação "pelo menos um elemento" em amostras**: backend rejeita create/update sem elementos selecionados (flash `warning`); frontend bloqueia com `alert()` via JS

### Bugfixes

- **Pipeline de testes**: limpeza de cookies (`page.context.clear_cookies()`) no fixture `login` eliminou timeouts em cascata entre testes — 27/29 testes passando estáveis
- **Tag roxa de quantidade removida da aba Leitura**: `var(--purple-light)` substituído por valor numérico puro

## [2.6.4] - 2026-06-17

### Bugfixes

- **amostra.py**: não-admin agora usa `get_authenticated_client()` (JWT da session) em vez de `get_supabase_client()` (anon key puro) para INSERT/UPDATE/DELETE — `auth.uid()` no RLS agora resolve corretamente
- **cilindro.py, elemento.py, leitura.py, pressao.py**: admin UPDATE usa `get_admin_client()` (bypass RLS) para permitir edição de dados de outros usuários
- **database/rls.sql**: adicionada política `FOR UPDATE` em `amostra_elemento` (análoga à de DELETE, via subquery `amostra.user_id`)

## [2.6.3] - 2026-06-17

### Bugfixes

- **Dashboard crash 500**: queries de `pressao` e `amostra` envolvidas em `try/except` para não quebrar o dashboard se a tabela não tiver acesso por RLS ou outro erro de consulta
- **Update amostra**: adicionada validação `if not lote` faltante no update (existia apenas no create), evitando envio de lote vazio

## [2.6.2] - 2026-06-17

### Features

- **Badges das entidades com COR_TIPO**: substituídas todas as referências `var(--X)` hardcoded nos templates por `COR_TIPO['X']['var']` (dashboard, amostra, leitura, pressao, elemento, cilindro)
- **Cor sólida `--amostra` para badges**: criada variável `--amostra: #6a1b9a` no CSS e alterado `COR_TIPO["amostra"]["var"]` de `var(--amostra-rainbow)` (gradient) para `var(--amostra)` (sólido) — badges do histórico agora exibem cor roxa
- **admin_user_data corrigido**: `background-color: var(--X)20` inválido trocado por `background-color: hex20` válido em todas as 4 ocorrências
- **Dashboard: novos cards "Últimas Pressões" e "Últimas Amostras"** na seção Atividade Recente, com badges coloridas seguindo o padrão COR_TIPO

## [2.6.1] - 2026-06-17

### Bugfixes

- **Admin não conseguia ativar/desativar aba "amostra"**: `"amostra"` faltando na validação (`admin.py:207`) e no dicionário padrão (`admin.py:213`) — corrigido
- **Histórico exibia UUID em vez do nome do usuário**: `buscar_perfis_usuarios()` usava `get_supabase_client()` (anon key com RLS restrito), impedia leitura dos nomes de outros usuários — alterado para `get_admin_client()` (bypass RLS)
- **Nome vazio no perfil**: fallback para exibir UUID quando `nome` é `None` ou string vazia
- **numero_amostra/lote agora apenas inteiros**: campo `numero_amostra` alterado de `NUMERIC` para `INTEGER` no banco; validação no backend trocada de `safe_float` para `safe_int`; frontend com `step="1"`

### Features

- **Sugestão de Lotes na aba Amostra**: campo "lote" agora exibe lista de sugestão (`<datalist>`) com lotes já registrados, ordenados do mais recente para o mais antigo — HTML5 nativo, sem JS
- **CHANGELOG.md**: criado a partir dos tópicos de atualização do README
- **cleanup_historico**: nova fixture de teste que remove registros do `historico_log` criados durante os testes, seguindo o padrão das demais fixtures de cleanup

## [2.6.0] — Rainbow + Intensity (v3.0)

### Novo Esquema de Cores Rainbow

Cada entidade possui cor própria seguindo o espectro visível ordenado por dependência:

| Entidade | Cor | Relação |
|----------|-----|---------|
| Cilindro (raiz) | 🔴 Vermelho `#e63946` | Início do espectro |
| Pressão (dep. Cilindro) | 🟠 Laranja `#f77f00` | Adjacente ao vermelho |
| Elemento (raiz) | 🟢 Verde `#2a9d8f` | Meio do espectro |
| Leitura (dep. Cilindro+Elemento) | 🔵 Azul `#457b9d` | Mistura RGB |
| Amostra (N:N Elementos) | 🌈 Rainbow | Arco-íris completo |

### Intensidade nos Gráficos (Chart.js)

Nova função `getColorByIntensity()` que mapeia valores por rank:
- **Valor baixo** → cor clara/brilhante
- **Valor alto** → cor escura/forte

### Cores de Sinalização Mantidas

Botões, alertas e mensagens de ação continuam usando cores padrão do Bootstrap.

### Centralização via COR_TIPO + ICON_TIPO

Ambos injetados pelo context processor em todos os templates. Trocar ícone/cor de qualquer entidade = alterar 1 linha em `constants.py`.

### Paletas de Intensidade para Gráficos

Cada entidade possui paleta de **5 níveis claro → escuro** para Chart.js.

### Fase 28: Rainbow + Intensity Color Scheme

- `COR_TIPO` atualizado com cores rainbow por dependência
- Botões de ação/aviso mantêm cores de sinalização padrão Bootstrap
- `PALETA_CILINDRO`, `PALETA_PRESSAO`, `PALETA_ELEMENTO`, `PALETA_LEITURA`, `PALETA_AMOSTRA` (5 níveis cada)
- Dashboards: Chart.js usa `getColorByIntensity()`
- CSS variables atualizadas
- `app.py` injeta paletas + COR_TIPO no context

## [2.5.0] — Nova Aba Amostra + Refactor Ícones

### Renomeação Amostra → Leitura

- A antiga aba "Amostras" foi renomeada para **"Leitura"**
- Blueprint `leitura.py`, template `leitura.html`, rota `/leitura`
- Migration SQL executada no Supabase

### Nova Aba Amostra (com N:N Elementos)

- Blueprint `amostra.py` com CRUD completo
- Associação **N:N** com Elementos via tabela `amostra_elemento`
- Número da amostra manual (real positivo) com placeholder = último + 1
- Lote, bulk delete, paginação, permissões de acesso
- Acesso do Assistente de Voz

### Refactor ICON_TIPO

- Centralização dos ícones Bootstrap em `utils/constants.py`
- Substituição de `bi-flask` (inexistente) por `bi-collection`
- Ícones injetados via context processor em todos os templates

### Fase 26: Número da Amostra Manual

- Migration v3: `numero_amostra INTEGER → NUMERIC`
- `schema.sql` + `DIAGRAM.MD` atualizados
- Blueprint: create/update lê `numero_amostra` do form, valida real positivo
- Template: create form `<input type="number">` com placeholder = último+1
- Template: edit modal `numero_amostra` editável

### Fase 27: Refatorar Cores (COR_TIPO)

- `COR_TIPO` completado com todos os campos (hex, var, bg, gradient)
- Entradas adicionadas: pressao, historico, perfil, dashboard
- CSS variable `--amostra: #6a1b9a` em base.html
- Context processor injeta `COR_TIPO` (app.py)

## [2.4.0] — Testes Playwright

### Testes Automatizados com Playwright

- 28+ testes end-to-end (Chromium)
- Cobertura: auth, dashboard, admin, cilindro, elemento, leitura, pressao, amostra
- Fixtures: login, cleanup, test user com permissões
- Conftest com Flask subprocess + wait_for_url

### Fase 24: Testes Playwright

- pytest-playwright + chromium instalados
- conftest.py (Flask subprocess, fixtures, test user)
- test_auth.py (7), test_dashboard.py (5), test_admin.py (2)
- test_cilindro.py (3), test_elemento.py (3), test_leitura.py (4), test_pressao.py (3)

## [2.3.0] — Segurança Avançada

- Cookie secure + Security headers
  - `SESSION_COOKIE_SECURE` (produção)
  - `SESSION_COOKIE_HTTPONLY` + `SAMESITE`
  - `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`

## [2.2.5] — Otimização Pressão

- Remove query duplicada de cilindro na aba Pressão
- Reutiliza query única para dropdown e map display
- Redução de 50% nas queries da página

## [2.2.4] — Otimização N+1 Admin

- 4 queries fixas independente do número de usuários
- Antes: 40 queries para 10 usuários
- Depois: 4 queries fixas (90% redução)
- Correção `pressao.py`: renomeado `list()` → `pressao_list()` (TypeError)

## [2.2.3] — Botão Voice Responsivo

- Ícone-only em mobile, texto completo em desktop
- `< lg`: mostra apenas ícone 🎤
- `>= lg`: mostra ícone + texto "Voice"

## [2.2.2] — Correções e Otimização

- `datetime.utcnow()` Deprecated: substituído por `datetime.now(timezone.utc)`
  - Resolve DeprecationWarning em Python 3.14+
- Cache otimizado: `habilitar_abas` cacheado na sessão
  - Evita query extra ao banco em cada verificação de permissão
  - Reduz queries por requisição de dashboard (4 → 3)
- Botão Voice responsivo

## [2.2.1] — Localização Português

- **Mensagem do Flask-Login**: "Por favor, faça login para acessar esta página."
- **Correção de Typo**: `app.py` — `get_habilitar_aba` → `get_habilitar_abas`

## [2.2.0] — Segurança e Melhorias

- **Rate Limiting Baseado em Sessão**: usa sessão Flask (funciona em production serverless)
  - 5 tentativas de login → bloqueio de 1 minuto
  - 3 tentativas de registro → bloqueio de 1 minuto
- **Verificação de Usuário Ativo**: usuários desativados (`ativo=False`) impedidos de fazer login
- **CORS Configurável**: nova variável `ALLOWED_ORIGINS`
- **Cache no Context Processor**: informações do usuário cacheadas na sessão
- **CASCADE Deletes**: foreign keys com `ON DELETE CASCADE` no Supabase
- **Tratamento de Erros Padronizado**: `formatar_erro_supabase()` em todos os blueprints

### Correções de Bugs

- Nome da função pressao renomeado para `list()` (consistência)
- Removidos imports locais duplicados em auth.py
- Lógica do register corrigida (bloco de bloqueio dentro do POST)
- Syntax error corrigido em cilindro.py (except fora de try)

## [2.1.0] — Sistema de Paleta de Cores

- Sistema completo de paleta de cores por KPI

## [2.0.2] — Correções de Consistência

- **Inconsistência pressao/temperatura**: nomenclatura em templates admin
  - `user.temperaturas` → `user.pressoes`
  - `habilitar_abas.temperatura` → `habilitar_abas.pressao`
- **Exportação**: correções em Excel, CSV, JSON
- **Delete usuário**: adiciona remoção de pressão e histórico
- **Documentação**: diretório `database/` com schema SQL, RLS, diagramas

## [2.0.1] — Log de Usuários

- Registro automático de eventos de usuários no histórico
  - Cadastro (tipo: perfil, ação: criado)
  - Alteração de role (tipo: perfil, ação: atualizado)
  - Ativação/desativação (tipo: perfil, ação: atualizado)
  - Alteração de permissões de abas (tipo: perfil, ação: atualizado)
- Visualizar senha: ícone de alternância (bi-eye / bi-eye-slash)

## [2.0.0] — Novo Padrão de Cores

- Novo padrão de cores `#0070b8`
- UI modernizada

## [1.9.3] — Pressão sem Obrigatoriedade

- Campos de registro na aba Pressão agora são opcionais
- Cilindro, Pressão, Data e Hora são campos facultativos

## [1.9.2] — Pressão com Temperatura

- Nova aba Pressão inclui campo de temperatura
- Pressão em bar (entre 0 e 300)
- Temperatura em °C (entre -50 e 100)
- Data default como data atual, hora editável (HH:MM)
- Vinculado a cilindro cadastrado, múltiplos registros por cilindro

## [1.9.1] — Renomear Temperatura para Pressão

- Aba "Temperatura" renomeada para "Pressão"
- Ícone `bi-activity`

## [1.9.0] — Nova Aba Pressão

- Registro de pressão dos cilindros (versão inicial)

## [1.8.0] — Expiração de Sessão

- Sessão expira após 10 minutos de inatividade
- Usuário redirecionado para login com mensagem explicativa

## [1.7.0] — Correções RLS

- Uso de cliente autenticado para operações no banco
- Mensagens de erro amigáveis (erros técnicos convertidos)

## [1.6.0] — Exportação e Controle de Abas

- **Exportação de Dados**: JSON, CSV, Excel (.xlsx), Markdown (.md)
- **Controle de Acesso por Abas**: admin pode habilitar/desabilitar abas por usuário
  - Abas controladas: Cilindros, Elementos, Amostras, Histórico

## [1.5.0] — Recursos de Segurança

- Proteção CSRF em todos os formulários
- Rate Limiting (5 tentativas/min login, 3 tentativas/min register)
- Validação de role e status contra valores permitidos
- Verificação de propriedade antes de delete (proteção IDOR)
- Session fixation protection
- Cliente autenticado para operações RLS

## [1.4.1] — Correções de UX

- Mensagens amigáveis
- Formatação de datas

## [1.4.0] — Refatoração para Blueprints

- Código modular com Flask Blueprints
