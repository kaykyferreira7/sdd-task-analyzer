# Roteiro do vídeo — TaskAnalyzer (Fase 2)

**Duração-alvo:** cerca de 5 minutos. Ajuste ao tempo oficial se o enunciado indicar outro.

**Formato:** o enunciado oficial não estava disponível, então os requisitos de formato não foram
confirmados. Por segurança, recomenda-se:

- vídeo **horizontal**;
- áudio claro;
- câmera ligada, se o professor exigir.

Antes de gravar, confira as regras na plataforma.

> Este documento é apenas o roteiro. **O vídeo ainda não foi gravado.**

## Preparação (antes de gravar)

- [ ] Abrir o repositório no editor, com o terminal na raiz do projeto.
- [ ] Ativar o ambiente virtual: `source .venv/bin/activate`.
- [ ] Rodar `pytest` uma vez para confirmar que tudo passa.
- [ ] Abrir no navegador o repositório e o Pull Request no GitHub, depois de publicados.
- [ ] Aumentar a fonte do terminal e do editor.

## Roteiro

| Tempo | Cena | O que mostrar | Fala sugerida |
|-------|------|---------------|---------------|
| 0:00–0:30 | Abertura | Rosto ou tela inicial com o título | "Olá, sou [nome]. Este é o TaskAnalyzer, Fase 2 do Bootcamp III. O objetivo é calcular métricas de tarefas com validação de dados, seguindo desenvolvimento orientado por especificação." |
| 0:30–1:00 | Estrutura | Árvore de pastas no editor | "O projeto separa especificação em `specs`, regras de governança em `CONTEXT_RULES.md`, código em `src`, testes em `tests` e a documentação de entrega em `docs`." |
| 1:00–1:45 | Especificação | `specs/task_analyzer_spec.md`, seções 3, 6 e 10 | "A especificação veio antes do código. Ela define requisitos, regras de negócio, por exemplo o que conta como atraso, os casos de borda e um conjunto de referência calculado à mão." |
| 1:45–2:45 | Implementação | `src/task_analyzer.py`: `TaskValidationError`, `_safe_mean`, `_parse_task`, `analyze_tasks` | "Todas as funções têm type hints. Datas inconsistentes disparam `TaskValidationError`. As médias usam `_safe_mean`, que devolve 0.0 para listas vazias e evita divisão por zero." |
| 2:45–3:15 | Demonstração | Terminal: `python examples/demo.py` | "No cenário de sucesso, a média geral é 12.67 horas e a taxa de atraso é 40%, iguais ao cálculo manual. No cenário de erro, a exceção é disparada para a tarefa 99." |
| 3:15–4:00 | Testes | Terminal: `pytest --cov=src --cov-branch --cov-report=term-missing` | "São 62 testes, todos aprovados, com 100% de cobertura de linhas e ramos. Eles cobrem lista vazia, só pendentes, prioridade sem concluídas, fuso horário e dados inválidos." |
| 4:00–4:40 | Git e Pull Request | Terminal: `git log --oneline --graph --all`; navegador com o Pull Request | "O histórico tem commits pequenos por etapa, nas branches main, develop e feature. O Pull Request da feature para develop resume as mudanças e os testes." |
| 4:40–5:00 | Conclusão | Tela do README | "A Fase 2 entrega as métricas, a validação e a rastreabilidade de cada requisito até seu teste. Obrigado." |

## Pendências do aluno

1. Publicar o repositório e abrir o Pull Request. Sem isso, a cena de 4:00 fica incompleta.
2. Gravar o vídeo seguindo este roteiro.
3. Enviar o vídeo e os links na plataforma acadêmica.
