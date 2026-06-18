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
Revisão completa de segurança baseada na `ANALISE_SEGURANCA.MD` (v1.4.1) versus estado atual (v2.6.16).
Itens já corrigidos desde o relatório original foram marcados como ✅. Os pendentes seguem listados abaixo com severidade, localização e recomendação técnica.

---

### 🔴 CRÍTICOS

#### 1. IDOR em DELETE via get_admin_client() — ⚠️ PENDENTE
**Localização:** `cilindro.py:165`, `elemento.py:96`, `amostra.py:139`
**Problema:** Operações DELETE usam `get_admin_client()` (service_role, bypass RLS) sem verificar se o registro pertence ao usuário logado. Qualquer usuário autenticado pode deletar dados de terceiros.
**Recomendação:** Antes do DELETE, fazer SELECT do `user_id` com `get_supabase_client()`, comparar com `get_user_id()`, e só então executar o DELETE com admin client.
**Mitigação atual:** O frontend só expõe registros do próprio usuário (filtro por `user_id` na query), mas a API backend não valida no servidor. Um request malicioso via curl/Postman contorna o frontend.

---

### 🟠 ALTOS

#### 2. Sem HSTS / CSP / Security Headers em Produção — ⚠️ PENDENTE
**Localização:** `app.py:121-140` (`after_request`)
**Problema:** Apenas `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` em produção. Faltam:
- `Strict-Transport-Security` (HSTS) — evitar downgrade HTTP
- `Content-Security-Policy` — mitigar XSS
- `Permissions-Policy` — controlar APIs do browser
**Recomendação:** Adicionar no `after_request`:
```python
response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
response.headers['Content-Security-Policy'] = "default-src 'self' ..."
response.headers['Permissions-Policy'] = 'geolocation=()'
```

#### 3. Flask Debug Mode Acessível em Produção — ⚠️ PENDENTE
**Localização:** `app.py:512`
```python
debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
app.run(host="0.0.0.0", port=port, debug=debug)
```
**Problema:** Se `FLASK_DEBUG=true` for acidentalmente configurado na Vercel, o debugger do Werkzeug fica exposto, permitindo execução remota de código (RCE).
**Recomendação:** Forçar `debug=False` em produção:
```python
if os.getenv('VERCEL_ENV') == 'production':
    debug = False
```

#### 4. CORS Permissivo Demais — ⚠️ PENDENTE
**Localização:** `app.py:121-129`
**Problema:** `ALLOWED_ORIGINS=*` é o default. `Access-Control-Allow-Origin: *` liberado sem restrição de origens confiáveis.
**Recomendação:** Remover suporte a `*` em produção; exigir lista explícita de origens.

---

### 🟡 MÉDIOS

#### 5. Validação de Role Ausente — ⚠️ PENDENTE
**Localização:** `admin.py:97`
```python
role = request.form.get("role")  # Sem validação!
```
**Recomendação:** Validar contra whitelist `["admin", "usuario"]` e garantir que apenas admins possam alterar roles.

#### 6. Validação de Status Ausente — ⚠️ PENDENTE
**Localização:** `cilindro.py:30,95`
```python
status = request.form.get("status", "ativo")  # Qualquer string aceita
```
**Recomendação:** Validar contra `utils.constants.STATUS_VALIDOS` ou whitelist inline.

#### 7. Perfil UPDATE Policy Insegura — ⚠️ PENDENTE
**Localização:** `database/rls.sql:79`
```sql
CREATE POLICY "Users can update own perfil" ON perfil
    FOR UPDATE USING (true) WITH CHECK (true);
```
**Problema:** Qualquer usuário autenticado pode alterar o `role` ou `habilitar_abas` de qualquer perfil via UPDATE direto.
**Recomendação:** Restringir `USING (auth.uid() = id)` e `WITH CHECK (auth.uid() = id)`. Admin deve usar service_role.

#### 8. JWT Validation usa app.secret_key — ⚠️ PENDENTE
**Localização:** `admin.py:26`
```python
decoded = jwt.decode(token, current_app.secret_key, algorithms=["HS256"])
```
**Problema:** Usa a mesma chave de sessão Flask para validar JWTs de usuário. Idealmente o JWT deve usar uma chave dedicada ou ser validado pelo Supabase Auth.
**Recomendação:** Validar JWT via `supabase.auth.get_user(token)` em vez de decodificar localmente.

#### 9. Auth Endpoints sem Rate Limit Específico — ⚠️ PENDENTE
**Localização:** `auth.py` (login/register)
**Problema:** O rate limit global (200/hora) protege de forma genérica, mas não há limite restrito específico para tentativas de login (ex: 5/min).
**Recomendação:** Adicionar `@limiter.limit("5 per minute")` nas rotas POST de login e register.

---

### 🟢 BAIXOS

#### 10. cache_utils.py não Integrado — ⚠️ PENDENTE
**Localização:** `utils/cache_utils.py`, `blueprints/*.py`
**Problema:** O módulo de cache foi criado com funções como `invalidate_user_caches`, mas nenhum blueprint chama essas funções. Cache está inoperante.
**Recomendação:** Chamar `invalidate_user_caches(user_id)` após cada CREATE/UPDATE/DELETE nos 5 blueprints de domínio.

#### 11. Session Cached User Info Pode Ficar Stale — ⚠️ PENDENTE
**Localização:** `app.py:151-173`
**Problema:** `cached_user_info` na session é populado uma vez (primeiro request) e nunca atualizado até o usuário fazer logout. Se um admin alterar a role do usuário, a mudança só reflete após relogin.
**Recomendação:** Invalidar o cache da session quando `perfil` for alterado, ou recarregar a cada request (trocando session por cache do flask-caching).

#### 12. Logging Pode Expor Dados Sensíveis — ⚠️ PENDENTE
**Localização:** `app.py:61-62`, `blueprints/helpers.py`
```python
logging.basicConfig(level=logging.INFO)
logger.info(f"Histórico registrado: {tipo} | {acao} | {nome} | User: {user_id}")
```
**Problema:** Em produção com nível DEBUG, dados como tokens JWT ou emails podem ser logados.
**Recomendação:** Garantir `level=logging.WARNING` em produção; revisar todas as calls `logger.info`/`logger.debug` para não incluírem dados sensíveis.

#### 13. Vercel sem Security Headers Configurados — ⚠️ PENDENTE
**Localização:** `vercel.json`
**Problema:** Nenhum header de segurança configurado no vercel.json (CSP, HSTS, X-Frame-Options).
**Recomendação:** Adicionar bloco `"headers"` no vercel.json com as políticas de segurança.

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

---

### 📊 Resumo

| Severidade | Pendentes | Corrigidos |
|------------|-----------|------------|
| 🔴 CRITICAL | 1 | 1 |
| 🟠 HIGH | 3 | 1 |
| 🟡 MEDIUM | 5 | 4 |
| 🟢 LOW | 4 | 1 |
| **Total** | **13** | **7** |

### 🎯 Recomendação de Ordem de Implementação

1. 🔴 **IDOR DELETE** — risco imediato de perda de dados
2. 🟠 **HSTS/CSP headers** — segurança de produção
3. 🟠 **CORS restrito** — evitar vazamento cross-origin
4. 🟠 **Debug mode** — risco RCE
5. 🟡 **Role validation** — escalada de privilégio
6. 🟡 **Perfil RLS policy** — escalada de privilégio
7. 🟡 **Auth rate limit** — brute force
8. 🟡 **JWT validation** — falsificação de token
9. Restante (cache, logging, vercel, status) — baixo risco

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
