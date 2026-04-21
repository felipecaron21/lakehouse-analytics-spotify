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

## 3. Conectar ao PostgreSQL

Preencha os campos com os valores do seu `.env`:

| Campo | Valor |
|---|---|
| Display name | Spotify Lakehouse |
| Host | `postgres` |
| Port | `5432` |
| Database name | `spotify_lakehouse` |
| Username | `spotify` |
| Password | `spotify` |

Clique em **Save** e depois **Finish**.

---

## 4. Executar o pipeline pela primeira vez

Antes de criar dashboards, você precisa de dados no PostgreSQL. No Airflow (**http://localhost:8080**, login: `admin` / `admin`):

1. Ative o DAG `spotify_extraction`
2. Clique em **Trigger DAG** (ícone de play)
3. Aguarde o DAG concluir — ele vai disparar automaticamente o `spotify_transformation`
4. Confirme que ambos os DAGs terminaram com sucesso (status verde)

---

## 5. Criar os dashboards

No Metabase, clique em **+ New → Dashboard** e nomeie como `Spotify Analytics`.

### Dashboard 1 — Top Tracks por País

1. Clique em **+ Add a question**
2. Escolha a tabela `top_tracks_by_country`
3. Filtre por `country` e ordene por `position`
4. Adicione um filtro interativo de país no dashboard

### Dashboard 2 — Top Artistas Globais

1. Nova question → tabela `top_artists_global`
2. Visualização: **Bar chart**
3. Eixo X: `artist_name`, Eixo Y: `countries_count`
4. Limite: top 20 artistas

### Dashboard 3 — Distribuição de Gêneros

1. Nova question → tabela `genre_distribution`
2. Visualização: **Pie chart** ou **Bar chart**
3. Filtre por `country` para comparar países
4. Adicione filtro interativo de país

### Dashboard 4 — Audio Trends

1. Nova question → tabela `audio_trends`
2. Visualização: **Line chart**
3. Eixo X: `week`, Eixo Y: `avg_danceability`, `avg_energy`, `avg_valence`
4. Filtre por `country` para ver evolução semanal

---

## 6. Acessar a documentação do dbt

A documentação gerada pelo dbt (lineage, modelos, testes) fica disponível em:

**http://localhost:8081**

> O serviço `dbt-docs` executa `dbt docs generate` na inicialização e serve o site estático. Na primeira vez pode demorar alguns segundos para ficar disponível.
