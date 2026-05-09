# Desenvolva um pipeline de dados para extrair dados via API do Spotify e disponibiliza-los tratados para consumo e geração de dashboards

Quero criar um lakehouse para extração, tranformação e carregamento de dados que serão extraídos da API do Sportify.

O lakehouse deve seguir o conceito de arquitetura medalhão, ou seja, seram 3 camadas (Bronze, Silver and Gold). Inicialmente vamos realizar a extração dos dados do Spotify via API e armazena-los em na camada Bronze(raw) e posteriomente utilizando o dbt faremos as transformações para as camadas Silver(Intermediate) e Gold(Metrics). O banco utilizado será o DuckDB e para orquestração do pipeline usaremos o airflow. Por fim, devemos possuir um script para exportar o DuckDB para PostgreSQL para que seja possível a integração com o Metabase.

Stack: Python, DuckDB, dbt (Data Build Tool), Airflow(Docker), PostgreSQL(Docker), Metabase(Docker)

Link API Spotify: https://developer.spotify.com/documentation/web-api