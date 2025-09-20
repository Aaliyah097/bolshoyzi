import asyncio
from aiogram import Dispatcher, Bot, F, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from db.settings.creds import creds
from db.clients.rabbit.client import RabbitMQClient
import logging
from api.bot.menu import (
    main_menu, 
    group_menu, 
    script_menu,
    input_accepted_menu,
    retry_menu
)
from distributor.user_req import UserReq
from api.input_cleaner import validate_input, make_input_label

logging.basicConfig(level=logging.INFO)

bot = Bot(token=creds.TGBOT_API_KEY)
dp = Dispatcher(storage=MemoryStorage())
tasks_rabbit = RabbitMQClient(creds.rabbitmq_conn_string, 'tasks')

class Form(StatesGroup):
    waiting_for_input = State()


@dp.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    text, menu = await main_menu(again=False)
    await message.answer(text, reply_markup=menu, parse_mode="Markdown")


@dp.callback_query(F.data.startswith("group:"))
async def menu_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    group = callback.data.split(":")[1]

    if group == "home":
        text, menu = await main_menu(again=True)
        await callback.message.edit_text(text, reply_markup=menu, parse_mode="Markdown")
    else:
        text, menu = await group_menu(group)
        await callback.message.edit_text(text, reply_markup=menu, parse_mode="Markdown")

    await callback.answer()


@dp.callback_query(F.data.startswith("script:"))
async def menu_handler(callback: types.CallbackQuery, state: FSMContext):
    script_name = callback.data.split(":")[1]
    text, menu, has_input, script_input = await script_menu(script_name)
    await state.update_data(selected_script_name=script_name)
    await state.update_data(script_input_required=script_input)

    if has_input:
        await state.set_state(Form.waiting_for_input)
    else:
        # когда скрипт не требует ввода
        try:
            await tasks_rabbit.send(
                UserReq(
                    user_id=callback.from_user.id, 
                    script_name=script_name, 
                    payload=None
                ).model_dump()
            )
            text, menu = input_accepted_menu()
            await state.clear()
        except Exception as exc:
            logging.error(exc)
            text, menu = retry_menu()

    await callback.message.edit_text(text, reply_markup=menu, parse_mode="Markdown")
    await callback.answer()


# TODO если иметь инпут и аутпут стандартиизированный для программ и скриптов, то можно строить рекомендательную систему
# предлагая типа а вот хотите глубже копнуть, есть такие-то скрипты
@dp.message(Form.waiting_for_input)
async def process_input(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_script_name = user_data.get("selected_script_name")
    script_input_required = user_data.get("script_input_required")

    try:
        validate_input(script_input_required, message.text)
    except ValueError as exc:
        input_label, _ = make_input_label(script_input_required)
        text, menu = input_accepted_menu(error_happend=True)
        await message.answer(
            f"То, что ты написал(а) не похоже на *{input_label}*." + "\n\n" + text, 
            reply_markup=menu,
            parse_mode="Markdown"
        )
        return

    await state.update_data(user_payload=message.text)

    try:
        # когда скрипт требует ввода
        await tasks_rabbit.send(
            UserReq(
                user_id=message.from_user.id, 
                script_name=selected_script_name, 
                payload=message.text
            ).model_dump()
        )
        text, menu = input_accepted_menu()
        await state.clear()
    except Exception as exc:
        logging.error(exc)
        text, menu = retry_menu()

    await message.answer(text, reply_markup=menu)


@dp.callback_query(F.data == "retry_send_task")
async def retry_send_task(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    selected_script_name = user_data.get("selected_script_name")
    user_payload = user_data.get("user_payload")

    try:
        # повтор отправки скрипта
        await tasks_rabbit.send(
            UserReq(
                user_id=callback.from_user.id, 
                script_name=selected_script_name, 
                payload=user_payload
            ).model_dump()
        )
        text, menu = input_accepted_menu()
        await state.clear()
    except Exception as exc:
        logging.error(exc)
        text, menu = retry_menu()

    await callback.message.edit_text(text, reply_markup=menu, parse_mode="Markdown")
    await callback.answer()


async def main():
    await tasks_rabbit.connect()
    try:
        await dp.start_polling(bot)
    finally:
        await tasks_rabbit.close()


if __name__ == '__main__':
    asyncio.run(main())
