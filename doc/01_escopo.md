Escopo e Detalhamento Funcional (atualizado)
1) Objetivo do sistema

Construir um sistema FIPE-like para captura de preços em lojas e consulta pública de referência.
O sistema completo suporta múltiplos papéis, mas nesta semana será implementada apenas a interface de consulta do Usuário (sem login).

2) Escopo do que vamos ENTREGAR (no desafio)
Entrega implementada (código)

✅ Tela do Usuário (Consulta):

Usuário escolhe Mês/Ano de referência

Seleciona Marca → Modelo → Versão/Ano-modelo

Sistema calcula o preço de referência do mês, usando dados de pesquisa_preco

Regra de ausência: se não houver pesquisa no mês escolhido, o sistema busca o último mês anterior disponível (fallback) e informa qual mês foi usado

Entrega projetada (documento, não implementada)

✅ Protótipos/fluxos para:

Admin (gestão de usuários/perfis)

Gerente (cadastro catálogo: marca/modelo/versões e atributos)

Coordenador (agenda de lojas por região + aprovação)

Pesquisador (registro de pesquisas)

Lojista (cadastro de loja)

Batch mensal (fechamento do mês e auditoria de qualidade)

3) Fora de escopo (nesta semana)

Login/controle de acesso

CRUD completo dos papéis

Workflow real de aprovação e agenda semanal

Integração com FIPE real

Deploy / observabilidade

4) Papéis e responsabilidades (sistema completo)

Admin: gerencia usuários e perfis

Gerente: gerencia catálogo (marca/modelo/versão)

Coordenador: define lojas da semana e aprova inclusão

Lojista: cadastra loja (pendente de aprovação)

Pesquisador: registra cotações coletadas

Usuário: consulta preço (implementado)

Batch (projetado): calcula média mensal, valida dados e fecha referência

5) Fluxo principal (implementado): Consultar preço

Usuário escolhe mês/ano + versão

Sistema busca pesquisas na tabela pesquisa_preco dentro do mês

Se existir, calcula média do mês e retorna como preço de referência

Se não existir, busca último mês anterior com dados e retorna média desse mês, informando o fallback

Exibe resultado ao usuário

6) Critérios de aceite (MVP Usuário)

Dropdowns dependentes (marca filtra modelos, modelo filtra versões)

Retorna preço e mês efetivo usado

Caso sem dados em nenhum mês anterior: mensagem clara “sem cotação disponível”

(Opcional) registra log de consulta