# LabGas Manager — Progresso

## Fase 23: Renomear Amostra → Leitura ✅
- [x] Migration SQL (ALTER TABLE + RENAME COLUMN) executada no Supabase
- [x] Blueprint `leitura.py` criado (api REST)
- [x] `amostra.html` deletado, `leitura.html` criado
- [x] helpers.py, constants.py, auth, admin atualizados
- [x] voice_assistant.js + voice_modal.html atualizados
- [x] database/DIAGRAM.MD atualizado

## Fase 24: Testes Playwright ✅
- [x] pytest-playwright + chromium instalados
- [x] conftest.py (Flask subprocess, fixtures, test user)
- [x] test_auth.py (7), test_dashboard.py (5), test_admin.py (2)
- [x] test_cilindro.py (3), test_elemento.py (3), test_leitura.py (4), test_pressao.py (3)
- [x] 25 passed, 2 skipped, 0 failed

## Fase 25: Nova Aba Amostra ✅
- [x] database/schema.sql + rls.sql + migration_amostra_v2.sql
- [x] Migration executada no Supabase ✅
- [x] Blueprint `amostra.py` (CRUD com N:N elementos)
- [x] Template `amostra.html` (form, tabela, modais, bulk delete)
- [x] `app.py` — register amostra_bp
- [x] `helpers.py` — ABAS_DISPONIVEIS com "amostra"
- [x] `constants.py` — COR_TIPO["amostra"] (purple), ICON_TIPO dict
- [x] `base.html` — sidebar link (dynamic icon via ICON_TIPO)
- [x] `admin.html` — coluna + toggle (desktop + mobile, dynamic icons)
- [x] `admin_user_data.html` — badge + stats + filter (dynamic icons)
- [x] `perfil.html` — stats card + permission toggle + cor roxa (dynamic icons)
- [x] `dashboard.html` — stat card (dynamic icons)
- [x] `historico.html` — filter + badge color (dynamic icon)
- [x] `voice_modal.html` — botão amostra adicionado
- [x] `database/DIAGRAM.MD` — tabelas amostra + amostra_elemento
- [x] `tests/conftest.py` — habilitar_abas + cleanup fixture
- [x] `tests/test_amostra.py` — 3 testes criados e passando ✅
- [x] `app.py` — context processor injects ICON_TIPO
- [x] Icon refactor: 11 templates migrated to `bi bi-{{ ICON_TIPO[...] }}`

## Fase 26: Número da Amostra Manual ✅
- [x] Migration v3: `numero_amostra INTEGER → NUMERIC`
- [x] `schema.sql` + `DIAGRAM.MD` atualizados (INTEGER → NUMERIC)
- [x] Blueprint: create lê `numero_amostra` do form, valida real positivo
- [x] Blueprint: update também lê/valida `numero_amostra` do form
- [x] Template: create form `<input type="number">` com placeholder = último+1
- [x] Template: edit modal `numero_amostra` editável
- [x] Migration executada no Supabase SQL Editor
- [x] Testes: 3/3 passando

## Fase 27: Refatorar Cores (COR_TIPO) ✅
- [x] `COR_TIPO` completado com todos os campos (hex, var, bg, gradient)
- [x] Entradas adicionadas: pressao, historico, perfil, dashboard
- [x] CSS variable `--amostra: #6a1b9a` em base.html
- [x] Context processor injeta `COR_TIPO` (app.py)
- [x] `admin_user_data.html` → cores via COR_TIPO
- [x] `perfil.html` → corrigido de #0070b8 genérico para cor específica de cada entidade
- [x] `historico.html` → mapeamento de badge substituído por `COR_TIPO[h.tipo]['var']`
- [x] `admin_user_data.html` → badge histórico usa mesma lógica
- [x] 3/3 testes passando

## Fase 28: Rainbow + Intensity Color Scheme ✅
- [x] `COR_TIPO` atualizado com cores rainbow por dependência:
  - Cilindro(root) → Vermelho, Pressão(dep.cilindro) → Laranja, Elemento(root) → Verde,
    Leitura(dep.cilindro+elemento) → Azul, Amostra(N:N elementos) → Violeta,
    Histórico → Cinza neutro, Perfil → Azul marca, Admin → Azul escuro
- [x] Botões de ação/aviso mantêm cores de sinalização padrão (Bootstrap: primary=danger=success=warning)
- [x] `PALETA_CILINDRO`, `PALETA_PRESSAO`, `PALETA_ELEMENTO`, `PALETA_LEITURA`, `PALETA_AMOSTRA` (5 níveis claro→escuro cada)
- [x] Dashboards: Chart.js usa `getColorByIntensity()` — valor baixo=claro, valor alto=escuro
- [x] CSS variables atualizadas (`--cilindro: #e63946`, `--pressao: #f77f00`, `--elemento: #2a9d8f`, `--leitura: #457b9d`, `--amostra: #6a1b9a`)
- [x] app.py injeta paletas + COR_TIPO no context
- [x] admin_user_data.html, perfil.html, historico.html com novas cores
- [x] 3/3 testes passando

## Bugs Encontrados 🐛

### 1. Admin não consegue ativar/desativar aba "amostra"
**Arquivo:** `frontend/blueprints/admin.py:207,213`
- `"amostra"` estava faltando na lista de validação (`if aba not in [...]`) — linha 207
- `"amostra"` estava faltando no dicionário padrão `habilitar_abas` — linha 213
- O toggle existe no template (`admin.html`), mas o servidor rejeitava com "Aba inválida"
- **Status:** ✅ Corrigido — adicionado `"amostra"` em ambas as listas

### 2. Teste `test_amostra_empty_state` não limpa dados
**Arquivo:** `frontend/tests/test_amostra.py:26`
- Não usava a fixture `cleanup_amostras`
- Se houvesse dados no banco, o estado vazio nunca era testado de fato
- **Status:** ✅ Corrigido — adicionada fixture `cleanup_amostras`

## Melhorias Recentes ✨

### 1. Sugestão de Lotes no campo "lote" da aba Amostra
**Status:** ✅ Implementado
- `frontend/blueprints/amostra.py` — query de lotes distintos ordenados por `created_at` descendente
- `frontend/templates/amostra.html` — `<datalist id="loteSuggestions">` com os lotes; inputs de criação e edição vinculados via `list="loteSuggestions"`
- Usa HTML5 nativo (`<datalist>`), sem dependência de JS

## Fase 35: Otimização de Consultas SQL ⚡ (parcial)
- [x] database: add missing indexes (schema.sql + migration_v5) ✅
- [x] amostra.py: batch insert elemento_ids (create + update) — 🔁 revertido em v2.6.8 (batch insert falhava, voltou para loop individual)
- [x] amostra.py: batch delete_multiple com in_() ✅
- [x] amostra.py: eliminar re-query de lotes (extrair do resultado principal) ✅
- [x] cilindro.py: batch delete_multiple com in_() ✅
- [x] elemento.py: batch delete_multiple com in_() ✅
- [x] leitura.py: batch delete_multiple com in_() ✅
- [x] pressao.py: batch delete_multiple com in_() ✅
- [x] historico.py: count + data em 1 query ✅

## Fase 36: Corrigir persistência de amostra_elemento 🐛 (v2.6.8)
- [x] amostra.py: batch insert não persistia → voltar para loop individual
- [x] cleanup_amostras: deletava registros de todos os usuários
- [x] test_create_amostra: agora seleciona elemento e verifica badge
- [x] 29/29 testes passando

## Fase 37: Modais dentro do tbody — HTML inválido 🐛 (v2.6.9)
- [x] amostra.html: modais edit + delete estavam dentro de `<tbody>` (filho direto inválido)
- [x] Movidos para depois de `</table>` em loop separado
- [x] Verificado: `registrar_historico("amostra", "atualizado")` presente no update

## Fase 38: Padronizar Paginação da Aba Amostra 📄 (v2.6.10)
- [x] amostra.py: adicionar `pages`, `end`, `max_pages` no backend
- [x] amostra.html: substituir paginação simples pelo padrão leitura:
  - Dropdown seletor de `per_page` (10/25/50/100)
  - `per_page` em todas as URLs de paginação
  - `Anterior`/`Próxima` com classe `disabled`
  - `...` para N > 10 páginas
  - Usar `end` e `max_pages` do backend

## Fase 34: Corrigir encoding no teste admin + padronizar warning elementos 🐛
- [x] test_admin.py: substituir locator com `ç` por `text=Admin` estável
- [x] amostra.html: substituir `alert()` por `div.alert-warning` inline (padrão flash)

## Fase 33: Formatar nomes do histórico (amostra) ✏️
- [x] amostra.py: `f"#{n} Lote {l}"` → `f"A/{n} L{l}"` (4 calls)

## Fase 32: Corrigir Pipeline de Testes (sessão suja + feedback CLI) 🧪
- [x] `page.context.clear_cookies()` no fixture login
- [x] Logs de progresso no fixture flask_app
- [x] testes passando sem timeouts em cascata

## Fase 31: Padronizar Botões de Ação (padrão amostra) 🎯
- [x] cilindro.html: horizontal, outline-primary/outline-danger, só ícone
- [x] elemento.html: idem
- [x] leitura.html: idem
- [x] pressao.html: idem

## Fase 30: Layout Column-Major nos Seletores de Elementos 📐
- [x] Substituir `.row` + `.col-*` por `.elemento-grid` (CSS multi-column)
- [x] Ordem vertical (coluna a coluna) em vez de horizontal (linha a linha)
- [x] CSS responsivo: 2 colunas mobile, 3 tablet, 4 desktop
- [x] Mantém gutter e responsividade

## Fase 29: Correções RLS e Client Auth 🔒

### Problemas Identificados

1. **`amostra.py`** — Non-admin writes usam `get_supabase_client()` (anon key sem JWT).
   `auth.uid()` fica NULL → RLS bloqueia INSERT/UPDATE/DELETE.
   **Fix:** Usar `get_authenticated_client()` (com JWT da session) para não-admin.

2. **`cilindro.py`, `elemento.py`, `leitura.py`, `pressao.py`** — Admin UPDATE usa `get_supabase_client()` sem `.eq("user_id", ...)`.
   Admin logado como user_id=A, registro pertence a user_id=B → RLS exige `A = B` → bloqueia.
   **Fix:** Admin UPDATE deve usar `get_admin_client()` (bypass RLS).

3. **`database/rls.sql`** — Falta política `FOR UPDATE` em `amostra_elemento`.
   **Fix:** Adicionar política análoga à de DELETE (subquery via `amostra.user_id`).

- [x] Fix amostra.py: import + usar `get_authenticated_client()` para não-admin
- [x] Fix cilindro.py: admin UPDATE usa `get_admin_client()`
- [x] Fix elemento.py: admin UPDATE usa `get_admin_client()`
- [x] Fix leitura.py: admin UPDATE usa `get_admin_client()`
- [x] Fix pressao.py: admin UPDATE usa `get_admin_client()`
- [x] Add FOR UPDATE policy for amostra_elemento em rls.sql
- [x] Testes: 28 passed, 1 failed (pre-existing), 2 skipped

## Sugestões Futuras 🚀

### Exportação
- [ ] Adicionar tabelas `amostra` e `amostra_elemento` nos exports (JSON/CSV/Excel/MD) em `admin.py`
- [ ] Adicionar coluna "Amostras" no cabeçalho da tabela de exportação Markdown

### Dashboard
- [ ] Gráfico de amostras por lote (bar chart)
- [ ] Últimas amostras registradas na seção de atividades recentes
- [ ] Card de total de elementos nas amostras
- [ ] Melhor adaptação e colorização do dashboard com as paletas rainbow

### Admin
- [ ] Filtro por aba "amostra" no painel admin
- [ ] Coluna "Amostras" na tabela de usuários com contagem

### Geral
- [ ] Badge `h.tipo == 'amostra'` com cor roxa no dashboard (últimas atividades)
- [ ] Teste de criação com elementos selecionados (test_create_amostra_with_elementos) ✅ (v2.6.8)
- [ ] Teste de bulk delete no Playwright

### Testes em Modais 🧪
- [x] Abrir modal de edição da amostra e verificar se checkboxes de elemento estão marcados (`checked`) ✅ (v2.6.11)
- [x] Abrir modal de edição do cilindro e verificar campos preenchidos ✅ (v2.6.11)
- [x] Abrir modal de edição do elemento e verificar campos preenchidos ✅ (v2.6.11)
- [x] Abrir modal de edição da leitura e verificar campos preenchidos ✅ (v2.6.11)
- [x] Abrir modal de edição da pressão e verificar campos preenchidos ✅ (v2.6.11)
- [x] Abrir modal de exclusão e confirmar exclusão ✅ (v2.6.11)
- [x] Abrir modal de exclusão em massa e confirmar ✅ (v2.6.11)

## Fase 39: Testes de Modais (v2.6.11) 🧪
- [x] conftest.py: adicionar `--run-modais` (pytest_addoption) e skip automático via `pytest_collection_modifyitems`
- [x] test_amostra.py: 6 testes modais (edit preenche, edit valida JS, edit submit, delete, cancel, bulk)
- [x] test_cilindro.py: 3 testes modais (edit preenche, delete, bulk)
- [x] test_elemento.py: 3 testes modais (edit preenche, delete, bulk)
- [x] test_leitura.py: 3 testes modais (edit preenche, delete, bulk)
- [x] test_pressao.py: 3 testes modais (edit preenche, delete, bulk)
- [x] Total: 18 testes modais, executados com `pytest --run-modais`

## Fase 40: Bugfix Leitura (v2.6.12) 🐛
- [x] `formatar_tempo_chama(1 arg)` → TypeError (assinatura espera 3 args) — corrigir para aceitar string `HH:MM:SS` ✅
- [x] `test_create_leitura`: falso positivo (não seleciona cilindro nem elemento) — refatorado cria dados frescos e preenche todos os campos ✅
- [x] `test_create_leitura`: verifica persistência com assert no banco (`quantidade == 3`) ✅

## Fase 41: Segurança dos Cleanups (v2.6.13) 🛡️
- [x] Remover `.neq("id", 0)` de todos os cleanups — não filtra nada e cria falsa sensação de segurança ✅
- [x] Reforçar scoping do `amostra_elemento` cleanup: SELECT de amostras já escopada por `user_id`; filtro `if a.get("id")` para IDs válidos ✅
- [x] Garantir que nenhum cleanup rode com `test_user_id = None` — guard `if test_user_id` em todos os 6 cleanups já existente ✅

## Fase 42: Autocomplete de Horário (v2.6.14) ⌨️
- [x] JS `autoFormatTime()`: digitar só números no campo hora insere `:` automaticamente ✅
  - `tempo_chama` (leitura.html): HH:MM:SS com 6 dígitos
  - `hora` (pressao.html): HH:MM com 4 dígitos

## Fase 43: Padronizar Header da Tabela de Histórico 🎨 (v2.6.15)
- [x] historico.html: remover gradiente escuro do card-header, usar `bg-light` como as outras abas ✅
- [x] Separar filtros em card próprio (igual cilindro.html), tabela em card separado ✅

## Fase 44: Seed com Senha no .env.local 🔐
- [x] `database/seed.sql`: remover manipulação de `auth.users` (senha não fica no SQL versionado) ✅
  - Agora só faz upsert do `perfil` — seguro para commit
- [x] `scripts/seed.py`: novo script Python que lê `TEST_PASSWORD` do `.env.local` e cria/reseta:
  - `auth.users` via Admin API (update_user_by_id se existir, create_user se não)
  - `perfil` via upsert (admin + todas as abas)
- [x] `frontend/.env.local`: adicionado `TEST_EMAIL` e `TEST_PASSWORD` ✅
- [x] `frontend/.env.example`: adicionado `TEST_EMAIL` e `TEST_PASSWORD` (comentados) ✅

## Fase 44: Seed SQL com Usuário Teste Admin 🗄️ (v2.6.15)
- [x] database/seed.sql: script executável que cria/reseta `teste@labgas.com` / `123456` com `role=admin` ✅
  - `auth.users`: cria com `crypt('123456', gen_salt('bf'))` se não existir; se existir, só reseta a senha
  - `auth.identities`: criada apenas para usuários novos (exigência do Supabase Auth)
  - `perfil`: upsert com `ON CONFLICT DO UPDATE` — sempre sobrescreve nome, role e abas habilitadas
  - Idempotente: pode rodar quantas vezes quiser sem erro

## Fase 45: Correção de Rate Limiting e Otimização de Consultas ⚡ (v2.6.16)

### Problema Identificado
Usuários relatavam timeout/rate limit ao fazer múltiplos registros consecutivos. Causas:
1. **Flask-Limiter default 50 req/hora** — muito restritivo, sem variável `RATE_LIMIT` configurada
2. **N+1 no amostra_elemento** — loop individual em vez de batch insert
3. **Consultas redundantes** — verificações de existência duplicadas antes de INSERT/UPDATE
4. **Múltiplas queries no dashboard** — 6+ chamadas independentes ao Supabase
5. **Sem cache** — toda renderização de página faz queries frescas ao banco

### Soluções Implementadas
- [x] Aumentar default limits do Flask-Limiter (200/dia → 500/dia, 50/hora → 200/hora)
- [x] Adicionar `RATE_LIMIT` no `.env.example` como variável documentada
- [x] Eliminar verificações redundantes de existência antes de INSERT nos blueprints (leitura, pressao)
- [x] Otimizar updates: buscar nomes antes de atualizar em vez de re-query pós-update (leitura.py)
- [x] amostra_elemento: batch insert com `client.table("amostra_elemento").insert(lista)` em vez de loop
- [x] Adicionar `flask-caching` ao `requirements.txt` e configurar cache nas listagens
- [x] Cache de 5 minutos nas queries de listagem (dashboard, cilindro, elemento, leitura, pressao, amostra)
- [x] Otimizar dashboard: combinar queries de contagem, cachear resultados
- [x] Registrar `AVISO` no .env.example sobre configuração de `RATE_LIMIT`

## Fase 46: Análise de Segurança 🔒 (Relatório — Nenhuma Implementação)

### Contexto
Revisão completa de segurança baseada na `ANALISE_SEGURANCA.MD` (v1.4.1) versus estado atual (v2.6.17).
Itens já corrigidos desde o relatório original foram marcados como ✅. Os pendentes seguem listados abaixo com severidade, localização e recomendação técnica.

---

### 🔴 CRÍTICOS

#### 1. IDOR em DELETE via get_admin_client() — ⚠️ PARCIALMENTE CORRIGIDO (v2.6.17)
**Localização:** `cilindro.py:191`, `elemento.py:120`, `amostra.py:190`, `leitura.py:179`, `pressao.py:192`
**Problema original (v1.4.1):** Operações DELETE usavam `get_admin_client()` (service_role, bypass RLS) sem verificar ownership. Qualquer admin podia deletar dados de terceiros via admin panel ou via POST direto.

**O que foi corrigido na v2.6.17:**
- `admin.py:delete_user()` — agora restrito a `is_dev()` (admin não pode mais deletar contas)
- Todos os 5 blueprints de CRUD já fazem SELECT de `user_id` e comparam com `get_user_id()` **antes** do DELETE (verificação em nível de aplicação)
- `cilindro.py`, `elemento.py`, `leitura.py`: ownership check **incondicional** (válido para todos os roles)
- `amostra.py`, `pressao.py`: ownership check **condicional** (`if not dev and ...`) — dev pode deletar qualquer registro (by design)
- CRUD Create/Update agora usam `get_authenticated_client()` para não-dev (respeita RLS)

**Risco remanescente:** O DELETE em si ainda usa `get_admin_client()` (service_role), portanto a única barreira entre um bug de lógica no ownership check e um vazamento de dados é o código Python. Nenhuma defesa em profundidade via RLS.
**Recomendação adicional:** Trocar DELETE para `get_authenticated_client()` para não-dev, eliminando a dependência de service_role nesses endpoints.

---

### 🟠 ALTOS

#### 2. Sem HSTS / CSP / Security Headers em Produção — ✅ CORRIGIDO (v2.6.18)
**Localização:** `app.py:139-141`
**O que foi corrigido:** Adicionados `Strict-Transport-Security`, `Content-Security-Policy` e `Permissions-Policy` no `after_request`. CSP configurado com `default-src 'self'` e exceções para CDNs (jsdelivr, cdnjs.cloudflare).

#### 3. Flask Debug Mode Acessível em Produção — ✅ CORRIGIDO (v2.6.18)
**Localização:** `app.py:517-518`
**O que foi corrigido:** Adicionado `if is_production: debug = False` antes do `app.run()`, utilizando a mesma flag `is_production` já definida em `app.py:29`.

#### 4. CORS Permissivo Demais — ✅ CORRIGIDO (v2.6.18)
**Localização:** `app.py:126-128`
**O que foi corrigido:** Fallback `*` removido. Se `ALLOWED_ORIGINS` não definido, defaults são `["http://localhost:5000", "http://127.0.0.1:5000"]`. Apenas origens na lista explícita recebem `Access-Control-Allow-Origin`.

---

### 🟡 MÉDIOS

#### 5. Validação de Role Ausente — ✅ CORRIGIDO (v2.6.17)
**Localização:** `admin.py:141`
```python
if role not in ("admin", "usuario"): flash("Função inválida.")
```
**O que foi corrigido:** Whitelist rígida que impede atribuição de `'dev'` via web. Admin nunca pode promover ninguém a dev. A rota ainda exige `is_admin()`.

#### 6. Validação de Status Ausente — ✅ CORRIGIDO (pre-existente)
**Localização:** `cilindro.py:41,114`
```python
if status not in CILINDRO_STATUS: status = "ativo"
```
**O que foi corrigido:** Validação contra `utils.constants.CILINDRO_STATUS` já existia antes da análise. O relatório original não detectou esta proteção.

#### 7. Perfil UPDATE Policy Insegura — ✅ CORRIGIDO (v2.6.18)
**Localização:** `database/rls.sql:79`
**O que foi corrigido:** `FOR UPDATE USING (true) WITH CHECK (true)` → `FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id)`. Admin/Dev continuam usando `get_admin_client()` (service_role, bypass RLS) para gerenciar outros usuários.

#### 8. JWT Validation usa app.secret_key — ✅ CORRIGIDO (v2.6.18)
**Localização:** `admin.py:15-35`
**O que foi corrigido:** `validate_admin_token()` agora usa `supabase.auth.get_user(token)` com o token do Supabase Auth (`session["supabase_token"]`) em vez de decodificar localmente com `app.secret_key`. Import `jwt` removido de admin.py.

#### 9. Auth Endpoints sem Rate Limit Específico — ✅ CORRIGIDO (v2.6.18)
**Localização:** `auth.py:44,142`
**O que foi corrigido:** Adicionado `@limiter.limit("5 per minute", methods=["POST"])` nas rotas `/login` e `/register`. Apenas POST é limitado; GET (renderizar formulário) não é afetado.

---

### 🟢 BAIXOS

#### 10. cache_utils.py não Integrado — ✅ CORRIGIDO (Fase 45, pré-existente)
**Localização:** `utils/cache_utils.py`, `blueprints/*.py`
**O que foi corrigido:** `invalidate_user_caches(user_id)` já é chamado após cada CREATE/UPDATE/DELETE nos 5 blueprints de domínio (cilindro, elemento, leitura, pressao, amostra) desde a Fase 45. A auditoria original (Fase 46) não detectou esta integração. `get_cached_or_fetch()` para leitura ainda não é utilizado — baixo risco.

#### 11. Session Cached User Info Pode Ficar Stale — ✅ CORRIGIDO (v2.6.18)
**Localização:** `app.py:151-173`
**O que foi corrigido:** `session.pop("cached_user_info", None)` e `invalidate_user_caches(target_user_id)` adicionados em `set_role()` e `toggle_user()` no admin.py. Quando um admin altera a própria role, o cache é limpo imediatamente. Para role de terceiros, o cache do flask-caching é invalidado.

#### 12. Logging Pode Expor Dados Sensíveis — ✅ CORRIGIDO (v2.6.18)
**Localização:** `app.py:61-62`
**O que foi corrigido:** `logging.basicConfig(level=logging.INFO)` → `level=logging.WARNING if is_production else logging.INFO`. Em produção, apenas WARNING+ são logados. Revisão manual confirmou que nenhum logger registra tokens JWT, emails ou senhas.

#### 13. Vercel sem Security Headers Configurados — ✅ CORRIGIDO (v2.6.18)
**Localização:** `vercel.json`
**O que foi corrigido:** Bloco `"headers"` adicionado com `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Strict-Transport-Security` e `Permissions-Policy`. Defense-in-depth: Flask já define os mesmos headers em `after_request`.

---

### ✅ Itens Já Corrigidos desde a v1.4.1

| # | Item | Severidade | Status |
|---|------|------------|--------|
| 1 | CSRF Protection (`app.py:35`) | CRITICAL | ✅ CORRIGIDO |
| 2 | Secret Key Fallback removido (`app.py:24-26`) | HIGH | ✅ CORRIGIDO |
| 3 | Rate Limiting implementado (`app.py:37-42`) | MEDIUM | ✅ CORRIGIDO |
| 4 | Session Security Headers (Secure, HttpOnly, SameSite) | MEDIUM | ✅ CORRIGIDO |
| 5 | Security Headers (X-Frame-Options, X-Content-Type-Options, Referrer-Policy) | MEDIUM | ✅ CORRIGIDO |
| 6 | Mensagens de erro amigáveis | MEDIUM | ✅ CORRIGIDO (v1.4.1) |
| 7 | Safe int/float validators | LOW | ✅ CORRIGIDO (v1.4.1) |
| 8 | Validação de Role — whitelist `("admin", "usuario")` (`admin.py:141`) | MEDIUM | ✅ CORRIGIDO (v2.6.17) |
| 9 | Validação de Status — `CILINDRO_STATUS` (`cilindro.py:41,114`) | MEDIUM | ✅ CORRIGIDO (pre-existente) |
| 10 | IDOR DELETE — ownership checks + admin panel dev-only + DELETE usa authenticated client p/ não-dev | CRITICAL | ✅ CORRIGIDO (v2.6.18) |
| 11 | HSTS/CSP/Security Headers (`app.py after_request`) | HIGH | ✅ CORRIGIDO (v2.6.18) |
| 12 | Debug Mode (`app.py run`) | HIGH | ✅ CORRIGIDO (v2.6.18) |
| 13 | CORS Permissivo (`app.py after_request`) | HIGH | ✅ CORRIGIDO (v2.6.18) |
| 14 | Perfil RLS Policy (`database/rls.sql`) | MEDIUM | ✅ CORRIGIDO (v2.6.18) |
| 15 | Auth Rate Limit (`auth.py login/register`) | MEDIUM | ✅ CORRIGIDO (v2.6.18) |
| 16 | JWT Validation (`admin.py validate_admin_token`) | MEDIUM | ✅ CORRIGIDO (v2.6.18) |
| 17 | Session Cached User Info Stale (`admin.py set_role/toggle_user`) | LOW | ✅ CORRIGIDO (v2.6.18) |
| 18 | cache_utils integrado (`invalidate_user_caches` nos 5 blueprints) | LOW | ✅ CORRIGIDO (Fase 45) |
| 19 | Logging (`app.py logging.basicConfig`) | LOW | ✅ CORRIGIDO (v2.6.18) |
| 20 | Vercel Security Headers (`vercel.json`) | LOW | ✅ CORRIGIDO (v2.6.18) |

---

### 📊 Resumo

| Severidade | Pendentes | Corrigidos |
|------------|-----------|------------|
| 🔴 CRITICAL | 0 | 2 |
| 🟠 HIGH | 0 | 4 |
| 🟡 MEDIUM | 0 | 9 |
| 🟢 LOW | 0 | 5 |
| **Total** | **0** | **20** |

### 🎯 Fase 46 Concluída — Hotfix CSP (v2.6.19)

Todos os 13 itens de segurança identificados na análise foram corrigidos entre as fases 46-48 (v2.6.17 + v2.6.18). Nenhum item pendente.

#### Hotfix: CSP font-src bloqueava Bootstrap Icons no Vercel
- **Problema:** `font-src 'self' https://cdnjs.cloudflare.com` impedia carregamento das fontes dos ícones servidas de `cdn.jsdelivr.net`
- **Correção:** `font-src 'self' https://cdn.jsdelivr.net` (v2.6.19, `app.py:134`)
- Limpeza: `style-src` também removido o `cdnjs.cloudflare.com` não utilizado

---

## Fase 47: Hierarquia de Roles — Dev (supremo) vs Admin (restrito) ✅ (v2.6.17)

### Contexto
Atualmente a role `admin` tem acesso total via `get_admin_client()` (service_role, bypass RLS): deleta dados de qualquer usuário, gerencia contas, promove outros admins. Isso concentra **poder excessivo** em uma única role — se um admin for comprometido, todo o sistema é comprometido.

A solução é quebrar em 3 roles com responsabilidades distintas:

| Role | Acesso a dados próprios | Acesso a dados alheios | Gerenciar usuários | Export total | Deletar usuários |
|------|------------------------|----------------------|-------------------|-------------|------------------|
| `dev` | ✅ | ✅ (supremo) | ✅ | ✅ | ✅ (qualquer um) |
| `admin` | ✅ | ❌ (só dele) | ✅ (nunca p/ dev) | ✅ | ❌ (só a própria conta) |
| `usuario` | ✅ | ❌ | ❌ | ❌ | ❌ (só a própria conta) |

**Princípio:** `admin` gerencia usuários (promove/rebaixa entre admin/usuario) e exporta dados totais, mas no CRUD de dados (cilindro, elemento, leitura, pressao, amostra) só enxerga os próprios — como `usuario`. `dev` substitui o poder absoluto que `admin` tinha antes, incluindo deletar qualquer dado ou conta.

---

### 1. Seed SQL — Novo role `dev`

**Arquivo:** `database/seed.sql`

**Mudança:** Trocar `role = 'admin'` por `role = 'dev'`:
```sql
INSERT INTO perfil (id, role, ativo, nome, email, habilitar_abas)
VALUES (v_user_id, 'dev', true, 'Usuário Teste', 'teste@labgas.com', ...)
ON CONFLICT (id) DO UPDATE SET role = 'dev', ...;
```

Também adicionar no comentário/README que:
- `dev` é a role de desenvolvimento/super-admin (criada via seed, não via UI)
- `admin` pode gerenciar usuários (promover/rebaixar para admin/usuario) e exportar dados totais, mas no CRUD de dados só enxerga os próprios registros (como `usuario`)

---

### 2. Backend — Novas funções de role check

**Arquivo:** `frontend/blueprints/helpers.py`

**Adicionar:**
```python
ROLES_HIERARCHY = {"dev": 3, "admin": 2, "usuario": 1}

def get_user_role():
    cached = session.get('cached_user_info', {})
    return cached.get('user_role', 'usuario')

def is_dev():
    return get_user_role() == 'dev'

def is_admin():
    role = get_user_role()
    return role == 'admin' or role == 'dev'

def role_at_least(min_role):
    return ROLES_HIERARCHY.get(get_user_role(), 0) >= ROLES_HIERARCHY.get(min_role, 0)
```

**Importante:** `is_admin()` continua retornando `True` para `dev` também (para não quebrar `pode_acessar_aba` e o template context). A distinção real entre `dev` e `admin` será feita com `is_dev()` nas rotas que exigem poder supremo.

---

### 3. Backend — `cached_user_info` guarda role literal

**Arquivo:** `frontend/app.py` (context_processor, ~linha 160)

**Mudança:** Em vez de `'is_admin': perfil.get('role') == 'admin'`, guardar a role literal:
```python
user_role = perfil.get('role', 'usuario')
session['cached_user_info'] = {
    'user_role': user_role,
    'user_name': perfil.get('nome', ''),
    'is_admin': user_role in ('admin', 'dev'),
    'is_dev': user_role == 'dev',
    'habilitar_abas': ...
}
```

---

### 4. Backend — Escolha do cliente Supabase nos CRUDs

**Arquivo:** Todos os blueprints de domínio (cilindro, elemento, leitura, pressao, amostra)

**Regra atual:**
```python
client = get_admin_client() if admin else get_authenticated_client()
```

**Nova regra:**
```python
client = get_admin_client() if is_dev() else get_authenticated_client()
```

Apenas `dev` usa service_role (bypass RLS). `admin` e `usuario` usam `get_authenticated_client()` que respeita RLS — só acessam dados próprios.

**Efeito colateral:** As verificações de duplicidade (SELECT antes de INSERT/UPDATE) que hoje usam `get_admin_client()` para admin ver globalmente também precisam mudar — `admin` só verifica duplicidade dentro dos próprios dados, `dev` verifica globalmente.

---

### 5. Backend — Rotas do admin panel

**Arquivo:** `frontend/blueprints/admin.py`

**Regra geral:**
- Rotas que **gerenciam usuários** (panel, toggle_user, set_role, update_habilitar_abas, user_data) e **export_data**: guard `if not is_admin()` — admin e dev acessam.
- Rota **delete_user**: guard `if not is_dev()` — só dev pode deletar contas.

**Mudanças em `set_role()`:**
- Validar que a role alvo só pode ser `'admin'` ou `'usuario'` (nunca `'dev'`)
- Se admin (não-dev) estiver alterando a própria role para `'usuario'`: exibir `flash` de warning (`"Você está se rebaixando para usuário. Esta ação não pode ser desfeita por você."`)
- Se admin (não-dev) estiver promovendo um `usuario` para `admin` ou rebaixando outro `admin` para `usuario`: exibir `flash` de warning (`"Atenção: você alterou a role de {nome} para {role}."`)
- Se dev estiver alterando roles: sem warning (silencioso)

```python
ROLES_VALIDAS = ("admin", "usuario")
if role not in ROLES_VALIDAS:
    flash("Role inválida.", "danger")
    return redirect(...)

if role == "admin" and target_user_id == user_id and not is_dev():
    flash("Você se promoveu para admin.", "warning")
elif not is_dev():
    flash(f"Atenção: você alterou a role de {target_name} para {role}.", "warning")
```

**Mudanças em `delete_user()`:**
- Guard `if not is_dev()` — só dev pode deletar contas
- Adicionar proteção extra: não permitir deletar outro `dev`:
```python
target_perfil = client.table("perfil").select("role").eq("id", target_user_id).execute()
if target_perfil.data and target_perfil.data[0].get("role") == "dev":
    flash("Não é possível deletar outro desenvolvedor.", "danger")
    return redirect(...)
```

**Mudanças em `toggle_user()`:**
- Guard permanece `if not is_admin()` — admin e dev podem ativar/desativar
- Se admin (não-dev) estiver desativando outro admin: exibir `flash` de warning

**Mudanças em `export_data()`:**
- Guard permanece `if not is_admin()` — admin e dev podem exportar dados totais

---

### 6. Backend — API endpoints de busca

**Arquivo:** `frontend/app.py` (rotas `/api/buscar-codigo`, `/api/buscar-elemento`)

**Regra atual:** `if admin:` busca global (sem filtro user_id)
**Nova regra:** `if is_dev():` busca global

---

### 7. Backend — `validate_admin_token()` permanece

**Arquivo:** `frontend/blueprints/admin.py`

A função `validate_admin_token()` continua válida — ela valida JWT + user_id match. Apenas os guards das rotas mudam (de `is_admin()` para `is_dev()`).

---

### 8. Seed SQL corrigido

O seed atual cria `role = 'admin'`. Após a implementação, deve criar `role = 'dev'`:

```sql
-- database/seed.sql (versão atualizada)
INSERT INTO perfil (id, role, ativo, nome, email, habilitar_abas)
VALUES (v_user_id, 'dev', true, 'Usuário Teste', 'teste@labgas.com', ...)
ON CONFLICT (id) DO UPDATE SET role = 'dev', ...;
```

---

### 9. Resumo de arquivos que serão alterados (quando implementar)

| Arquivo | Tipo de mudança |
|---------|----------------|
| `database/seed.sql` | role `admin` → `dev` |
| `frontend/blueprints/helpers.py` | + `is_dev()`, + `role_at_least()`, refatorar `is_admin()` usa hierarchy |
| `frontend/app.py` | `cached_user_info` guarda `user_role` literal + `is_dev` |
| `frontend/blueprints/admin.py` | `delete_user`: guard `is_admin()` → `is_dev()`. Demais rotas: mantêm `is_admin()` (admins continuam acessando). `set_role()`: valida whitelist + warnings |
| `frontend/blueprints/cilindro.py` | client choice: `is_admin()` → `is_dev()` |
| `frontend/blueprints/elemento.py` | client choice: `is_admin()` → `is_dev()` |
| `frontend/blueprints/leitura.py` | client choice: `is_admin()` → `is_dev()` |
| `frontend/blueprints/pressao.py` | client choice: `is_admin()` → `is_dev()` |
| `frontend/blueprints/amostra.py` | client choice: `is_admin()` → `is_dev()` |
| `frontend/app.py` (APIs) | `is_admin()` → `is_dev()` nas buscas globais |

**Total estimado: ~10 arquivos, ~50 linhas alteradas**

---

### 10. Observações Importantes

1. **Não mexer em RLS:** As policies atuais (`auth.uid() = user_id`) continuam protegendo os dados. Dev usa service_role (bypass), admin e usuario respeitam RLS. Nenhuma migration SQL de RLS é necessária.

2. **`pode_acessar_aba`:** Continua funcionando — `is_admin()` retorna True para dev e admin, ambos veem todas as abas. A diferença é que admin vê as abas mas só com dados próprios no CRUD.

3. **Template context:** `is_admin` no template continua True para dev e admin. Ambos veem o link "Admin" no sidebar. A diferenciação visual entre dev e admin nos templates é opcional e pode vir depois.

4. **Ordem de implementação:** Esta fase (Fase 47) deve ser implementada **antes** da correção de IDOR (Fase 46, item 1), porque a correção de IDOR depende da hierarquia de roles — dev pode deletar de outros, admin não. Implementar a hierarquia primeiro evita refatorar duas vezes.

5. **Warnings de ação:** Toda vez que um admin (não-dev) alterar a role de alguém (incluindo a si mesmo), exibir `flash("...", "warning")` para deixar explícito no histórico visual que a ação foi tomada. Dev não recebe warnings — as ações de dev são silenciosas (presume-se que dev sabe o que está fazendo).

6. **Admin pode se rebaixar:** Se um admin alterar a própria role para `'usuario'`, perde acesso ao admin panel imediatamente (o guard `is_admin()` para de passar). A mensagem de warning deve deixar claro que é irreversível pelo próprio usuário.

---

## Fase 48: Remover Senha Fraca do .env.example e Validar no seed.py 🔒 (v2.6.17) ✅

### Problema
A senha `123456` estava hardcoded como default no `scripts/seed.py` e referenciada no `frontend/.env.example`. Qualquer desenvolvedor que clonasse o repositório e criasse um `.env.local` baseado no exemplo automaticamente usaria uma senha fraca e previsível.

### Mudanças Implementadas
- [x] `frontend/.env.example`: `# TEST_PASSWORD=123456` → `# TEST_PASSWORD=` (sem valor, sem sugestão de senha fraca)
- [x] `scripts/seed.py`: default `"123456"` removido — se `TEST_PASSWORD` não estiver no `.env.local`, o script exibe erro e aborta
- [x] `scripts/seed.py`: role do perfil alterada de `'admin'` para `'dev'` (consistência com Fase 47)

---

## Bugfix: Footer Sumindo (Timezone Mismatch) 🐛 (v2.6.21)

### Problema
`auth.py:82` armazenava `last_activity` com `datetime.utcnow().isoformat()` (naive, sem timezone), mas `inject_user_info` calculava `remaining` com `datetime.now(timezone.utc)` (aware). A subtração naive − aware levantava `TypeError`, engolido por `except (ValueError, TypeError): pass`, deixando `remaining = 0` — o JS então escondia o footer imediatamente.

`check_inactivity()` sofria do mesmo bug, mas "se curava" no primeiro request (catch → reescreve com `now.isoformat()` que inclui `+00:00`). Já `inject_user_info` só engolia o erro sem se curar.

### Correção (3 arquivos)
- [x] `app.py` (`inject_user_info`): tornar `last_dt` aware com `replace(tzinfo=timezone.utc)` se naive
- [x] `auth.py`: armazenar `last_activity` já aware (`datetime.now(timezone.utc)`) — preventivo
- [x] `test_session_footer.py`: locator mais específico (`> div:first-child`) + `wait_for` explícito

## v2.6.22: Footer Global Fixed sobre o Sidebar 🦶

### Mudanças
- [x] `base.html`: footer movido para fora de `.content-wrapper` — vira filho direto do `<body>`
- [x] `base.html` CSS: `position: fixed; bottom: 0; left: 0; width: 100%; z-index: 1050`
- [x] `base.html` CSS: `.content-wrapper` perde `display:flex`, ganha `padding-bottom: 36px`
- [x] `base.html` JS: timer usa `sessionStorage` — persiste entre páginas sem reiniciar
- [x] `base.html` JS: `sessionStorage` limpo no logout e ao expirar

### Comportamento
| Situação | Timer |
|----------|-------|
| Login | Inicia com `data-seconds` do servidor (600) |
| Navegação entre páginas | Continua do `sessionStorage` |
| F5 / reload | Continua do `sessionStorage` (desconta tempo perdido) |
| Logout | `sessionStorage` limpo |
| Sessão expira | Footer some, `sessionStorage` limpo |

## Fase 49: Footer de Sessão com Timer Regressivo 🔄

### Contexto
Não há indicador visual de sessão para o usuário — ele só descobre que a sessão expirou quando tenta uma ação e é redirecionado ao login. Um footer com nome do usuário e tempo restante antes do timeout de inatividade (10 min) melhora a experiência e evita perda de trabalho.

### O que foi implementado (v2.6.20)

#### Backend
- **`app.py` (`inject_user_info`)**: `session_remaining_seconds` computado a partir de `last_activity` e `INACTIVITY_TIMEOUT` — injetado em todos os templates

#### Frontend
- **`base.html`**: Footer fixo no final da página com:
  - Nome do usuário + `bi-person-circle` (alinhado à esquerda)
  - Timer regressivo `MM:SS` + `bi-clock-history` (alinhado à direita)
  - CSS responsivo (flexível em mobile e desktop)
  - JS countdown com `setInterval(1000)` — cor muda para 🟡 warning (<60s) e 🔴 danger (<30s)
  - Some (`display: none`) quando expira (0:00)
- **Layout**: `.page-content` e footer envolvidos em flex container `min-height: calc(100vh - 60px)` para footer sempre no final da viewport

#### Testes
- **`test_session_footer.py`**: 4 testes (footer visível, nome do usuário, timer regressivo, cores de warning/danger)
- **`pytest.ini`**: marcador `footer` adicionado — `pytest -m footer` executa só os testes de footer, `pytest -m "not footer"` pula footer, default executa todos
