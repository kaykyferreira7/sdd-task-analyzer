"""Harness de testes do TaskAnalyzer (Fase 2).

Os valores esperados foram calculados manualmente (ver `specs/task_analyzer_spec.md`, seção 10)
e estão comentados junto a cada asserção. Nenhum valor esperado é obtido chamando
a própria função testada.
"""

from __future__ import annotations

import doctest
import inspect
import math
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import task_analyzer
from task_analyzer import AnalysisResult, Task, TaskValidationError, analyze_tasks

REFERENCIA: datetime = datetime(2026, 1, 10, 0, 0)

EXPECTED_KEYS: set[str] = {
    "total_tarefas",
    "total_concluidas",
    "total_pendentes",
    "tempo_medio_conclusao_horas",
    "tempo_medio_conclusao_horas_por_prioridade",
    "taxa_atraso_percentual",
}


def make_task(
    task_id: int | str,
    prioridade: str,
    criacao: datetime,
    conclusao: datetime | None = None,
    prazo: datetime | None = None,
) -> dict[str, Any]:
    """Monta uma tarefa no formato de dicionário do contrato."""
    return {
        "id": task_id,
        "prioridade": prioridade,
        "data_criacao": criacao,
        "data_conclusao": conclusao,
        "prazo": prazo,
    }


@pytest.fixture
def reference_tasks() -> list[dict[str, Any]]:
    """Conjunto de referência da seção 10 da especificação."""
    return [
        # 4 h, concluída antes do prazo
        make_task(1, "alta", datetime(2026, 1, 1, 8), datetime(2026, 1, 1, 12), datetime(2026, 1, 1, 18)),
        # 24 h, concluída após o prazo -> atrasada
        make_task(2, "alta", datetime(2026, 1, 1, 8), datetime(2026, 1, 2, 8), datetime(2026, 1, 1, 20)),
        # 10 h, sem prazo
        make_task(3, "media", datetime(2026, 1, 2, 9), datetime(2026, 1, 2, 19)),
        # pendente, prazo 05/01 < referência 10/01 -> atrasada
        make_task(4, "baixa", datetime(2026, 1, 3, 10), None, datetime(2026, 1, 5, 10)),
        # pendente, prazo 20/01 > referência -> em dia
        make_task(5, "media", datetime(2026, 1, 4, 10), None, datetime(2026, 1, 20, 10)),
    ]


# --------------------------------------------------------------------------- #
# Cenário 1 — sucesso (RF-01 a RF-07, CA-01)
# --------------------------------------------------------------------------- #
class TestSuccessScenario:
    def test_full_result_matches_manual_calculation(self, reference_tasks: list[dict[str, Any]]) -> None:
        result: AnalysisResult = analyze_tasks(reference_tasks, referencia=REFERENCIA)
        assert result == {
            "total_tarefas": 5,
            "total_concluidas": 3,
            "total_pendentes": 2,
            "tempo_medio_conclusao_horas": 12.67,  # (4 + 24 + 10) / 3 = 12.666...
            "tempo_medio_conclusao_horas_por_prioridade": {
                "alta": 14.0,  # (4 + 24) / 2
                "baixa": 0.0,  # nenhuma concluída
                "media": 10.0,  # só a tarefa 3
            },
            "taxa_atraso_percentual": 40.0,  # 2 atrasadas / 5 * 100
        }

    def test_result_has_exactly_the_contract_keys(self, reference_tasks: list[dict[str, Any]]) -> None:
        result = analyze_tasks(reference_tasks, referencia=REFERENCIA)
        assert set(result.keys()) == EXPECTED_KEYS

    def test_result_types(self, reference_tasks: list[dict[str, Any]]) -> None:
        result = analyze_tasks(reference_tasks, referencia=REFERENCIA)
        for key in ("total_tarefas", "total_concluidas", "total_pendentes"):
            assert type(result[key]) is int
        for key in ("tempo_medio_conclusao_horas", "taxa_atraso_percentual"):
            assert type(result[key]) is float
        assert all(type(v) is float for v in result["tempo_medio_conclusao_horas_por_prioridade"].values())

    def test_completed_and_pending_counts(self) -> None:
        tasks = [
            make_task(1, "alta", datetime(2026, 1, 1), datetime(2026, 1, 1, 1)),
            make_task(2, "alta", datetime(2026, 1, 1)),
            make_task(3, "baixa", datetime(2026, 1, 1)),
        ]
        result = analyze_tasks(tasks, referencia=REFERENCIA)
        assert result["total_tarefas"] == 3
        assert result["total_concluidas"] == 1
        assert result["total_pendentes"] == 2
        assert result["total_concluidas"] + result["total_pendentes"] == result["total_tarefas"]

    def test_average_completion_time_in_hours(self) -> None:
        # 30 min, 1 h 30 min e 2 dias -> (0.5 + 1.5 + 48) / 3 = 16.666... -> 16.67
        base = datetime(2026, 3, 1, 9)
        tasks = [
            make_task(1, "x", base, base + timedelta(minutes=30)),
            make_task(2, "x", base, base + timedelta(hours=1, minutes=30)),
            make_task(3, "x", base, base + timedelta(days=2)),
        ]
        assert analyze_tasks(tasks, referencia=REFERENCIA)["tempo_medio_conclusao_horas"] == 16.67

    def test_average_per_priority(self) -> None:
        base = datetime(2026, 3, 1)
        tasks = [
            make_task(1, "alta", base, base + timedelta(hours=2)),
            make_task(2, "alta", base, base + timedelta(hours=6)),  # alta = (2 + 6) / 2 = 4.0
            make_task(3, "baixa", base, base + timedelta(hours=9)),  # baixa = 9.0
            make_task(4, "critica", base, base + timedelta(hours=1)),
            make_task(5, "critica", base, base + timedelta(hours=1)),
            make_task(6, "critica", base, base + timedelta(hours=2)),  # critica = 4 / 3 = 1.33
        ]
        result = analyze_tasks(tasks, referencia=REFERENCIA)
        assert result["tempo_medio_conclusao_horas_por_prioridade"] == {
            "alta": 4.0,
            "baixa": 9.0,
            "critica": 1.33,
        }
        # geral = (2 + 6 + 9 + 1 + 1 + 2) / 6 = 3.5
        assert result["tempo_medio_conclusao_horas"] == 3.5

    def test_priority_keys_are_sorted(self, reference_tasks: list[dict[str, Any]]) -> None:
        keys = list(analyze_tasks(reference_tasks, referencia=REFERENCIA)[
            "tempo_medio_conclusao_horas_por_prioridade"
        ])
        assert keys == ["alta", "baixa", "media"]

    def test_accepts_task_dataclass(self) -> None:
        tasks = [
            Task(1, "alta", datetime(2026, 1, 1, 8), datetime(2026, 1, 1, 11)),
            Task(2, "alta", datetime(2026, 1, 1, 8)),
        ]
        result = analyze_tasks(tasks, referencia=REFERENCIA)
        assert result["total_concluidas"] == 1
        assert result["tempo_medio_conclusao_horas"] == 3.0

    def test_task_concluida_property(self) -> None:
        assert Task(1, "a", datetime(2026, 1, 1), datetime(2026, 1, 2)).concluida is True
        assert Task(2, "a", datetime(2026, 1, 1)).concluida is False

    def test_does_not_mutate_input(self, reference_tasks: list[dict[str, Any]]) -> None:
        snapshot = [dict(t) for t in reference_tasks]
        analyze_tasks(reference_tasks, referencia=REFERENCIA)
        assert reference_tasks == snapshot


# --------------------------------------------------------------------------- #
# Taxa de atraso (RF-07, RN-04)
# --------------------------------------------------------------------------- #
class TestDelayRate:
    def test_completed_after_deadline_is_late(self) -> None:
        t = make_task(1, "a", datetime(2026, 1, 1), datetime(2026, 1, 3), datetime(2026, 1, 2))
        assert analyze_tasks([t], referencia=REFERENCIA)["taxa_atraso_percentual"] == 100.0

    def test_completed_exactly_on_deadline_is_not_late(self) -> None:
        prazo = datetime(2026, 1, 2, 12)
        t = make_task(1, "a", datetime(2026, 1, 1), prazo, prazo)
        assert analyze_tasks([t], referencia=REFERENCIA)["taxa_atraso_percentual"] == 0.0

    def test_pending_with_expired_deadline_is_late(self) -> None:
        t = make_task(1, "a", datetime(2026, 1, 1), None, datetime(2026, 1, 5))
        assert analyze_tasks([t], referencia=REFERENCIA)["taxa_atraso_percentual"] == 100.0

    def test_pending_with_future_deadline_is_not_late(self) -> None:
        t = make_task(1, "a", datetime(2026, 1, 1), None, datetime(2026, 2, 1))
        assert analyze_tasks([t], referencia=REFERENCIA)["taxa_atraso_percentual"] == 0.0

    def test_task_without_deadline_is_never_late(self) -> None:
        t = make_task(1, "a", datetime(2025, 1, 1))
        assert analyze_tasks([t], referencia=REFERENCIA)["taxa_atraso_percentual"] == 0.0

    def test_rate_uses_total_tasks_as_denominator(self) -> None:
        # 1 atrasada em 3 tarefas -> 33.33 %
        tasks = [
            make_task(1, "a", datetime(2026, 1, 1), datetime(2026, 1, 3), datetime(2026, 1, 2)),
            make_task(2, "a", datetime(2026, 1, 1), datetime(2026, 1, 2)),
            make_task(3, "a", datetime(2026, 1, 1)),
        ]
        assert analyze_tasks(tasks, referencia=REFERENCIA)["taxa_atraso_percentual"] == 33.33

    def test_default_reference_is_now(self) -> None:
        # prazo muito no passado/futuro garante resultado estável sem passar referencia
        tasks = [
            make_task(1, "a", datetime(2000, 1, 1), None, datetime(2000, 1, 2)),
            make_task(2, "a", datetime(2000, 1, 1), None, datetime(2999, 1, 1)),
        ]
        assert analyze_tasks(tasks)["taxa_atraso_percentual"] == 50.0

    def test_default_reference_with_timezone_aware_dates(self) -> None:
        tz = timezone(timedelta(hours=-3))
        tasks = [make_task(1, "a", datetime(2000, 1, 1, tzinfo=tz), None, datetime(2000, 1, 2, tzinfo=tz))]
        assert analyze_tasks(tasks)["taxa_atraso_percentual"] == 100.0


# --------------------------------------------------------------------------- #
# Casos de borda (RF-09, RF-10, CB-01 a CB-08)
# --------------------------------------------------------------------------- #
class TestEdgeCases:
    EMPTY_RESULT: dict[str, Any] = {
        "total_tarefas": 0,
        "total_concluidas": 0,
        "total_pendentes": 0,
        "tempo_medio_conclusao_horas": 0.0,
        "tempo_medio_conclusao_horas_por_prioridade": {},
        "taxa_atraso_percentual": 0.0,
    }

    @pytest.mark.parametrize("empty", [[], (), None, iter([])])
    def test_empty_input(self, empty: Any) -> None:
        assert analyze_tasks(empty, referencia=REFERENCIA) == self.EMPTY_RESULT

    def test_only_pending_tasks(self) -> None:
        tasks = [
            make_task(1, "alta", datetime(2026, 1, 1)),
            make_task(2, "baixa", datetime(2026, 1, 2)),
        ]
        result = analyze_tasks(tasks, referencia=REFERENCIA)
        assert result["total_concluidas"] == 0
        assert result["total_pendentes"] == 2
        assert result["tempo_medio_conclusao_horas"] == 0.0
        assert result["tempo_medio_conclusao_horas_por_prioridade"] == {"alta": 0.0, "baixa": 0.0}
        assert result["taxa_atraso_percentual"] == 0.0

    def test_priority_group_without_completed_tasks(self) -> None:
        tasks = [
            make_task(1, "alta", datetime(2026, 1, 1, 0), datetime(2026, 1, 1, 5)),
            make_task(2, "baixa", datetime(2026, 1, 1)),
        ]
        by_priority = analyze_tasks(tasks, referencia=REFERENCIA)["tempo_medio_conclusao_horas_por_prioridade"]
        assert by_priority == {"alta": 5.0, "baixa": 0.0}

    def test_zero_duration_task(self) -> None:
        moment = datetime(2026, 1, 1, 10)
        result = analyze_tasks([make_task(1, "a", moment, moment)], referencia=REFERENCIA)
        assert result["total_concluidas"] == 1
        assert result["tempo_medio_conclusao_horas"] == 0.0

    def test_fractional_hours_are_rounded_to_two_places(self) -> None:
        # 20 min = 0.3333... h -> 0.33
        base = datetime(2026, 1, 1)
        result = analyze_tasks([make_task(1, "a", base, base + timedelta(minutes=20))], referencia=REFERENCIA)
        assert result["tempo_medio_conclusao_horas"] == 0.33

    def test_generator_input(self) -> None:
        def gen() -> Iterator[dict[str, Any]]:
            yield make_task(1, "a", datetime(2026, 1, 1, 0), datetime(2026, 1, 1, 2))
            yield make_task(2, "a", datetime(2026, 1, 1, 0), datetime(2026, 1, 1, 4))

        result = analyze_tasks(gen(), referencia=REFERENCIA)
        assert result["total_tarefas"] == 2
        assert result["tempo_medio_conclusao_horas"] == 3.0

    def test_timezone_aware_dates(self) -> None:
        tz = timezone(timedelta(hours=-3))
        t = make_task(
            1, "a",
            datetime(2026, 1, 1, 8, tzinfo=tz),
            datetime(2026, 1, 1, 10, tzinfo=tz),
            datetime(2026, 1, 1, 9, tzinfo=tz),
        )
        result = analyze_tasks([t], referencia=datetime(2026, 1, 10, tzinfo=tz))
        assert result["tempo_medio_conclusao_horas"] == 2.0
        assert result["taxa_atraso_percentual"] == 100.0

    def test_priority_is_normalized(self) -> None:
        base = datetime(2026, 1, 1)
        tasks = [
            make_task(1, "Alta", base, base + timedelta(hours=2)),
            make_task(2, " alta ", base, base + timedelta(hours=4)),
        ]
        by_priority = analyze_tasks(tasks, referencia=REFERENCIA)["tempo_medio_conclusao_horas_por_prioridade"]
        assert by_priority == {"alta": 3.0}

    def test_missing_optional_keys_in_dict(self) -> None:
        t = {"id": "T-1", "prioridade": "a", "data_criacao": datetime(2026, 1, 1)}
        result = analyze_tasks([t], referencia=REFERENCIA)
        assert result["total_pendentes"] == 1
        assert result["taxa_atraso_percentual"] == 0.0

    def test_no_nan_or_infinity(self, reference_tasks: list[dict[str, Any]]) -> None:
        for tasks in (reference_tasks, [], [make_task(1, "a", datetime(2026, 1, 1))]):
            result = analyze_tasks(tasks, referencia=REFERENCIA)
            floats = [
                result["tempo_medio_conclusao_horas"],
                result["taxa_atraso_percentual"],
                *result["tempo_medio_conclusao_horas_por_prioridade"].values(),
            ]
            assert all(math.isfinite(v) for v in floats)


# --------------------------------------------------------------------------- #
# Cenário 2 — erros (RF-08, RF-11, EX-01 a EX-08)
# --------------------------------------------------------------------------- #
class TestValidationErrors:
    def test_completion_before_creation_raises(self) -> None:
        t = make_task(42, "alta", datetime(2026, 1, 2), datetime(2026, 1, 1))
        with pytest.raises(TaskValidationError, match="anterior a 'data_criacao'") as info:
            analyze_tasks([t], referencia=REFERENCIA)
        assert info.value.task_id == 42
        assert "Tarefa 42" in str(info.value)

    def test_one_invalid_task_invalidates_whole_analysis(self, reference_tasks: list[dict[str, Any]]) -> None:
        reference_tasks.append(make_task(99, "a", datetime(2026, 1, 2), datetime(2026, 1, 1, 23, 59)))
        with pytest.raises(TaskValidationError) as info:
            analyze_tasks(reference_tasks, referencia=REFERENCIA)
        assert info.value.task_id == 99

    def test_pending_task_is_not_confused_with_inconsistent_dates(self) -> None:
        t = make_task(1, "a", datetime(2026, 1, 2), None)
        assert analyze_tasks([t], referencia=REFERENCIA)["total_pendentes"] == 1

    def test_exception_is_value_error_subclass(self) -> None:
        assert issubclass(TaskValidationError, ValueError)
        err = TaskValidationError("mensagem")
        assert err.task_id is None
        assert str(err) == "mensagem"

    @pytest.mark.parametrize(
        ("task", "fragment"),
        [
            ({"prioridade": "a", "data_criacao": datetime(2026, 1, 1)}, "'id'"),
            ({"id": True, "prioridade": "a", "data_criacao": datetime(2026, 1, 1)}, "'id'"),
            ({"id": 1.5, "prioridade": "a", "data_criacao": datetime(2026, 1, 1)}, "'id'"),
            ({"id": 1, "data_criacao": datetime(2026, 1, 1)}, "'prioridade'"),
            ({"id": 1, "prioridade": "   ", "data_criacao": datetime(2026, 1, 1)}, "'prioridade'"),
            ({"id": 1, "prioridade": 3, "data_criacao": datetime(2026, 1, 1)}, "'prioridade'"),
            ({"id": 1, "prioridade": "a"}, "'data_criacao' ausente"),
            ({"id": 1, "prioridade": "a", "data_criacao": "2026-01-01"}, "deve ser datetime"),
            (
                {"id": 1, "prioridade": "a", "data_criacao": datetime(2026, 1, 1), "data_conclusao": "2026-01-02"},
                "'data_conclusao' deve ser datetime",
            ),
            (
                {"id": 1, "prioridade": "a", "data_criacao": datetime(2026, 1, 1), "prazo": 20260102},
                "'prazo' deve ser datetime",
            ),
        ],
    )
    def test_missing_or_invalid_fields(self, task: dict[str, Any], fragment: str) -> None:
        with pytest.raises(TaskValidationError, match=fragment):
            analyze_tasks([task], referencia=REFERENCIA)

    def test_mixed_naive_and_aware_dates_raise(self) -> None:
        t = make_task(1, "a", datetime(2026, 1, 1), datetime(2026, 1, 2, tzinfo=timezone.utc))
        with pytest.raises(TaskValidationError, match="fuso horário"):
            analyze_tasks([t], referencia=REFERENCIA)

    def test_mixed_reference_and_deadline_timezones_raise(self) -> None:
        t = make_task(1, "a", datetime(2026, 1, 1), None, datetime(2026, 1, 2))
        with pytest.raises(TaskValidationError, match="fuso horário"):
            analyze_tasks([t], referencia=datetime(2026, 1, 10, tzinfo=timezone.utc))

    @pytest.mark.parametrize(
        "bad_collection",
        [
            {"id": 1, "prioridade": "a", "data_criacao": datetime(2026, 1, 1)},
            "tarefas",
            b"tarefas",
            42,
            Task(1, "a", datetime(2026, 1, 1)),
        ],
    )
    def test_invalid_collection_type(self, bad_collection: Any) -> None:
        with pytest.raises(TaskValidationError, match="'tasks'"):
            analyze_tasks(bad_collection, referencia=REFERENCIA)

    @pytest.mark.parametrize("bad_item", [None, 1, "tarefa", ["lista"]])
    def test_invalid_item_type(self, bad_item: Any) -> None:
        with pytest.raises(TaskValidationError, match="tipo de tarefa inválido"):
            analyze_tasks([bad_item], referencia=REFERENCIA)

    def test_invalid_reference_type(self) -> None:
        with pytest.raises(TaskValidationError, match="'referencia'"):
            analyze_tasks([], referencia="2026-01-10")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Governança (RNF-01 a RNF-04, CA-06) e regressão
# --------------------------------------------------------------------------- #
class TestGovernance:
    def test_every_function_is_fully_annotated(self) -> None:
        functions = [
            obj
            for _, obj in inspect.getmembers(task_analyzer, inspect.isfunction)
            if obj.__module__ == task_analyzer.__name__
        ]
        methods = [TaskValidationError.__init__, Task.concluida.fget]
        for func in [*functions, *methods]:
            signature = inspect.signature(func)
            for name, param in signature.parameters.items():
                if name == "self":
                    continue
                assert param.annotation is not inspect.Parameter.empty, f"{func.__name__}.{name}"
            assert signature.return_annotation is not inspect.Signature.empty, func.__name__

    def test_every_function_has_docstring(self) -> None:
        for _, obj in inspect.getmembers(task_analyzer, inspect.isfunction):
            if obj.__module__ == task_analyzer.__name__:
                assert inspect.getdoc(obj), obj.__name__

    def test_module_doctests(self) -> None:
        results = doctest.testmod(task_analyzer)
        assert results.attempted > 0
        assert results.failed == 0

    def test_public_api(self) -> None:
        assert set(task_analyzer.__all__) == {"AnalysisResult", "Task", "TaskValidationError", "analyze_tasks"}

    def test_regression_reference_dataset_stays_stable(self, reference_tasks: list[dict[str, Any]]) -> None:
        # Repetir a análise não altera o resultado (função pura).
        first = analyze_tasks(reference_tasks, referencia=REFERENCIA)
        second = analyze_tasks(reference_tasks, referencia=REFERENCIA)
        assert first == second
