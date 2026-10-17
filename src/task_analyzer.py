"""TaskAnalyzer — Fase 2.

Calcula métricas de um conjunto de tarefas conforme `specs/task_analyzer_spec.md`:
totais, tempo médio de conclusão (geral e por prioridade) e taxa de atraso,
validando a consistência das datas.

Requer Python 3.11+ e usa somente a biblioteca padrão.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, tzinfo
from typing import Any, TypedDict

__all__ = ["AnalysisResult", "Task", "TaskValidationError", "analyze_tasks"]

_SECONDS_PER_HOUR: float = 3600.0
_DECIMAL_PLACES: int = 2


class TaskValidationError(ValueError):
    """Erro de validação de tarefa: dados ausentes, tipos inválidos ou datas inconsistentes.

    Attributes:
        task_id: identificador da tarefa que causou o erro, quando conhecido.
    """

    def __init__(self, message: str, task_id: str | int | None = None) -> None:
        """Cria o erro, prefixando a mensagem com o id da tarefa quando informado."""
        self.task_id: str | int | None = task_id
        prefix: str = f"Tarefa {task_id!r}: " if task_id is not None else ""
        super().__init__(f"{prefix}{message}")


@dataclass(frozen=True, slots=True)
class Task:
    """Tarefa de entrada (alternativa tipada ao uso de dicionários).

    Attributes:
        id: identificador da tarefa.
        prioridade: rótulo de prioridade (ex.: "alta").
        data_criacao: instante de criação.
        data_conclusao: instante de conclusão; ``None`` indica tarefa pendente.
        prazo: prazo de entrega; ``None`` indica tarefa sem prazo.
    """

    id: str | int
    prioridade: str
    data_criacao: datetime
    data_conclusao: datetime | None = None
    prazo: datetime | None = None

    @property
    def concluida(self) -> bool:
        """Indica se a tarefa foi concluída (RN-01)."""
        return self.data_conclusao is not None


class AnalysisResult(TypedDict):
    """Resultado de `analyze_tasks` (seção 5.3 da especificação)."""

    total_tarefas: int
    total_concluidas: int
    total_pendentes: int
    tempo_medio_conclusao_horas: float
    tempo_medio_conclusao_horas_por_prioridade: dict[str, float]
    taxa_atraso_percentual: float


def _safe_mean(values: list[float]) -> float:
    """Média aritmética; retorna 0.0 para lista vazia, evitando divisão por zero (RN-07)."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def _safe_percentage(part: int, total: int) -> float:
    """Percentual ``part / total * 100``; retorna 0.0 quando ``total`` não é positivo (RN-07)."""
    if total <= 0:
        return 0.0
    return (part / total) * 100.0


def _require_datetime(value: Any, field: str, task_id: str | int | None) -> datetime:
    """Garante que o campo obrigatório ``value`` é ``datetime``.

    Raises:
        TaskValidationError: campo ausente (EX-04) ou tipo inválido (EX-05).
    """
    if value is None:
        raise TaskValidationError(f"campo obrigatório '{field}' ausente.", task_id)
    return _check_datetime_type(value, field, task_id)


def _optional_datetime(value: Any, field: str, task_id: str | int | None) -> datetime | None:
    """Aceita ``None`` ou ``datetime`` para um campo opcional.

    Raises:
        TaskValidationError: tipo inválido (EX-05).
    """
    if value is None:
        return None
    return _check_datetime_type(value, field, task_id)


def _check_datetime_type(value: Any, field: str, task_id: str | int | None) -> datetime:
    """Rejeita valores que não sejam ``datetime`` (sem conversão silenciosa — DEC-01).

    Raises:
        TaskValidationError: tipo inválido (EX-05).
    """
    if not isinstance(value, datetime):
        raise TaskValidationError(
            f"campo '{field}' deve ser datetime, recebido {type(value).__name__}.", task_id
        )
    return value


def _is_after(later: datetime, earlier: datetime, fields: str, task_id: str | int | None) -> bool:
    """Retorna ``later > earlier``.

    Raises:
        TaskValidationError: as datas misturam valores com e sem fuso horário (EX-06).
    """
    try:
        return later > earlier
    except TypeError as exc:
        raise TaskValidationError(
            f"não é possível comparar {fields}: use datas todas com ou todas sem fuso horário.",
            task_id,
        ) from exc


def _parse_task(raw: Any) -> Task:
    """Converte e valida um item de entrada (``Task`` ou mapeamento) em ``Task`` normalizada.

    Raises:
        TaskValidationError: em qualquer violação de EX-01 a EX-07.
    """
    if isinstance(raw, Task):
        fields: Mapping[str, Any] = {
            "id": raw.id,
            "prioridade": raw.prioridade,
            "data_criacao": raw.data_criacao,
            "data_conclusao": raw.data_conclusao,
            "prazo": raw.prazo,
        }
    elif isinstance(raw, Mapping):
        fields = raw
    else:
        raise TaskValidationError(
            f"tipo de tarefa inválido: {type(raw).__name__}. Use Task ou um mapeamento (dict)."
        )

    task_id: Any = fields.get("id")
    if task_id is None or isinstance(task_id, bool) or not isinstance(task_id, (str, int)):
        raise TaskValidationError("campo 'id' ausente ou inválido (esperado str ou int).")

    prioridade: Any = fields.get("prioridade")
    if not isinstance(prioridade, str) or not prioridade.strip():
        raise TaskValidationError(
            "campo 'prioridade' ausente ou inválido (esperado texto não vazio).", task_id
        )

    data_criacao: datetime = _require_datetime(fields.get("data_criacao"), "data_criacao", task_id)
    data_conclusao: datetime | None = _optional_datetime(
        fields.get("data_conclusao"), "data_conclusao", task_id
    )
    prazo: datetime | None = _optional_datetime(fields.get("prazo"), "prazo", task_id)

    if data_conclusao is not None and _is_after(
        data_criacao, data_conclusao, "'data_criacao' e 'data_conclusao'", task_id
    ):
        raise TaskValidationError(
            "datas inconsistentes: 'data_conclusao' é anterior a 'data_criacao'.", task_id
        )

    return Task(
        id=task_id,
        prioridade=prioridade.strip().lower(),
        data_criacao=data_criacao,
        data_conclusao=data_conclusao,
        prazo=prazo,
    )


def _is_late(task: Task, referencia: datetime) -> bool:
    """Aplica RN-04: concluída após o prazo, ou pendente com prazo vencido em ``referencia``."""
    if task.prazo is None:
        return False
    if task.data_conclusao is not None:
        return _is_after(task.data_conclusao, task.prazo, "'data_conclusao' e 'prazo'", task.id)
    return _is_after(referencia, task.prazo, "'referencia' e 'prazo'", task.id)


def _collect_raw_tasks(tasks: Any) -> list[Any]:
    """Materializa a coleção de entrada em lista, rejeitando tipos que não são coleções (EX-07)."""
    if tasks is None:
        return []
    if isinstance(tasks, (str, bytes, Mapping, Task)):
        raise TaskValidationError(
            "'tasks' deve ser uma coleção de tarefas, não uma tarefa isolada ou texto."
        )
    try:
        return list(tasks)
    except TypeError as exc:
        raise TaskValidationError(
            f"'tasks' deve ser iterável, recebido {type(tasks).__name__}."
        ) from exc


def _default_reference(tasks: list[Task]) -> datetime:
    """Retorna o instante atual, no fuso das datas de entrada quando elas têm fuso."""
    zone: tzinfo | None = next(
        (t.data_criacao.tzinfo for t in tasks if t.data_criacao.tzinfo is not None), None
    )
    return datetime.now(zone)


def analyze_tasks(
    tasks: Iterable[Task | Mapping[str, Any]] | None,
    referencia: datetime | None = None,
) -> AnalysisResult:
    """Calcula as métricas de um conjunto de tarefas.

    Args:
        tasks: tarefas como ``Task`` ou ``dict`` com as chaves ``id``, ``prioridade``,
            ``data_criacao``, ``data_conclusao`` (opcional) e ``prazo`` (opcional).
            ``None`` é tratado como coleção vazia.
        referencia: instante usado para decidir se tarefas pendentes estão atrasadas.
            Padrão: agora (no fuso das datas, quando houver).

    Returns:
        ``AnalysisResult`` com ``total_tarefas``, ``total_concluidas``, ``total_pendentes``,
        ``tempo_medio_conclusao_horas``, ``tempo_medio_conclusao_horas_por_prioridade`` e
        ``taxa_atraso_percentual``. Médias e taxas valem ``0.0`` quando não há dados.

    Raises:
        TaskValidationError: se alguma tarefa for inválida — em especial quando
            ``data_conclusao`` é anterior a ``data_criacao``.

    Example:
        >>> from datetime import datetime
        >>> analyze_tasks([{"id": 1, "prioridade": "alta",
        ...                 "data_criacao": datetime(2026, 1, 1, 8),
        ...                 "data_conclusao": datetime(2026, 1, 1, 12)}])["tempo_medio_conclusao_horas"]
        4.0
    """
    parsed: list[Task] = [_parse_task(raw) for raw in _collect_raw_tasks(tasks)]

    if referencia is None:
        referencia = _default_reference(parsed)
    elif not isinstance(referencia, datetime):
        raise TaskValidationError(
            f"'referencia' deve ser datetime, recebido {type(referencia).__name__}."
        )

    duracoes_geral: list[float] = []
    duracoes_por_prioridade: dict[str, list[float]] = {}
    total_concluidas: int = 0
    total_atrasadas: int = 0

    for task in parsed:
        grupo: list[float] = duracoes_por_prioridade.setdefault(task.prioridade, [])
        if task.data_conclusao is not None:  # RN-01: concluída
            total_concluidas += 1
            horas: float = (
                task.data_conclusao - task.data_criacao
            ).total_seconds() / _SECONDS_PER_HOUR
            duracoes_geral.append(horas)
            grupo.append(horas)
        if _is_late(task, referencia):
            total_atrasadas += 1

    total_tarefas: int = len(parsed)

    return AnalysisResult(
        total_tarefas=total_tarefas,
        total_concluidas=total_concluidas,
        total_pendentes=total_tarefas - total_concluidas,
        tempo_medio_conclusao_horas=round(_safe_mean(duracoes_geral), _DECIMAL_PLACES),
        tempo_medio_conclusao_horas_por_prioridade={
            prioridade: round(_safe_mean(valores), _DECIMAL_PLACES)
            for prioridade, valores in sorted(duracoes_por_prioridade.items())
        },
        taxa_atraso_percentual=round(
            _safe_percentage(total_atrasadas, total_tarefas), _DECIMAL_PLACES
        ),
    )
