#!/usr/bin/env python3
"""
Local demo script для демонстрации работы Code Agent
Работает без реальных API ключей, показывает логику работы
"""

import sys
from pathlib import Path

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


def demo_code_agent():
    """Демонстрация работы Code Agent."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]Code Agent Demo[/bold cyan]\n"
        "Демонстрация обработки Issue и создания Pull Request",
        border_style="cyan"
    ))

    # Симуляция Issue
    console.print("\n[bold]📋 Шаг 1: Получение Issue[/bold]")
    console.print("[dim]GET /repos/demo/repo/issues/1[/dim]")

    mock_issue = {
        "number": 1,
        "title": "Добавить функцию для вычисления суммы",
        "body": """
Необходимо создать файл `calculator.py` с функцией `add(a, b)`:
- Принимает два числа
- Возвращает их сумму
- Добавить docstring

Также создать тест для этой функции.
        """,
        "state": "open"
    }

    console.print(f"[green]✓[/green] Issue #{mock_issue['number']}: {mock_issue['title']}")
    console.print(f"[dim]{mock_issue['body'].strip()}[/dim]")

    # Симуляция анализа через LLM
    console.print("\n[bold]🤖 Шаг 2: Анализ требований через LLM[/bold]")
    console.print("[dim]POST /v1/chat/completions[/dim]")
    console.print("[yellow]⏳[/yellow] Отправка запроса к GPT-4o-mini...")

    analysis = """
Задача: Создать калькулятор с функцией сложения
Файлы для создания:
1. calculator.py - основной модуль
2. test_calculator.py - тесты

Функция add(a, b) должна:
- Принимать два аргумента (int или float)
- Возвращать их сумму
- Иметь docstring
    """

    console.print("[green]✓[/green] Получен анализ задачи")
    console.print(Panel(analysis.strip(), border_style="yellow", title="LLM Analysis"))

    # Симуляция генерации кода
    console.print("\n[bold]📝 Шаг 3: Генерация кода[/bold]")
    console.print("[yellow]⏳[/yellow] Генерация кода через LLM...")

    generated_code = '''"""Simple calculator module."""


def add(a: float, b: float) -> float:
    """
    Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b
'''

    console.print("[green]✓[/green] Код сгенерирован")
    console.print(Panel(generated_code, border_style="green", title="calculator.py",
                       subtitle="Generated Code"))

    # Симуляция создания ветки
    console.print("\n[bold]🌿 Шаг 4: Создание ветки[/bold]")
    console.print("[dim]POST /repos/demo/repo/git/refs[/dim]")
    branch_name = "agent/issue-1"
    console.print(f"[green]✓[/green] Создана ветка: [cyan]{branch_name}[/cyan]")

    # Симуляция коммита
    console.print("\n[bold]💾 Шаг 5: Создание коммита[/bold]")
    console.print("[dim]POST /repos/demo/repo/git/commits[/dim]")
    commit_msg = "feat: add calculator with add function\n\nImplements #1"
    console.print("[green]✓[/green] Коммит создан:")
    console.print(f"[dim]{commit_msg}[/dim]")

    # Симуляция создания PR
    console.print("\n[bold]🔀 Шаг 6: Создание Pull Request[/bold]")
    console.print("[dim]POST /repos/demo/repo/pulls[/dim]")

    pr_data = {
        "number": 2,
        "title": "feat: add calculator with add function",
        "body": f"Closes #{mock_issue['number']}\n\nАвтоматически создано Code Agent.",
        "html_url": "https://github.com/demo/repo/pull/2"
    }

    console.print(f"[green]✓[/green] Pull Request создан: [cyan]PR #{pr_data['number']}[/cyan]")
    console.print(f"[dim]URL: {pr_data['html_url']}[/dim]")

    console.print("\n[bold green]✅ Code Agent завершил работу успешно![/bold green]")


def demo_reviewer_agent():
    """Демонстрация работы Reviewer Agent."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold magenta]AI Reviewer Demo[/bold magenta]\n"
        "Демонстрация анализа Pull Request и публикации review",
        border_style="magenta"
    ))

    # Симуляция получения PR
    console.print("\n[bold]📋 Шаг 1: Получение Pull Request[/bold]")
    console.print("[dim]GET /repos/demo/repo/pulls/2[/dim]")

    mock_pr = {
        "number": 2,
        "title": "feat: add calculator with add function",
        "body": "Closes #1\n\nАвтоматически создано Code Agent.",
        "html_url": "https://github.com/demo/repo/pull/2"
    }

    console.print(f"[green]✓[/green] PR #{mock_pr['number']}: {mock_pr['title']}")

    # Симуляция получения diff
    console.print("\n[bold]📄 Шаг 2: Получение diff[/bold]")
    console.print("[dim]GET /repos/demo/repo/pulls/2/files[/dim]")

    diff_sample = """
+++ b/calculator.py
+def add(a: float, b: float) -> float:
+    \"\"\"Add two numbers together.\"\"\"
+    return a + b
    """

    console.print("[green]✓[/green] Получен diff (1 файл изменен)")
    console.print(Panel(diff_sample.strip(), border_style="cyan", title="Diff"))

    # Симуляция анализа через LLM
    console.print("\n[bold]🤖 Шаг 3: Анализ кода через LLM[/bold]")
    console.print("[dim]POST /v1/chat/completions[/dim]")
    console.print("[yellow]⏳[/yellow] Отправка кода на review к GPT-4o-mini...")

    review_text = """
## Code Review

### ✅ Положительные моменты:
- Функция реализована корректно
- Есть type hints
- Присутствует docstring
- Код соответствует требованиям Issue #1

### 💡 Предложения:
- Можно добавить проверку типов входных параметров
- Рекомендуется добавить примеры использования в docstring

### ✅ Вердикт: APPROVE
Код готов к merge. Все требования Issue выполнены.
    """

    console.print("[green]✓[/green] Получен AI review")
    console.print(Panel(review_text.strip(), border_style="green", title="AI Review"))

    # Симуляция проверки CI
    console.print("\n[bold]🔍 Шаг 4: Проверка CI/CD[/bold]")
    console.print("[dim]GET /repos/demo/repo/commits/abc123/check-runs[/dim]")

    ci_results = [
        ("Ruff Lint", "✅ Success"),
        ("Pytest", "✅ Success"),
        ("Docker Build", "✅ Success"),
    ]

    console.print("[green]✓[/green] CI проверки:")
    for check_name, status in ci_results:
        console.print(f"  {status} {check_name}")

    # Симуляция публикации review
    console.print("\n[bold]💬 Шаг 5: Публикация review комментария[/bold]")
    console.print("[dim]POST /repos/demo/repo/pulls/2/reviews[/dim]")

    console.print("[green]✓[/green] Review комментарий опубликован")
    console.print(f"[dim]URL: {mock_pr['html_url']}#review-123[/dim]")

    console.print("\n[bold green]✅ AI Reviewer завершил работу успешно![/bold green]")


def main():
    """Главная функция демо."""
    console.print("\n" + "="*70)
    console.print("[bold cyan]Code Agent System - Local Demo[/bold cyan]")
    console.print("Демонстрация работы без реальных API ключей")
    console.print("="*70)

    try:
        # Demo 1: Code Agent
        demo_code_agent()

        console.print("\n[dim]" + "-"*70 + "[/dim]")
        console.print("\n[yellow]⏳ Запуск AI Reviewer...[/yellow]\n")

        # Demo 2: Reviewer Agent
        demo_reviewer_agent()

        # Итоговая статистика
        console.print("\n" + "="*70)
        console.print(Panel.fit(
            "[bold green]✅ Демонстрация завершена успешно![/bold green]\n\n"
            "Показано:\n"
            "• Code Agent: Issue → Анализ → Генерация кода → PR\n"
            "• AI Reviewer: PR → Анализ → CI проверка → Review\n\n"
            "[dim]Для реальной работы настройте .env файл с API ключами[/dim]",
            border_style="green",
            title="🎉 Demo Complete"
        ))

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Демонстрация прервана пользователем[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()

