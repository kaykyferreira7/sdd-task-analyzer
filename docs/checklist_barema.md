# Checklist de avaliação — TaskAnalyzer (Fase 2)

> **O barema oficial não foi disponibilizado.** Este checklist é **provisório**. Ele foi montado a
> partir dos requisitos conhecidos: as regras de governança, a especificação de negócio e os
> critérios de aceitação do prompt de entrega. Quando o barema oficial estiver disponível, cada
> item dele deve ser acrescentado aqui com seu status real.

Legenda: ✅ comprovado · ⏳ pendente · ⚠️ depende de material não disponível

| # | Item | Status | Evidência |
|---|------|--------|-----------|
| 1 | Requisitos oficiais da Fase 2 identificados | ⚠️ | Foram usados os requisitos fornecidos pelo autor. O enunciado e o barema oficiais não estavam disponíveis (spec, seção 1). |
| 2 | Especificação registrada (SDD) | ✅ | `specs/task_analyzer_spec.md` |
| 3 | Regras de contexto registradas | ✅ | `CONTEXT_RULES.md` |
| 4 | Código implementado | ✅ | `src/task_analyzer.py` |
| 5 | `analyze_tasks` funcionando | ✅ | 62 testes aprovados; `python examples/demo.py` |
| 6 | `TaskValidationError` conforme o contrato | ✅ | `TestValidationErrors` |
| 7 | Métricas corretas (6 métricas) | ✅ | `test_full_result_matches_manual_calculation` (valores calculados à mão) |
| 8 | Python 3.11+ | ✅ | Suíte aprovada em 3.11.17 e 3.13.16 |
| 9 | Type hints em 100% das funções | ✅ | `test_every_function_is_fully_annotated` |
| 10 | Docstrings | ✅ | `test_every_function_has_docstring` |
| 11 | Prevenção de divisão por zero | ✅ | `test_empty_input`, `test_only_pending_tasks`, `test_no_nan_or_infinity` |
| 12 | Testes automatizados executados | ✅ | 62 aprovados e 0 reprovados |
| 13 | Casos de borda cobertos | ✅ | `TestEdgeCases` (CB-01 a CB-08) |
| 14 | Cobertura medida | ✅ | `pytest-cov`: 100% de linhas e ramos em `src/task_analyzer.py` |
| 15 | README completo | ✅ | `README.md` |
| 16 | Relatório de entrega | ✅ | `docs/relatorio_entrega.md` |
| 17 | Matriz de rastreabilidade | ✅ | `docs/matriz_rastreabilidade.md` |
| 18 | Roteiro do vídeo | ✅ | `docs/roteiro_video.md` |
| 19 | Histórico Git com commits descritivos | ✅ | Branches `main`, `develop` e `feature/task-analyzer-phase-2` locais (ver relatório, seção 7) |
| 20 | Autor dos commits configurado com os dados do aluno | ⏳ | Os commits locais foram assinados com a identidade do ambiente de desenvolvimento. O aluno deve redefinir o autor (relatório, seção 9). |
| 21 | Repositório público no GitHub | ⏳ | Não publicado: o GitHub CLI não estava autenticado |
| 22 | Branches publicadas | ⏳ | Depende do item 21 |
| 23 | Pull Request aberto | ⏳ | Depende do item 21 |
| 24 | Vídeo gravado e enviado | ⏳ | Depende do aluno |
| 25 | Entrega na plataforma acadêmica | ⏳ | Depende do aluno |
| 26 | Relatório em PDF | ✅ | `docs/relatorio_entrega.pdf`, gerado como precaução porque não se sabe se é exigido |
