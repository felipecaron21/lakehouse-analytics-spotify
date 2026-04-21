# Post LinkedIn — Spotify Lakehouse com Claude Code

---

Construí um pipeline de dados completo do zero usando o **Claude Code** como parceiro de desenvolvimento — e o resultado virou um Spotify Wrapped personalizado, rodando localmente.

O projeto é um **Lakehouse com arquitetura medalhão** que extrai os meus próprios dados da API do Spotify: músicas mais ouvidas, artistas favoritos e histórico de reprodução — organizados em 3 períodos (últimas 4 semanas, 6 meses e todos os tempos).

**Stack utilizada:**
- Python (extração via API do Spotify)
- DuckDB (banco de dados local, leve e sem servidor)
- dbt (transformações com testes e documentação automática)
- Apache Airflow (orquestração com 2 DAGs)
- PostgreSQL + Metabase (dashboards interativos)
- Docker Compose (ambiente completo em um comando)

---

**O que o dashboard mostra:**

- Minhas 50 músicas mais ouvidas por período
- Meus 50 artistas favoritos por período
- Histórico recente de reproduções
- Em quais dias da semana e horários eu mais ouço música

É exatamente o conceito do Spotify Wrapped — mas rodando localmente, com dados atualizados sempre que eu quiser e com toda a infraestrutura visível e compreensível.

---

**O que aprendi além do código:**

**1. Criar um PRD antes de codar muda tudo**
Antes de escrever uma linha de código, documentei o projeto: objetivos, stack, endpoints, camadas do lakehouse. Isso evitou retrabalho e me deu clareza sobre o que construir.

**2. Brainstorming estruturado com IA**
Usei o processo de brainstorming do Claude Code para refinar a ideia: perguntas uma por vez, proposta de abordagens com trade-offs, design validado antes da implementação. A diferença de começar com um design aprovado versus sair codando é enorme.

**3. Arquitetura medalhão na prática**
Bronze (raw), Silver (limpo e enriquecido) e Gold (métricas prontas para consumo). Cada camada com responsabilidade clara — e o dbt tornando as transformações testáveis e documentadas.

**4. Lidar com limitações reais de API**
Durante o desenvolvimento, descobri que a Spotify restringiu o acesso a playlists editoriais para apps em Development Mode. Precisei adaptar o projeto para usar endpoints de dados pessoais do usuário — uma situação muito comum no mundo real que nenhum tutorial te ensina.

**5. Separação de responsabilidades no Airflow**
Dois DAGs independentes: um para extração (Bronze) e outro para transformação (Silver → Gold → export). O segundo é disparado automaticamente pelo primeiro. Simples, mas demonstra boa prática de modularidade.

**6. Segurança desde o início**
`.env` para credenciais, `.gitignore` configurado antes do primeiro commit, `.env.example` como template. Pequenos hábitos que fazem diferença em projetos reais.

---

Este projeto foi um teste deliberado: usar o **Claude Code** como ferramenta de aprendizado e desenvolvimento acelerado. O resultado foi um pipeline funcional, bem documentado e com boas práticas — em uma fração do tempo que levaria sozinho.

Se você está estudando engenharia de dados ou quer entender como IA pode acelerar seu aprendizado técnico, recomendo muito essa abordagem: não peça para a IA fazer por você, mas construa junto, entendendo cada decisão.

---

🔗 Repositório: [link do projeto]

**#DataEngineering #Python #dbt #Airflow #DuckDB #Spotify #SpotifyWrapped #ClaudeCode #LakeHouse #Portfolio**
