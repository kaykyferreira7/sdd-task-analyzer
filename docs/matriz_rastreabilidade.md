# Matriz de rastreabilidade — TaskAnalyzer (Fase 2)

Esta matriz liga cada requisito de `specs/task_analyzer_spec.md` à implementação em
`src/task_analyzer.py` e aos testes em `tests/test_harness.py`.

A evidência é a mesma para todas as linhas: execução local de
`pytest --cov=src --cov-branch` em 17/10/2026, com **62 testes aprovados e 0 reprovados**.

## Requisitos funcionais

| Requisito | Implementação | Testes | Status |
|-----------|---------------|--------|--------|
| RF-01 — função `analyze_tasks` | `analyze_tasks` | `TestSuccessScenario::test_full_result_matches_manual_calculation`, `TestGovernance::test_public_api` | Aprovado |
| RF-02 — `total_tarefas` | `analyze_tasks` (`len(parsed)`) | `test_full_result_matches_manual_calculation`, `test_completed_and_pending_counts` | Aprovado |
| RF-03 — `total_concluidas` | `analyze_tasks`, laço RN-01 | `test_completed_and_pending_counts` | Aprovado |
| RF-04 — `total_pendentes` | `analyze_tasks` | `test_completed_and_pending_counts`, `test_only_pending_tasks` | Aprovado |
| RF-05 — `tempo_medio_conclusao_horas` | `_safe_mean`, `_SECONDS_PER_HOUR` | `test_average_completion_time_in_hours`, `test_fractional_hours_are_rounded_to_two_places` | Aprovado |
| RF-06 — média por prioridade | `duracoes_por_prioridade` em `analyze_tasks` | `test_average_per_priority`, `test_priority_keys_are_sorted`, `test_priority_is_normalized` | Aprovado |
| RF-07 — `taxa_atraso_percentual` | `_is_late`, `_safe_percentage` | Todos os testes de `TestDelayRate` | Aprovado |
| RF-08 — conclusão < criação lança erro | `_parse_task` | `test_completion_before_creation_raises`, `test_one_invalid_task_invalidates_whole_analysis` | Aprovado |
| RF-09 — entrada vazia retorna 0.0 | `_collect_raw_tasks`, `_safe_mean`, `_safe_percentage` | `TestEdgeCases::test_empty_input` (4 variações) | Aprovado |
| RF-10 — só pendentes retorna 0.0 | `_safe_mean` | `test_only_pending_tasks` | Aprovado |
| RF-11 — `TaskValidationError` | classe `TaskValidationError` | `test_exception_is_value_error_subclass` | Aprovado |

## Requisitos não funcionais (Context Rules)

| Requisito | Implementação | Testes / evidência | Status |
|-----------|---------------|--------------------|--------|
| RNF-01 — Python 3.11+ | `pyproject.toml` (`requires-python = ">=3.11"`) | Suíte executada em 3.11.17 e 3.13.16 | Aprovado |
| RNF-02 — type hints em 100% | Todo o módulo | `TestGovernance::test_every_function_is_fully_annotated` | Aprovado |
| RNF-03 — erro específico | `TaskValidationError` em toda validação | Todos os testes de `TestValidationErrors` | Aprovado |
| RNF-04 — sem divisão por zero | `_safe_mean`, `_safe_percentage` | `test_empty_input`, `test_only_pending_tasks`, `test_no_nan_or_infinity` | Aprovado |
| RNF-05 — sem dependências externas | Imports apenas da biblioteca padrão | `requirements.txt` lista só ferramentas de teste | Aprovado |

## Exceções

| Exceção | Condição | Testes | Status |
|---------|----------|--------|--------|
| EX-01 | Conclusão anterior à criação | `test_completion_before_creation_raises` | Aprovado |
| EX-02 | `id` ausente ou inválido | `test_missing_or_invalid_fields` (3 casos) | Aprovado |
| EX-03 | `prioridade` inválida | `test_missing_or_invalid_fields` (3 casos) | Aprovado |
| EX-04 | `data_criacao` ausente | `test_missing_or_invalid_fields` | Aprovado |
| EX-05 | Data que não é `datetime` | `test_missing_or_invalid_fields` (3 casos) | Aprovado |
| EX-06 | Mistura de datas com e sem fuso | `test_mixed_naive_and_aware_dates_raise`, `test_mixed_reference_and_deadline_timezones_raise` | Aprovado |
| EX-07 | Coleção ou item de tipo inválido | `test_invalid_collection_type` (5 casos), `test_invalid_item_type` (4 casos) | Aprovado |
| EX-08 | `referencia` inválida | `test_invalid_reference_type` | Aprovado |

## Regras de negócio e casos de borda

| ID | Testes | Status |
|----|--------|--------|
| RN-01 | `test_completed_and_pending_counts`, `test_task_concluida_property`, `test_pending_task_is_not_confused_with_inconsistent_dates` | Aprovado |
| RN-02 | `test_average_completion_time_in_hours` | Aprovado |
| RN-03 | `test_priority_group_without_completed_tasks` | Aprovado |
| RN-04 | `TestDelayRate` (8 testes) | Aprovado |
| RN-05 | `test_priority_is_normalized` | Aprovado |
| RN-06 | `test_only_pending_tasks`, `test_priority_group_without_completed_tasks` | Aprovado |
| RN-07 | `test_empty_input`, `test_no_nan_or_infinity` | Aprovado |
| RN-08 | `test_one_invalid_task_invalidates_whole_analysis` | Aprovado |
| CB-01 | `test_empty_input` | Aprovado |
| CB-02 | `test_only_pending_tasks` | Aprovado |
| CB-03 | `test_priority_group_without_completed_tasks` | Aprovado |
| CB-04 | `test_zero_duration_task` | Aprovado |
| CB-05 | `test_completed_exactly_on_deadline_is_not_late` | Aprovado |
| CB-06 | `test_fractional_hours_are_rounded_to_two_places` | Aprovado |
| CB-07 | `test_generator_input` | Aprovado |
| CB-08 | `test_timezone_aware_dates` | Aprovado |

## Critérios de aceitação

| CA | Testes | Status |
|----|--------|--------|
| CA-01 | `test_full_result_matches_manual_calculation` | Aprovado |
| CA-02 | `test_empty_input` | Aprovado |
| CA-03 | `test_only_pending_tasks` | Aprovado |
| CA-04 | `test_completion_before_creation_raises` | Aprovado |
| CA-05 | `TestValidationErrors` | Aprovado |
| CA-06 | `test_every_function_is_fully_annotated` | Aprovado |
| CA-07 | `test_no_nan_or_infinity` | Aprovado |
