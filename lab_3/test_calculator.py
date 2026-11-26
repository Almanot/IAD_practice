import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


CALCULATOR = Path(__file__).resolve().with_name("calculator.py")


@dataclass(frozen=True)
class TestCase:
    title: str
    commands: tuple[tuple[str, ...], ...]
    expected_text: str
    expected_code: int = 0


CASES = (
    TestCase(
        "ТК-01 Стандартна доставка 2 кг",
        (("2", "--tariff", "standard"),),
        "74,00 грн",
    ),
    TestCase(
        "ТК-02 Доставка 2 кг за тарифом «Експрес»",
        (("2", "--tariff", "express"),),
        "116,00 грн",
    ),
    TestCase(
        "ТК-03 Пакування вантажу",
        (("2", "--tariff", "standard", "--pack"),),
        "99,00 грн",
    ),
    TestCase(
        "ТК-04 Найменша допустима маса",
        (("0,10", "--tariff", "standard"),),
        "51,20 грн",
    ),
    TestCase(
        "ТК-05 Маса нижча за нижню межу",
        (("0,09", "--tariff", "standard"),),
        "Маса має бути від 0,10 до 20,00 кг.",
        1,
    ),
    TestCase(
        "ТК-06 Найбільша допустима маса",
        (("20,00", "--tariff", "standard"),),
        "290,00 грн",
    ),
    TestCase(
        "ТК-07 Маса вища за верхню межу",
        (("20,01", "--tariff", "standard"),),
        "Маса має бути від 0,10 до 20,00 кг.",
        1,
    ),
    TestCase(
        "ТК-08 Порожнє значення маси",
        (("", "--tariff", "standard"),),
        "Введіть масу вантажу.",
        1,
    ),
    TestCase(
        "ТК-09 Три десяткові знаки в масі",
        (("2,005", "--tariff", "standard"),),
        "Введіть число з 0–2 десятковими знаками.",
        1,
    ),
    TestCase(
        "ТК-10 Тариф не задано",
        (("2",),),
        "Оберіть тариф.",
        1,
    ),
    TestCase(
        "ТК-11 Кома і крапка в десятковому записі",
        (("1,25", "--tariff", "standard"), ("1.25", "--tariff", "standard")),
        "65,00 грн",
    ),
    TestCase(
        "ТК-12 Нечислова маса",
        (("abc", "--tariff", "standard"),),
        "Введіть число з 0–2 десятковими знаками.",
        1,
    ),
    TestCase(
        "ТК-13 Невідомий тариф",
        (("2", "--tariff", "premium"),),
        "Невідомий тариф.",
        1,
    ),
)


def run_case(case: TestCase) -> bool:
    print(case.title)
    expected_line = case.expected_text + "\n"
    expected_stdout = expected_line if case.expected_code == 0 else ""
    expected_stderr = expected_line if case.expected_code != 0 else ""

    passed = True
    for args in case.commands:
        printable_args = json.dumps(args, ensure_ascii=False)
        print(f"  Аргументи {printable_args}")
        print(f"  Очікував «{case.expected_text}» (код {case.expected_code}).")

        try:
            result = subprocess.run(
                [sys.executable, "-X", "utf8", str(CALCULATOR), *args],
                capture_output=True,
                encoding="utf-8",
                check=False,
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            print("  Час очікування результату вичерпано.")
            passed = False
            continue

        actual_text = (result.stdout or result.stderr).rstrip("\n")
        print(f"  Отримав «{actual_text}» (код {result.returncode}).")
        if (result.returncode, result.stdout, result.stderr) != (
            case.expected_code,
            expected_stdout,
            expected_stderr,
        ):
            print(f"  Стандартний вивід {result.stdout!r}, вивід помилок {result.stderr!r}.")
            passed = False

    print("  Тест пройдено.\n" if passed else "  Тест не пройдено.\n")
    return passed


def main() -> int:
    print(f"Практична робота № 3. Тестування калькулятора доставки.\nPython {platform.python_version()}\n")
    passed = sum(run_case(case) for case in CASES)
    print(f"Успішно пройдено {passed} із {len(CASES)} тест-кейсів.")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
