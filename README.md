# Spotify Lakehouse Analytics

Pipeline de dados pessoais do Spotify com arquitetura medalhão (Bronze → Silver → Gold), orquestrado com Airflow, transformado com dbt e visualizado no Metabase.

---

## Visão Geral

Extrai seus dados pessoais da API do Spotify (músicas favoritas, artistas favoritos e histórico de reprodução), armazena localmente no DuckDB e gera dashboards com seus padrões de escuta.

```
Spotify API
    │
    ▼
[DAG 1 — spotify_extraction]  (manual)
    │  top tracks + top artists + recently played
    ▼
Bronze Layer (DuckDB)
    │  raw_top_tracks · raw_top_artists · raw_recently_played
    ▼
[DAG 2 — spotify_transformation]  (trigger automático)
    │  dbt run + dbt test
    ▼
Silver Layer (DuckDB)
    │  stg_top_tracks · stg_top_artists · stg_recently_played
    ▼
Gold Layer (DuckDB)
    │  top_tracks_by_period · top_artists_by_period
    │  listening_history · listening_patterns
    ▼
PostgreSQL (spotify_analytics)  →  Metabase Dashboards
```

---

## Stack

| Ferramenta | Papel |
|---|---|
| Python | Extração da API do Spotify |
| DuckDB | Banco de dados local (arquivo `.duckdb`) |
| dbt | Transformações Silver e Gold com testes e documentação |
| Apache Airflow | Orquestração (LocalExecutor) |
| PostgreSQL | Destino do export para o Metabase |
| Metabase | Dashboards e visualizações |
| Docker Compose | Ambiente completo em um comando |

---

## Pré-requisitos

- Docker Desktop instalado e rodando
- Python 3.11+
- Conta no [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

---

## Configuração

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd lakehouse-analytics-spotify
```

### 2. Configurar credenciais do Spotify

Crie um app no [Spotify Developer Dashboard](https://developer.spotify.com/dashboard):
- Redirect URI: `http://127.0.0.1:8888`
- Habilite a **Web API**

Copie o template de variáveis de ambiente:

```bash
cp .env.example .env
```

Preencha `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET` no `.env`.

### 3. Gerar o Refresh Token

```bash
pip install requests python-dotenv
python extraction/get_refresh_token.py
```

O script abre o navegador para login no Spotify e salva o `SPOTIFY_REFRESH_TOKEN` automaticamente no `.env`.

### 4. Subir o ambiente

```bash
docker-compose up -d --build
```

---

## Serviços

| Serviço | URL | Credenciais |
|---|---|---|
| Airflow | http://localhost:8080 | admin / admin |
| Metabase | http://localhost:3000 | configurado no primeiro acesso |
| dbt docs | http://localhost:8081 | — |
| PostgreSQL | localhost:5432 | spotify / spotify |

---

## Executar o pipeline

1. Acesse o Airflow em http://localhost:8080
2. Ative os DAGs `spotify_extraction` e `spotify_transformation`
3. Dispare o `spotify_extraction` manualmente (botão ▶)
4. Aguarde — o DAG 2 é disparado automaticamente ao final

O pipeline é disparado manualmente pelo Airflow.

---

## Dashboards no Metabase

Conecte o Metabase ao banco `spotify_analytics` (host: `postgres`, porta: `5432`).

Tabelas disponíveis:

| Tabela | Descrição |
|---|---|
| `top_tracks_by_period` | Top 50 músicas por período (4 semanas / 6 meses / all time) |
| `top_artists_by_period` | Top 50 artistas por período |
| `listening_history` | Últimas 50 reproduções com timestamp |
| `listening_patterns` | Padrões de escuta por dia da semana e hora |

Consulte o guia completo em [`docs/metabase-setup.md`](docs/metabase-setup.md).

---

## Estrutura do Projeto

```
├── docker-compose.yml
├── .env.example
├── requirements.txt
│
├── extraction/
│   ├── auth.py                  # Autenticação (refresh token flow)
│   ├── get_refresh_token.py     # Script one-time para gerar o token
│   ├── top_tracks.py            # /me/top/tracks
│   ├── top_artists.py           # /me/top/artists + enrich via /artists
│   ├── recently_played.py       # /me/player/recently-played
│   └── loader.py                # Carga Bronze no DuckDB
│
├── airflow/dags/
│   ├── spotify_extraction.py    # DAG 1 — extração semanal
│   └── spotify_transformation.py # DAG 2 — dbt + export
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── silver/              # stg_top_tracks · stg_top_artists · stg_recently_played
│       └── gold/                # top_tracks_by_period · top_artists_by_period
│                                # listening_history · listening_patterns
│
├── export/
│   └── duckdb_to_postgres.py    # Export Gold → PostgreSQL
│
├── docker/
│   ├── airflow/Dockerfile       # Imagem customizada com dependências Python
│   └── postgres-init/init.sql   # Criação dos bancos metabase e spotify_analytics
│
├── data/
│   └── spotify.duckdb           # Banco de dados local (gerado pelo pipeline)
│
└── docs/
    ├── metabase-setup.md        # Guia de configuração do Metabase
    ├── pipeline-guide.md        # Guia completo do pipeline
    ├── linkedin-post.md         # Post LinkedIn sobre o projeto
    └── superpowers/specs/       # Design spec do projeto
```

---

## Documentação dbt

Após o primeiro run do pipeline, a documentação dos modelos (lineage, testes, descrições) fica disponível em **http://localhost:8081**.
