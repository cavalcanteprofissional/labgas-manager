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
| `public` | perfil, cilindro, elemento, leitura, amostra, amostra_elemento, pressao, historico_log |
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

## Bugfix: `.backup_result.json` não gerado quando `conectar()` falha 🐛

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
