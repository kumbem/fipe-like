Design / TDD (atualizado com fallback)
1) Arquitetura (monólito com responsabilidades)

UI (Streamlit) → Serviços (Domínio) → Repositórios (SQLite)

UI: inputs/outputs

Domínio: regra de negócio (média mensal + fallback)

Repo: SQL e acesso ao SQLite

2) Componentes e interfaces
UI (Streamlit)

UserQuotePage

Inputs: mes_ref, ano_ref, marca_id, modelo_id, versao_id

Output: preco, mes_usado/ano_usado, mensagens

Domínio
CatalogService

list_brands()

list_models(marca_id)

list_versions(modelo_id)

QuoteService

get_reference_price(mes_ref, ano_ref, versao_id) -> QuoteResult

Regra do serviço:

Buscar pesquisas no mês solicitado

Se houver, calcular media_mes

Se não houver, buscar mês anterior mais recente com dados e calcular média

Se não houver dados em nenhum mês anterior, retornar “sem cotação”

Estrutura de retorno (QuoteResult):

status: OK | FALLBACK | NOT_FOUND

preco

mes_usado, ano_usado

mensagem

Repositórios (SQLite)
CatalogRepository

get_brands()

get_models_by_brand(marca_id)

get_versions_by_model(modelo_id)

PriceResearchRepository

get_prices_for_month(versao_id, year, month) -> list[preco]

get_latest_month_with_prices_before(versao_id, year, month) -> (year, month) | None

LogRepository (opcional)

insert_query_log(...)

3) Diagrama de sequência (texto)

Usuário consulta preço

UI chama QuoteService.get_reference_price(mes_ref, ano_ref, versao_id)

Service chama repo: get_prices_for_month(...)

Se vazio, chama repo: get_latest_month_with_prices_before(...)

Com (ano,mes) encontrado, chama get_prices_for_month(...) novamente

Service calcula média e retorna QuoteResult

UI exibe preço + mês efetivo usado

(opcional) Service chama LogRepository.insert_query_log(...)

4) Casos de teste (lista)

CT01: mês tem dados → status OK + média correta

CT02: mês sem dados, existe anterior → status FALLBACK + mês_usado correto

CT03: nenhum mês anterior → status NOT_FOUND + mensagem clara

CT04: dropdown inválido (versao inexistente) → erro tratado / mensagem