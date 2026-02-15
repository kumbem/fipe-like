# 1) Visao Geral da Arquitetura

Arquitetura em camadas (monolito organizado):

- Interface: `src/app.py` (Streamlit)
- Repositorio: `src/repo_fipe.py`
- Persistencia: SQLite (`src/data/fipe.db`), conexao em `src/db.py`

Separacao de responsabilidades:

- A camada de interface coleta filtros, aciona o repositorio e apresenta resultado.
- A camada de repositorio concentra SQL e mapeamento de retorno para a aplicacao.
- A camada de persistencia executa armazenamento e integridade referencial.

Justificativa do monolito organizado:

- Escopo pequeno e baixa latencia local favorecem deploy simples.
- Menor custo operacional que arquitetura distribuida para este caso.
- Fronteiras internas claras permitem evolucao incremental sem acoplamento da UI ao SQL.

# 2) Fluxo da Consulta (Diagrama Sequencial - texto)

1. Usuario seleciona `marca`, `modelo`, `versao`, `mes` e `ano` na interface Streamlit.
2. Frontend chama `repo_fipe.buscar_cotacao(versao_id, mes, ano)`.
3. Repositorio abre conexao via `db.get_connection()`.
4. Repositorio executa query em `cotacao` por `versao_id` e periodo `<=` ao selecionado.
5. Repositorio retorna:
   - cotacao exata do mes/ano, quando existir;
   - fallback para o ultimo periodo anterior disponivel, quando nao existir cotacao exata;
   - `None`, quando nao houver nenhum periodo anterior.
6. Frontend decide:
   - Se `None`: exibe "Sem cotacao para o periodo selecionado".
   - Se valor com fallback: informa periodo solicitado e periodo efetivamente usado.
   - Se valor: exibe preco formatado e tenta registrar log.
7. Frontend chama `repo_fipe.registrar_consulta(...)`, que executa `INSERT` em `consulta_log`.
8. Conexoes sao fechadas em `finally` no repositorio (consulta e log).

# 3) Decisoes Tecnicas Importantes

- Por que SQLite?
  - Banco embarcado, suficiente para o volume do projeto e simples de distribuir.
  - Remove dependencia de servidor de banco para execucao local e avaliacao.
- Por que conexao por uso?
  - Evita conexao global compartilhada entre sessoes/threads do Streamlit.
  - Reduz risco de estado residual e contention de conexao.
- Por que `PRAGMA foreign_keys = ON`?
  - Em SQLite, FKs nao sao garantidas sem ativacao por conexao.
  - Garante integridade entre `marca`, `modelo`, `versao`, `cotacao` e `consulta_log`.
- Por que log nao pode quebrar fluxo?
  - Objetivo principal da tela e retornar preco; logging e concern secundario.
  - Falha de telemetria nao pode causar indisponibilidade da funcionalidade principal.
- Por que sem SQL no frontend?
  - Mantem UI focada em experiencia e orquestracao.
  - Centraliza acesso a dados no repositorio, facilitando manutencao e testes.

# 4) Modelo de Responsabilidades


| Camada | Tipo Arquitetural | Responsabilidade | Nao faz |
|---|---|---|---|
| `app.py` | Interface | Renderizacao da UI e orquestracao do fluxo | Nao executa SQL |
| `repo_fipe.py` | Data Access Layer | Encapsula queries e persistencia | Nao renderiza UI |
| `db.py` | Infraestrutura | Configuracao e gerenciamento de conexao | Nao contem regra de negocio nem query |

# 5) Riscos Tecnicos e Limitacoes

Embora o sistema atenda ao escopo proposto, existem limitacoes estruturais importantes:

1. Uso de SQLite
   - Adequado para projeto educacional.
   - Nao escalavel horizontalmente.
   - Sem controle avancado de concorrencia.
2. Ausencia de Autenticacao
   - Sistema de consulta e publico.
   - Nao ha controle de identidade ou autorizacao.
3. Sem Cache
   - Toda consulta acessa diretamente o banco.
   - Pode impactar performance em grande volume.
4. Sem Versionamento de Schema
   - Nao ha ferramenta de migracao (ex: Alembic).
   - Alteracoes futuras exigiriam recriacao manual.
5. Log nao armazena valor exibido
   - O sistema registra os parametros da consulta.
   - Nao registra o preco exibido no momento.
   - Caso o valor mude no futuro, o historico nao refletira exatamente o valor visualizado pelo usuario.

