# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python tool for Instagram data analysis and lead generation targeting aesthetics/health professionals in Maringá, PR, Brazil. The codebase is written entirely in Portuguese (variable names, comments, output messages).

## Commands

```bash
# Run all analyses
python main.py

# Run specific analyses
python main.py --posts          # Post metrics only
python main.py --stories        # Stories metrics only
python main.py --seguidores     # Followers/following analysis only
python main.py --amostra        # Generate sample data, then run all analyses

# Lead generation pipeline
python buscar_leads.py          # Requires GOOGLE_PLACES_KEY env var
python formatar_excel.py        # Convert leads CSV to formatted XLSX

# Generate sample data standalone
python scripts/gerar_amostra.py
```

## Architecture

**Data flow — Instagram analysis:**
```
dados/brutos/*.csv → scripts/analise_*.py → dados/processados/ + saida/
```

**Data flow — Lead generation:**
```
Google Places API → buscar_leads.py → saida/leads_maringá.csv → formatar_excel.py → saida/leads_formatado.xlsx
```

### Key modules

| File | Role |
|------|------|
| `main.py` | CLI orchestrator; dispatches to analysis modules |
| `scripts/utils.py` | Shared path constants, CSV I/O, report writing |
| `scripts/analise_posts.py` | Engagement rate, best posting times, metrics distribution |
| `scripts/analise_stories.py` | Retention rates, stories metrics distribution |
| `scripts/analise_seguidores.py` | Mutual follow analysis, growth trends |
| `scripts/gerar_amostra.py` | Generates fake CSV data for testing |
| `buscar_leads.py` | Google Places API (v1) search + website scraping for Instagram handles |
| `formatar_excel.py` | Formats lead CSV into color-coded XLSX with filters and hyperlinks |

### Input/Output paths

- Raw Instagram exports: `dados/brutos/` (posts.csv, stories.csv, seguidores.csv, seguindo.csv)
- Processed data: `dados/processados/`
- Charts (PNG): `saida/graficos/`
- Text reports: `saida/relatorios/`
- Lead files: `saida/leads_maringá.csv`, `saida/leads_formatado.xlsx`

### Notable implementation details

- CSV columns are normalized on load (lowercase, spaces → underscores) in `utils.py`
- Lead deduplication uses a compound `(name, phone)` key
- `buscar_leads.py` rotates user agents and rate-limits requests to respect scraping limits
- Windows UTF-8 terminal compatibility is handled at startup in `main.py`
- Excel output uses openpyxl with color-coding by professional category and a legend sheet

## Dependencies

`pandas`, `numpy`, `matplotlib`, `seaborn`, `requests`, `beautifulsoup4`, `lxml`, `openpyxl`

Install: `pip install -r requirements.txt`

External: Google Places API key set as `GOOGLE_PLACES_KEY` environment variable.

## GitHub Repository

**URL:** https://github.com/mateusarqxis-design/analise-instagram
**Usuário:** mateusarqxis-design
**Branch principal:** `main`

### Sincronização automática

Todo arquivo criado ou editado pelo Claude Code é automaticamente commitado e enviado ao GitHub via hook configurado em `.claude/settings.json` (evento `PostToolUse` nos tools `Write` e `Edit`).

Para push manual:
```bash
cd "/c/Users/user/analise-instagram"
git add -A
git commit -m "mensagem do commit"
git push origin main
```

O token de acesso está embutido na URL do remote (`git remote -v` para verificar). Para trocar o token:
```bash
git remote set-url origin "https://SEU_TOKEN@github.com/mateusarqxis-design/analise-instagram.git"
```
