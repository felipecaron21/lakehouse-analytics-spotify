# Spotify Lakehouse Pipeline — Design Spec

**Date:** 2026-04-21  
**Status:** Approved

---

## Overview

Pipeline de dados que extrai informações públicas da API do Spotify (Top 50 por país), armazena em um lakehouse local com arquitetura medalhão (Bronze/Silver/Gold) usando DuckDB, transforma via dbt, exporta para PostgreSQL e disponibiliza dashboards no Metabase.

---

## Objetivos

- Construir um pipeline de portfólio completo com boas práticas de engenharia de dados
- Demonstrar arquitetura medalhão, orquestração com Airflow e transformações com dbt
- Gerar dashboards com indicadores globais do Spotify: rankings, gêneros, audio features e tendências

---

## Stack

| Ferramenta | Papel |
|---|---|
| Python | Extração da API e scripts de suporte |
| DuckDB | Banco de dados local (arquivo `.duckdb`) |
| dbt | Transformações Silver e Gold |
| Airflow (Docker) | Orquestração — LocalExecutor |
| PostgreSQL (Docker) | Destino do export para o Metabase |
| Metabase (Docker) | Dashboards |
| dbt docs (Docker) | Documentação e lineage dos modelos |

**Memória estimada total Docker:** ~1GB (Airflow LocalExecutor sem Redis/Celery)

---

## Autenticação Spotify

- Fluxo: **Client Credentials** (sem login de usuário)
- Credenciais: `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET` via `.env`
- Criação do app: Spotify Developer Dashboard → Create App → copiar Client ID e Secret

---

## Dados Extraídos

| Endpoint | Descrição | Tabela Bronze |
|---|---|---|
| `/playlists/{id}/tracks` | Top 50 músicas por país (20-30 países) | `raw_top_tracks` |
| `/audio-features` | Dançabilidade, energia, valência, BPM (batch de 100) | `raw_audio_features` |
| `/artists` | Nome, gêneros, popularidade, followers | `raw_artists` |

**Volume estimado por execução:** ~1.500 faixas, ~500 artistas únicos — dentro dos rate limits da API.

**Países:** lista configurável em `extraction/countries.py` com IDs das playlists "Top 50" públicas da Spotify.

---

## Arquitetura

```
Spotify API
    │
    ▼
[DAG 1 — spotify_extraction]  (Airflow, semanal)
    │  Python: auth → playlists → audio_features → artists → loader
    ▼
Bronze Layer (DuckDB)
    │  raw_top_tracks, raw_audio_features, raw_artists
    ▼
[DAG 2 — spotify_transformation]  (Airflow, trigger após DAG 1)
    │  dbt run + dbt test
    ▼
Silver Layer (DuckDB)
    │  stg_tracks, stg_artists
    ▼
Gold Layer (DuckDB)
    │  top_tracks_by_country, top_artists_global, genre_distribution, audio_trends
    ▼
[export/duckdb_to_postgres.py]
    ▼
PostgreSQL  →  Metabase (Dashboards)
```

---

## Camadas do Lakehouse

### Bronze (raw — sem transformação)
- `raw_top_tracks`: posição, track_id, nome da música, artist_id, país, data de carga
- `raw_audio_features`: track_id, dançabilidade, energia, valência, BPM, loudness, acousticness
- `raw_artists`: artist_id, nome, gêneros (array), popularidade, followers

### Silver (limpo e enriquecido — dbt)
- `stg_tracks`: join de raw_top_tracks + raw_audio_features, tipagem correta, deduplicação
- `stg_artists`: gêneros explodidos (1 linha por gênero), campos normalizados

### Gold (métricas para dashboard — dbt)
- `top_tracks_by_country`: ranking semanal por país com variação de posição semana a semana
- `top_artists_global`: artistas com mais presença nos charts, contagem de países simultâneos
- `genre_distribution`: distribuição percentual de gêneros por país e globalmente
- `audio_trends`: médias semanais de energia, dançabilidade e valência por país

---

## Orquestração (Airflow)

**DAG 1 — `spotify_extraction`**
- Schedule: `@weekly`
- Tasks: `auth_check` → `extract_playlists` → `extract_audio_features` → `extract_artists` → `load_to_bronze`
- Em caso de falha: retries = 2, retry_delay = 5min

**DAG 2 — `spotify_transformation`**
- Trigger: `TriggerDagRunOperator` ao final do DAG 1 (ou schedule independente)
- Tasks: `dbt_run_silver` → `dbt_test_silver` → `dbt_run_gold` → `dbt_test_gold` → `export_to_postgres`

---

## Estrutura de Pastas

```
lakehouse-analytics-spotify/
├── docker-compose.yml
├── .env
│
├── airflow/
│   ├── dags/
│   │   ├── spotify_extraction.py
│   │   └── spotify_transformation.py
│   └── plugins/
│
├── extraction/
│   ├── auth.py
│   ├── playlists.py
│   ├── audio_features.py
│   ├── artists.py
│   ├── loader.py
│   └── countries.py
│
├── dbt/
│   ├── models/
│   │   ├── silver/
│   │   └── gold/
│   ├── tests/
│   └── dbt_project.yml
│
├── export/
│   └── duckdb_to_postgres.py
│
└── data/
    └── spotify.duckdb
```

---

## Docker Compose — Serviços

| Serviço | Porta | Memória aprox. |
|---|---|---|
| Airflow (LocalExecutor) | 8080 | ~300MB |
| PostgreSQL | 5432 | ~100MB |
| Metabase | 3000 | ~512MB |
| dbt docs serve | 8081 | ~50MB |

---

## Configuração Inicial (Spotify Developer)

1. Acessar [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Fazer login com conta Spotify
3. Clicar em "Create App"
4. Preencher nome, descrição e Redirect URI (`http://127.0.0.1:8888`)
5. Copiar `Client ID` e `Client Secret` para o arquivo `.env`

---

## Fora do Escopo

- Dados pessoais do usuário (histórico de reprodução, liked songs)
- Streaming em tempo real
- Deploy em cloud
- Testes de carga ou performance
