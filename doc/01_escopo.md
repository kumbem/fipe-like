# Escopo do Projeto FIPE-like

## 1. Objetivo

Definir o escopo funcional e tecnico do MVP FIPE-like implementado neste repositorio.
O foco da entrega e disponibilizar uma tela de consulta de preco de veiculo baseada em dados locais (SQLite), com interface Streamlit e arquitetura em camadas.

## 2. Escopo do MVP (Implementado)

Funcionalidades entregues:

- Consulta publica sem autenticacao.
- Selecao encadeada de `marca -> modelo -> versao`.
- Selecao de `mes` e `ano` para consulta.
- Busca de cotacao por chave (`versao_id`, `mes`, `ano`).
- Exibicao de preco medio quando existe cotacao.
- Exibicao de mensagem clara quando nao existe cotacao para o periodo.
- Registro de log de consulta em `consulta_log` quando ha resultado.
- Tolerancia a falha no log (a consulta principal nao e interrompida).

## 3. Escopo Tecnico

Componentes do MVP:

- Interface: `src/app.py` (Streamlit).
- Repositorio de dados: `src/repo_fipe.py`.
- Conexao e configuracao do banco: `src/db.py`.
- Persistencia local: SQLite em `src/data/fipe.db`.
- Schema e inicializacao: `src/data/schema.sql` e `src/data/init_db.py`.

## 4. Requisitos Funcionais

- RF01: listar marcas em ordem alfabetica.
- RF02: listar modelos filtrados por marca.
- RF03: listar versoes filtradas por modelo.
- RF04: consultar cotacao por versao, mes e ano.
- RF05: exibir preco formatado em BRL quando houver cotacao.
- RF06: informar ausencia de cotacao quando nao houver dados.
- RF07: registrar consulta bem-sucedida com marca/modelo/versao/mes/ano.

## 5. Requisitos Nao Funcionais

- RNF01: integridade referencial obrigatoria (FKs ativas por conexao).
- RNF02: separacao de responsabilidades (UI sem SQL direto).
- RNF03: conexao com banco por uso e fechamento em `finally`.
- RNF04: operacao local sem dependencia de servidor de banco externo.

## 6. Fora de Escopo (Atual)

- Login e controle de acesso por perfil.
- CRUD administrativo de catalogo e usuarios.
- Workflow de aprovacao operacional (coordenador, pesquisador, lojista).
- Integracao com API externa FIPE.
- Pipeline batch de consolidacao mensal.
- Observabilidade avancada e deploy produtivo.

## 7. Criterios de Aceite

- CA01: usuario consegue selecionar marca, modelo e versao de forma dependente.
- CA02: consulta com dados retorna preco e nao apresenta erro na interface.
- CA03: consulta sem dados retorna mensagem "Sem cotacao para o periodo selecionado".
- CA04: consulta com resultado registra nova linha em `consulta_log`.
- CA05: falha no registro de log nao impede exibicao do preco.

## 8. Premissas e Restricoes

- O banco `src/data/fipe.db` deve existir antes da execucao da app.
- O schema vigente usa `cotacao.preco` como coluna de valor.
- O conjunto de anos no frontend esta fixo em `[2023, 2024, 2025]` no estado atual.