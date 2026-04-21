# Configuração do Metabase

## 1. Subir o ambiente Docker

```bash
docker-compose up -d
```

Aguarde todos os serviços subirem. Verifique com:

```bash
docker-compose ps
```

Todos devem estar com status `healthy` ou `running`.

---

## 2. Acessar o Metabase

Abra o navegador em: **http://localhost:3000**

Na primeira vez, o Metabase vai exibir um assistente de configuração inicial:

1. Escolha o idioma
2. Preencha nome, e-mail e senha do usuário administrador
3. Na etapa "Add your data", clique em **PostgreSQL**

---

## 3. Conectar ao banco spotify_analytics

Preencha os campos com os valores do seu `.env`:

| Campo | Valor |
|---|---|
| Display name | Spotify Analytics |
| Host | `postgres` |
| Port | `5432` |
| Database name | `spotify_analytics` |
| Username | `spotify` |
| Password | `spotify` |

> **Atenção:** use `spotify_analytics` e não `spotify_lakehouse`. O banco `spotify_lakehouse` contém tabelas internas do Airflow.

Clique em **Save** e depois **Finish**.

---

## 4. Executar o pipeline pela primeira vez

Antes de criar dashboards, você precisa de dados no PostgreSQL. No Airflow (**http://localhost:8080**, login: `admin` / `admin`):

1. Ative o DAG `spotify_extraction`
2. Ative o DAG `spotify_transformation`
3. No DAG `spotify_extraction`, clique em **Trigger DAG** (ícone de play)
4. Aguarde o DAG 1 concluir — ele dispara o DAG 2 automaticamente
5. Confirme que ambos terminaram com sucesso (status verde)

---

## 5. Tabelas disponíveis

Após o pipeline rodar, o banco `spotify_analytics` terá 4 tabelas:

| Tabela | Descrição |
|---|---|
| `top_tracks_by_period` | Suas 50 músicas mais ouvidas por período |
| `top_artists_by_period` | Seus 50 artistas mais ouvidos por período |
| `listening_history` | Últimas 50 músicas reproduzidas com timestamp |
| `listening_patterns` | Padrões de escuta por dia da semana e hora do dia |

Os períodos disponíveis em `top_tracks_by_period` e `top_artists_by_period`:

| `time_range` | `time_range_label` | Descrição |
|---|---|---|
| `short_term` | 4 semanas | Últimas 4 semanas |
| `medium_term` | 6 meses | Últimos 6 meses |
| `long_term` | Todos os tempos | Histórico completo |

---

## 6. Criar os dashboards

No Metabase, clique em **+ New → Dashboard** e nomeie como `Meu Spotify`.

### Dashboard 1 — Minhas Músicas Favoritas

1. Clique em **+ Add a question**
2. Escolha a tabela `top_tracks_by_period`
3. Filtre por `time_range = short_term`
4. Ordene por `position` (crescente)
5. Visualização: **Table** com colunas `position`, `track_name`, `artist_name`, `popularity`
6. Adicione um filtro interativo de `time_range_label` no dashboard para alternar entre períodos

### Dashboard 2 — Meus Artistas Favoritos

1. Nova question → tabela `top_artists_by_period`
2. Filtre por `time_range = medium_term`
3. Ordene por `position` (crescente)
4. Visualização: **Table** com `position`, `artist_name`, `followers`
5. Adicione filtro interativo de período

### Dashboard 3 — Histórico Recente

1. Nova question → tabela `listening_history`
2. Visualização: **Table**
3. Ordene por `played_at` (decrescente)
4. Colunas: `track_name`, `artist_name`, `played_at`

### Dashboard 4 — Quando Você Ouve Música

1. Nova question → tabela `listening_patterns`
2. Visualização: **Bar chart**
3. Eixo X: `day_name`, Eixo Y: `plays`
4. Segunda visualização: Eixo X: `hour_of_day`, Eixo Y: `plays` (para ver o horário de pico)

---

## 7. Acessar a documentação do dbt

A documentação gerada pelo dbt (lineage, modelos, testes) fica disponível em:

**http://localhost:8081**

> O serviço `dbt-docs` executa `dbt docs generate` na inicialização e serve o site estático. Estará disponível após o primeiro run do pipeline.
