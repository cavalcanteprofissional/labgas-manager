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

## v2.6.23 — Dashboard pressao_chart TypeError 🐛

### 3. Dashboard: TypeError com builtin_function_or_method em serie.values
**Arquivos:** `app.py:295-302`, `templates/dashboard.html:260`
- Quando `pressao_chart` tem entries sem a chave `"values"`, Jinja2 cai de `serie['values']` (KeyError) para `getattr(serie, 'values')`, retornando `dict.values` (um método nativo) em vez de uma lista — `tojson` falha com `TypeError: Object of type builtin_function_or_method is not JSON serializable`
- **Causa raiz:** dado corrompido no banco ou construção inconsistente de `pressao_chart[cod]`
- **Correção:** sanitização defensiva pós-construção + template usa `serie.get('values', [])` que delega a `dict.get()` no lugar de acesso direto por atributo
- **Status:** ✅ Corrigido (v2.6.23)

### 4. Dashboard: TypeError com Undefined em pressao_chart.values()|first|attr('labels')
**Arquivos:** `app.py:342`, `templates/dashboard.html:272`
- `pressao_chart.values()|first|attr('labels')` no template depende de Jinja2 resolver `dict.values` como método (via `getattr`) em vez de chave `"values"` (via `__getitem__`). Se `pressao_chart` contém uma chave cujo codigo do cilindro coincide literalmente com o string `"values"`, `pressao_chart["values"]` retorna o entry do cilindro em vez do método nativo, e `|first` retorna `Undefined` — `tojson` falha com `TypeError: Object of type Undefined is not JSON serializable`
- **Correção:** extrair `pressao_chart_labels` no backend (dict key `labels` do primeiro entry), passar como variável flat — elimina a cadeia frágil de filtros Jinja2
- **Status:** ✅ Corrigido (v2.6.23)

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

## Fase 50: Refatoração do Dashboard 📊 ✅

### Problemas do Dashboard Atual

| # | Problema | Localização |
|---|----------|-------------|
| 1 | **Cards são contadores crus** — Cilindros, Elementos, Leituras, Amostras não contam história | `app.py:231-246` |
| 2 | **"Eficiência" é misnamed** — na verdade conta `quantidade` de leituras por par (cilindro, elemento), não eficiência real (consumo_lpm × tempo_chama / gas_disponivel) | `app.py:310-325` | 
| 3 | **Atividade Recente redundante** — "Últimos Cilindros" e "Últimos Elementos" só duplicam CRUD; 5 cards ocupam 2 linhas | `dashboard.html:167-313` |
| 4 | **Elemento mostra `consumo_lpm` duplicado** — linha 214 e 216 do template | `dashboard.html:214,216` |
| 5 | **Pressão não integrada** — sem gráfico de tendência (curva de decaimento por cilindro) | ausente |
| 6 | **Amostra não integrada** — sem distribuição por lote, sem correlação com leituras | `app.py:240-246` |
| 7 | **Sem série temporal** — nada mostra evolução ao longo do tempo (leituras/mês, pressão/dia) | todo o `app.py:224-357` |
| 8 | **Nenhum KPI de negócio** — custo médio por leitura, gás restante, vida útil estimada | ausente |
| 9 | **3 queries separadas no backend** — cilindro, elementos, leituras são independentes, sem JOIN | `app.py:231-233` |

### Schema e Correlações Possíveis

```
┌──────────┐     ┌──────────┐     ┌───────────┐
│ cilindro │────→│ leitura  │←────│ elemento  │
│  - gas_kg│     │ - tempo  │     │consumo_lpm│
│litros_eq │     │quantidade│     └───────────┘
│  - custo │     │ - data   │         
│  -status │     └──────────┘         
└────┬─────┘     ┌──────────┐         
     └──────────→│ pressao  │         
                  │ - valor  │
                  │ - data   │
                  └──────────┘

┌──────────┐     ┌──────────────────┐
│ amostra  │────→│ amostra_elemento │────→│elemento│
│ - lote   │     └──────────────────┘     └────────┘
│ - num    │
└──────────┘
```

**Correlações que o dashboard DEVERIA mostrar:**

| Correlação | Fórmula | Insight |
|------------|---------|---------|
| Gás consumido | `Σ(leitura.tempo_chama × elemento.consumo_lpm)` | Quanto gás foi gasto em análises |
| Gás restante | `cilindro.litros_equivalentes - gas_consumido` | Vida útil restante do cilindro |
| Curva de pressão | `pressao.valor` ao longo do tempo por cilindro | Decaimento real vs esperado |
| Custo por leitura | `Σ(cilindro.custo) / Σ(leitura.quantidade)` | ROI operacional |
| Elementos por amostra | `COUNT(amostra_elemento)` por amostra | Complexidade média das amostras |
| Amostras por lote | `COUNT(amostra)` GROUP BY lote | Produtividade por lote |
| Leituras por mês | `COUNT(leitura)` GROUP BY month | Sazonalidade do laboratório |
| Top cilindros por leitura | `COUNT(leitura)` GROUP BY cilindro | Quais cilindros mais usados |

### Proposta de Novo Layout

```
┌──────────────────────────────────────────────────────────────┐
│ LINHA 1 — KPI Cards (6 cards, 2 linhas no mobile)           │
├──────────┬──────────┬──────────┬──────────┬─────────┬───────┤
│Cilindros │ Gás      │ Leituras │ Amostras │ Custo/  │ Gás   │
│ Ativos   │ Restante │ Totais   │ Totais   │ Leitura │Consum.│
├──────────┴──────────┴──────────┴──────────┴─────────┴───────┤
│ LINHA 2 — Gráficos Principais (2 colunas)                    │
├─────────────────────────────────────┬───────────────────────┤
│  Curva de Pressão por Cilindro      │  Leituras por Mês    │
│  (line chart, multicolor)           │  (bar chart)          │
├─────────────────────────────────────┴───────────────────────┤
│ LINHA 3 — Análise (2 colunas)                               │
├─────────────────────────────────────┬───────────────────────┤
│  Consumo de Gás por Cilindro        │  Elementos por       │
│  (doughnut, litros consumidos)      │  Amostra (bar)       │
├─────────────────────────────────────┴───────────────────────┤
│ LINHA 4 — Atividade Recente (3 cards)                       │
├──────────────────┬──────────────────┬───────────────────────┤
│ Últimas Leituras │ Últimas Pressões │ Últimas Amostras     │
│ (5 recentes)     │ (5 recentes)     │ (5 recentes)         │
└──────────────────┴──────────────────┴───────────────────────┘
```

### Mudanças Planejadas

#### Backend (`app.py` dashboard route — ~130 linhas alteradas)

| Mudança | Descrição |
|---------|-----------|
| Query única de leituras com JOIN | `leitura` + `cilindro.codigo` + `elemento.nome` + `elemento.consumo_lpm` em 1 chamada |
| Query de pressão com cilindro | `pressao` + `cilindro.codigo` ordenado por `data` |
| Query de amostras com contagem | `amostra` + `COUNT(amostra_elemento)` via subquery |
| Cálculo de gás consumido | `Σ(leitura.tempo_chama_em_minutos × elemento.consumo_lpm / 60)` — litros |
| Cálculo de gás restante | Para cada cilindro: `litros_equivalentes - gas_consumido_no_cilindro` |
| Custo médio por leitura | Soma de todos os `cilindro.custo` / total de leituras |
| Pressão trend data | Últimas N leituras de pressão por cilindro ativo |
| Leituras por mês | `COUNT(leitura)` GROUP BY mês nos últimos 12 meses |
| Agrupar elemento por amostra | `COUNT(ae.elemento_id)` por amostra, distribuição |

#### Frontend (`dashboard.html` — reescrita total)

| Seção | Descrição |
|-------|-----------|
| 6 KPI cards | Cilindros Ativos, Gás Restante (L), Leituras Totais, Amostras Totais, Custo/Leitura (R$), Gás Consumido (L) |
| Curva de Pressão | Chart.js line chart com múltiplas séries (1 por cilindro ativo), eixo X = data |
| Leituras por Mês | Chart.js bar chart, últimos 12 meses |
| Consumo por Cilindro | Doughnut similar ao atual, mas usando litros consumidos reais |
| Elementos por Amostra | Bar chart mostrando quantas amostras têm 1, 2, 3+ elementos |
| Atividade Recente | 3 cards em vez de 5 (remove "Últimos Cilindros" e "Últimos Elementos" — redundantes) |

#### Limpezas
- [x] Remover `ELEMENTO_CORES` e `ELEMENTO_CORES_LEITURAS` do context (aliases mortos)
- [x] Substituir consultas separadas por batch queries com `JOIN`
- [x] Renomear "Eficiência" para "Leituras por Par Cilindro×Elemento" (ou remover)

### Riscos
- `pressao` query pode ser cara se houver muitos registros — limitar a N recentes por cilindro
- Cálculo de gás consumido depende de `tempo_chama` parseável (HH:MM:SS) e `consumo_lpm` consistente
- Cilindros podem ter sido reciclados (status=esgotado) — filtrar ou mostrar separadamente
- Custo por leitura é estimativa grosseira (custo total dos cilindros / total leituras) — pode não refletir reality se cilindros forem reutilizados

---

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
---
---

## Fase 52: Migração pip + requirements.txt → Poetry 📦 (v2.7.0)

### Contexto
Projeto gerencia dependências com `pip` + `requirements.txt` separados (frontend/ + backend/).
Migrar para Poetry unifica as dependências, resolve conflitos e facilita o gerenciamento.

### Mudanças

| Arquivo | Ação |
|---------|------|
| `pyproject.toml` | **Novo** — declaração centralizada de dependências + grupos |
| `frontend/requirements.txt` | Substituído por redirecionamento ao pyproject |
| `backend/requirements.txt` | Substituído por redirecionamento ao pyproject |
| `Dockerfile` | Install poetry → `poetry install --no-dev` |
| `.gitignore` | Adicionar `.venv/`, remover `poetry.lock` do ignore |
| `README.MD` | Comandos de instalação/execução atualizados |

### Grupos de dependências

| Grupo | Inclui | Uso |
|-------|--------|-----|
| main | flask, supabase, boto3, psycopg2... | Runtime (app + scripts) |
| backend | flask-restx | API REST futura |
| dev | pytest, pytest-playwright | Testes |

### Execução

```bash
poetry install              # instala main + dev
poetry install --no-dev     # apenas runtime (produção)
poetry run python scripts/backup_db.py
python scripts/backup_db.py  # com poetry shell ativo
```

- [x] TODO.MD registrado
- [x] pyproject.toml criado
- [x] .gitignore atualizado (poetry.lock versionado, .venv ignorado)
- [x] frontend/requirements.txt → redirecionamento
- [x] backend/requirements.txt → redirecionamento
- [x] Dockerfile atualizado
- [x] README.MD atualizado
- [x] poetry lock + install --sync executado
- [x] scripts verificados

---

## Fase 51: Backup Automático via Cloudflare R2 + GitHub Actions 💾

### Contexto
Zero backup existente — dados só no Supabase free tier (sem backup automático incluso).
Backup lógico via conexão PostgreSQL direta com `pg_dump` caseiro, armazenado no Cloudflare R2 (10GB grátis), automatizado via GitHub Actions (cron diário).

### Arquitetura

```
Supabase PG ──(conexão direta psycopg2)──→ scripts/backup_db.py
                         │
                    .json.gz (comprimido)
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     Cloudflare R2 (S3)      GitHub Actions (cron)
     (10GB grátis)           (público, minutos ∞)
```

### Componentes Criados

| Arquivo | Propósito |
|---------|-----------|
| `scripts/backup_db.py` | Script de backup: conecta ao PostgreSQL, exporta schemas `public` + `auth.users`, compacta em `.json.gz`, envia ao Cloudflare R2 |
| `scripts/restore_db.py` | Script de restore: lista/selciona backup, dry-run preview, restaura com UPSERT via PostgreSQL direto |
| `.github/workflows/daily-backup.yml` | GitHub Action: cron diário (06:00 UTC) + disparo manual |
| `database/backup_user.sql` | Criação do usuário PostgreSQL readonly dedicado ao backup |

### Tabelas cobertas

| Schema | Tabelas |
|--------|---------|
| `public` | perfil, cilindro, elemento, leitura, amostra, amostra_elemento, pressao, historico_auditoria |
| `auth` | users (UUIDs preservados, senhas hasheadas intactas) |

### Segurança

- Usuário PostgreSQL **readonly** (`GRANT SELECT`) — não pode escrever nem executar DDL
- Conexão com `sslmode=require`
- `DATABASE_URL` armazenada como GitHub Secret (nunca versionada)
- Script de restore exige confirmação explícita (`"RESTAURAR"`) + modo `--dry-run`

### Setup necessário

1. Criar bucket `labgas-backups` no Cloudflare R2 + gerar Access Key
2. Executar `database/backup_user.sql` no Supabase SQL Editor (cria usuário readonly)
3. Adicionar 5 secrets no GitHub: `DATABASE_URL`, `R2_ENDPOINT`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`
4. Adicionar as mesmas variáveis ao `frontend/.env.local` para uso local

### Uso manual

```bash
python scripts/backup_db.py                    # backup + upload R2
python scripts/backup_db.py --no-upload        # só local
python scripts/restore_db.py --list            # lista backups no R2
python scripts/restore_db.py --latest --dry-run  # preview do restore
python scripts/restore_db.py --latest          # restaura backup mais recente
```

- [x] scripts/backup_db.py
- [x] scripts/restore_db.py
- [x] .github/workflows/daily-backup.yml
- [x] database/backup_user.sql → substituído por scripts/setup_backup_user.py
- [x] frontend/.env.example atualizado
- [x] frontend/requirements.txt atualizado
- [x] .gitignore atualizado (backups/)
- [x] README.MD atualizado

#### Melhoria: Senha dinâmica do backup_user via .env.local
- [x] `frontend/.env.example` — adicionado `BACKUP_DB_PASSWORD` (comentado)
- [x] `scripts/setup_backup_user.py` — lê `BACKUP_DB_PASSWORD` do `.env.local` e cria/atualiza a role `backup_user` no PostgreSQL
- [x] `scripts/backup_db.py` — fallback: se `DATABASE_URL` não existir, monta a URL a partir de `SUPABASE_URL` + `BACKUP_DB_PASSWORD`
- [x] `scripts/restore_db.py` — mesmo fallback
- [x] `database/backup_user.sql` — removido (substituído pelo script)
- [x] `.github/workflows/daily-backup.yml` — adicionado `SUPABASE_URL` + `BACKUP_DB_PASSWORD` aos envs do step de backup
- [x] `README.MD` — setup atualizado para usar `setup_backup_user.py`

#### Fase 51.1: DATABASE_URL removida do .env.local (construção dinâmica)
- [x] `frontend/.env.local`: removida `DATABASE_URL` (estava mal formatada — senha concatenada após `sslmode=require`)
- [x] Scripts já têm fallback que montam a URL automaticamente via `SUPABASE_URL` + `BACKUP_DB_PASSWORD`
- [x] `TODO.MD` registrado

#### Fase 51.2: Setup de infraestrutura R2 + backup_user 🔧
- [x] Bucket `labgas-backups` criado no Cloudflare R2
- [x] R2 Access Key ID + Secret Access Key gerados e adicionados ao `.env.local`
- [x] `frontend/.env.local`: adicionadas R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME
- [x] `frontend/.env.local`: adicionada DATABASE_URL_POSTGRES (superuser, apenas para setup)
- [x] `scripts/setup_backup_user.py`: alterado para ler DATABASE_URL_POSTGRES (com fallback DATABASE_URL)
- [x] `scripts/setup_backup_user.py` executado — backup_user criado + permissões SELECT concedidas
- [x] Backup local testado: 760 registros, 9 tabelas
- [x] Upload R2 testado: s3://labgas-backups/labgas_backup_2026-06-20_17-02-17.json.gz
- [x] Backups locais antigos limpos (mantido apenas o último)
- [x] GitHub Secrets configurados (8 secrets — Settings → Secrets → Actions):
  - `DATABASE_URL` — pooler: `postgresql://backup_user.PROJECT_REF:SENHA@aws-1-us-east-2.pooler.supabase.com:5432/postgres?sslmode=require`
  - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `BACKUP_DB_PASSWORD`, `R2_ENDPOINT`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`
- [x] Workflow `daily-backup.yml` testado manualmente via Actions → Run workflow

## Fase 53: Atualizar Docs + Testes de Backup 📄🧪

### Documentação
- [x] `CHANGELOG.md`: nova v2.7.0 com entries de Poetry migration + Cloudflare R2 Backup + DATABASE_URL dinâmica
- [x] `README.MD`: versão atualizada para 2.7.0, tech stack com Poetry, backup section refletindo DATABASE_URL dinâmica
- [x] `scripts/__init__.py`: criado (estava faltando)

### Testes de Backup
- [x] `frontend/tests/test_backup.py`: 32 testes (27 unitários + 5 integração)
  - 15 testes de serialização (datetime, date, time, timedelta, Decimal, UUID, bytes, dict, list)
  - 5 testes de construção de URL (fallback SUPABASE_URL + BACKUP_DB_PASSWORD)
  - 3 testes de geração SQL de colunas (colunas_para_sql)
  - 4 testes de ordem de operações (FK dependencies no DELETE/INSERT)
  - 5 testes de integração (subprocess backup_db.py + restore_db.py, flag `--run-backup`)
- [x] `frontend/tests/conftest.py`: adicionado `--run-backup` flag + skip automático via `pytest_collection_modifyitems`
- [x] `frontend/pytest.ini`: marker `backup` registrado
- [x] 27/27 unitários passando ✅

## Fase 54: IPv6 fix nos scripts de backup 🔧

### Problema
GitHub Actions runner não conseguia conectar ao Supabase via IPv6:
`psycopg2.OperationalError: connection to server at "db.ypnysprinkdwcfkiftvf.supabase.co" (2600:...), port 5432 failed: Network is unreachable`

### Correção
- [x] `scripts/backup_db.py`: adicionada função `_resolver_ipv4()` — resolve hostname para IPv4 antes de conectar
- [x] `scripts/restore_db.py`: mesma função `_resolver_ipv4()` adicionada
- [x] `.github/workflows/daily-backup.yml`: adicionado `supabase` às deps do pip install (faltava)
- [x] `.github/workflows/daily-backup.yml`: adicionado `permissions: issues: write` para criar Issue automática

### ✅ Corrigido: Pooler correto é `aws-1-us-east-2`

1. **Conexão direta** (`db.ypnysprinkdwcfkiftvf.supabase.co:5432`) é **IPv6 apenas** — sem registro A.
2. O pooler correto é `aws-1-us-east-2.pooler.supabase.com:5432` (não `aws-0-sa-east-1`).
3. `backup_user.ypnysprinkdwcfkiftvf` conecta com sucesso pelo pooler (IPv4).
4. `_obter_db_url()` atualizada para usar pooler em ambos os scripts.
5. Backup local com pooler testado: 760 registros ✅

- [x] `_obter_db_url()` usa `backup_user.{ref}@aws-1-us-east-2.pooler.supabase.com:5432`
- [x] `_resolver_ipv4()` mantido como safety net (pooler já resolve IPv4 nativamente)
- [x] `DATABASE_URL` do GitHub Secret deve usar pooler URL
- [x] Testar workflow manualmente via Actions → Run workflow

---

## v2.6.24 — Datas nos gráficos no formato "Mês Ano" 📅 + Filtro multi-usuário dev 👤

### Feature 1: Datas nos gráficos

**Problema:** Gráficos exibem `"2024-03-15"` e `"2024-03"` no eixo X.

**Solução:** Converter para `"Mar 2026"`, `"Fev 2026"` via dict `MESES_PT` + função `_formatar_mes_ano()` no backend.

| Arquivo | Mudança |
|---------|---------|
| `app.py` (novo) | `MESES_PT` dict + `_formatar_mes_ano(data_str)` |
| `app.py:_compute_kpis` | Aplicar `_formatar_mes_ano()` em `pressao_chart_labels` e `leituras_mes_labels` |

### Feature 2: Filtro multi-usuário exclusivo do dev

**Problema:** `dev` não consegue ver dados de outros usuários no dashboard, e export é "tudo ou nada".

**Solução:** Dropdown "Filtrar por usuário" (visível só para `dev`) com opções: "Todos os usuários" + cada usuário individualmente. Ao selecionar, dashboard recarrega com dados daquele usuário (usando `get_admin_client()` + filtro `user_id`). Export segue o mesmo filtro.

#### Arquivos alterados

| Arquivo | Mudança |
|---------|---------|
| `app.py` (dashboard route) | Se `is_dev()` e `?selected_user_id=...` presente: usar `get_admin_client()` + `.eq("user_id", selected_user_id)` |
| `app.py` (dashboard route) | Carregar `lista_usuarios` de todos os perfis (só para dev) |
| `admin.py` (export_data) | Se `is_dev()` e `?selected_user_id=...` presente: adicionar `.eq("user_id", selected_user_id)` nas queries |
| `helpers.py` | Nova função `get_all_users()` |
| `dashboard.html` | Dropdown visível `{% if is_dev %}`, recarrega com `?selected_user_id=X` |
| `dashboard.html` | Export links dinâmicos com `&selected_user_id=X` |

- [x] `app.py`: adicionar `MESES_PT` e `_formatar_mes_ano()`
- [x] `app.py:_compute_kpis`: aplicar `_formatar_mes_ano()` nas labels dos gráficos
- [x] `helpers.py`: adicionar `get_all_users()`
- [x] `app.py` dashboard: lógica de filtro `selected_user_id` para dev
- [x] `admin.py`: filtro `selected_user_id` para dev no export
- [x] `dashboard.html`: dropdown de usuários + export dinâmico
- [x] Testes: 24 passed, 11 skipped, 0 failed

### Correções pós-implantação (v2.6.24)

#### 1. Labels da Curva de Pressão — dia+mes+ano
- `app.py:362`: `pressao_chart_labels` usava `_formatar_mes_ano()` → `formatar_data()` — exibe `"15/03/2024"` em vez de `"Mar 2024"`, evitando rótulos duplicados no eixo X do gráfico de linha

#### 2. Bug leituras_mes_values
- `app.py:333`: `leituras_mes_values` usava `leituras_mes_labels` (labels formatados como `"Mar 2024"`) para lookup em `leituras_por_mes` (chaves originais `"2024-03"`) → retornava 0 para tudo. Corrigido para usar `meses` (chaves originais)

#### 3. is_dev ausente do template
- `app.py:189`: adicionado `is_dev=cached.get('is_dev', False)` ao context processor — dropdown de filtro de usuário agora aparece para devs

## Fase 55: Fix pgbouncer param + hostaddr IPv4 🔧

### Correções no CI do GitHub Actions
- [x] `scripts/backup_db.py`: `_resolver_ipv4()` agora retorna tupla `(url, hostaddr)` e `conectar()` usa parâmetro `hostaddr` do psycopg2 para forçar IPv4
- [x] `scripts/restore_db.py`: mesma correção
- [x] `scripts/backup_db.py`: `_resolver_ipv4()` também remove parâmetro `pgbouncer` da URL (psycopg2 não suporta)
- [x] `scripts/restore_db.py`: mesma correção
- [x] `_obter_db_url()`: revertida para URL de conexão direta (pooler não funciona — ver Fase 54)

### ✅ Resolvido via pooler
- `_obter_db_url()` agora usa pooler `aws-1-us-east-2.pooler.supabase.com:5432` — sempre IPv4
- `backup_user` conecta com sucesso pelo pooler (testado localmente)
- `_resolver_ipv4()` mantido como safety net (redundante com pooler, mas inofensivo)

---

## Fase 56: Análise Profunda de Vulnerabilidades 🔒 (Relatório v2 — Nenhuma Implementação)

### Contexto
Análise de segurança abrangente realizada em 20/06/2026 via auditoria direta do código-fonte. 
Nenhuma implementação deve ser feita — apenas registro para planejamento futuro.

---

### 🔴 CRÍTICOS (5)

#### C1. `SUPABASE_SERVICE_KEY` no Histórico do Git (via antigo `frontend/.env`)
**Localização:** Histórico do git — commits que tinham `frontend/.env` antes da renomeação para `.env.local`
**Problema:** Até o commit `f94c384` (29/04/2026), o arquivo `frontend/.env` era versionado e continha:
```
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlwbnlzcHJpbmtkd2Nma2lmdHZmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjI4MDkzMiwiZXhwIjoyMDg3ODU2OTMyfQ.SkmPHPTWzl_aAuZ22m8T9HY6lpOw5VKrkGz87ub64iI
```
Este JWT com role `service_role` **continua ativo** (expira em ~2036) e dá bypass total de RLS.
Também continha `SECRET_KEY=labgas-secret-key-change-in-production` (placeHolder, baixo risco).
**Situação atual:** `frontend/.env.local` **NÃO** está rastreado pelo git (corretamente no `.gitignore`). 
              `backend/.env` está rastreado mas só contém `SUPABASE_KEY` (publishable key, pública por design).
**Ação:** Rotacionar o `SUPABASE_SERVICE_KEY` no painel Supabase e remover o arquivo antigo do histórico com `git filter-repo`.

---

#### C2. SQL Injection via `%` String Formatting em `setup_backup_user.py`
**Localização:** `scripts/setup_backup_user.py:46-56`
```python
cur.execute("""...""" % (BACKUP_PASSWORD, BACKUP_PASSWORD))
```
**Problema:** `BACKUP_PASSWORD` é interpolada com `%` formatting em vez de placeholders do psycopg2. Uma aspa simples na senha quebra a query. Com acesso ao `.env.local`, um atacante injeta SQL arbitrário no PostgreSQL como superuser.
**Recomendação:** Usar `cur.execute(sql, (password, password))`.

---

#### C3. `app.secret_key` Derivado de `SUPABASE_SECRET_KEY`
**Localização:** `frontend/app.py:23`
```python
app.secret_key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("FLASK_SECRET_KEY") or os.getenv("SECRET_KEY")
```
**Problemas:** (1) Rotação da chave Supabase invalida todas as sessões Flask; (2) Se `SUPABASE_SECRET_KEY` for comprometida, atacantes forjam sessões Flask; (3) Ordem de fallback incentiva reuso de chaves.
**Recomendação:** Usar `FLASK_SECRET_KEY` independente.

---

#### C4. Backend API Gera JWT sem Expiração
**Localização:** `backend/utils/decorators.py:36-41`
```python
def generate_token(user_id, email):
    payload = {'user_id': user_id, 'email': email}
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```
**Problema:** O token JWT não possui claim `exp` (expiration). Tokens nunca expiram. Aliado ao `SECRET_KEY` ser um placeholder (`dev-secret-key-change-in-production` na config, `dev_secret_key_change_in_production` no `.env`), qualquer um que conheça essas strings pode forjar tokens e acessar toda a API backend.
**Recomendação:** Adicionar `exp`, `iat` ao payload. Usar chave secreta forte e independente.

---

#### C5. Non-dev UPDATE Operations Usam `get_supabase_client()` (Anon Key, sem JWT)
**Localização:** 
- `frontend/blueprints/cilindro.py:156`
- `frontend/blueprints/elemento.py:87`
- `frontend/blueprints/leitura.py:147`
- `frontend/blueprints/pressao.py:157`
**Problema:** As operações de UPDATE para usuários não-dev usam `get_supabase_client()` (apenas anon key, sem JWT de usuário). O RLS do PostgreSQL avalia `auth.uid() = user_id` como `NULL = uuid` (falso), bloqueando a operação. INSERT e DELETE usam `get_authenticated_client()` (com JWT) corretamente — apenas UPDATE está inconsistente.
**Impacto:** Usuários não-dev recebem erro de permissão ao tentar atualizar seus próprios registros.
**Recomendação:** Substituir `get_supabase_client()` por `get_authenticated_client()` nos 4 UPDATEs.

---

### 🟠 ALTOS (6)

#### H1. CSV Injection (Formula Injection) em Exportação Admin
**Localização:** `frontend/blueprints/admin.py:488-543`
**Problema:** Exportação CSV escreve valores sem sanitizar caracteres de fórmula (`=`, `+`, `-`, `@`). Um cilindro com código `=CMD|' /C calc'!A0` executaria comando ao abrir no Excel.
**Recomendação:** Prefixar valores suspeitos com `'` (aspas simples) no CSV.

---

#### H2. Dockerfile Executa como Root
**Localização:** `Dockerfile` (sem instrução `USER`)
**Problema:** Container roda como root. Se uma vulnerabilidade no Flask permitir RCE, atacante tem controle total do container.
**Recomendação:** Adicionar `RUN addgroup --system app && adduser --system --ingroup app app` e `USER app`.

---

#### H3. Política de Senha Fraca — Mínimo 6 Caracteres
**Localização:** `frontend/blueprints/auth.py:171`
```python
if len(password) < 6:
```
**Problema:** Mínimo de 6 caracteres é insuficiente. Sem validação de complexidade (maiúsculas, números, símbolos).
**Recomendação:** Aumentar para 8+ caracteres com requisitos de complexidade. Configurar política no Supabase Auth.

---

#### H4. Registro sem Verificação de Email
**Localização:** `frontend/blueprints/auth.py:186-214`
**Problema:** Contas são criadas e imediatamente utilizáveis sem confirmação de email.
**Recomendação:** Exigir confirmação de email no Supabase Auth (Settings → Authentication).

---

#### H5. Bloqueio de Login por Sessão — Burlável
**Localização:** `frontend/blueprints/auth.py:50-56, 130-134`
**Problema:** Bloqueio de login armazenado na sessão Flask (cookie). Atacante limpa cookies e contorna o bloqueio.
**Recomendação:** Bloquear por email (não por sessão). Usar Redis para bloqueio server-side.

---

#### H6. Backend API Aceita `role` do Cliente no Registro
**Localização:** `backend/routes/auth.py:54`
```python
"role": data.get('role', 'viewer')
```
**Problema:** O endpoint `/api/auth/register` permite que o cliente especifique a própria role via `user_metadata`. Embora a autorização do frontend use a tabela `perfil` (não `user_metadata`), outros consumidores da API podem confiar neste campo, e ele fica registrado em `auth.users.raw_user_meta_data`.
**Recomendação:** Remover o campo `role` do registro ou fixá-lo como `'viewer'`.

---

### 🟡 MÉDIOS (5)

#### M1. Ausência de Auditoria de Login no Banco
**Localização:** `frontend/blueprints/auth.py:126-138`
**Problema:** Tentativas de login falhas registradas apenas na sessão (cookie), não persistem.
**Recomendação:** Criar tabela `historico_login` (email, ip, user_agent, sucesso, timestamp).

---

#### M2. Sem 2FA/MFA
**Localização:** Arquitetura geral
**Problema:** Supabase Auth suporta MFA (TOTP), mas não está configurado.
**Recomendação:** Habilitar MFA ao menos para roles `admin` e `dev`.

---

#### M3. `setup_backup_user.py` Conecta como Superuser
**Localização:** `scripts/setup_backup_user.py:42`
**Problema:** Conecta como `postgres` (superuser). `DATABASE_URL_POSTGRES` no `.env.local`.
**Recomendação:** Remover `DATABASE_URL_POSTGRES` do `.env.local` após setup. Rotacionar senha.

---

#### M4. Error Messages Verbosos em API
**Localização:** `frontend/app.py:558, 590, 611`
**Problema:** `formatar_erro_supabase(str(e), ...)` pode vazar detalhes internos em erros inesperados.
**Recomendação:** Logar erro completo no servidor, retornar `{"error": "Erro interno"}` em produção.

---

#### M5. `backend/config.py` Carrega `.env.local` (Arquivo Errado)
**Localização:** `backend/config.py:4`
```python
load_dotenv('.env.local')
```
**Problema:** O backend tenta carregar `.env.local`, mas seu arquivo de ambiente se chama `.env`. O `load_dotenv` falha silenciosamente, e todas as configs usam fallbacks placeholder (`"dev-secret-key-change-in-production"`, `SUPABASE_JWT_SECRET=""`). Isso significa que a API backend roda com `SECRET_KEY` placeholder e sem `SUPABASE_JWT_SECRET` — qualquer um pode forjar JWTs.
**Recomendação:** Corrigir para `load_dotenv('.env')` ou usar `load_dotenv(dotenv_path=BASE_DIR / 'backend' / '.env')`.

---

### 🟢 BAIXOS (4)

#### L1. Falta de `pre-commit` Hook para Bloquear Credenciais
**Problema:** Nada impede commit de `.env*` ou strings com padrões de secret.
**Recomendação:** Adicionar `detect-secrets` ou `git-secrets` como pre-commit hook.

---

#### L2. Sem Auditoria de Vulnerabilidades nas Dependências
**Problema:** `flask`, `supabase`, `python-jose`, `psycopg2-binary` sem verificação de CVEs.
**Recomendação:** Configurar Dependabot ou `poetry audit`.

---

#### L3. `SESSION_COOKIE_SAMESITE='Lax'`
**Localização:** `frontend/app.py:32`
**Recomendação:** Mudar para `'Strict'` se não houver integração com subdomínios.

---

#### L4. Erro Genérico sem Log no Perfil
**Localização:** `frontend/app.py:511`
**Recomendação:** Adicionar `logger.error(...)` antes do flash genérico.

---

### 📊 Resumo Consolidado

| ID | Severidade | Tipo | Arquivo |
|----|-----------|------|---------|
| **C1** | 🔴 CRÍTICO | Service Key no histórico git | Histórico do git (`frontend/.env` removido) |
| **C2** | 🔴 CRÍTICO | SQL Injection | `scripts/setup_backup_user.py:56` |
| **C3** | 🔴 CRÍTICO | Acoplamento de chaves | `frontend/app.py:23` |
| **C4** | 🔴 CRÍTICO | JWT sem expiração | `backend/utils/decorators.py:36` |
| **C5** | 🔴 CRÍTICO | RLS bypass em UPDATEs (non-dev) | `cilindro.py:156`, `elemento.py:87`, `leitura.py:147`, `pressao.py:157` |
| **H1** | 🟠 ALTO | CSV Injection | `frontend/blueprints/admin.py:488-543` |
| **H2** | 🟠 ALTO | Container root | `Dockerfile` |
| **H3** | 🟠 ALTO | Senha fraca | `frontend/blueprints/auth.py:171` |
| **H4** | 🟠 ALTO | Sem verificação de email | `frontend/blueprints/auth.py:186` |
| **H5** | 🟠 ALTO | Rate-limit burlável | `frontend/blueprints/auth.py:50-56` |
| **H6** | 🟠 ALTO | Role do cliente no registro | `backend/routes/auth.py:54` |
| **M1** | 🟡 MÉDIO | Sem auditoria de login | `frontend/blueprints/auth.py:126-138` |
| **M2** | 🟡 MÉDIO | Sem 2FA/MFA | Arquitetura geral |
| **M3** | 🟡 MÉDIO | Superuser no setup | `scripts/setup_backup_user.py:42` |
| **M4** | 🟡 MÉDIO | Error messages verbosos | `frontend/app.py:558,590,611` |
| **M5** | 🟡 MÉDIO | Backend carrega .env errado | `backend/config.py:4` |
| **L1** | 🟢 BAIXO | Sem pre-commit hook | Repositório |
| **L2** | 🟢 BAIXO | Sem auditoria de deps | `poetry.lock` |
| **L3** | 🟢 BAIXO | Samesite=Lax | `frontend/app.py:32` |
| **L4** | 🟢 BAIXO | Erro genérico sem log | `frontend/app.py:511` |

### Nota sobre Itens Já Corrigidos (Fase 46)
A análise anterior (Fase 46, v2.6.17-18) já documentou e corrigiu 20 itens, incluindo IDOR em DELETE, HSTS/CSP, CORS, debug mode, JWT validation, rate limiting, RLS policies e logging. Os 20 itens acima são **adicionais** descobertos nesta auditoria e **não foram implementados**.

### Recomendação Principal
Rotacionar imediatamente o `SUPABASE_SERVICE_KEY` (JWT exposto no git history) e as credenciais do banco PostgreSQL. Em seguida, remover o arquivo `frontend/.env` do histórico do git com `git filter-repo`.

---

## Fase 57: Correção de Vulnerabilidades 🔒 (Implementação)

### Contexto
Implementação das correções para as 16 vulnerabilidades documentadas na Fase 56. Nenhum commit da C1 (git filter-repo pendente).

### Alterações Realizadas

#### 🔴 Críticos (C2–C5)
- **C2**: SQL Injection em `scripts/setup_backup_user.py` — substituído `%` formatting por placeholders `%s` do psycopg2
- **C3**: `app.secret_key` separado de `SUPABASE_SECRET_KEY` — prioridade: `FLASK_SECRET_KEY` > `SECRET_KEY` > `SUPABASE_SECRET_KEY`
- **C4**: JWT sem expiração em `backend/utils/decorators.py` — adicionados claims `iat` e `exp` (24h)
- **C5**: UPDATEs sem autenticação — `get_supabase_client()` → `get_authenticated_client()` nos 4 blueprints

#### 🔴 Altos (H1–H6)
- **H1**: CSV injection sanitized em `frontend/blueprints/admin.py` com função `sanitize_csv()` (prefixa `'` em valores que começam com `=`, `+`, `-`, `@`)
- **H2**: Dockerfile agora roda como usuário não-root (`app`)
- **H3**: Senha mínima 8 caracteres com exigência de maiúscula, minúscula e número
- **H4**: Login bloqueado se email não confirmado (`email_confirmed_at`)
- **H5**: Rate-limit server-side por email via dicionário `LOGIN_ATTEMPTS` in-memory
- **H6**: Backend `backend/routes/auth.py` não aceita mais `role` do cliente no registro

#### 🟡 Médios (M1, M4, M5)
- **M1**: Migration `database/migrations/20260620_add_login_history.sql` com tabela `historico_login` + RLS
- **M4**: Mensagens de erro genéricas no backend (removido vazamento de `str(e)`)
- **M5**: `load_dotenv` agora resolve caminho absoluto para `frontend/.env.local`

#### 🟢 Baixos (L1–L4)
- **L1**: `.pre-commit-config.yaml` criado com hooks de segurança e lint
- **L2**: `.github/dependabot.yml` criado (pip weekly, actions monthly)
- **L3**: `SESSION_COOKIE_SAMESITE` alterado de `Lax` para `Strict`
- **L4**: `logger.error()` adicionado no except genérico do perfil

### Problema de Processo e Solução

**Problema:** Ao tentar executar testes, o Flask foi iniciado em background via `python app.py &` dentro de uma tool call do shell. Quando a chamada terminava, o processo filho era morto pelo SO (cada tool call abre um novo shell independente).

**Solução:** Executar o Flask e os testes na mesma tool call, ou iniciar o Flask separadamente com `nohup` e verificar a porta antes de rodar os testes. O `conftest.py` já gerencia isso automaticamente (tenta subir o Flask via `subprocess.Popen`), mas a app crashou porque `FLASK_SECRET_KEY` não estava definida — corrigido mantendo `SUPABASE_SECRET_KEY` como fallback.

### Status dos Testes
- 35 testes passaram, 13 skipped (modais pré-existentes), 0 falhas
- Testes lentos (~3min) devido a Playwright com Chromium; `test_create_leitura` e `test_pressao_list_page_loads` exigem timeout ≥ 300s

---

## Fase 58: Backup Inteligente com Hash SHA256 + GitHub Artifacts 💾✨

### Contexto
O backup atual roda todo dia às 06:00 UTC independentemente de haver mudanças nos dados — gera dump, comprime e sobe para o R2 mesmo que nada tenha mudado. Com o tempo, backups idênticos se acumulam no R2 (até o lifecycle de 30 dias limpar). Esta fase adiciona:

1. **Hash SHA256** do dump para comparar com o último backup — se os dados não mudaram, o dump não é gerado nem enviado
2. **GitHub Actions Artifacts** como camada secundária de armazenamento (além do R2)
3. **Notificação de falha aprimorada** com contexto dinâmico (branch, commit, workflow URL)
4. **Logs de erro persistidos como artifact** em caso de falha

### Arquitetura Atualizada

```
Supabase PG ──(psycopg2)──→ scripts/backup_db.py ──(.json.gz)──→ R2 (primário)
                                     │
                                     ├── SHA256 do dump
                                     ├── compara com hash do R2
                                     │   ├── iguais → skip (sem upload)
                                     │   └── diferentes → upload dump + hash
                                     │
                                     └── GitHub Artifact (secundário)
                                         (apenas quando há mudança)
```

### Mudanças

#### A. `scripts/backup_db.py` — Hash SHA256 + skip inteligente

| Item | Descrição |
|------|-----------|
| `compute_sha256(path)` | Nova função — lê arquivo em chunks de 64KB, retorna hex digest |
| `download_hash_from_r2(client, bucket)` | Nova função — baixa `last_backup_hash.txt` do R2, retorna conteúdo ou `None` |
| `upload_hash_to_r2(client, bucket, hash_value)` | Nova função — sobe `last_backup_hash.txt` |
| `--check-hash` | Novo argumento — ativa fluxo com comparação de hash |
| `--result-file` | Novo argumento — path do JSON de resultado (default: `.backup_result.json`) |

**Fluxo com `--check-hash`:**
1. Conecta ao banco, exporta tabelas (idêntico ao atual)
2. Gera dump em **arquivo temporário** (`tempfile.NamedTemporaryFile`)
3. Computa SHA256 do dump temporário
4. Tenta baixar `last_backup_hash.txt` do R2
   - Se R2 indisponível → loga aviso, prossegue com backup (segurança > economia)
5. **Hash igual** → apaga temp, escreve `.backup_result.json`:
   ```json
   {"status": "skipped", "reason": "no changes", "hash": "abc123..."}
   ```
6. **Hash diferente** (ou primeira execução) → move para `backups/labgas_backup_<timestamp>.json.gz`, upload R2 + hash, escreve:
   ```json
   {"status": "uploaded", "filename": "backups/...", "timestamp": "2026-06-21_06-00-00", "hash": "abc123...", "size_mb": 1.23}
   ```

**Sem `--check-hash`:** Comportamento original inalterado (backward compatible).

#### B. `.github/workflows/daily-backup.yml` — Refatorado

| Mudança | Detalhe |
|---------|---------|
| `--check-hash` | Adicionado ao comando do step de backup |
| Parse do resultado | Step `Parse backup result` lê `.backup_result.json` com `jq`, extrai `status`, `filename`, `timestamp` |
| Artifact condicional | `actions/upload-artifact@v4` roda **apenas** quando `status == 'uploaded'`, retenção 30 dias |
| Logs de erro | `actions/upload-artifact@v4` em caso de `failure()` — salva `.backup_result.json` por 7 dias |
| Issue aprimorada | Título + corpo com tabela dinâmica: data, workflow URL, branch, commit, ações recomendadas |

### Arquivos alterados

| Arquivo | Tipo |
|---------|------|
| `scripts/backup_db.py` | +~70 linhas (3 funções hash + fluxo `--check-hash`) |
| `.github/workflows/daily-backup.yml` | Reescrever (~75 linhas) |

### Nenhuma alteração em

- `scripts/restore_db.py` (100% compatível)
- Schema do banco (sem migrations)
- Secrets do GitHub (mesmas 8 variáveis)
- Bucket R2 e prefixo (`labgas_backup_*`)
- Lifecycle do R2 (30 dias, 7 dias multipart abort)
- Formato do dump (JSON gzip)

### Checklist

- [x] `scripts/backup_db.py`: adicionar `compute_sha256()`
- [x] `scripts/backup_db.py`: adicionar `download_hash_from_r2()`
- [x] `scripts/backup_db.py`: adicionar `upload_hash_to_r2()`
- [x] `scripts/backup_db.py`: adicionar `--check-hash` + `--result-file`
- [x] `scripts/backup_db.py`: fluxo `--check-hash` com temp file, comparação, skip/upload
- [x] `.github/workflows/daily-backup.yml`: step backup com `--check-hash`
- [x] `.github/workflows/daily-backup.yml`: step parse result JSON
- [x] `.github/workflows/daily-backup.yml`: artifact upload condicional (30 dias)
- [x] `.github/workflows/daily-backup.yml`: error log artifact (7 dias)
- [x] `.github/workflows/daily-backup.yml`: issue aprimorada com contexto dinâmico
- [ ] Testar workflow manualmente via Actions → Run workflow

---

## Fase 59: Removida — Backup MySQL não se aplica ao projeto 🗑️

O workflow `mysql-backup.yml` foi criado para backup de banco MySQL externo,
mas o projeto usa **Supabase (PostgreSQL)** como único banco de dados.

- Backup PostgreSQL já está 100% coberto pelo `daily-backup.yml` (Fases 51 + 58)
- Workflow MySQL removido, TODO.MD limpo, referências removidas do README e CHANGELOG

---

## Fase 60: Backup Inteligente — Pre-flight, Schema Tracking, Métricas, Retenção 🔧

### Contexto
Aprimoramentos no `scripts/backup_db.py` para tornar o backup mais robusto, rastreável e eficiente:
1. **Pre-flight checks** — valida DB, R2 e disco antes de iniciar
2. **Schema version tracking** — hash das colunas de cada tabela no metadata do backup
3. **Hash por tabela** — detecção granular de quais tabelas mudaram (logs salvos em `last_backup_hashes.json`)
4. **Verificação pós-upload** — baixa o objeto do R2 e compara SHA256
5. **Métricas estruturadas** — duração, compressão, rows por tabela no JSON de resultado
6. **Retenção automática** — `--max-backups N` limpa backups antigos no R2
7. **Export paralelo** — `auth.users` via ThreadPoolExecutor (páginas simultâneas)

### Mudanças

| Arquivo | Tipo |
|---------|------|
| `scripts/backup_db.py` | ~+120 linhas (7 novas funcionalidades) |
| `frontend/tests/test_backup.py` | ~+40 linhas (teste de restore dry-run) |

### Checklist

- [x] `SCHEMA_VERSION = "1.1"` + `_get_table_schema_hash()` no backup metadata
- [x] `pre_flight()` — valida DB, R2, disco antes de começar
- [x] `verify_upload()` — baixa e compara SHA256 pós-upload
- [x] `_compute_table_hash()` — hash SHA256 individual por tabela
- [x] `_parse_user()` — fatorado do loop de export_auth_users para reuso
- [x] `_prune_old_backups()` — limpa backups antigos no R2 (--max-backups)
- [x] `--max-backups` argumento (default 30)
- [x] Métricas estruturadas no `_run_backup_with_hash_check()`:
  - `duration_sec`, `total_rows`, `size_mb`, `compression_ratio`
  - `tables` com contagem de registros por tabela
- [x] Hash por tabela armazenado em `last_backup_hashes.json` no R2
- [x] Teste `test_restore_dry_run_funciona` no `test_backup.py`
- [ ] Testar workflow manualmente via Actions → Run workflow

---

## Bugfix: JS SyntaxError na Issue de Falha (daily-backup.yml) 🐛

### Problema
Quando o script Python falha com erro contendo aspas simples (ex: `type object 'datetime.time' has no attribute 'monotonic'`), a linha 82 do workflow:
```javascript
const reason = '${{ steps.parse_result.outputs.reason }}';
```
quebra com `SyntaxError: Unexpected identifier 'datetime'`, pois as aspas simples do Python fecham a string JS prematuramente. Isso impede a criação da Issue de notificação.

### Solução
Substituir a interpolação direta no JS por `fs.readFileSync()`:

1. **Novo step** `Save failure reason` — salva `.reason` do `.backup_result.json` em `backup_reason.txt`
2. **JS** — lê o arquivo com `fs.readFileSync('backup_reason.txt', 'utf8').trim()` — 100% imune a caracteres especiais

### Arquivo alterado
- `.github/workflows/daily-backup.yml` — +7 linhas (step novo), -1 linha (interpolação removida)

### Checklist
- [x] Step `Save failure reason` adicionado (if: failure())
- [x] `const reason` lê de arquivo em vez de interpolação ${{ }}
- [ ] Testar workflow manualmente via Actions → Run workflow

---

## Bugfix: `dict(tuple_de_4)` em `_get_table_schema_hash` — RealDictCursor faltando 🐛

### Problema
`_get_table_schema_hash()` usava `conn.cursor()` (cursor padrão), que retorna
tuplas. `dict(tupla_de_4)` espera 2 elementos, mas recebe 4 colunas:
```
dictionary update sequence element #1 has length 4; 2 is required
```
O erro aparecia na primeira tabela (`public.perfil`) porque `_get_table_schema_hash`
é chamada antes de `exportar_tabela()` no loop.

### Solução
Adicionar `cursor_factory=psycopg2.extras.RealDictCursor`, que retorna dicionários
compatíveis com `dict()`. Mesmo padrão usado em `exportar_tabela()`.

### Arquivo alterado
- `scripts/backup_db.py` — 1 linha: `conn.cursor()` → `conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)`

### Checklist
- [x] `RealDictCursor` adicionado em `_get_table_schema_hash()`
- [ ] Testar workflow manualmente via Actions → Run workflow

---

## Bugfix: Shadowing — `import time` sobrescrito por `from datetime import time` 🐛

### Problema
Em `scripts/backup_db.py`, a ordem dos imports causava shadowing:
```python
import time                          # módulo time (correto)
from datetime import datetime, date, time, timedelta, UTC  # time = datetime.time (SOBRESCREVE)
```
A segunda linha sobrescrevia o `time` módulo com a classe `datetime.time`.
Quando `time.monotonic()` era chamado, o Python resolvia `time` como a
classe `datetime.time`, que não tem método `monotonic()`:
```
type object 'datetime.time' has no attribute 'monotonic'
```
Isso acontecia nas 4 chamadas a `time.monotonic()` em `_run_backup_simple()`
e `_run_backup_with_hash_check()`.

### Solução
Renomear o módulo importado para `time_mod`:
```python
import time as time_mod
from datetime import datetime, date, time, timedelta, UTC
# time.monotonic() → time_mod.monotonic()
```

### Arquivo alterado
- `scripts/backup_db.py` — import renomeado + 4 referências atualizadas

### Checklist
- [x] `import time as time_mod`
- [x] 4 ocorrências de `time.monotonic()` → `time_mod.monotonic()`
- [ ] Testar workflow manualmente via Actions → Run workflow

### Problema
`conectar()` em `scripts/backup_db.py` usa `sys.exit()` quando `DB_URL` é None:
```python
if not DB_URL:
    sys.exit("ERRO: DATABASE_URL não definida no .env.local")
```
`sys.exit()` levanta `SystemExit` (herda de `BaseException`, não de `Exception`).
Como `conectar()` é chamado dentro de `_run_backup()` → `_run_backup_with_hash_check()`, o `SystemExit` **escapa do `except Exception`** (linha 546). O `.backup_result.json` nunca é escrito, e o workflow não tem resultado para parsear.

### Solução
Substituir `sys.exit()` por `raise ValueError(...)` em `conectar()`. O `except Exception` captura, escreve o result JSON com `reason`, e o workflow prossegue para notificação.

### Arquivo alterado
- `scripts/backup_db.py` — 1 linha: `sys.exit(...)` → `raise ValueError(...)`

### Checklist
- [x] `conectar()` usa `raise` em vez de `sys.exit()`
- [ ] Testar workflow manualmente via Actions → Run workflow

---

## Fase 61: Correção do Artigo Científico (artigo.md / artigo.tex) 📄✏️

### Contexto
O artigo científico (`latex/artigo.md` e `latex/artigo.tex`) estava desatualizado em relação ao estado real do projeto (v2.9.0). Principais discrepâncias encontradas:

### Problemas Identificados e Corrigidos

| # | Problema | Severidade | Correção |
|---|----------|------------|----------|
| 1 | `amostra` descrita com FK diretas `cilindro_id`+`elemento_id` (modelo antigo) | 🔴 Crítico | Renomeado para `leitura` em todo o texto; `amostra` atual tem N:N via `amostra_elemento` |
| 2 | ER Diagram com `AMOSTRA` antiga (cilindro_id, elemento_id, quantidade_amostras) | 🔴 Crítico | Substituído por `LEITURA` + `AMOSTRA` nova + `AMOSTRA_ELEMENTO` |
| 3 | Tabela `leitura` ausente do modelo de dados | 🔴 Crítico | Adicionada ao ER e descrições |
| 4 | Tabela `amostra_elemento` ausente do modelo | 🔴 Crítico | Adicionada ao ER e descrições |
| 5 | Apenas 4 métricas antigas no dashboard | 🟠 Alto | Substituído por 6 KPIs + 4 gráficos (Fase 50) |
| 6 | Dashboard descrito como "amostras por cilindro" | 🟠 Alto | Corrigido para "leituras por cilindro" |
| 7 | Backup como "backup automático Supabase" | 🟠 Alto | Corrigido para Cloudflare R2 + GitHub Actions (Fases 51, 58, 60) |
| 8 | Apenas roles `admin`/`usuario` | 🟠 Alto | Adicionada role `dev` (Fase 47) + hierarquia |
| 9 | `is_admin()` simples nos exemplos | 🟡 Médio | Atualizado para incluir `is_dev()`, `role_at_least()`, `ROLES_HIERARCHY` |
| 10 | Gerenciamento pip/requirements.txt | 🟡 Médio | Atualizado para Poetry (Fase 52, v2.7.0) |
| 11 | Sistema de cores não mencionado | 🟡 Médio | Adicionado Rainbow v3.0 (Fases 27-28) |
| 12 | URL do repositório: `cavalcanteprofissional/lagbas-manager` | 🟡 Médio | Corrigido typos em todos os arquivos |
| 13 | Data "Abril de 2026" | 🟢 Baixo | Atualizado para "Junho de 2026" |
| 14 | `\subsubsubsection` no .tex (comando inválido) | 🔴 Crítico | Substituído por `\subsubsection` |
| 15 | `includegraphics` sem `\` (linha 222 .tex) | 🔴 Crítico | Corrigido para `\includegraphics` |
| 16 | `.tex` com `thebibliography` manual em vez de `.bib` | 🟠 Alto | Integrado `referencias.bib` via `\bibliography` + `\bibliographystyle` |
| 17 | Cache: "5 minutos" genérico | 🟢 Baixo | Detalhado: 5min listagens, 30s KPIs, 300s usuários |

### Arquivos Modificados

| Arquivo | Ação |
|---------|------|
| `latex/artigo.md` | ✅ Reescrevido — modelo de dados, dashboard, roles, URLs, datas |
| `latex/artigo.tex` | ✅ Reescrevido — mesmas correções + LaTeX syntax + bib |
| `README.MD` (raiz) | ✅ URL do repositório corrigida |
| `ARTIGO_COMPLETO.MD` (raiz) | ✅ Corrigido — sincronizado com artigo.md |
| `latex/README.MD` | ✅ URL corrigida + referências de figuras |
| `latex/figuras/banco_dados.mmd` | ✅ ER Diagram refeito — LEITURA + AMOSTRA + AMOSTRA_ELEMENTO |
| `latex/figuras/banco_dados.png` | ✅ Regenerado do .mmd |
| `latex/figuras/arquitetura.mmd` | ✅ Adicionado Leitura blueprint + Leitura tabela |
| `latex/figuras/arquitetura.png` | ✅ Regenerado do .mmd |
| `latex/figuras/navegacao_abas.mmd` | ✅ Adicionado is_dev() + Leitura |
| `latex/figuras/navegacao_abas.png` | ✅ Regenerado do .mmd |
| `latex/figuras/fluxo_dados.mmd` | ✅ Revisado (sem alterações necessárias) |
| `latex/figuras/fluxo_dados.png` | ✅ Regenerado do .mmd |
| `TODO.MD` | ✅ Registro desta fase |

---

## Fix Deploy Vercel: requirements.txt obsoleto

- [x] **`frontend/requirements.txt`** — Arquivo estava obsoleto (continha apenas comentários indicando uso do Poetry). O build `@vercel/python` precisa de um `requirements.txt` válido para instalar dependências. A falta dele causava `FUNCTION_INVOCATION_FAILED` (500) no deploy. Substituído por lista real de dependências de produção compatível com o `pyproject.toml`.

---

## Fase 62: Aba Disclaimer

**Objetivo:** Adicionar página estática de disclaimer/copyright com informações legais, licença e autoria.

### Arquivos

| Arquivo | Ação |
|---------|------|
| `frontend/templates/disclaimer.html` | ✅ Criado — template com 4 cards: Sobre, Licença, Repositório, Autoria |
| `frontend/app.py` | ✅ Modificado — rota `/disclaimer` adicionada |
| `frontend/templates/base.html` | ✅ Modificado — link no sidebar entre Histórico e Perfil |
| `frontend/utils/constants.py` | ✅ Modificado — `"disclaimer": "info-circle"` em ICON_TIPO |
| `TODO.MD` | ✅ Registro desta fase |

### Especificação

- **Visibilidade:** Todos os usuários logados (sem verificação de role)
- **Posição no sidebar:** Entre Histórico e Perfil
- **Ícone:** `bi bi-info-circle`
- **Licença:** Resumo MIT + link para LICENSE no GitHub
- **Conteúdo:** Sobre o software, licença, repositório, autoria

---

## Fase 63: Cleanup — Remoção de Arquivos Não Utilizados

**Objetivo:** Eliminar código morto e artefatos históricos que não são mais referenciados por nenhum arquivo ativo do projeto.

### 🔴 Remoção Prioritária

| # | Arquivo/Diretório | Motivo | Ação |
|---|-------------------|--------|------|
| 1 | `backend/` (inteiro) | API Flask standalone (porta 5001) nunca importada pelo frontend. Deploy real usa `frontend/app.py`. Nenhum workflow, teste ou config referencia. | `rm -rf backend/` |
| 2 | `database/seed.sql` | Substituído por `scripts/seed.py` (CHANGELOG linha 309 confirma) | `rm database/seed.sql` |
| 3 | `database/rls.sql` | Gerenciado via Supabase Dashboard / Python SDK. Nunca carregado. | `rm database/rls.sql` |
| 4 | `database/backup_user.sql` | Auto-declarado **OBSOLETO** no próprio cabeçalho. Substituído por `scripts/setup_backup_user.py` | `rm database/backup_user.sql` |
| 5 | `database/migration_amostra_v2.sql` | Migração histórica, nunca referenciada | `rm database/migration_amostra_v2.sql` |
| 6 | `database/migration_amostra_v3.sql` | Migração histórica, nunca referenciada | `rm database/migration_amostra_v3.sql` |
| 7 | `database/migration_amostra_v4.sql` | Migração histórica, nunca referenciada | `rm database/migration_amostra_v4.sql` |
| 8 | `database/migration_v5_indices.sql` | Migração histórica, nunca referenciada | `rm database/migration_v5_indices.sql` |
| 9 | `database/migration_v6_composite_indices.sql` | Migração histórica, nunca referenciada | `rm database/migration_v6_composite_indices.sql` |
| 10 | `database/migrations/20260620_add_login_history.sql` | Nunca referenciado em código, workflow ou config | `rm database/migrations/20260620_add_login_history.sql` |
| 11 | `scripts/__init__.py` | Pacote vazio (0 linhas). Scripts carregados via `importlib` ou chamados diretamente, nunca como pacote. | `rm scripts/__init__.py` |
| 12 | `test.png` | Stray gerado durante teste do Mermaid API nesta sessão | `rm test.png` |

### 🟡 Avaliar Manutenção

| # | Arquivo | Situação | Recomendação |
|---|---------|----------|--------------|
| 13 | `scripts/seed.py` | Script standalone de uso manual. Não importado por ninguém. | Manter se usado periodicamente; senão, arquivar no CHANGELOG e remover |
| 14 | `scripts/setup_backup_user.py` | Script standalone de uso manual. Não importado por ninguém. | Manter se usado periodicamente; senão, arquivar no CHANGELOG e remover |
| 15 | `database/DIAGRAM.MD` | ER do banco, superseded pelo ER em `latex/figuras/` | Manter como documentação de referência ou remover |
| 16 | `database/schema.sql` | Schema de referência, mencionado em CHANGELOG | Manter (fonte da verdade para o schema) |

### ✅ Mantidos

- `frontend/` (tudo) — 15 templates renderizados, 2 estáticos linkados, blueprints registrados
- `latex/` — Artigo acadêmico referenciado pelo README
- `.github/` — Workflows ativos
- `scripts/backup_db.py`, `scripts/restore_db.py` — Usados em workflow e testes
- `CHANGELOG.md`, `README.MD`, `LICENSE`, `TODO.MD`
- `pyproject.toml`, `poetry.lock`, `Dockerfile`, `.pre-commit-config.yaml`
- `frontend/Procfile`, `frontend/vercel.json`, `frontend/.env.example`
- `database/schema.sql` (mantido como schema de referência)

### ⚠️ Ordem Segura de Deleção

1. `rm test.png` (mais seguro, independente)
2. `rm scripts/__init__.py` (mais seguro, independente)
3. `rm database/seed.sql database/rls.sql database/backup_user.sql`
4. `rm database/migration_amostra_v2.sql database/migration_amostra_v3.sql database/migration_amostra_v4.sql`
5. `rm database/migration_v5_indices.sql database/migration_v6_composite_indices.sql`
6. `rm database/migrations/20260620_add_login_history.sql`
7. `rm -rf backend/` (por último, após verificar que nenhum teste importa `backend/`)

---

## Fase 62b: UI/UX — Aba Disclaimer (Revisão)

**Objetivo:** Melhorar layout da página de disclaimer: cards empilhados (full-width), card-headers com gradiente, badges de assinatura dos autores.

### Arquivos

| Arquivo | Ação |
|---------|------|
| `frontend/static/img/assinatura_lucas.png` | ✅ Movido de `ASSINATURA LUCAS CAVALCANTE DOS SANTOS.png` na raiz para `frontend/static/img/` |
| `frontend/static/img/assinatura_thiago_placeholder.png` | ✅ Criado — placeholder genérico para assinatura do Thiago |
| `frontend/templates/disclaimer.html` | ✅ Reescrevido — layout empilhado, cards com header gradiente, badges de assinatura |
| `TODO.MD` | ✅ Registro desta fase |

### Melhorias

- **Layout:** Cards empilhados (full-width, `col-12`) com espaçamento vertical (`mb-4`)
- **Headers:** Cada card com `card-header` gradiente colorido + ícone (padrão do projeto, como `perfil.html`)
- **Autoria:** Badges retangulares arredondados com assinatura em PNG como avatar, hover animado (`scale(1.08)` + `box-shadow`)
- Lucas: badge linkável para portfolio; Thiago: placeholder a ser substituído por assinatura real
- **Aviso:** Mantido como alerta no final

### Pendente

- [ ] Substituir `assinatura_thiago_placeholder.png` pela assinatura real do Thiago quando disponível

## Fase 64: UI/UX — Dashboard (Melhorias Visuais) 🎨

**Objetivo:** Melhorar a apresentação visual da aba Dashboard sem alterar a lógica de dados (multi-usuário, cache e cálculo de KPIs permanecem intactos).

### Arquivos

| Arquivo | Ação |
|---------|------|
| `frontend/templates/dashboard.html` | 🔨 Melhorias visuais (KPIs, gráficos, listas, cabeçalho) |
| `frontend/app.py` | ✨ Novo filter `data_relativa` + `gas_pct` no `_compute_kpis` |
| `TODO.MD` | ✅ Registro desta fase |

### Mudanças Planejadas

#### 1. KPI Cards (`dashboard.html:41-90`)
- Ícone de cada entidade em destaque (grande, semitransparente) no canto do card
- Tooltip (Bootstrap) em cada KPI explicando o cálculo (mesmo texto do README)
- Formatação de milhar nos números (ex: `1.250`)
- Barra de progresso em "Gás Restante" com % (litros restantes ÷ litros totais dos ativos)
- Responsividade: `col-6 col-md-4 col-xxl-2` (substitui `col-4 col-lg-2`)
- Hover: leve elevação + sombra

#### 2. Cards de Gráfico (`dashboard.html:93-162`)
- Gradientes inline substituídos por classes CSS reutilizáveis (bloco `{% block extra_css %}`)
- Estados vazios aprimorados (ícone grande + mensagem centralizada)
- Tooltips do Chart.js com melhor formatação (fundo escuro, arredondado)

#### 3. Listas de Atividade (`dashboard.html:164-241`)
- Datas relativas via novo filter Jinja (`data_relativa`): "hoje", "ontem", "há X dias"
- Badges e espaçamento mais consistentes

#### 4. Cabeçalho da Página (`dashboard.html:6-22`)
- Subtítulo com data de atualização + botão de recarregar dados
- Melhor alinhamento do dropdown de exportação (só admin)

### Garantias
- `canvas`, `.stat-card` e seções "Últimas Leituras / Elementos mais analisados / Últimas Amostras" permanecem no DOM (testes `test_dashboard.py`)
- Lógica multi-usuário (filtro por `selected_user_id`) intacta

### Status
- [x] Registro do plano no TODO.MD
- [x] Filter `data_relativa` + `gas_pct` (backend)
- [x] KPI cards melhorados
- [x] Cards de gráfico melhorados
- [x] Listas de atividade melhoradas
- [x] Cabeçalho melhorado
- [x] Verificação visual + testes (5/5 `test_dashboard.py`; suíte 59 passed)

## Fase 65: Navegação entre Abas — Sidebar Colapsável + Drawer Mobile 🧭

**Objetivo:** Melhorar a navegação entre abas: sidebar fixa colapsável (rail de ícones) em desktop/tablet e drawer melhorado no mobile.

### Arquivos

| Arquivo | Ação |
|---------|------|
| `frontend/templates/base.html` | 🔨 CSS, estrutura do header da sidebar, top bar mobile, JS |
| `TODO.MD` | ✅ Registro desta fase |

### Decisões (confirmadas com o usuário)
- Mobile (<768px): **drawer melhorado** (top bar fixa + auto-close + scroll lock)
- Tablet retrato (768–991px): usa **rail de ícones** (breakpoint 992 → 768)

### Mudanças Planejadas

#### 1. Breakpoint 992px → 768px
- `@media (min-width: 768px)` exibe sidebar fixa; `.mobile-toggle`/`.sidebar-overlay` ocultos em ≥768px
- Tablet retrato passa a usar a sidebar fixa (rail de ícones)

#### 2. Sidebar colapsável (desktop + tablet)
- Nova variável `--sidebar-collapsed-width: 76px`
- Header da sidebar flex: brand + botão colapsar (chevron)
- `body.sidebar-collapsed`: `padding-left` 76px, `.sidebar` 76px, `a span` oculto, ícones centralizados
- Tooltips Bootstrap nos links (placement right, container body) quando colapsado
- Persistência em `localStorage` (`lg_sidebar_collapsed`)

#### 3. Mobile drawer melhorado
- Top bar fixa (hambúrguer + logo) substitui botão flutuante
- Cabeçalho do drawer com botão fechar
- Auto-close ao navegar + trava de scroll

#### 4. Acessibilidade
- `aria-expanded`, `aria-label` nos botões de toggle/colapso/fechar

### Status
- [x] Registro do plano no TODO.MD
- [x] Breakpoint 768 + CSS do rail
- [x] Header da sidebar (brand + colapsar + fechar)
- [x] Top bar mobile + drawer
- [x] JS (colapso, tooltips, persistência, auto-close, scroll lock)
- [x] Verificação visual + testes (15 checks Playwright nas 3 viewports; `test_dashboard.py` 5/5 isolado — flake de login no harness é pré-existente, confirmado via `git stash`)

## Fase 66: Navegação — Logo como Toggle + Bottom Navigation Mobile 🧭

**Objetivo:** Refinar a navegação: no desktop/tablet a logo "LabGas" vira o botão de expandir/colapsar (sem seta indicadora, sem sublinhado) com animação mais rápida e sincronizada; no mobile, substituir o drawer lateral por **bottom navigation** com bottom sheet "Mais" e ocultar o footer de sessão.

### Arquivos

| Arquivo | Ação |
|---------|------|
| `frontend/templates/base.html` | 🔨 CSS, HTML (sidebar header, top bar, bottom nav, offcanvas), JS |
| `TODO.MD` | ✅ Registro desta fase |

### Decisões (confirmadas com o usuário)
- Desktop/tablet: **logo "LabGas" é o toggle** de colapso (remove chevron e `updateSidebarCollapseIcon`)
- Animação: ~0.18s, com `padding-left` do body sincronizado + fade dos spans (sem `display:none` brusco)
- Mobile (<768px): **bottom navigation** (5 slots) + **bottom sheet "Mais"** (Offcanvas Bootstrap `place="bottom"`)
- Conflito com o footer de sessão no mobile: **ocultar `.session-footer`** em <768px (nome/timer seguem no desktop/tablet)

### Mudanças Planejadas

#### 1. Logo "LabGas" como botão de colapso (desktop/tablet)
- `<a class="sidebar-brand" href>` → `<button type="button" class="sidebar-brand" onclick="toggleSidebarCollapse()">`
- Remove `.sidebar-btn` desktop (chevron `#collapseIcon`) e `updateSidebarCollapseIcon()`
- Reset de botão no `.sidebar-brand`: `background: transparent; border: none; padding: 0; text-align: left; text-decoration: none` (sem sublinhado)
- `applySidebarCollapsed` atualiza apenas `aria-expanded` do brand; guarda `if (window.innerWidth < 768) return;` em `toggleSidebarCollapse()`
- Logo deixa de navegar para o Dashboard (permanece como aba no menu)

#### 2. Animação mais rápida e sincronizada
- `.sidebar`: `transition: transform .3s ease, width .18s ease`
- `body`: `transition: padding-left .18s ease`
- Spans da brand + nav: `opacity: 0; max-width: 0; overflow: hidden` com `transition: opacity .12s ease, max-width .18s ease` (substitui `display: none`)

#### 3. Mobile: bottom navigation (substitui drawer)
- Remove: hambúrguer `.mobile-toggle`, `.sidebar-overlay`, drawer lateral (sidebar `display:none` no mobile), `toggleSidebar()`, auto-close, scroll lock
- Top bar mobile simplificada: só a marca "LabGas"
- Bottom nav fixa (56px, fundo `--primary-darkest`), 5 slots:
  1. Dashboard (sempre)
  2–4. Primeiras 3 abas acessíveis na prioridade [Cilindros, Pressão, Elementos, Leitura, Amostras] (via Jinja + `pode_acessar_aba`/admin)
  5. **Mais** → bottom sheet (Offcanvas `place="bottom"`) com: abas restantes + Histórico + Perfil + Disclaimer + Administração (admin) + Sair
- Item ativo destacado; `padding-bottom` no `body` no mobile para não esconder conteúdo

#### 4. Footer de sessão
- `@media (max-width: 767px) { .session-footer { display: none; } }`

### Status
- [x] Registro do plano no TODO.MD
- [x] Logo como toggle (remover chevron/sublinhado + guards JS)
- [x] Animação sincronizada (~0.18s, fade dos spans)
- [x] Bottom nav + bottom sheet "Mais" (Jinja/permissões)
- [x] Remoção do drawer mobile + top bar simplificada + footer oculto
- [x] Verificação visual + testes (25/25 Playwright nas 3 viewports; `test_dashboard.py` 5/5, `test_session_footer.py` 4/4, `test_auth.py` isolados — flake de login/timer no harness é pré-existente)

## Fase 67: Isolamento por usuário nas abas de listagem
- Decisão do usuário: cada usuário vê só os próprios dados (padrão do dashboard); dev continua vendo tudo. Escopo: todas as 5 abas.
- **Causa raiz do bug "Pressão 44"**: dropdown de cilindros filtra por `user_id`, mas as queries de listagem das abas não filtram → usuário sem cilindros vê pressões/cilindros de outros usuários, com badge caindo para o `cilindro_id` bruto ("44").

### Mudanças Planejadas

#### 1. Filtrar query principal de listagem por `user_id` (não-dev)
Padrão (cliente anon atual + `.eq` condicional):
```python
query = get_supabase_client().table("X").select("*", count="exact")
if not dev:
    query = query.eq("user_id", user_id)
response = query.order(...).range(offset, offset + per_page - 1).execute()
```
- `pressao.py:251` — `table("pressao")`, order `created_at` desc
- `cilindro.py:256` — `table("cilindro")`, order `created_at` desc
- `leitura.py:239` — `table("leitura")`, order `data` desc
- `amostra.py:240` — `table("amostra")`, order `numero_amostra` desc
- `elemento.py:185` — `table("elemento")`, order `nome`

#### 2. Dropdown de elementos em `amostra.py:261`
- `elementos_disponiveis` sem filtro → adicionar `.eq("user_id", user_id)` para não-dev (mesma inconsistência do `pressao.py:27`)

#### 3. Badge "44" em `pressao.html`
- Linhas `109` e `197`: `{{ p.cilindro_codigo or p.cilindro_id }}` → `{{ p.cilindro_codigo or '—' }}`

### Status
- [x] Registro do plano no TODO.MD
- [x] Filtro por usuário em `pressao.py` + `cilindro.py`
- [x] Filtro por usuário em `leitura.py` + `amostra.py` (lista + dropdown) + `elemento.py`
- [x] Badge "44" → placeholder em `pressao.html`
- [x] Verificação concluída via Playwright:
  - Usuário sem dados (`isolacao@labgas.com`, role `usuario`): todas as abas (pressão, leitura, amostras, cilindros, elementos) exibem 0 linhas — mesmo com dados de outros usuários no banco. Histórico segue global (log de atividades compartilhado, por design)
  - Dev (`teste@labgas.com`, role `dev`): vê dados em todas as abas
  - Smoke test HTTP das rotas com filtros Fase 68 (inclui `?page=999` → sem 416)

## Fase 68: Filtros e busca — correções e melhorias

### Mudanças Planejadas

1. **Filtro da aba Pressão** — o seletor de cilindros não está funcionando corretamente: somente a opção "Todos os cilindros" filtra. Corrigir o filtro por cilindro (e demais campos) na lista de pressões.

2. **Filtro de elementos na aba Pressão** — ~~adicionar um menu seletor de elementos no filtro da aba Pressão (mesmo padrão do seletor de cilindros), listando somente os elementos do usuário~~. **DECISÃO DO USUÁRIO: item removido** — a tabela `pressao` não possui `elemento_id` (schema.sql:42-51), então o filtro é impossível sem mudança de schema. Em seu lugar: melhorar o placeholder do filtro pesquisador e corrigir o funcionamento do filtro.

3. **Filtro da aba Leitura** — corrigir o filtro (mesmo problema da aba Pressão) **e otimizar a query**: está muito lenta. Avaliar uso dos índices existentes (`idx_leitura_user_id`, `idx_leitura_cilindro_id`, `idx_leitura_elemento_id`, `idx_leitura_data`) e reduzir `select("*")` para as colunas necessárias.

4. **Filtro da aba Amostras** — adicionar filtro de busca/filtragem (equivalente ao padrão das demais abas).

5. **Placeholder do filtro da aba Histórico** — especificar melhor o texto, ex.: "Busque por data, nome, etc..." (atualmente vago).

### Implementação

- Filtros movidos de JS client-side (`display:none`, só filtrava a página corrente) para **GET params no backend**, usando os índices existentes.
- Helper `qs()` no context_processor (`app.py`) preserva os filtros na paginação (exclui `page`/`per_page`).
- Helper `consultar_paginado` (`blueprints/helpers.py`): conta primeiro e limita a página ao intervalo existente, evitando o erro **416 "JSON could not be generated"** do PostgREST (count=exact + range além do fim), que afetava também `?page=N` fora do alcance em pressão/leitura/amostra/histórico.
- **Pressão** (`pressao.py` + `pressao.html`): filtros `q` (código do cilindro ou data dd/mm/aaaa), `cilindro_id`, `data_inicio`, `data_fim`; placeholder "Busque por código do cilindro (ex: CIL-001) ou data (16/06/2025)". JS `filterPressao` removido.
- **Leitura** (`leitura.py` + `leitura.html`): filtros `q` (código do cilindro ou nome do elemento), `cilindro_id`, `elemento_id`, `data_inicio`, `data_fim`; select reduzido de `*` para `id,data,tempo_chama,cilindro_id,elemento_id,quantidade,user_id`. JS `filterLeitura` removido.
- **Amostras** (`amostra.py` + `amostra.html`): filtros `q` (N° da amostra ou lote, numérico) e `elemento_id` (via `amostra_elemento`); select reduzido para `id,numero_amostra,lote,user_id`.
- **Histórico** (`historico.html`): placeholder "Busque por ação, tabela, detalhes ou responsável...".

### Status
- [x] Filtro Pressão funcionando (todos os campos, não só "Todos os cilindros")
- [x] Item 2 substituído (placeholder melhorado + filtro pesquisador corrigido) — ver decisão acima
- [x] Filtro Leitura corrigido + query otimizada
- [x] Filtro na aba Amostras
- [x] Placeholder do Histórico melhorado
- [x] Paginação segura (fix 416) em pressão/leitura/amostra/histórico
- [x] Smoke test HTTP das rotas (incluindo `?page=999`)

## Fase 69: Ajuste dos testes (unitários e globais) às mudanças executadas

### Contexto
As implementações das Fases 66 (navegação), 67 (isolamento por usuário nas abas) e do dashboard (KPIs, filtros `milhar`/`data_relativa`, barra de progresso de gás) foram aplicadas e commitadas na v2.10.0, mas a suíte de testes ainda não foi atualizada/validada integralmente contra essas mudanças.

### Mudanças Planejadas

- Revisar e ajustar os testes unitários afetados pelas mudanças:
  - `test_dashboard.py` — novos KPIs (`gas_total`, `gas_pct`) e filtros `milhar`/`data_relativa` no template
  - `test_pressao.py`, `test_cilindro.py`, `test_leitura.py`, `test_amostra.py`, `test_elemento.py` — isolamento por usuário nas listagens (não-dev só vê os próprios dados); badge placeholder "—" em `pressao.html`
  - `test_session_footer.py` — footer oculto no mobile + bottom navigation (Fase 66)
- Rodar e validar a suíte completa/global, incluindo `--run-modais` e demais marcadores, corrigindo falhas decorrentes das mudanças
- Observar o flake pré-existente de login/timer no harness combinado (rodar suítes isoladas quando necessário)

### Status
- [x] Revisão dos testes de dashboard (KPIs/filtros) — `test_dashboard.py` (5 testes) OK sem alterações
- [x] Ajuste dos testes das abas (isolamento por usuário) — `test_amostra.py` modais ajustados para usar o filtro `q` (usuário dev vê todos os dados; amostra criada com numeração baixa ficava fora da página 1)
- [x] Ajuste dos testes de navegação/footer (Fase 66) — `test_session_footer.py` (4 testes) OK sem alterações
- [x] Suíte global validada (isolada por arquivo; flake de rede/Supabase pré-existente reaproveitado com rerun):
  - `test_pressao` (5 com modais), `test_leitura` (7 com modais), `test_amostra` (8+1 flake, rerun OK), `test_cilindro`+`test_elemento` (12 com modais), `test_dashboard` (5), `test_session_footer` (4), `test_auth` (7), `test_admin` (2), `test_backup` (27), `test_export` (5 com `--run-export`)
- [x] Smoke test HTTP das rotas com filtros Fase 68 (inclui `?page=999` → sem 416)

## Fase 70: Filtros da aba Pressão + Nomenclatura dos cilindros 🧭

### Decisões (confirmadas com o usuário)

1. **Filtro de datas da aba Pressão** — seletor de coluna (`filtro_data`) com opções "Data" (padrão) e "Registrado em" (`created_at`) + os dois campos de intervalo (`data_inicio`/`data_fim`).
2. **Busca `q`** — passa a aceitar pressão e temperatura (valor numérico exato) além de código do cilindro e data `dd/mm/aaaa`; placeholder atualizado.
3. **Regex do código** — "001" deve identificar `CIL-001` (normalização de dígitos, não só substring).
4. **Nomenclatura** — código `CIL-XXX` permanece estável (histórico/exports/busca intactos); exibição enriquecida com rótulos dinâmicos:
   - Todos os cilindros com `status = 'ativo'` recebem destaque **"EM USO"** (pode haver vários simultâneos)
   - Entre os ativos, ordenação e rótulo por **% de carga** (última pressão ÷ 300 bar) — o mais cheio aparece primeiro
   - Esgotados mantêm o código com badge **"ESGOTADO"**

### Mudanças Planejadas

- [x] `frontend/utils/cilindro_utils.py` — 🆕 helpers: `enriquecer_cilindros()` (carga_pct, estado_rotulo, rotulo_exibicao), `normalizar_codigo_cilindro()`, `codigo_corresponde()`
- [x] `frontend/utils/constants.py` — `PRESSAO_MAXIMA_BAR = 300` e regex de código compartilhada
- [x] `frontend/blueprints/pressao.py` — filtro por coluna selecionável (data/created_at com normalização de datetime), `q` numérico (pressão/temperatura) e código normalizado
- [x] `frontend/templates/pressao.html` — seletor `filtro_data`, placeholder novo, dropdown de cilindros com rótulo dinâmico
- [x] `frontend/blueprints/cilindro.py` — enriquecer + ordenar lista (ativos por carga % desc, depois esgotados)
- [x] `frontend/templates/cilindro.html` — badges de estado (EM USO / ESGOTADO) e % de carga
- [x] `frontend/blueprints/leitura.py` — dropdown com rótulo + mesma normalização de código (consistência)
- [x] `frontend/tests/test_pressao.py` + `test_cilindro.py` — novos testes de filtros e badges
- [x] `CHANGELOG.md` — entrada v2.12.0
- [x] Suíte validada isolada por arquivo (`test_pressao` + `test_cilindro` com `--run-modais`: 15 passed, 1 skipped)

### Fora de escopo (follow-up)

- Rótulos dinâmicos nos gráficos do dashboard e no histórico (mantêm `codigo` puro)
- Campo `em_uso` BOOLEAN com migration (apenas se um único cilindro em uso for necessário no futuro)

## Fase 71: Aba Pressão — paleta de temperatura, filtro de data por tipo e busca por campo 🎨

### Objetivo
Melhorar a aba Pressão com três mudanças visuais/funcionais:

1. **Paleta de cores para temperatura** — baseada na média de todas as temperaturas (do conjunto filtrado): verde próximo à média, amarelo e vermelho em escala conforme o desvio (média ± desvio padrão). Gradiente contínuo verde → amarelo → vermelho, com cor de texto ajustada por luminância.
2. **Novo seletor de data** — remover o seletor atual `filtro_data` ("Data" / "Registrado em") que fica sempre visível. Nova estratégia: um `select` opcional "Filtrar por data" com opções vazia (default, sem data) / "Data do registro" (`data`) / "Data de criação" (`created_at`); ao escolher um tipo, os campos De/Até são revelados; ao desmarcar, os campos somem e nenhum filtro de data é aplicado.
3. **Busca de texto estilo cilindro com campo selecionável** — input de texto igual ao da aba Cilindro + `select` de campo que restringe a busca às colunas da tabela filtrada: Tudo (default) / Cilindro / Pressão / Temperatura / Data / Hora.

### Decisões (interpretação confirmável)

- Média/desvio padrão calculados **no conjunto filtrado** (mesmos filtros da listagem), não na página corrente — "média de todas as temperaturas". PostgREST do projeto tem agregados desabilitados (PGRST123), então calculamos em Python via fetch da coluna `temperatura` apenas (query leve, sem `*`).
- O intervalo De/Até é mantido (não removido) — o usuário pediu para reorganizar o seletor, não para perder o intervalo da Fase 70.
- "Registrado em" (`created_at`) permanece pesquisável apenas pelo filtro de data (item 2), não pela busca de texto (a busca textual por timestamp exato tem pouco uso).

### Mudanças Planejadas

- [x] `frontend/blueprints/pressao.py` — `_estatisticas_temperatura()` (média + desvio em Python), `_temperatura_cor()` (gradiente verde→amarelo→vermelho + luminância para cor do texto), `filtro_data` default vazio (sem filtro quando não selecionado), novo parâmetro `q_campo` restringindo a busca
- [x] `frontend/templates/pressao.html` — remover select "Data/Registrado"; novo select "Filtrar por data" + campos De/Até com toggle (JS + estado inicial no server); input `q` + select de campo (Tudo/Cilindro/Pressão/Temperatura/Data/Hora); célula de temperatura com badge colorido inline
- [x] `frontend/tests/test_pressao.py` — testes novos: `q_campo=pressao` restringe busca; `q_campo=temperatura`; badge de temperatura com cor inline (média)
- [x] `CHANGELOG.md` — entrada v2.13.0
- [x] Suíte validada isolada por arquivo (`test_pressao` com `--run-modais`: novos testes OK; flakes pré-existentes do harness reaproveitados com rerun, consistente com a Fase 69)

> **Nota (Fase 72)**: a paleta de temperatura passou de verde→amarelo→vermelho para uma **escala de vermelho** (claro na média → profundo no desvio), por decisão do usuário. `q_campo` e `filtro_data` foram posteriormente removidos na Fase 72 (filtros padronizados).

## Fase 72: Pressão — paleta de cor para pressão + filtros padronizados 🔄

### Objetivo
1. **Paleta de cor da pressão** — mesma lógica da paleta de temperatura (cor relativa ao desvio da média do conjunto filtrado), mas usando **somente laranja → vermelho** em escala (sem verde/amarelo).
2. **Filtros refeitos no padrão das outras abas** (leitura/amostra): `q` único (busca código/data/pressão/temperatura) + dropdown `cilindro_id` + intervalo `data_inicio`/`data_fim` sempre visível (coluna `data`). **Removidos** `q_campo` (seletor de campo) e `filtro_data` (tipo de coluna de data + campos condicionais) da Fase 71 — decisão do usuário para padronizar com as demais abas.

### Mudanças Planejadas

- [x] `frontend/blueprints/pressao.py` — remover `q_campo` e `filtro_data`; `montar()` padronizado (igual leitura); helpers genéricos `_estatisticas_valores()` (média + desvio em Python, 1 query só para `pressao,temperatura`) e `_cor_escala()` (gradiente por pontos, retorna cor de fundo + cor de texto por luminância)
- [x] `frontend/templates/pressao.html` — filtro no layout padrão (q col-3, cilindro col-2, data_inicio col-2, data_fim col-2, botões col-1); badge de pressão com gradiente laranja→vermelho; remover o JS `toggleDataFields`
- [x] `frontend/tests/test_pressao.py` — `test_pressao_filter_por_data` (intervalo na coluna `data`, no padrão das outras abas), `test_pressao_pressao_cor` (badge laranja/vermelho); remover os testes de `q_campo`
- [x] `CHANGELOG.md` — entrada v2.14.0
- [x] Suíte validada isolada por arquivo (`test_pressao`: 10 passed + 1 skip; `test_cilindro`: 7 passed) — **causa dos flakes identificada**: um servidor Flask antigo na porta 5000 estava sendo reutilizado pelo conftest com código velho; encerrado o processo, os testes passam de forma consistente

## Fase 73: Filtros da aba Pressão — busca por campo separado 🔍

### Objetivo
Corrigir o campo de texto do filtro da aba Pressão, separando a busca em **três inputs independentes** — um para cada campo: **código**, **pressão** e **temperatura**. Placeholders por campo ("Buscar por código", "Buscar por pressão", "Buscar por temperatura"), substituindo o `q` único (que misturava código + data `dd/mm/aaaa` + pressão/temperatura). Filtros combinados com AND (padrão das outras abas). A busca textual por data é removida — datas continuam no intervalo `data_inicio`/`data_fim`.

### Mudanças Planejadas

- [x] `frontend/blueprints/pressao.py` — remover `q`; novos params `q_codigo` (via `codigo_corresponde`), `q_pressao` e `q_temperatura` (numérico via `safe_float`); remover parsing de data do texto e o import `re` (fica sem uso)
- [x] `frontend/templates/pressao.html` — três inputs separados com placeholders próprios, mantendo dropdown `cilindro_id` + intervalo de datas
- [x] `frontend/tests/test_pressao.py` — ajustar `q` → `q_codigo`/`q_pressao`; novo teste `q_temperatura`
- [x] `CHANGELOG.md` — entrada v2.15.0
- [x] Suíte validada isolada por arquivo (`test_pressao` com `--run-modais`: 11 passed + 1 skip)

## Fase 74: Nomenclatura dos cilindros — somente o número 🔢

### Objetivo
Reelaborar a refatoração de nomenclatura dos cilindros (Fase 70): **remover as tags `EM USO`/`ESGOTADO` e o badge de `%`** e **mostrar ao usuário somente o número do cilindro** (extraído do código, ex: `CIL-001` → `1`, `CIL-010` → `10`). O código `CIL-XXX` continua armazenado no banco (identidade estável) e **histórico + exportações (CSV/Markdown) preservam o código completo** (decisão do usuário). Mudança somente de exibição, sem migração de dados.

### Mudanças Planejadas

- [x] `frontend/utils/cilindro_utils.py` — remover `_buscar_ultima_pressao_por_cilindro` (query extra) e os campos `carga_pct`/`estado_rotulo`/`rotulo_exibicao`; `enriquecer_cilindros` passa a adicionar apenas `numero_exibicao` (`normalizar_codigo_cilindro(codigo) or codigo`)
- [x] `frontend/blueprints/cilindro.py` — `_chave_ordenacao_cilindros`: ativos primeiro, tie-break numérico pelo número do cilindro (sem `carga_pct`)
- [x] `frontend/templates/cilindro.html` — coluna Código exibe `numero_exibicao`; remover badge de `%`; coluna Status com badge neutro `Ativo`/`Esgotado` (sem ícone de raio); modal de exclusão e `#searchCilindro` com número; modal de edição mantém `c.codigo` completo
- [x] `frontend/templates/pressao.html` + `leitura.html` — dropdowns usam `c.numero_exibicao`; badges das tabelas e modais de exclusão usam novo campo `cilindro_numero`; placeholder do filtro `q_codigo` → "Buscar por número"
- [x] `frontend/blueprints/pressao.py` + `leitura.py` — manter `cilindro_dict`/`cilindro_dict_lookup` com código completo para `registrar_historico`; adicionar `cilindro_numero` na renderização da lista (mapa id → `numero_exibicao`)
- [x] `frontend/app.py` — dashboard: rótulos dos gráficos de cilindro usam o número
- [x] `frontend/tests/test_cilindro.py` — atualizar `test_cilindro_badge_estado_e_carga` → `test_cilindro_exibe_numero_sem_rotulos` (célula exibe `1`, status `Ativo`, ausência de `EM USO`/`ESGOTADO`/`50%`/`CIL-001` na tabela)
- [x] `CHANGELOG.md` — entrada v2.16.0
- [x] Suíte validada por arquivo (`test_cilindro` 7 passed; `test_pressao` 10 passed + 1 skip; `test_leitura` 7 passed — 3 testes isolados re-rodaram verdes após flakes de rede do Supabase)

## Fase 75: Dashboard vazio/zerado — diagnóstico e correção 🐛

### Objetivo
Investigar por que o dashboard exibe dados vazios/zerados enquanto o banco tem dados válidos. Análise do código (`_compute_kpis` + fetch + RLS + cache) mostrou que **o working tree atual não zera os dados** (diff da Fase 73/74 só alterou rótulos; repro offline de `_compute_kpis` retornou valores corretos). Causas prováveis: processo servidor antigo (PID 18732 na porta 5000), cache em memória com resultado vazio, mismatch de `user_id` (dashboard filtra estrito por `user_id`), ou URL com `selected_user_id` de usuário sem dados. Usuário confirmou que ocorre no **localhost:5000**.

### Mudanças Planejadas

- [x] `frontend/app.py` — adicionar log diagnóstico temporário na rota `/dashboard` (len de cada fetch, `current_user_id` e resumo dos KPIs)
- [x] Restart do servidor local com o working tree atual (limpa SimpleCache em memória) — PID antigo 18732 derrubado; relançado (PID 27124)
- [x] Comparar log × banco para confirmar a causa — **reproduzido com código e banco reais**: o código computa corretamente; o vazio é dependente da sessão (isolamento por usuário)
- [x] `frontend/tests/test_dashboard.py` — reforçar para assertar valores de KPI (não só seções/canvas); novo `test_compute_kpis.py` unitário (5 testes verdes); Playwright `test_dashboard.py` 8 testes (1 flake de login, re-rodou verde)
- [x] Remover diagnóstico temporário após confirmação (ou manter gated por DEBUG) — **removido** (logs `[DIAG dashboard]` de app.py apagados)

## Fase 76: Refatoração historico_log → historico_auditoria 🗄️ (Opção C)

### Objetivo
Substituir a coluna `nome` heterogênea de `historico_log` por uma tabela nova `historico_auditoria` com `label` (texto legível), `ref_id` (id do registro de origem, polimórfico conforme `tipo`) e `detalhe` (JSONB estruturado). Migrar os dados existentes (backfill de `ref_id` onde inequívoco) e **descartar a tabela legada** após verificação. Documentar toda a migração no `schema.sql`, `rls.sql` e migration nova.

### Novo esquema
```sql
CREATE TABLE historico_auditoria (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    acao VARCHAR(20) NOT NULL CHECK (acao IN ('criado','atualizado','excluido')),
    ref_id INTEGER,
    label VARCHAR(150),
    detalhe JSONB,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);
-- Índices: idx_historico_aud_tipo, idx_historico_aud_user_id, idx_historico_aud_created_at, idx_historico_aud_ref (tipo, ref_id)
```

### Mudanças Planejadas

- [x] `database/migrations/20260805_historico_auditoria.sql` — CREATE TABLE + índices + INSERT...SELECT com backfill (cilindro por codigo+user_id; elemento por nome+user_id; amostra por `A/N Lx`; pressao/leitura/perfil com ref_id NULL documentado) + verificação de contagem + DROP TABLE historico_log
- [x] Executar a migration no Supabase real — **351/351 registros migrados** (`historico_log=351` → `historico_auditoria=351`); `ref_id` preenchido em 89 (cilindro/elemento/amostra), 262 sem ref (pressao/leitura/perfil, esperado); `detalhe`=0 (dados antigos não tinham); escrita/leitura de ponta a ponta OK (`registrar_historico` → `historico_auditoria` com `ref_id`+`detalhe`); **DROP da legada fica comentado** (decisão pendente)
- [x] `frontend/blueprints/helpers.py` — `registrar_historico(tipo, acao, label, user_id, ref_id=None, detalhe=None)` → insere em `historico_auditoria`
- [x] Call sites (32): `cilindro.py` (4), `pressao.py` (4, `detalhe={pressao,temperatura}`), `elemento.py` (4), `leitura.py` (4, `detalhe={cilindro_id,elemento_id}`), `amostra.py` (4), `admin.py` (3, `detalhe={alvo,role,aba}`), `auth.py` (1) — capturar `resp.data[0]["id"]` nos inserts p/ `ref_id`; bulk → `detalhe={quantidade}`
- [x] `frontend/blueprints/historico.py` + `templates/historico.html` — nova tabela; `h.nome` → `h.label`; renderizar `detalhe` e badge de `ref_id`
- [x] `frontend/blueprints/admin.py` (204 purge + 277-288 detalhe usuário) → `historico_auditoria`
- [x] `scripts/backup_db.py` (74) e `scripts/restore_db.py` (61, 74) → `historico_auditoria`
- [x] `frontend/tests/conftest.py` (225 cleanup) e `test_backup.py` (230, 247, 342) → nova tabela; novo teste `registrar_historico` com `ref_id`/`detalhe`
- [x] `database/schema.sql` e `database/rls.sql` — atualizar tabela + policy SELECT
- [x] Docs: `README.MD`, `database/DIAGRAM.MD`, `latex/artigo.md`, `latex/figuras/arquitetura.mmd`, `CHANGELOG.md`, e `labgas-migracao-supabase-local.MD` (plano de migração local)
- [x] Suíte validada por arquivo — `test_compute_kpis.py` (5) + novo `test_helpers_historico.py` (4) verdes; blueprint tests verdes (test_cilindro/pressao/elemento/leitura/amostra/admin/auth/export/session_footer); `test_backup.py --run-backup` 33 verdes (inclui backup real exportando `historico_auditoria` + restore dry-run); `test_dashboard.py` 8 (1 flake de login por rate-limit 429 — re-roda verde isolado). **Nota**: rodadas repetidas esgotam o rate-limit de login (5/min) e derrubam o fixture Playwright — reiniciar o servidor local para zerar

## Fase 77: DROP TABLE historico_log (descarte da tabela legada) 🗑️

### Objetivo
Remover a tabela legada `historico_log` do Supabase real após a migração completa para `historico_auditoria` (Fase 76), com snapshot de segurança e validação pós-drop.

### Itens

- [x] Pré-verificação (read-only): `historico_log` = 351, `historico_auditoria` = 351; nenhuma FK aponta para `historico_log`; código ativo sem refs à tabela legada
- [x] Snapshot de segurança `historico_log_bkp_20260805` (CREATE TABLE AS SELECT)
- [x] `DROP TABLE historico_log;`
- [x] Verificação pós-drop: `to_regclass('public.historico_log') IS NULL` e `historico_auditoria` intacta (351)
- [x] Pós-validação: smoke no app local (`/historico` + insert/leitura/limpeza via `registrar_historico`) e `backup_db.py --no-upload`
- [x] `DROP TABLE historico_log_bkp_20260805;` (após validação — decisão do usuário)
- [x] `database/migrations/20260805_historico_auditoria.sql` — bloco 4 marcado como executado em 2026-08-05

## Fase 78: Filtro da aba Cilindro — busca server-side por número (bugfix) 🔍

### Objetivo
O campo de filtro da aba Cilindro não funciona corretamente: alguns números filtram e outros "não acham nada" (relatado: 5,6,7,8,10-13 funcionam; 1,2,3,4,9 não). Causa raiz — **dois bugs** no filtro client-side (`filterCilindro` em `cilindro.html`):
- **Vazamento de dígitos (falsos positivos)**: `row.cells[1].textContent.includes(search)` casa substring na célula inteira, que concatena o badge (`numero_exibicao`) com o `<div>` mobile de `gas_kg`/`custo` (ex.: `"1"+"1.00kg | R$ 290.00"`). Dígitos de `kg`/`R$` "vazam": buscar "2"/"9" casa com qualquer cilindro com custo `290.00`. Ampliado na Fase 74 (badge passou de código completo para número puro).
- **Cegueira de paginação (falsos negativos / "não acha nada")**: filtro opera só nas linhas da página atual (10/página default). A listagem busca `order(created_at, desc)` e ordena por número **depois** do slice da página (`cilindro.py`), então cilindros de páginas 2+ não existem no DOM.

### Mudanças Planejadas

- [x] `frontend/blueprints/cilindro.py` — filtro server-side: ler `q` (GET) e aplicar `codigo_corresponde` (de `cilindro_utils`, mesmo helper de pressão/leitura) via `in_("id", ids)`/`eq("id", 0)`; ler `status` (GET) e aplicar `eq("status", ...)` validado contra `CILINDRO_STATUS`
- [x] `frontend/templates/cilindro.html` — envolver input `#searchCilindro` + select `#filterStatus` + botão em `<form method="get">`; remover `filterCilindro()`/listener `keyup`; adicionar `{{ qs() }}` nos links de paginação e no select `per_page` (preserva `q`/`status`)
- [x] `frontend/tests/test_cilindro.py` — testes do filtro: achar cilindro em outra página (`?q=1` com 12 cilindros), sem vazamento de dígitos de `kg`/`R$`, substring por código (`?q=5` acha CIL-005 e CIL-015) e filtro por status
- [x] Validar suíte e registrar no `CHANGELOG.md`/`README.MD` se necessário

## Fase 79: Filtros da aba Cilindro — data (de/até), busca dinâmica e ordenação por código 📅

### Objetivo
Aprimoramentos no filtro da aba Cilindro solicitados pelo usuário: (1) filtro por **Data de Compra** em intervalo (de/até), no padrão da aba Leituras (`data_inicio`/`data_fim` com `gte`/`lte`); (2) voltar o comportamento **dinâmico** da busca (digitar e já filtrar, sem clicar em Filtrar ou dar Enter) mantendo o filtro server-side da Fase 78 (debounce no `input` de `#searchCilindro`); (3) **ordenar a tabela por ordem do código** (número), removendo o agrupamento "ativos primeiro" e paginando globalmente na ordem do código (`order("codigo")`).

### Mudanças Planejadas

- [x] `frontend/blueprints/cilindro.py` — filtro por `data_compra`: ler `data_inicio`/`data_fim` (GET), validar `%Y-%m-%d` e aplicar `gte`/`lte`; ordenação: `_chave_ordenacao_cilindros` só pelo número e listagem com `order("codigo")` (asc) no lugar de `created_at desc`
- [x] `frontend/templates/cilindro.html` — inputs `data_inicio`/`data_fim` (date) no form de filtro com valores preservados; JS de debounce (~350ms) no `#searchCilindro` que submete o form; datas e status com `onchange="this.form.submit()"`
- [x] `frontend/tests/test_cilindro.py` — testes: ordem por código (códigos distintos fora de ordem/status mistos), filtro data de compra em intervalo e busca dinâmica ao digitar (esperar URL `?q=`)
- [x] Validar suíte e registrar no `CHANGELOG.md`

## Fase 80: Cilindro passa a usar `numero` inteiro — integridade, RLS e docs (refatoração) 🔢

### Objetivo
Refatorar o identificador de cilindro de `codigo VARCHAR(50)` ("CIL-XXX") para `numero INTEGER` (1, 2, 3...), exibindo **só números em tudo** (tabela, exports CSV/Markdown e label do histórico). Aproveitar para fechar lacunas de integridade/segurança identificadas na análise do schema (banco vivo via `DATABASE_URL_POSTGRES`): UNIQUE e CHECK que hoje só existem a nível de app, RLS que permite qualquer usuário autenticado ler dados de todos, e sync de `schema.sql`/`rls.sql`/`DIAGRAM.MD` com o banco real.

### Mudanças Planejadas

- [x] `database/migrations/20260806_cilindro_numero.sql` — `cilindro.numero` (backfill numérico, NOT NULL, `UNIQUE(numero, user_id)`, CHECK `status`), `elemento UNIQUE(nome, user_id)`, CHECK `tipo` em `historico_auditoria`, RLS dev-aware (próprio usuário ou role `dev`) em cilindro/elemento/leitura/pressao/amostra/amostra_elemento/historico_auditoria
- [x] `frontend/utils/cilindro_utils.py` — `codigo_corresponde` por número (aceita "1"/"001"/"CIL-015"), `enriquecer_cilindros` → `str(numero)`, remover `normalizar_codigo_cilindro`; `constants.py`/`validators.py` — remover regex/validador de CIL-XXX
- [x] `frontend/blueprints/cilindro.py`, `leitura.py`, `pressao.py`, `admin.py`, `app.py` — criar/atualizar por `numero`, `order("numero")`, histórico/exports com só número, `/api/buscar-codigo` aceita número ou "CIL-XXX"
- [x] `cilindro.html` (input number) e `static/js/voice_assistant.js` (remove `/^CIL-\d{3}$/` e `padStart`)
- [x] `backend/routes/cilindro.py` — campo `numero`
- [x] Testes atualizados (`test_cilindro`, `test_leitura`, `test_pressao`, `test_compute_kpis`, `test_export`, `test_helpers_historico`) + comentário nos fixtures temporários (CIL-800/900)
- [x] Sync `database/schema.sql`/`rls.sql`/`DIAGRAM.MD` + `CHANGELOG.md`

## Fase 81: Padronizar filtros de todas as abas (padrão aba Cilindro) 🔍

### Objetivo
Padronizar os filtros de todas as abas pelo padrão da aba Cilindro (Fases 78-79): filtro `GET` no servidor, busca com debounce ~350ms, selects/datas com `onchange`, paginação preservando filtros via `{{ qs() }}` e seletor `per_page`. Decisões do usuário: Pressão mantém os 3 campos (só padroniza interação e renomeia `q_codigo`→`q_numero`); Histórico vira server-side com `q` (label + responsável) + `tipo` + `acao` + datas; Admin `user_data` server-side; Admin ganha busca por nome/email; Amostra `q` passa a substring.

### Mudanças Planejadas

- [x] `frontend/blueprints/leitura.py` — dropdowns `cilindro`/`elementos` com `if not dev:` antes do `.eq("user_id")` (corrige dev enxergando tudo na tabela mas dropdowns/busca só dos próprios)
- [x] `frontend/templates/leitura.html` — `id="searchLeitura"` + debounce no `q`; `onchange="this.form.submit()"` no select cilindro, select elemento e datas
- [x] `frontend/blueprints/pressao.py` — renomear `q_codigo` → `q_numero`; `cilindro_list` com `if not dev:`
- [x] `frontend/templates/pressao.html` — `id`s nos 3 inputs + debounce; `onchange` no select cilindro e datas
- [x] `frontend/blueprints/amostra.py` — `q` substring (padrão cilindro, match em Python por `numero_amostra`/`lote` + `in_("id")`); mantém filtro `elemento_id`
- [x] `frontend/templates/amostra.html` — `id="searchAmostra"` + debounce; `onchange` no select de elemento
- [x] `frontend/blueprints/historico.py` — migrar para server-side: `montar(query)` com `q` (label ilike + user_id via nomes), `tipo`, `acao`, `data_inicio`/`data_fim`; `per_page` param
- [x] `frontend/templates/historico.html` — filtros em `<form method="get">` com `name`; remover `filterHistory()`; `qs()` na paginação + seletor `per_page`
- [x] `frontend/blueprints/admin.py` — `user_data()` com filtros `tipo`/`acao` server-side + `per_page`; `panel()` com busca `q` por nome/email
- [x] `frontend/templates/admin_user_data.html` — selects em `<form method="get">` com `onchange`; remover `filterHistory()`; `qs()` na paginação
- [x] `frontend/templates/admin.html` — input `q` (debounce) para buscar usuários
- [x] Testes: `test_leitura` (filtros), `test_pressao` (`q_numero`), `test_amostra` (substring + elemento), `test_historico` (novo), `test_admin` (busca + user_data)
- [x] `CHANGELOG.md`

## Fase 82: Dashboard — gráficos vazios (bug Chart.js) + ícone "Leituras por Cilindro" 🐛📊 (v2.20.2)

### Bug reportado
Com o usuário Thiago, os 4 gráficos centrais do dashboard ("Curva de Pressão por Cilindro", "Leituras por Mês", "Leituras por Cilindro", "Elementos por Amostra") apareciam **vazios**, embora os cards de KPI computassem valores corretos.

### Diagnóstico (causa raiz)
- O servidor envia **todos** os dados dos gráficos corretamente (13 labels/valores de cilindro; pressão do cilindro 12 com 10 pontos; 11 meses; elementos [5,1,0,22]).
- Chart.js carrega (CDN), mas o **1º gráfico** (doughnut "Leituras por Cilindro") lança `TypeError: n.reduce is not a function` no layout da legenda (`_fitCols`).
- **Trigger isolado empiricamente (Playwright):** labels **numéricos** + legenda visível. `cilindro_leituras_labels` eram inteiros `[1..13]` (de `numero_cilindro.get(cid, str(cid))`). Probes: numérico+legenda → ERRO; numérico sem legenda → OK; string+legenda → OK.
- Os 4 `new Chart(...)` estão num **único bloco `<script>`** — o erro no primeiro aborta o bloco inteiro, impedindo a criação dos outros 3 (por isso os 4 aparecem vazios).

### Correções
- [x] `frontend/app.py` — `cilindro_leituras_labels.append(str(numero_cilindro.get(cid, str(cid))))` (labels viram strings, elimina o crash da legenda)
- [x] `frontend/templates/dashboard.html` — ícone de "Leituras por Cilindro" (header + empty-state) `bi-pie-chart` → `bi-thermometer-half` (decisão do usuário)
- [x] `frontend/templates/dashboard.html` — legenda do doughnut "Leituras por Cilindro" substituída por **grid customizado** (`#cilindroLegend`): 13 itens em células de tamanho igual (2 colunas), cada uma com ponto de cor + número do cilindro + **quantidade total de leituras**; chart à esquerda (56%), legenda à direita, empilha no mobile
- [x] `frontend/utils/constants.py` — `PALETA_CILINDRO` virou **escala vermelha pura claro→escuro** (`#ffc2c2 → #f9706a → #e63946 → #c1121f → #780000`); com `getColorByIntensity`, menor quantidade = vermelho mais claro e maior = vermelho mais escuro (verificado: cilindro 5/143 → `#ffc2c2`, cilindro 6/689 → `#780000`)
- [x] `frontend/templates/dashboard.html` — **filtro de ordenação/cores** do doughnut "Leituras por Cilindro": `btn-group` no header com **"Por Número"** (default) e **"Por Leituras"**; JS refatorado em `renderCilindro(modo)` — "Por Número" ordena 1→13 e colore por número (1 = `#ffc2c2`, 13 = `#780000`); "Por Leituras" ordena crescente por quantidade e colore por quantidade (143 = claro, 689 = escuro); fatias do doughnut **e** legenda reordenam juntas (`chart.update()` + reconstrução de `#cilindroLegend`)
- [x] Testes: `test_compute_kpis.py` + `test_dashboard.py` passando (o teste existente de labels continua válido — `str(str)` é idempotente)
- [x] Verificação Playwright: 4 charts criados (`Chart.instances` — doughnut/line/bar/bar, canvas 506x250), **zero** pageerrors, screenshot conferido
- [x] `CHANGELOG.md`

### Achado secundário (fora do escopo — registrado)
Console do navegador mostra `[VOICE] Erro ao carregar dados do usuário: SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON` — o widget de voz busca um endpoint que devolve HTML em vez de JSON (pré-existente, não relacionado aos gráficos). Investigar em fase futura.

## Fase 83: Remover logo TSA e padronizar ícone LabGas (gota) 🎨 (v2.20.3)

### Objetivo
Remover por completo o logo **TSA** do projeto (favicon + overlay de loading + logo do login usavam o mesmo path SVG do TSA, `M825.57...` — inclusive o "logo LabGas" do login/loading era o próprio TSA) e substituir pelo ícone LabGas da sidebar: **`bi-moisture`** (gota, Bootstrap Icons 1.11.0) em `#0070b8`. Decisão do usuário: usar o mesmo ícone que aparece na sidebar de abas ao lado do texto "LabGas".

### Correções
- [x] `frontend/static/favicon.svg` — conteúdo substituído: sai o SVG TSA (`id="Camada_1"`, classes `cls-1`, 3 paths/polygon); entra a gota `bi-moisture` em `#0070b8` (`viewBox="0 0 16 16"`); nome do arquivo mantido para não quebrar a referência em `base.html`
- [x] `frontend/templates/base.html` — overlay de loading: `viewBox="0 0 1080 1080"` → `"0 0 16 16"` e path TSA → gota (mantém `class="logo-fill"` e animação `fillUp` com `var(--primary)`)
- [x] `frontend/templates/login.html` — logo do login: mesma troca (gota 36×36, `class="logo-fill"`)
- [x] `CHANGELOG.md`
- [x] Verificação: `grep` por `M825.57|TSA|Camada_1|cls-1` → 0 resultados; favicon servido com conteúdo novo; testes do dashboard passando

### Observação
- `register.html:33` e a sidebar (`base.html:514,520`) já usavam a gota `bi-moisture` — agora o favicon, o loading e o login ficam consistentes com eles.

## Fase 84: Corrigir filtros das abas — bugs identificados (planejado) 🔍

### Objetivo
Corrigir os problemas reais encontrados nos filtros das abas após a padronização da Fase 81. Todos os itens foram **verificados** com análise de código (arquivo:linha) — nenhum foi implementado ainda, este é o plano.

### Decisões do usuário (2026-08-07)
1. **Histórico (item abaixo de Segurança):** não-dev (incluindo admin) vê somente as **próprias** ações via `.eq("user_id", ...)`; dev vê tudo (branch global mantido). Aprovado — substitui o design anterior (log global).
2. **Pressão — stats (item Consistência/UX):** manter as estatísticas de cor (média/desvio) calculadas sobre o **conjunto filtrado** (decisão da Fase 71, confirmada). **Sem mudança de código** — apenas documentar no TODO.
3. **Cilindro — busca server-side (item Consistência/UX):** **Migration + índice funcional** — coluna gerada `numero_txt` (`LPAD(numero::text, 3, '0')`) + índice GIN `pg_trgm`; busca via `or_("numero.eq.{num},numero_txt.ilike.%{q}%")`. **Redis foi avaliado e descartado** (ver Fase 86).

### Segurança (fazer primeiro)
- [ ] `frontend/blueprints/elemento.py:196-197` — dropdown de elementos não filtra por `user_id` (vaza elementos de todos os usuários); aplicar o padrão `if not dev:` usado nos demais blueprints
- [ ] `frontend/blueprints/historico.py:82` — query do Histórico sem `.eq("user_id")` para não-dev: usuário comum enxerga o log de auditoria completo; filtrar por `user_id` mantendo o branch dev (**decisão**: não-dev vê só as próprias ações; dev vê tudo)
- [ ] `frontend/blueprints/historico.py:57` — `q` cru (sem escapar `%`/`_`) no branch de `ilike` simples, inconsistente com a sanitização da L51; padronizar

### Admin
- [ ] `frontend/blueprints/admin.py:61-79` — contagem de usuários sempre 0: `r.get("count", 0)` lê de linhas que não possuem campo `count` (o total real está no envelope `response.count` da resposta)
- [ ] `frontend/blueprints/admin.py:93,342` + `frontend/blueprints/helpers.py:155-164` — `get_habilitar_abas()` nunca consulta o banco (só lê `session['cached_user_info']` do admin logado): as "Permissões de Acesso" do usuário alvo aparecem todas habilitadas; ler a coluna real `habilitar_abas` do usuário

### Datas e paginação
- [ ] `frontend/blueprints/historico.py:75` / `admin.py:310-311` — `lte("created_at", "YYYY-MM-DD")` sobre timestamp exclui os registros do último dia após 00:00; usar `lt(data_fim + 1 dia)` ou normalizar
- [ ] `frontend/blueprints/helpers.py:136` — `(total + per_page - 1) // per_page` → `ZeroDivisionError` com `?per_page=0`
- [ ] `frontend/blueprints/cilindro.py:263-294` — sem clamp de `page`/`per_page`: `page=0` → offset negativo; `per_page=0` → `range(0,-1)`; padronizar com `consultar_paginado` ou clamp explícito em todas as abas

### Consistência / UX
- [ ] `frontend/blueprints/pressao.py:334-340` — `montar(query_stats)` reaplica os filtros às estatísticas de cor (média/desvio mudam com o filtro ativo → badges de cor inconsistentes com a linha); **decisão**: manter stats sobre o conjunto filtrado — **sem mudança de código**, só documentar
- [ ] `frontend/app.py:205-214` — `qs()` concatena `{k}={v}` cru sem URL-encoding (valores com `&`/espaço quebram a query string); usar `urlencode`
- [ ] `frontend/blueprints/cilindro.py:272-278` — scan completo `(id, numero)` de todos os cilindros a cada tecla para busca substring; **decisão**: busca SQL server-side com coluna gerada `numero_txt` + índice GIN `pg_trgm` (migration `20260807`); detalhes na Fase 86

### Verificação
- [ ] Testes por aba (segurança de dados + filtros) + `test_dashboard` 8/8
- [ ] `CHANGELOG.md` + `README.MD`

## Fase 85: Backup preserva schema + RLS (pg_dump schema-only) 💾🔒

**Motivo (auditoria 2026-08-06):** o backup atual (`scripts/backup_db.py`) exporta **apenas dados** (JSON → `.json.gz` → R2). O campo `_schema` é só um SHA256 das colunas (`name, data_type, is_nullable, column_default`). Consequências:
- Zero DDL no dump: sem `CREATE TABLE/INDEX/FUNCTION`, sem `CREATE POLICY`, sem `ENABLE ROW LEVEL SECURITY`.
- `--check-hash` pode **pular backups** quando só schema/policies mudam (linhas inalteradas).
- Restore (`restore_db.py`) só faz DELETE/INSERT — assume que o schema já existe.

**Plano de alterações:**
- [ ] `scripts/backup_db.py`: gerar dump de schema (`pg_dump --schema-only --no-owner --no-privileges -n public`); fallback via `pg_catalog` quando `pg_dump` não estiver instalado; gravar em `backup["schema"]` e incluir `__schema__` no hash por tabela (fecha a brecha do `--check-hash`)
- [ ] `scripts/backup_db.py`: adicionar `historico_login` a `PUBLIC_TABLES` + guarda para tabela ausente (warn + `backup["missing_tables"]`, não falhar)
- [ ] `scripts/restore_db.py`: adicionar `public.historico_login` a `DELETE_ORDER`/`INSERT_ORDER`
- [ ] `database/rls.sql`: tornar fonte única executável e idempotente — `CREATE OR REPLACE FUNCTION public.is_dev()`, `ENABLE ROW LEVEL SECURITY` nas 8 tabelas, policy de `historico_login`, `DROP POLICY IF EXISTS` antes de cada `CREATE POLICY`
- [ ] `.github/workflows/daily-backup.yml`: instalar `postgresql-client` (binário `pg_dump` no runner)
- [ ] Testes (`frontend/tests/test_backup.py`) + docs (`README.MD` seção Backup/Restore)

**Critérios de sucesso:**
- Dump contém schema e policies RLS (artefato com `backup["schema"]`).
- Nenhuma tabela com RLS fica sem policies exportadas.
- Restore documentado: aplicar `schema.sql` + migrations + `rls.sql` **antes** de `restore_db.py`.

## Fase 85b: Backup quebrado por RLS + policies stale em produção (correção) 🚨🔒

**Motivo (verificação 2026-08-07):** ao auditar a Fase 85 contra o banco vivo descobriu-se que o backup de **dados** estava gerando **dumps vazios** e que o banco estava dessincronizado do `rls.sql`:

- `scripts/backup_db.py` conecta como `backup_user`, criado com `NOBYPASSRLS` (`setup_backup_user.py`). Com as policies dev-aware (`auth.uid() = user_id OR is_dev()`), um role sem sessão vê **0 linhas** — os backups R2 (0.01 MB desde 2026-07-11) estavam vazios. O único backup com dados (2026-06-20) é anterior ao fechamento do RLS. O banco vivo **tem dados** (perfil 4, cilindro 14, elemento 23, leitura 216, pressao 22, amostra 28, amostra_elemento 159, historico_auditoria 351) — confirmado via `postgres` (superuser).
- `_introspect_schema` dropa as policies: a linha `cur.execute("SELECT oid, rolname FROM pg_roles")` sobrescreve o result set das policies → `cur.fetchall()` posterior devolve vazio → fallback sem nenhum `CREATE POLICY`.
- Banco vivo stale vs `rls.sql`: `perfil` UPDATE policy = `USING true WITH CHECK true` (furo: qualquer autenticado edita qualquer perfil); `leitura` com nomes antigos (`... amostra`); `historico_login` **não existe** (migration 20260620 nunca aplicada em produção).

**Plano de alterações:**
- [x] `ALTER ROLE backup_user BYPASSRLS` no banco vivo (via `DATABASE_URL_POSTGRES`) + `setup_backup_user.py` com `BYPASSRLS` (CREATE e ALTER idempotente)
- [x] `scripts/backup_db.py`: corrigir `_introspect_schema` — `pg_roles` em cursor separado para não descartar as policies; teste unitário cobrindo o bug
- [x] `scripts/apply_rls.py` (novo): aplica `20260620_add_login_history.sql` (se tabela ausente) + `database/rls.sql` (idempotente) via `DATABASE_URL_POSTGRES`
- [x] Aplicar no banco vivo: migration 20260620 + `rls.sql` → perfil UPDATE seguro, leitura renomeada, `historico_login` + policy (28 → 29 policies)
- [x] Rodar backup real e **comparar**: dados não-zero + 29 `CREATE POLICY` no schema
- [x] Docs: CHANGELOG (entrada 85b + nota na 2.20.4), README (`setup_backup_user`/BYPASSRLS), TODO

**Critérios de sucesso:**
- Backup de dados volta a conter todas as linhas (contagem `backup_user` == `postgres`).
- Dump de schema contém as 29 policies.
- `perfil` UPDATE policy em produção = `USING (auth.uid() = id) WITH CHECK (auth.uid() = id)`.
- `historico_login` presente em produção com policy `admins_select_historico_login`.

## Fase 86: Otimização de buscas e seletores de todas as abas (planejado) ⚡

### Objetivo
Eliminar os scans Python por tecla e os re-fetches de dropdowns nas buscas/seletores de **todas** as abas, integrado às decisões já fechadas da Fase 84. Nada foi implementado ainda — este é o plano.

### Diagnóstico consolidado (2026-08-07, verificado no código)
**Buscas com scan Python / re-fetch por tecla:**
- `cilindro.py:272-278` — `q`: fetch de todos `(id, numero)` + `numero_corresponde` em Python
- `pressao.py:269` — `q_numero`: scan Python do dropdown `cilindro_list` (L28-34) a cada tecla
- `leitura.py:261-272` — `q`: scan Python dos arrays cilindro (numero) + elemento (nome substring)
- `amostra.py:246-259` — `q`: fetch extra de TODAS as amostras (`todas_amostras`, L246-249) + substring Python; confirmado que `todas_amostras` **não vai ao template** → pode ser removido
- `historico.py:44-57` — `label ilike` já é server-side; falta sanitização de `q` (Fase 84) e índice GIN

**Seletores (dropdowns) sem cache — 1-2 queries DB por requisição, inclusive a cada tecla do debounce:**
- pressao (`cilindro_list`), leitura (cilindro+elementos), amostra (`elementos_disponiveis`), elemento (`todos_elementos`)
- `cache_utils.py` confirma: cache de listas **nunca foi implementado** (Fase 45) — só `dashboard:{user_id}`/`dashboard:all`; as chaves `{prefix}:{user_id}` estão livres e são exatamente as que `invalidate_user_caches`/`invalidate_cache` já apagam (cache_utils.py:40) → cache de seletores casa com a invalidação existente, sem mudança nela
- Filtro da aba Elemento é um `<select>` (elemento.html:46), não uma busca → otimização = filtro `user_id` (Fase 84) + cache, sem mudança de comportamento

**Índices já existentes (sem conflito):** `amostra_elemento(elemento_id)` em schema.sql:124; `historico_auditoria.label` **sem índice**; `amostra.numero_amostra`/`amostra.lote` são INTEGER (schema.sql:84-85) → colunas geradas válidas.

### Decisões do usuário (2026-08-07)
1. **Amostra — busca:** opção 1 (server-side com colunas geradas). **Análise de Redis solicitada e respondida:** Redis **não está provisionado** (`.env.example:28` — opcional; app roda em Vercel serverless, `vercel.json` → `@vercel/python`, SimpleCache por instância; `REDIS_URL` só é lido pelo flask-limiter com default `memory://`). Adotar Redis para busca = cachear a lista pesquisável e varrer em Python → continua O(N) por tecla, só troca a origem (DB→Redis). **Recomendação aceita:** manter colunas geradas + `pg_trgm` (server-side, mais rápido e correto); Redis ficaria como opt-in **apenas no cache** (`CACHE_TYPE=RedisCache` + `CACHE_REDIS_URL`) se um dia houver necessidade de consistência entre instâncias — sem tocar nas buscas.
2. **Cache de seletores:** **aprovado** — cache por usuário com TTL 5 min, chave `{prefix}:{user_id}`, invalidação já coberta pelos CRUDs.

### Migration (única): `database/migrations/20260807_otimizacao_buscas.sql` (aplicar no SQL Editor do Supabase)
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Decisão Fase 84 (cilindro): coluna gerada + índice funcional
ALTER TABLE cilindro
  ADD COLUMN IF NOT EXISTS numero_txt TEXT
  GENERATED ALWAYS AS (LPAD(numero::text, 3, '0')) STORED;
CREATE INDEX IF NOT EXISTS idx_cilindro_numero_txt_gin
  ON cilindro USING gin (numero_txt gin_trgm_ops);

-- Busca leitura/elemento por nome (substring)
CREATE INDEX IF NOT EXISTS idx_elemento_nome_gin
  ON elemento USING gin (nome gin_trgm_ops);

-- Busca amostra por número/lote
ALTER TABLE amostra
  ADD COLUMN IF NOT EXISTS numero_amostra_txt TEXT
    GENERATED ALWAYS AS (LPAD(numero_amostra::text, 3, '0')) STORED,
  ADD COLUMN IF NOT EXISTS lote_txt TEXT
    GENERATED ALWAYS AS (lote::text) STORED;
CREATE INDEX IF NOT EXISTS idx_amostra_numero_amostra_txt_gin
  ON amostra USING gin (numero_amostra_txt gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_amostra_lote_txt_gin
  ON amostra USING gin (lote_txt gin_trgm_ops);

-- Busca histórico por label (com sanitização da Fase 84)
CREATE INDEX IF NOT EXISTS idx_historico_aud_label_gin
  ON historico_auditoria USING gin (label gin_trgm_ops);
```
Schema change é **aditiva e segura** (colunas geradas + índices, sem reescrever dados; rollback = `DROP COLUMN/INDEX`). Aplicada muda o hash de schema → o próximo `daily-backup` detecta mudança e gera backup completo (comportamento esperado; `_pg_dump_schema`/restore já cobrem colunas geradas).

### Buscas server-side (remover scans Python)
- [ ] `cilindro_utils.py` — helper `_sanitizar_busca(q)`: remove `,()%_` (não quebra a gramática do `or_` do PostgREST)
- [ ] `cilindro.py:272-278` — trocar scan por `or_("numero.eq.{num},numero_txt.ilike.%{q}%")` (via `normalizar_numero_cilindro`); q não-numérico → só `ilike`
- [ ] `pressao.py:269` — `q_numero`: lookup de ids via `numero_txt` **hoisted antes do `montar`** (montar roda 2×: count+data); mantém `.in_`
- [ ] `leitura.py:261-272` — `q`: 2 lookups hoisted (cilindro via `numero_txt`; elemento via `nome ilike`) → `montar` só monta o `or_` com os ids
- [ ] `amostra.py:246-259` — `q`: `or_("numero_amostra_txt.ilike.%{q}%,lote_txt.ilike.%{q}%")`; **remover o fetch `todas_amostras`** (L246-249)
- [ ] `historico.py:44-57` — sanitização de `q` (Fase 84) → passa a usar o GIN novo

### Seletores com cache por usuário
- [ ] `cache_utils.py` — helper `obter_selectores_cached(prefixo, user_id, fetch_func, timeout=300)` com chave `f"{prefixo}:{user_id}"`
- [ ] Aplicar em: pressao (cilindro), leitura (cilindro+elementos), amostra (`elementos_disponiveis`), elemento (`todos_elementos`)
- [ ] `elemento.py:196-197` — aplicar também o filtro `user_id` (`if not dev:`) junto com o cache (Fase 84 #1)
- [ ] Invalidação: **sem mudanças** — `invalidate_user_caches`/`invalidate_cache` já apagam `{prefix}:{user_id}` a cada CRUD; TTL 5 min cobre edições externas

### Fase 84 restante (ordem A→F já acordada)
Itens de Segurança (1-3), Admin (4-5), Datas e paginação (6-8), Consistência/UX (10) e Verificação (testes + docs), conforme checklist acima. Pressão stats (item 9) fica documentado como decisão, sem código.

### Verificação
- [ ] Equivalência dos testes de cilindro com a busca server-side (`?q=5` → 5 e 15; `?q=CIL-015` → 15)
- [ ] Testes novos: amostra `q` (número/lote), leitura `q`, pressao `q_numero`, invalidação do cache de seletores
- [ ] Suíte por arquivo isolado em `frontend` (venv) permanece verde
- [ ] `CHANGELOG.md` (v2.21.x) + `README.MD` + `schema.sql`/`DIAGRAM.MD` (colunas novas) + TODO
- [ ] Docs: ressalva Vercel no cache de seletores (staleness ≤5 min por instância) + nota do backup full no próximo cron

## Fase 87: Melhoria de exportação e registro no histórico (concluído) ✅

### Objetivo
Padronizar nomenclatura de arquivos exportados e registrar todas as exportações no histórico de auditoria, exibindo na aba Histórico.

### Alterações implementadas

#### 1. Padrão de nomenclatura de arquivos
- **Antes:** `labgas_export_YYYY-MM-DD_HHMMSS_User_Name.ext`
- **Depois:** `labgas_export_YYYYMMDD_HHMMSS_User_Name.ext`
- Mais compacto, mantém legibilidade e ordenação cronológica

#### 2. Registro no histórico de auditoria
- Nova `tipo`: `"exportacao"` (com ícone `download` e cor teal `#0d9488`)
- Nova `acao`: `"exportado"` (badge teal na aba Histórico)
- `detalhe` JSONB contém `formato` e `filename` para rastreabilidade completa
- Ação registrada **antes** da geração do arquivo (garante registro mesmo se a geração falhar)

#### 3. Atualizações nos templates
- `historico.html`: filtro de tipo inclui "Exportação", ação inclui "Exportado"
- `admin_user_data.html`: mesmos filtros adicionados para consistência
- Badges de ação: `exportado` usa cor teal `#0d9488`

#### 4. Constantes
- `constants.py`: `ICON_TIPO["exportacao"] = "download"` e `COR_TIPO["exportacao"]` com gradiente teal

#### 5. Testes
- `test_export.py`: novo teste `test_export_registers_in_history` verifica que a exportação aparece no histórico

### Arquivos modificados
- `frontend/blueprints/admin.py` — padrão de filename + `registrar_historico()`
- `frontend/blueprints/historico.py` — `TIPOS_VALIDOS` e `ACOES_VALIDAS` expandidos
- `frontend/utils/constants.py` — `ICON_TIPO` e `COR_TIPO` para `exportacao`
- `frontend/templates/historico.html` — filtros de tipo/ação + badge teal
- `frontend/templates/admin_user_data.html` — filtros de tipo/ação + badge teal
- `frontend/tests/test_export.py` — teste de registro no histórico

## Fase 88: Correção do loading infinito + melhorias nas exportações (concluído) ✅

### Objetivo
Corrigir o bug de loading infinito ao baixar exportações e padronizar a distribuição de dados nos 4 formatos (JSON, CSV, Excel, Markdown) seguindo boas práticas (RFC 4180 para CSV, formatação para Excel).

### Bugs corrigidos

#### 1. Loading infinito no download (CRITICAL)
- **Causa**: links de exportação são `<a>` tags que disparam `showLoadingDelayed()` no handler global de `click`, mas a resposta `Content-Disposition: attachment` não navega a página → `pageshow` nunca dispara → overlay fica preso
- **Correção**: adicionar `data-no-loading` nos 4 links de exportação em `dashboard.html`

#### 2. CSV: coluna "elementos" das amostras sempre vazia (CRITICAL)
- **Causa**: header diz `"elementos"` mas a chave no dict é `"elementos_nomes"` → `row.get("elementos")` retorna `""` 
- **Correção**: usar `csv.writer` com headers corretos

#### 3. CSV sem módulo csv (RFC 4180) (HIGH)
- **Causa**: writing manual com `",".join()` não trata vírgulas, aspas ou quebras de linha
- **Correção**: substituir por `csv.writer` com `io.StringIO`

#### 4. sanitize_csv aplicado parcialmente (MEDIUM)
- **Causa**: só cilindros/elementos usavam `sanitize_csv` — leituras, pressões e amostras ficavam sem proteção
- **Correção**: aplicar em todas as tabelas

### Melhorias implementadas

#### 5. Excel — formatação profissional
- Largura de colunas automáticas baseada no maior valor
- `auto_filter` na aba Resumo para ordenação
- Formatação numérica: custo como moeda (R$ #,##0.00), litros com 1 decimal

#### 6. JSON — campo versão
- Adicionado `"versao": "2.21.0"` para compatibilidade futura

#### 7. Markdown — colunas consistentes + escape
- Colunas adicionadas: `data_compra`, `data_inicio_consumo`, `data_fim`, `litros_equivalentes`, `usuario_nome`, `created_at`
- Escape de `|` nos valores para não quebrar tabelas

#### 8. Testes atualizados
- `test_export_csv` valida conteúdo com `csv.reader` (não só substring)
- `test_export_json` valida campo `versao`

### Arquivos modificados
- `frontend/templates/dashboard.html` — `data-no-loading` nos links de exportação
- `frontend/blueprints/admin.py` — reescrita do bloco CSV (módulo csv), correção header amostras, Excel com formatação, JSON com versão, Markdown com colunas consistentes
- `frontend/tests/test_export.py` — asserts atualizados

## Fase 89: Validação manual + suíte de testes + relatório roadmap (planejado) 🔍🧪

### Objetivo
Validar manualmente as atividades recentes (Fases 87-88), atualizar a suíte de testes unitários e globais, e criar um relatório/roadmap visual do estado atual dos testes seguindo boas práticas.

### Parte 1: Validação manual das atividades recentes

#### Exportação (Fases 87-88)
- [ ] Testar download JSON → verificar campo `versao`, KPIs, todas as 5 tabelas
- [ ] Testar download CSV → verificar com `csv.reader` que todos os campos preenchem (especialmente `elementos_nomes` nas amostras)
- [ ] Testar download Excel → verificar largura de colunas, `auto_filter`, valores numéricos
- [ ] Testar download Markdown → verificar colunas de cilindros (data_compra, litros, etc.), escape de `|`
- [ ] Verificar que o loading NÃO aparece ao clicar em exportar
- [ ] Verificar que a exportação aparece na aba Histórico com tipo "Exportação" e ação "Exportado"
- [ ] Testar exportação filtrada por usuário (dev com `selected_user_id`)

#### Histórico (Fase 87)
- [ ] Filtrar por tipo "Exportação" → deve listar exportações
- [ ] Filtrar por ação "Exportado" → deve listar exportações
- [ ] Verificar badge teal no histórico

### Parte 2: Atualizar suíte de testes

#### Testes existentes para atualizar
- [ ] `test_export.py` — validar cobertura dos 4 formatos + histórico + loading
- [ ] `test_admin.py` — garantir que filtros de tipo/acao incluem `exportacao`/`exportado`
- [ ] `test_historico.py` — adicionar testes para o tipo `exportacao` e ação `exportado`

#### Testes novos para criar
- [ ] `test_export_csv_integrity` — valida com `csv.reader` que colunas de amostras têm `elementos_nomes` preenchido
- [ ] `test_export_json_version` — valida que `versao` está presente e correto
- [ ] `test_export_excel_column_widths` — valida que colunas têm largura > 0
- [ ] `test_export_md_consistency` — valida que todas as tabelas têm headers equivalentes ao CSV
- [ ] `test_export_no_loading` — valida que links de exportação têm `data-no-loading` no HTML

#### Testes de regressão
- [ ] Rodar suíte completa (`pytest frontend/tests/ -v`) e registrar resultado
- [ ] Rodar testes de export isolados (`pytest frontend/tests/test_export.py --run-export -v`)
- [ ] Verificar que nenhum teste existente quebrou com as mudanças das Fases 87-88

### Parte 3: Relatório Roadmap de Testes

#### Conceito
Criar um relatório visual/estruturado do estado dos testes, similar a um dashboard de roadmap:

```
┌─────────────────────────────────────────────────────────────┐
│  LABGAS MANAGER — TEST ROADMAP                              │
├──────────────────────┬──────┬──────┬──────┬─────────────────┤
│  Módulo              │ Total│ ✅   │ ❌   │ Cobertura       │
├──────────────────────┼──────┼──────┼──────┼─────────────────┤
│  test_auth           │   7  │  7   │  0   │ ██████████ 100% │
│  test_cilindro       │  12  │ 12   │  0   │ ██████████ 100% │
│  test_pressao        │   5  │  5   │  0   │ ██████████ 100% │
│  test_leitura        │   7  │  7   │  0   │ ██████████ 100% │
│  test_amostra        │   9  │  9   │  0   │ ██████████ 100% │
│  test_elemento       │  12  │ 12   │  0   │ ██████████ 100% │
│  test_dashboard      │   8  │  8   │  0   │ ██████████ 100% │
│  test_export         │   8  │  ?   │  ?   │ ████████░░  ??% │
│  test_historico      │   7  │  7   │  0   │ ██████████ 100% │
│  test_admin          │   2  │  2   │  0   │ ██████████ 100% │
│  test_backup         │  33  │ 33   │  0   │ ██████████ 100% │
│  test_session_footer │   4  │  4   │  0   │ ██████████ 100% │
│  test_helpers        │   4  │  4   │  0   │ ██████████ 100% │
├──────────────────────┼──────┼──────┼──────┼─────────────────┤
│  TOTAL               │ 118  │  ??  │  ??  │ ████████░░  ??% │
└──────────────────────┴──────┴──────┴──────┴─────────────────┘
```

#### Entregáveis
- [ ] Criar `tests/TEST_REPORT.md` ou integrar no README — snapshot do estado dos testes
- [ ] Listar cobertura por módulo (total, passando, falhando, pulado)
- [ ] Marcar testes pendentes de implementação (Fase 89)
- [ ] Incluir data/hora da última execução e versão do commit testado
- [ ] Atualizar o relatório sempre que a suíte rodar (script ou CI)

#### Formato do relatório
- Markdown com tabelas (legível no GitHub)
- Barra de progresso visual com Unicode (`█` / `░`)
- Seções: Resumo Geral, Por Módulo, Testes Novos (Fase 89), Pendências, Histórico de Execuções
- Metadata: commit hash, data, versão, runner (local/CI)

### Arquivos a modificar/criar
- `frontend/tests/test_export.py` — testes novos de integridade
- `frontend/tests/test_historico.py` — testes de tipo/acao exportacao
- `frontend/tests/test_admin.py` — validação de filtros expandidos
- `tests/TEST_REPORT.md` — relatório roadmap (novo)
- `scripts/run_tests.sh` ou `Makefile` — comando para gerar relatório
- `CHANGELOG.md` — entrada v2.21.2
- `TODO.MD` — marcar como concluído

---

## Fase 67: Correções de Integridade de Dados (RELATORIO_ANALISE) 🔧

### Contexto
Baseado no relatório `RELATORIO_ANALISE_LABGAS_md_2026_09_03T16_42_37.md` (análise do backup `labgas_backup_2026-08-31_20-55-22.json`). Correções de bugs de dados, validações e melhorias de qualidade.

### Fase 1 — Correções de Dados (SQL)

#### 1.1 BUG-01: Cilindro #1 (id=33) com data_fim invertida
- [x] Criar migration `database/migrations/20260903_correcoes_dados.sql`
- [ ] Executar no Supabase: `UPDATE public.cilindro SET data_fim = '2025-09-16' WHERE id = 33;`

#### 1.2 BUG-02: Mercúrio (id=69) com consumo_lpm = 0
- [x] Correção no `frontend/utils/constants.py` (Mercúrio default 0.5)
- [ ] Executar no Supabase: `UPDATE public.elemento SET consumo_lpm = 0.5 WHERE id = 69;`

#### 1.3 BUG-03: Remover 4 duplicatas exatas
- [ ] Executar no Supabase: `DELETE FROM public.leitura WHERE id IN (112, 121, 154, 159);`
- Duplicatas divergentes (IDs 145/146, 148/149, 197/198, 234/235, 259/260): revisão manual necessária

#### 1.4 BUG-04: Leituras fora do período
- [ ] Cil #5 (id=37): `UPDATE public.cilindro SET data_fim = '2025-12-23' WHERE id = 37;`
- [ ] Cil #9 (id=41) → Cil #8 (id=40): `UPDATE public.leitura SET cilindro_id = 40 WHERE id = 194;`
- [ ] Cil #13 (id=151): `UPDATE public.cilindro SET data_fim = '2026-07-16' WHERE id = 151;`

#### 1.5 BUG-05: Permissões admin
- [ ] Executar no Supabase: habilitar todas as abas para `a908e61d-ac27-4ba1-af2a-698836aab07b`

### Fase 2 — Validações no Código ✅

- [x] 2.1 Validação `consumo_lpm > 0` em `frontend/blueprints/elemento.py` (create + update)
- [x] 2.2 Validação `data_fim >= data_inicio_consumo` em `frontend/blueprints/cilindro.py` (create + update)
- [x] 2.3 Override de permissões admin/dev em `frontend/blueprints/helpers.py` (já existia, documentado)
- [x] 2.4 Validação período da leitura vs cilindro em `frontend/blueprints/leitura.py` (create + update)

### Fase 3 — Melhorias ✨

- [x] 3.1 `helpers.py::registrar_historico` — detalhe obrigatório para 'atualizado' (flag `_incomplete`)
- [x] 3.2 Migrations de constraints: `database/migrations/20260903_constraints_validacao.sql`
- [x] 3.2 Migration trigger período: `database/migrations/20260903_trigger_leitura_periodo.sql`
- [x] 3.3 Alerta de pressão para cilindro ativo: `helpers.py::verificar_alerta_pressao` + dashboard
- [x] 3.4 Flag retroativo: `database/migrations/20260903_flag_retroativo.sql`

### Arquivos Modificados

| Arquivo | Ação |
|---------|------|
| `frontend/blueprints/elemento.py` | Validação consumo_lpm > 0 |
| `frontend/blueprints/cilindro.py` | Validação data_fim >= data_inicio |
| `frontend/blueprints/leitura.py` | Validação período leitura vs cilindro |
| `frontend/blueprints/helpers.py` | Registrar histórico com detalhe obrigatório + alerta pressão |
| `frontend/app.py` | Dashboard inclui alerta_pressao |
| `frontend/templates/dashboard.html` | Exibe alerta de pressão |
| `frontend/utils/constants.py` | Mercúrio default 0.5 |
| `database/migrations/20260903_correcoes_dados.sql` | SQL Fase 1 (executar no Supabase) |
| `database/migrations/20260903_constraints_validacao.sql` | Constraints DB |
| `database/migrations/20260903_trigger_leitura_periodo.sql` | Trigger período leitura |
| `database/migrations/20260903_flag_retroativo.sql` | Flag retroativo |
| `.gitignore` | + RELATORIO_ANALISE + prompts/ |

### Pendências
- [x] Testes executados e passando (4+7+18+12+20+8+6+41+41=testes locais validados)
- [x] **Backup prévio criado**: `backups/labgas_backup_2026-09-03_18-19-59.json.gz`
- [x] **Executado no Supabase** — `20260903_correcoes_dados.sql` (BUG-01, BUG-02, exatas 112/121/154/159, BUG-04, BUG-05) + correção leitura 194 → Cil#7 (id=39)
- [x] **Executado no Supabase** — `20260903_flag_retroativo.sql` (adic. coluna retroativo; 132 marcadas)
- [x] **Executado no Supabase** — constraints VAL-01, VAL-02, pressão/temp/quantidade (**VAL-03 adiado**)
- [x] **Executado no Supabase** — `20260903_trigger_leitura_periodo.sql` (função + trigger ATIVO)
- [x] Validação pós-correção OK: datas=0, consumo≤0=0, fora-do-período=0, duplicatas-exatas=0; total 219 leituras
- [ ] **BUG-03 — 5 duplicatas DIVERGENTES (aguardando decisão manual — investigar origem antes de excluir):**
      - Par 1 — Ferro @2026-01-22 (Cil#6): manter 145(48)/excluir 146(37)
      - Par 2 — Zinco @2026-01-23 (Cil#6): manter 148(48)/excluir 149(47)
      - Par 3 — Cromo @2026-03-13 (Cil#9): manter ??? / excluir ??? — created_at quase iguais, decidir 197(25) vs 198(45)
      - Par 4 — Manganês @2026-04-22 (Cil#11): manter 234(24)/excluir 235(24, tempo difere)
      - Par 5 — Zinco @2026-05-27 (Cil#12): manter 259(37)/excluir 260(27)
      - Todos do mesmo user_id (a908e61d). Histórico de auditoria não registrou essas leituras (não auxilia).
- [ ] **VAL-03 (idx_leitura_unique) — BLOQUEADO pelas 5 divergentes:** só aplicar após resolver os pares, senão a criação do índice falha.
- [ ] Testar tudo localmente antes de push

