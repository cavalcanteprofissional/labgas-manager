# Artigo - LabGas Manager

## Sistema de Gestão e Rastreabilidade para Laboratórios Químicos

Este diretório contém os arquivos LaTeX para publicação do artigo científico.

---

## Arquivos

| Arquivo | Descrição |
|--------|-----------|
| `artigo.tex` | Documento principal LaTeX |
| `referencias.bib` | Referências BibTeX |
| `figuras/` | Imagens das figuras do artigo |
| `codigo/` | Listagens de código |

---

## Como Usar no Overleaf

### Opção 1: Upload Manual

1. Acesse [overleaf.com](https://www.overleaf.com)
2. Crie um novo projeto em branco
3. Faça upload dos arquivos:
   - `artigo.tex`
   - `referencias.bib`
4. Crie as pastas `figuras/` e `codigo/` no Overleaf
5. Faça upload das imagens necessárias
6. Compile com **PDFLaTeX**

### Opção 2: Git (Avançado)

1. Clone o repositório no Overleaf (funcionalidade nativa)
2. Os arquivos serão sincronizados automaticamente

---

## Imagens Necessárias

| Figura | Arquivo | Descrição |
|--------|---------|-----------|
| Figura 1 | `figuras/figura1_arquitetura.png` | Arquitetura do Sistema LabGas Manager |
| Figura 2 | `figuras/figura2_navegacao.png` | Fluxo de Navegação entre Abas |

### Como Gerar as Imagens

Os diagramas Mermaid do artículo podem ser convertidos para PNG usando:

1. **Mermaid Live Editor** (online):
   - Acesse: https://mermaid.live
   - Copie o código do diagrama
   - Exporte como PNG

2. **VS Code** (extensão):
   - Instale a extensão "Mermaid Preview"
   - Exporte o diagrama

---

## Estrutura do Diretório

```
latex/
├── artigo.tex           # Artigo principal
├── referencias.bib     # Referências BibTeX
├── figuras/            # Imagens
│   ├── figura1_arquitetura.png
│   └── figura2_navegacao.png
├── codigo/             # Listagens de código
│   └── permissoes.json
└── readme.md          # Este arquivo
```

---

## Compilação Local (Opcional)

Se preferir compilar localmente:

```bash
# Instale uma distribuição LaTeX
# (MiKTeX, TeX Live, ou MacTeX)

# Compilar com bibtex
pdflatex artigo
bibtex artigo
pdflatex artigo
pdflatex artigo
```

---

## Referências

O arquivo `referencias.bib` contém 21 referências nos formatos:

- `@book` - Livros e normas
- `@article` - Artigos científicos
- `@techreport` - Relatórios técnicos (RFC)
- `@misc` - Recursos online

---

## License

Este artigo está disponível para fins acadêmicos.

---

**Autor:** Lucas Cavalcante dos Santos e Thiago Bricio Pinheiro Sandre  
**Data:** Abril de 2026

**Repositório do Projeto:** https://github.com/cavalcanteprofessional/labgas-manager