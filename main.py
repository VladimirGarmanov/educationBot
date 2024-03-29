import time
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, executor
import openai

client = openai.OpenAI(api_key="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")
users = []
Assistant_ID = 'asst_3VD5o0y388LdPlOxzIbUZucd'
TELEGRAM_TOKEN = '7117382557:AAG3fXF_0WKRveNlCqZBLmig8VbUy3xI9Bg'

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    thread TEXT
)''')
conn.commit()


# Функция для добавления пользователя в базу данных
async def handle_with_assistant(message, chat_id):
    print('генерация началась')
    cursor.execute('SELECT thread FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    thread_id = result[0] if result is not None else add_user(chat_id)
    message_answer = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message.text

    )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=Assistant_ID,

    )

    time.sleep(10)
    run_status = client.beta.threads.runs.retrieve(
    )

    print(run_status.status)
    run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
    print(run_status.status)
    if run_status.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )

        msg = messages.data[0]
        role = msg.role
        content = msg.content[0].text.value
        print(f"{role.capitalize()}: {content}")
        await bot.send_message(chat_id=message.chat.id, text=content)


def add_user(chat_id):
    cursor.execute('SELECT chat_id FROM users WHERE chat_id = ?', (chat_id,))
    thread = client.beta.threads.create()
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO users (chat_id, thread) VALUES (?, ?)', (chat_id, thread.id))
        conn.commit()
    return thread.id


async def answer_user(message_response, message):
    await message.answer(message_response)

@dp.message_handler(commands=['start','help'])
async def start_command(message: types.Message):
        await message.answer("Добро пожаловать в бота для обучения менеджеров продаж\nСписок команд\n/about_company -  о компании\n/diverse - ассортимент\n/price - прайс\n/study - начать обучение\n/study_stop - закончить обучение\n/help - узнать о функциях бота")
@dp.message_handler(commands=['study'])
async def start_command(message: types.Message):
    add_user(message.chat.id)
    await message.answer("Диалог для обучения начат!")
    users.append(message.chat.id)
@dp.message_handler(commands=['study_stop'])
async def start_command(message: types.Message):
    add_user(message.chat.id)
    await message.answer("Привет! Вы зарегистрированы.")
    users.remove(message.chat.id)
@dp.message_handler(commands=['about_company'])
async def start_command(message: types.Message):

    await message.answer("Информация о компании.")
@dp.message_handler(commands=['diverse'])
async def start_command(message: types.Message):
    await bot.send_document(message.chat.id, open('files/buklet.pdf', 'rb'))


@dp.message_handler(commands=['price'])
async def start_command(message: types.Message):
    await bot.send_document(message.chat.id, open('files/price.xlsx', 'rb'))
    await message.answer("Прайс")


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def echo_message(message: types.Message):
    if message.chat.id in users:
        await handle_with_assistant(message, message.chat.id)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
