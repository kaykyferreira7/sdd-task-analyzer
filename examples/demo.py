"""Demonstração de uso do TaskAnalyzer com o conjunto de referência da especificação.

Execute a partir da raiz do repositório:

    python examples/demo.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from task_analyzer import TaskValidationError, analyze_tasks  # noqa: E402

TAREFAS: list[dict[str, Any]] = [
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


def main() -> None:
    """Executa a análise de sucesso e demonstra o cenário de erro."""
    print("== Cenário 1: sucesso ==")
    resultado = analyze_tasks(TAREFAS, referencia=datetime(2026, 1, 10))
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    print("\n== Cenário 2: datas inconsistentes ==")
    invalida: dict[str, Any] = {"id": 99, "prioridade": "alta",
                                "data_criacao": datetime(2026, 1, 2),
                                "data_conclusao": datetime(2026, 1, 1)}
    try:
        analyze_tasks([invalida])
    except TaskValidationError as erro:
        print(f"TaskValidationError: {erro}")


if __name__ == "__main__":
    main()
