# Guia Completo do Pipeline — Spotify Lakehouse

## Pré-requisitos

- Docker e Docker Compose instalados
- Conta no [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) com `Client ID` e `Client Secret`
- Python 3.11+

---

## 1. Clonar e configurar o projeto

```bash
git clone <url-do-repositorio>
cd lakehouse-analytics-spotify
```

Copie o arquivo de variáveis de ambiente:

```bash
cp .env.example .env
```

Edite o `.env` e preencha suas credenciais do Spotify:

```
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret
```

---

## 2. Subir o ambiente Docker

```bash
docker-compose up -d
```

Na primeira execução, o `airflow-init` vai:
- Instalar as dependências Python (dbt, duckdb, requests)
- Inicializar o banco de metadados do Airflow
- Criar o usuário admin

Aguarde o init concluir antes de prosseguir:

```bash
docker-compose logs -f airflow-init
```

Quando aparecer `Admin user admin created`, o ambiente está pronto.

---

## 3. Serviços disponíveis

| Serviço | URL | Credenciais |
|---|---|---|
| Airflow | http://localhost:8080 | admin / admin |
| Metabase | http://localhost:3000 | configurado no primeiro acesso |
| dbt docs | http://localhost:8081 | — |
| PostgreSQL | localhost:5432 | spotify / spotify |

---

## 4. Executar o pipeline

### Via Airflow (recomendado)

1. Acesse http://localhost:8080
2. Ative o DAG `spotify_extraction` (toggle na coluna esquerda)
3. Clique no botão **Trigger DAG** para rodar manualmente
4. Acompanhe a execução clicando no DAG → Graph View

O `spotify_extraction` dispara automaticamente o `spotify_transformation` ao final.

### Fluxo completo

```
spotify_extraction (DAG 1)
  extract_playlists
      ├── extract_audio_features
      └── extract_artists
              └── load_bronze
                      └── trigger_transformation
                              │
                              ▼
              spotify_transformation (DAG 2)
                dbt_run_silver
                    └── dbt_test_silver
                            └── dbt_run_gold
                                    └── dbt_test_gold
                                            └── export_to_postgres
```

---

## 5. Verificar os dados no DuckDB

Para inspecionar os dados diretamente:

```bash
docker-compose exec airflow-scheduler python3 -c "
import duckdb
conn = duckdb.connect('/opt/airflow/data/spotify.duckdb')
print(conn.execute('SHOW TABLES').fetchdf())
"
```

---

## 6. Executar o export manualmente

Se precisar re-exportar para o PostgreSQL sem rodar o pipeline completo:

```bash
docker-compose exec airflow-scheduler python3 /opt/airflow/export/duckdb_to_postgres.py
```

---

## 7. Atualização semanal automática

O DAG `spotify_extraction` está configurado com `schedule_interval="@weekly"`. Ele roda automaticamente toda semana enquanto o Docker estiver em execução.

Para verificar a próxima execução agendada, acesse o Airflow → DAG `spotify_extraction` → coluna **Next Run**.

---

## 8. Parar o ambiente

```bash
docker-compose down
```

Os dados do PostgreSQL são persistidos no volume `postgres_data`. O DuckDB é um arquivo local em `data/spotify.duckdb`.

Para remover tudo (incluindo dados):

```bash
docker-compose down -v
```

---

## Estrutura do projeto

```
lakehouse-analytics-spotify/
├── docker-compose.yml        # Orquestração dos serviços Docker
├── .env                      # Credenciais (não vai para o git)
├── .env.example              # Template de credenciais
├── requirements.txt          # Dependências Python
│
├── extraction/               # Módulos de extração da API do Spotify
│   ├── auth.py               # Autenticação Client Credentials
│   ├── countries.py          # Lista de países e IDs das playlists
│   ├── playlists.py          # Busca Top 50 por país
│   ├── audio_features.py     # Busca audio features em batch
│   ├── artists.py            # Busca dados de artistas
│   └── loader.py             # Carga na camada Bronze (DuckDB)
│
├── airflow/dags/
│   ├── spotify_extraction.py     # DAG 1 — extração semanal
│   └── spotify_transformation.py # DAG 2 — dbt + export
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── silver/           # stg_tracks, stg_artists
│       └── gold/             # top_tracks_by_country, top_artists_global,
│                             # genre_distribution, audio_trends
│
├── export/
│   └── duckdb_to_postgres.py # Export Gold → PostgreSQL
│
└── data/
    └── spotify.duckdb        # Banco de dados local
```
