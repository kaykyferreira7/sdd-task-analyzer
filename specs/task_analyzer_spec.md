# Especificação — TaskAnalyzer (Fase 2)

> Fonte de verdade do contrato da aplicação. Código, testes e README devem estar de acordo com este documento.
> Versão do contrato: **0.2.0** (Fase 2).

## 1. Fontes consultadas

| Fonte | Situação |
|-------|----------|
| Regras de governança (Context Rules) fornecidas pelo autor do projeto | Consultadas — reproduzidas em `CONTEXT_RULES.md` |
| Especificação de negócio (SDD) fornecida pelo autor do projeto | Consultada — reproduzida nas seções 3 e 4 |
| Prompt mestre da Fase 2 (instruções de entrega) | Consultado |
| Enunciado oficial da Fase 2 publicado pelo professor | **Não disponibilizado** |
| Barema oficial de avaliação | **Não disponibilizado** |
| Artefatos da Fase 1 | **Não disponibilizados** |

Como o enunciado oficial e o barema não estavam disponíveis, os pontos que eles poderiam detalhar
(formato das datas, definição de atraso, nomes de chaves secundárias) foram decididos de forma
explícita na seção 8. Se o enunciado oficial divergir, ele prevalece e este documento deve ser atualizado.

## 2. Objetivo

Fornecer a função `analyze_tasks`, que recebe uma coleção de tarefas e devolve métricas de
produtividade: totais, tempo médio de conclusão (geral e por prioridade) e taxa de atraso,
validando a consistência das datas.

## 3. Requisitos funcionais

| ID | Requisito |
|----|-----------|
| RF-01 | O sistema deve expor uma função principal chamada `analyze_tasks`. |
| RF-02 | Calcular `total_tarefas`. |
| RF-03 | Calcular `total_concluidas`. |
| RF-04 | Calcular `total_pendentes`. |
| RF-05 | Calcular `tempo_medio_conclusao_horas` (geral). |
| RF-06 | Calcular o tempo médio de conclusão **por prioridade**. |
| RF-07 | Calcular `taxa_atraso_percentual`. |
| RF-08 | Se `data_conclusao < data_criacao`, disparar `TaskValidationError`. |
| RF-09 | Entrada vazia deve retornar `0.0` nas médias de tempo. |
| RF-10 | Entrada só com tarefas pendentes deve retornar `0.0` nas médias de tempo. |
| RF-11 | Expor a exceção customizada `TaskValidationError`. |

## 4. Requisitos não funcionais (Context Rules)

| ID | Requisito |
|----|-----------|
| RNF-01 | Python 3.11 ou superior. |
| RNF-02 | Type hints em 100% das funções e parâmetros. |
| RNF-03 | Tratamento de erros específico, com `TaskValidationError`. |
| RNF-04 | Prevenção ativa de divisão por zero (médias de listas vazias = `0.0`). |
| RNF-05 | Nenhuma dependência externa em tempo de execução. |

## 5. Contrato

### 5.1 Assinatura

```python
def analyze_tasks(
    tasks: Iterable[Task | Mapping[str, Any]] | None,
    referencia: datetime | None = None,
) -> AnalysisResult: ...
```

### 5.2 Entrada — cada tarefa

Cada item pode ser um `Task` (dataclass exportada pelo módulo) ou um mapeamento (`dict`) com:

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `id` | `str` ou `int` (não `bool`) | Sim | Identifica a tarefa nas mensagens de erro. |
| `prioridade` | `str` não vazia | Sim | Agrupamento das médias por prioridade. |
| `data_criacao` | `datetime` | Sim | Início da tarefa. |
| `data_conclusao` | `datetime` ou `None` | Não | Ausente/`None` ⇒ tarefa **pendente**. |
| `prazo` | `datetime` ou `None` | Não | Ausente/`None` ⇒ tarefa nunca conta como atrasada. |

`tasks=None` é tratado como coleção vazia.

`referencia` é o instante usado para avaliar se uma tarefa **pendente** já passou do prazo.
Se omitido, usa-se o horário atual (com o fuso horário das datas de entrada, quando houver).

### 5.3 Saída — `AnalysisResult` (`dict`)

| Chave | Tipo | Definição |
|-------|------|-----------|
| `total_tarefas` | `int` | Número de tarefas recebidas. |
| `total_concluidas` | `int` | Tarefas com `data_conclusao` preenchida. |
| `total_pendentes` | `int` | `total_tarefas - total_concluidas`. |
| `tempo_medio_conclusao_horas` | `float` | Média de `(data_conclusao - data_criacao)` em horas, só sobre concluídas; `0.0` sem concluídas. |
| `tempo_medio_conclusao_horas_por_prioridade` | `dict[str, float]` | Mesma média, agrupada por prioridade; prioridade sem concluídas = `0.0`. |
| `taxa_atraso_percentual` | `float` | `atrasadas / total_tarefas * 100`; `0.0` se `total_tarefas == 0`. |

Valores `float` são arredondados para **2 casas decimais**. As chaves do dicionário por prioridade
aparecem em ordem alfabética.

### 5.4 Exceções

`TaskValidationError` (subclasse de `ValueError`), com atributo `task_id`, é lançada quando:

| ID | Condição |
|----|----------|
| EX-01 | `data_conclusao` é anterior a `data_criacao`. |
| EX-02 | `id` ausente ou de tipo inválido. |
| EX-03 | `prioridade` ausente, vazia ou não textual. |
| EX-04 | `data_criacao` ausente. |
| EX-05 | Qualquer data com tipo diferente de `datetime` (ex.: string). |
| EX-06 | Datas com e sem fuso horário misturadas de forma que não possam ser comparadas. |
| EX-07 | `tasks` não é uma coleção de tarefas (ex.: um `dict` isolado, uma `str`, um `int`) ou contém item que não é `Task`/mapeamento. |
| EX-08 | `referencia` informada com tipo diferente de `datetime`. |

## 6. Regras de negócio

| ID | Regra |
|----|-------|
| RN-01 | Tarefa **concluída** = possui `data_conclusao`. Tarefa **pendente** = não possui. |
| RN-02 | Tempo de conclusão (horas) = `(data_conclusao - data_criacao).total_seconds() / 3600`. |
| RN-03 | Só tarefas concluídas entram nas médias de tempo. |
| RN-04 | Tarefa **atrasada**: (a) concluída com `data_conclusao > prazo`; ou (b) pendente com `referencia > prazo`. Concluir exatamente no prazo **não** é atraso. |
| RN-05 | Prioridade é normalizada com `strip().lower()` antes do agrupamento (`"Alta"` e `" alta "` formam o mesmo grupo). |
| RN-06 | Toda prioridade presente na entrada aparece no resultado por prioridade, mesmo sem concluídas (valor `0.0`). Nenhuma prioridade é inventada. |
| RN-07 | Divisões só ocorrem com denominador positivo; caso contrário o resultado é `0.0`. |
| RN-08 | A validação ocorre para **todas** as tarefas antes de qualquer cálculo: uma tarefa inválida invalida a análise inteira. |

## 7. Casos de borda

| ID | Caso | Resultado esperado |
|----|------|--------------------|
| CB-01 | Lista vazia ou `None` | Totais `0`, médias `0.0`, taxa `0.0`, dicionário por prioridade vazio. |
| CB-02 | Só tarefas pendentes | Médias `0.0`; prioridades listadas com `0.0`. |
| CB-03 | Prioridade sem concluídas, ao lado de outras com concluídas | Essa prioridade vale `0.0`, as demais têm média real. |
| CB-04 | `data_conclusao == data_criacao` | Válido; duração `0.0` h. |
| CB-05 | `data_conclusao == prazo` | Não é atraso. |
| CB-06 | Durações fracionárias | Arredondamento para 2 casas. |
| CB-07 | Entrada como gerador (iterável de uso único) | Processada normalmente. |
| CB-08 | Datas com fuso horário (todas) | Processadas normalmente. |

## 8. Decisões e premissas

| ID | Decisão | Justificativa |
|----|---------|---------------|
| DEC-01 | Datas aceitas somente como `datetime`. | A regra de governança exige erros específicos e o prompt proíbe converter silenciosamente datas inválidas. Conversão de texto fica a cargo de quem chama. |
| DEC-02 | Definição de atraso conforme RN-04, usando o campo `prazo`. | A especificação pede `taxa_atraso_percentual` mas não define atraso; adotou-se a definição mais comum em gestão de tarefas. |
| DEC-03 | Denominador da taxa de atraso = `total_tarefas`. | Pendentes atrasadas também representam atraso; usar só concluídas esconderia esse risco. |
| DEC-04 | Parâmetro opcional `referencia`. | Torna o cálculo de atraso de pendentes determinístico e testável. |
| DEC-05 | Média por prioridade em chave própria (`tempo_medio_conclusao_horas_por_prioridade`). | A especificação pede média "geral e por prioridade"; manter `tempo_medio_conclusao_horas` como `float` preserva o nome exigido para a média geral. |
| DEC-06 | Arredondamento em 2 casas decimais. | Legibilidade de métricas em horas e percentuais. |
| DEC-07 | Normalização de prioridade (RN-05). | Evita grupos duplicados por diferença de caixa/espaços. |

## 9. Critérios de aceitação

| ID | Critério verificável |
|----|----------------------|
| CA-01 | Para o conjunto de referência da seção 10, o resultado é exatamente o indicado. |
| CA-02 | Lista vazia e `None` retornam o resultado de CB-01 sem exceção. |
| CA-03 | Lista só de pendentes retorna médias `0.0` sem exceção. |
| CA-04 | `data_conclusao < data_criacao` lança `TaskValidationError` com `task_id` da tarefa. |
| CA-05 | Cada condição EX-02 a EX-08 lança `TaskValidationError`. |
| CA-06 | Nenhuma função do módulo deixa de ter anotações de tipo (verificado por teste de introspecção). |
| CA-07 | O resultado nunca contém `NaN` ou infinito. |

## 10. Conjunto de referência (cálculo manual)

`referencia = 2026-01-10 00:00`

| id | prioridade | criação | conclusão | prazo | horas | atrasada? |
|----|-----------|---------|-----------|-------|-------|-----------|
| 1 | alta | 01/01 08:00 | 01/01 12:00 | 01/01 18:00 | 4 | não |
| 2 | alta | 01/01 08:00 | 02/01 08:00 | 01/01 20:00 | 24 | sim (concluída após prazo) |
| 3 | media | 02/01 09:00 | 02/01 19:00 | — | 10 | não (sem prazo) |
| 4 | baixa | 03/01 10:00 | — | 05/01 10:00 | — | sim (pendente, prazo vencido) |
| 5 | media | 04/01 10:00 | — | 20/01 10:00 | — | não (prazo futuro) |

Resultado esperado:

- `total_tarefas = 5`, `total_concluidas = 3`, `total_pendentes = 2`
- `tempo_medio_conclusao_horas = (4 + 24 + 10) / 3 = 12.67`
- por prioridade: `alta = (4 + 24) / 2 = 14.0`, `baixa = 0.0`, `media = 10.0`
- `taxa_atraso_percentual = 2 / 5 * 100 = 40.0`
