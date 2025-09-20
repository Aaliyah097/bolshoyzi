from typing import Callable
from executor.clean import clean_email, clean_username
from dataclasses import dataclass
import logging
from db.scripts.script_input import ScriptInput


@dataclass
class Cleaner:
    clean_func: Callable
    display_name: str


INPUT_MAP = {
    ScriptInput.USERNAME: Cleaner(clean_username, 'Имя пользователя'),
    ScriptInput.EMAIL: Cleaner(clean_email, 'Адрес электронной почты'),
}


def make_input_label(required_input: str) -> tuple[str, list[Cleaner]]:
    icleaners: list[Cleaner] = []
    ilabels: list[str] = []
    for itype in required_input.split(','):
        try:
            cleaner = INPUT_MAP[itype]
        except KeyError:
            logging.error(f"Клинер {itype} не найден !")
            continue
        ilabels.append(cleaner.display_name)
        icleaners.append(cleaner)
    return " или ".join(ilabels), icleaners


def validate_input(required_input: str, user_input: str):
    _, cleaners = make_input_label(required_input)
    if len(cleaners) == 0:
        return
    errors_count = 0
    for cleaner in cleaners:
        try:
            cleaner.clean_func(user_input)
        except ValueError:
            errors_count += 1
    if errors_count == len(cleaners):
        raise ValueError("Введенный текст не прошел валидацию")
