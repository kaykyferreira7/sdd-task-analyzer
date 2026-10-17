# CONTEXT_RULES — TaskAnalyzer

Regras de contexto que governam todo o código, testes e documentação deste repositório.
Qualquer alteração deve respeitar estas regras; quando uma regra precisar mudar, atualize este
arquivo **e** `specs/task_analyzer_spec.md` no mesmo commit.

## 1. Regras de governança (definidas pelo autor do projeto)

| ID | Regra |
|----|-------|
| CR-01 | O código deve ser escrito em **Python 3.11 ou superior**. |
| CR-02 | **Type hints são obrigatórios em 100%** das funções, parâmetros e retornos. |
| CR-03 | O tratamento de erros deve ser **específico** e usar a exceção customizada **`TaskValidationError`**. |
| CR-04 | O algoritmo deve **prevenir ativamente a divisão por zero**; médias de listas vazias retornam **`0.0`**. |

## 2. Arquitetura

- Código de produção em `src/task_analyzer.py`, sem dependências externas (somente a biblioteca padrão).
- API pública: `analyze_tasks`, `TaskValidationError`, `Task` e o tipo de retorno `AnalysisResult`.
- Funções auxiliares são privadas (prefixo `_`) e têm responsabilidade única
  (validação, média segura, percentual segura, comparação de datas, regra de atraso).
- A função pública não tem efeitos colaterais: não lê arquivos, não acessa rede e não altera a entrada.

## 3. Nomenclatura

- Domínio em português, alinhado à especificação: `data_criacao`, `data_conclusao`, `prazo`,
  `prioridade`, `total_tarefas`, `taxa_atraso_percentual` etc.
- As chaves do resultado são as definidas em `specs/task_analyzer_spec.md` (seção 5) e **não podem ser renomeadas**.
- Constantes em `UPPER_SNAKE_CASE`; funções e variáveis em `snake_case`; classes em `PascalCase`.

## 4. Validação

- Toda entrada inválida gera `TaskValidationError` (nunca `KeyError`, `TypeError` ou `AttributeError` vazando).
- Datas devem ser objetos `datetime`; strings **não** são convertidas silenciosamente.
- `data_conclusao < data_criacao` ⇒ `TaskValidationError`.
- Tarefa sem `data_conclusao` é **pendente**, não inválida.
- Mistura de datas com e sem fuso horário que impeça comparação ⇒ `TaskValidationError`.

## 5. Estilo de código

- Docstrings em todas as funções públicas e auxiliares.
- Nada de `assert` em código de produção (é removido com `python -O`).
- Sem valores codificados para passar em testes.

## 6. Testes

- Ferramenta: `pytest` (+ `pytest-cov` para medir cobertura).
- Arquivo principal: `tests/test_harness.py`.
- Valores esperados são calculados manualmente e documentados no próprio teste.
- Testes que dependem de "agora" devem passar `referencia` explicitamente (reprodutibilidade).
- Cada requisito da especificação deve estar mapeado em `docs/matriz_rastreabilidade.md`.

## 7. Decisões de negócio registradas

As decisões tomadas por ausência de definição nas fontes estão em
`specs/task_analyzer_spec.md`, seção 8 (Decisões e premissas).
