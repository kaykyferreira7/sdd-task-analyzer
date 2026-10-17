# sdd-task-analyzer — TaskAnalyzer (Fase 2)

Projeto do **Bootcamp III**, Fase 2. O objetivo é analisar uma lista de tarefas e calcular
métricas de produtividade com validação de dados. O trabalho segue o
**desenvolvimento orientado por especificação (SDD)**: a especificação foi escrita antes do
código e cada requisito está ligado a testes automatizados.

## Contexto da Fase 2

A Fase 2 entrega a função `analyze_tasks` e a exceção `TaskValidationError`. Ela segue as regras
de governança de `CONTEXT_RULES.md` e o contrato de `specs/task_analyzer_spec.md`.

O enunciado oficial e o barema do professor **não estavam disponíveis** durante o
desenvolvimento. Os pontos que eles não definiam foram decididos e registrados na seção 8 da
especificação.

## Funcionalidades

- Total de tarefas, concluídas e pendentes.
- Tempo médio de conclusão em horas, geral e por prioridade.
- Taxa de atraso percentual.
- Validação das datas: se `data_conclusao` for anterior a `data_criacao`, lança `TaskValidationError`.
- Validação de campos ausentes e de tipos inválidos.
- Proteção contra divisão por zero: médias sem dados retornam `0.0`.

## Tecnologias

- Python 3.11 ou superior. Foi testado com 3.11.17 e 3.13.16 e usa somente a biblioteca padrão.
- `pytest` e `pytest-cov`, usados apenas para os testes.

## Instalação

```bash
git clone <URL-do-repositório>    # o link ainda não foi publicado; veja "Links"
cd sdd-task-analyzer
python3 -m venv .venv
source .venv/bin/activate          # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Como executar os testes

```bash
pytest                                                  # suíte completa
pytest --cov=src --cov-branch --cov-report=term-missing  # com cobertura
```

## Como usar `analyze_tasks`

```python
import sys; sys.path.insert(0, "src")
from datetime import datetime
from task_analyzer import analyze_tasks, TaskValidationError

tarefas = [
    {"id": 1, "prioridade": "alta", "data_criacao": datetime(2026, 1, 1, 8),
     "data_conclusao": datetime(2026, 1, 1, 12), "prazo": datetime(2026, 1, 1, 18)},
    {"id": 2, "prioridade": "alta", "data_criacao": datetime(2026, 1, 1, 8),
     "data_conclusao": datetime(2026, 1, 2, 8), "prazo": datetime(2026, 1, 1, 20)},
    {"id": 3, "prioridade": "media", "data_criacao": datetime(2026, 1, 2, 9),
     "data_conclusao": datetime(2026, 1, 2, 19)},
    {"id": 4, "prioridade": "baixa", "data_criacao": datetime(2026, 1, 3, 10),
     "prazo": datetime(2026, 1, 5, 10)},
    {"id": 5, "prioridade": "media", "data_criacao": datetime(2026, 1, 4, 10),
     "prazo": datetime(2026, 1, 20, 10)},
]

print(analyze_tasks(tarefas, referencia=datetime(2026, 1, 10)))
```

Saída:

```python
{'total_tarefas': 5, 'total_concluidas': 3, 'total_pendentes': 2,
 'tempo_medio_conclusao_horas': 12.67,
 'tempo_medio_conclusao_horas_por_prioridade': {'alta': 14.0, 'baixa': 0.0, 'media': 10.0},
 'taxa_atraso_percentual': 40.0}
```

O mesmo exemplo, junto com o cenário de erro, pode ser executado com:

```bash
python examples/demo.py
```

### Entrada

Cada tarefa pode ser um `dict` ou um `Task`, com os campos abaixo:

| Campo | Tipo | Obrigatório | Observação |
|-------|------|-------------|------------|
| `id` | `str` ou `int` | sim | |
| `prioridade` | `str` | sim | É normalizada com `strip().lower()`. |
| `data_criacao` | `datetime` | sim | |
| `data_conclusao` | `datetime` | não | Se ausente, a tarefa é pendente. |
| `prazo` | `datetime` | não | Usado para calcular o atraso. |

O parâmetro opcional `referencia` define o "agora" usado para saber se uma tarefa pendente já
passou do prazo.

### Saída

A função devolve um dicionário com seis chaves: `total_tarefas`, `total_concluidas`,
`total_pendentes`, `tempo_medio_conclusao_horas`,
`tempo_medio_conclusao_horas_por_prioridade` e `taxa_atraso_percentual`. Os valores decimais são
arredondados para 2 casas.

## Regras de validação e exceções

`TaskValidationError` é uma subclasse de `ValueError` e tem o atributo `task_id`. Ela é lançada
quando:

- `data_conclusao` é anterior a `data_criacao`;
- `id`, `prioridade` ou `data_criacao` estão ausentes ou são inválidos;
- alguma data não é do tipo `datetime` (strings não são convertidas automaticamente);
- há datas com e sem fuso horário misturadas;
- `tasks` não é uma coleção de tarefas, ou algum item não é uma tarefa;
- `referencia` não é do tipo `datetime`.

Uma tarefa sem `data_conclusao` é **pendente**, e não inválida.

## Regras de negócio principais

- **Atraso:** a tarefa foi concluída depois do `prazo`, ou está pendente e a `referencia` já passou
  do `prazo`. Concluir exatamente no prazo não conta como atraso.
- **Taxa de atraso:** número de tarefas atrasadas dividido por `total_tarefas`, vezes 100.
- **Média de tempo:** considera somente as tarefas concluídas. Se não houver nenhuma, o valor é `0.0`.

## Estrutura

```
sdd-task-analyzer/
├── README.md
├── CONTEXT_RULES.md            # regras de governança
├── pyproject.toml              # configuração do pytest
├── requirements.txt
├── specs/task_analyzer_spec.md # contrato (fonte de verdade)
├── src/task_analyzer.py        # implementação
├── tests/test_harness.py       # testes automatizados
├── examples/demo.py            # demonstração executável
└── docs/
    ├── relatorio_entrega.md
    ├── matriz_rastreabilidade.md
    ├── checklist_barema.md
    └── roteiro_video.md
```

## Decisões técnicas

As decisões estão detalhadas em `specs/task_analyzer_spec.md`, seção 8:

- as datas precisam ser `datetime`;
- a definição de atraso usa o campo `prazo`;
- a taxa de atraso é calculada sobre o total de tarefas;
- existe o parâmetro `referencia`;
- a média por prioridade fica em uma chave própria;
- os valores são arredondados para 2 casas;
- as prioridades são normalizadas.

## Limitações conhecidas

- O enunciado oficial e o barema não foram consultados, porque não estavam disponíveis. Se
  eles definirem nomes de chaves ou regras de atraso diferentes, a especificação e o código
  precisam ser ajustados.
- As datas não são convertidas a partir de texto; quem chama a função deve fornecê-las como `datetime`.
- Quando `referencia` não é informada, o atraso de tarefas pendentes depende do horário em que
  a função é executada.

## Estado dos testes

Resultado da última execução local, em 17/10/2026:

- **62 testes aprovados e 0 reprovados**, em Python 3.13.16 e em Python 3.11.17.
- Cobertura medida com `pytest-cov`: **100% de linhas e de ramos** em `src/task_analyzer.py`.

## Links

- Repositório: **pendente de publicação**. O GitHub CLI não estava autenticado no ambiente de desenvolvimento.
- Pull Request: **pendente**.

## Reproduzir os resultados

1. Siga os passos de **Instalação**.
2. Execute `pytest --cov=src --cov-branch --cov-report=term-missing`.
3. Execute `python examples/demo.py` e compare a saída com a seção 10 da especificação.
