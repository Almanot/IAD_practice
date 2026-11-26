import argparse
import re
import sys
from typing import NoReturn


TARIFFS = {
    "standard": (50, 12),
    "express": (80, 18),
}
PACKAGING_KOPIYKAS = 2_500
MASS_RANGE_ERROR = "Маса має бути від 0,10 до 20,00 кг."
MASS_FORMAT = re.compile(r"([0-9]+)(?:[.,]([0-9]{1,2}))?")


class CalculatorParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        return (
            "python calculator.py МАСА --tariff ТАРИФ [--pack]\n\n"
            "Вкажіть масу від 0,10 до 20,00 кг. Можна ввести кому або крапку "
            "та до двох цифр після неї.\n"
            "Доступні тарифи standard (стандартний) та express (експрес).\n"
            "Додайте --pack, щоб урахувати пакування за 25 грн.\n"
        )

    def error(self, _message: str) -> NoReturn:
        self.exit(1, "Некоректні параметри запуску.\n" + self.format_help())


def parse_mass(text: str) -> int:
    text = text.strip()
    if not text:
        raise ValueError("Введіть масу вантажу.")

    match = MASS_FORMAT.fullmatch(text)
    if match is None:
        raise ValueError("Введіть число з 0–2 десятковими знаками.")

    kilograms, fraction = match.groups()
    kilograms = kilograms.lstrip("0") or "0"
    if len(kilograms) > 2:
        raise ValueError(MASS_RANGE_ERROR)

    mass = int(kilograms) * 100 + int((fraction or "").ljust(2, "0"))
    if not 10 <= mass <= 2_000:
        raise ValueError(MASS_RANGE_ERROR)

    return mass


def calculate_price(mass_hundredths: int, tariff: str | None, pack: bool) -> int:
    if not tariff:
        raise ValueError("Оберіть тариф.")
    if tariff not in TARIFFS:
        raise ValueError("Невідомий тариф.")

    base_hryvnias, hryvnias_per_kg = TARIFFS[tariff]
    # Ставка у гривнях за кілограм дорівнює ставці в копійках за 0,01 кг.
    price = base_hryvnias * 100 + hryvnias_per_kg * mass_hundredths
    if pack:
        price += PACKAGING_KOPIYKAS
    return price


def main() -> int:
    parser = CalculatorParser(allow_abbrev=False)
    parser.add_argument("mass", nargs="?", default="")
    parser.add_argument("--tariff")
    parser.add_argument("--pack", action="store_true")
    args = parser.parse_args()

    try:
        mass = parse_mass(args.mass)
        price = calculate_price(mass, args.tariff, args.pack)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1

    hryvnias, kopiykas = divmod(price, 100)
    print(f"{hryvnias},{kopiykas:02d} грн")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
