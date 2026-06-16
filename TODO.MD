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

## Sugestões Futuras 🚀

### Exportação
- [ ] Adicionar tabelas `amostra` e `amostra_elemento` nos exports (JSON/CSV/Excel/MD) em `admin.py`
- [ ] Adicionar coluna "Amostras" no cabeçalho da tabela de exportação Markdown

### Dashboard
- [ ] Gráfico de amostras por lote (bar chart)
- [ ] Últimas amostras registradas na seção de atividades recentes
- [ ] Card de total de elementos nas amostras

### Admin
- [ ] Filtro por aba "amostra" no painel admin
- [ ] Coluna "Amostras" na tabela de usuários com contagem

### Geral
- [ ] Badge `h.tipo == 'amostra'` com cor roxa no dashboard (últimas atividades)
- [ ] Teste de criação com elementos selecionados (test_create_amostra_with_elementos)
- [ ] Teste de bulk delete no Playwright
