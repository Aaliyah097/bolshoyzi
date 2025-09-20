from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from db.scripts.repository import get_scripts
import logging
from api.input_cleaner import make_input_label
from api.bot.zitalks import talk_to_zi


MAIN_MENU_BUTTON = InlineKeyboardButton(text="🏠 Главное меню", callback_data="group:home")
RETURN_MENU_BUTTON = InlineKeyboardButton(text="⬅️ Назад", callback_data="group:return")


async def main_menu(again: bool = True) -> tuple[str, InlineKeyboardMarkup]:
    # выбирает группу скриптов
    scripts = await get_scripts(is_active=True)
    groups = {script.group for script in scripts}
    kb = [
        [InlineKeyboardButton(text=group, callback_data=f"group:{group}")] 
        for group in groups
    ]
    return (
        talk_to_zi('main_menu', again=again), 
        InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)
    )


async def group_menu(group: str) -> tuple[str, InlineKeyboardMarkup]:
    # выбирает скрипт
    scripts = await get_scripts(is_active=True, group=group)
    return (
        talk_to_zi('scripts').format(category=group), 
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=script.label, callback_data=f"script:{script.name}")
                    for script in scripts
                ],
                [MAIN_MENU_BUTTON]
            ],
            resize_keyboard=True
        )
    )


async def script_menu(script_name: str) -> tuple[str, InlineKeyboardMarkup, bool, str | None]:
    # выбрал скрипт и он либо требует доп вода либо сразу в очередь уходит 
    scripts = await get_scripts(is_active=True, script_name=script_name)
    if len(scripts) == 0:
        logging.error(f"Не найден скрипт с ид {script_name}")
        message = talk_to_zi('error')
    else:
        script = scripts[0]
        if script.input:
            input_label, _ = make_input_label(script.input)
            message, has_input = talk_to_zi('input').format(param=input_label), True
        else:
            message, has_input = talk_to_zi('ok'), False

    return message, InlineKeyboardMarkup(
        inline_keyboard=[[MAIN_MENU_BUTTON]],
        resize_keyboard=True
    ), has_input, script.input


def input_accepted_menu(error_happend: bool = False) -> tuple[str, InlineKeyboardMarkup]:
    # скрипт принят в работу
    return talk_to_zi('ok' if not error_happend else 'error'), InlineKeyboardMarkup(
        inline_keyboard=[[MAIN_MENU_BUTTON]],
        resize_keyboard=True
    )


def retry_menu() -> tuple[str, InlineKeyboardMarkup]:
    # не удалось поставить задачу в очередь, предлагает повторить попытку
    return talk_to_zi('error'), InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Повторить попытку", callback_data="retry_send_task")],
            [MAIN_MENU_BUTTON]
        ],
        resize_keyboard=True
    )
