import asyncio
import logging

from aiogram import Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By

from tier_state import InstallGroupState, SendMessage
from connect_server import db_service
import datetime

import time
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from bot_creation import bot

import os
logging.basicConfig(level=logging.INFO)

dp = Dispatcher(bot, storage=MemoryStorage())


week_days = (
    'понедельник',
    'вторник',
    'среда',
    'четверг',
    'пятница',
    'суббота',
    'воскресенье',
)


number_week_days = {
    0: 'понедельник',
    1: 'вторник',
    2: 'среда',
    3: 'четверг',
    4: 'пятница',
    5: 'суббота',
    6: 'понедельник',
}

groups = []

with open('server/bot/data/day.html') as file:
    src = file.read()
soup = BeautifulSoup(src, 'lxml')
group_lxml = soup.find('div', id="wrapperTables").find_all('div')
for item in group_lxml[::2]:
    groups.append(item.text.strip().split(' ')[0])


def get_data(message):
    query_params = {'telegram_id': message.chat.id}
    response = db_service.get_chats(query_params)
    if len(response) == 0:
        chat_data = {'title_group': message.chat.title,
                     'telegram_id': message.chat.id}
        response = db_service.post_chat(chat_data)
        return [response]
    else:
        return response


def create_reply_kb(response):
    reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    if response[0]['group_number'] == '':
        reply_kb.add(KeyboardButton("🍻 Установить группу 🍻"))
    else:
        pagination_buttons = []
        pagination_buttons_2 = []
        pagination_buttons.append(KeyboardButton("🪦Расписание на день🪦"))
        pagination_buttons.append(KeyboardButton("♿️Расписание на неделю♿"))
        reply_kb.row(*pagination_buttons)
        pagination_buttons_2.append(KeyboardButton("👞🔄👟 Изменить группу"))
        pagination_buttons_2.append(KeyboardButton("🗿Расписание звонков🗿"))
        reply_kb.row(*pagination_buttons_2)
        if response[0]['is_sender'] == True:
            reply_kb.add(KeyboardButton("🔕 Отписаться от рассылки"))
        else:
            reply_kb.add(KeyboardButton("🔔 Подписаться на рассылку"))
    return reply_kb


async def check_admin(message):
    if str(message.chat.id['0']) == "-":
        chat_member = await bot.get_chat_member(message.chat.id, bot.id)
        if chat_member.status in ('administrator', 'creator'):
            return True
        return False
    return True


async def common_group_operation(message: types.Message, state: FSMContext):
    await message.answer('Введите номер группы: ', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(InstallGroupState.get_group.state)


async def startup(_):
    time.sleep(5)
    db_service.check_connect()


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    response = get_data(message)
    reply_kb = create_reply_kb(response)
    chat_member = await bot.get_chat_member(message.chat.id, bot.id)
    if response[0]['telegram_id'][0] == '-':
        if chat_member.status in ('administrator', 'creator'):
            await message.answer('Тыкай', reply_markup=reply_kb)
        else:
            await message.answer('Для работы бота в беседе требуется дать ему права администратора. после изменения прав доступа пропишите /start')
    else:
        await message.answer('Тыкай', reply_markup=reply_kb)


@dp.message_handler(commands=["info"])
async def info(msg: types.Message):
    chats = db_service.get_chats()
    users = []
    groups = []
    for chat in chats:
        if chat['telegram_id'][0] == '':
            users.append(chat)
        else:
            groups.append(chat)
    await msg.answer(f"Самый лучший бот, для самого лучшего коллджа МИРА 😈😈😈\n"
                     "Создатель: @hostnes\n"
                     f"Количесто пользователей использующий бота: {int(len(users))}\n"
                     f"Количесто групп в которые используют бота: {int(len(groups))}\n"
                     "Проект на GitHub: https://github.com/hostnes/TimetableBotMgkctPublic\n"
                     "Конфигурация сервера: 4 ядра CPU, 6 гб памяти, 100 гб NVMe")


@dp.message_handler(commands=["admin"])
async def info(msg: types.Message):
    if str(msg.chat.id) == '1044392516':
        reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        reply_kb.add(KeyboardButton("разослать сообщение"))
        reply_kb.add(KeyboardButton("обновить расписание на день"))
        reply_kb.add(KeyboardButton("обновить расписание на неделю"))
        await msg.answer("админка: ", reply_markup=reply_kb)
    else:
        await msg.answer("Права к админке надо заслужить. хе")


@dp.message_handler(text='👞🔄👟 Изменить группу')
async def change_group(message: types.Message, state: FSMContext):
    if await check_admin(message):
        response = get_data(message)
        if len(response) != 0:
            await common_group_operation(message, state)
        else:
            await message.answer("Вышло обновление бота. пропишите /start для того чтобы продолжить.")
    else:
        await message.answer("Права дайте боту, а")


@dp.message_handler(text='🍻 Установить группу 🍻')
async def install_group(message: types.Message, state: FSMContext):
    if await check_admin(message):
        response = get_data(message)
        if len(response) != 0:
            await common_group_operation(message, state)
        else:
            await message.answer("Вышло обновление бота. пропишите /start для того чтобы продолжить.")
    else:
        await message.answer("Права дайте боту, а")

@dp.message_handler(lambda message: True, state=InstallGroupState.get_group)
async def get_group_for_install(message: types.Message, state: FSMContext):
    if await check_admin(message):
        response = get_data(message)
        if len(response) != 0:
            if message.text in groups:
                db_data = {'group_number': message.text}
                response = db_service.patch_chat(chat_id=response[0]['id'], chat_data=db_data)
                reply_kb = create_reply_kb([response])
                await message.answer('окэ', reply_markup=reply_kb)
                await state.finish()
            else:
                await message.answer('введи норм группу э:')
        else:
            await message.answer("Вышло обновление бота. пропишите /start для того чтобы продолжить.")
    else:
        await message.answer("Права дайте боту, а")


@dp.message_handler(text='🪦Расписание на день🪦')
async def day_lessons(message: types.Message):
    if await check_admin(message):
        response = get_data(message)
        if len(response) != 0:
            group_number = str(response[0]['group_number'])
            with open('server/bot/data/lessons.json') as file:
                src = json.load(file)
            group_data = []
            for item in src:
                for key, value in item.items():
                    if key == group_number:
                        group_data = value
            text = ''
            text += f'*Группа {group_number}*\n'
            text += f"*{src[0]['week_day']} - {src[0]['day']}*\n"
            if group_data[0]['number_lesson'] != None:
                for i in group_data:
                    count = 0
                    text += f'\n*{i["number_lesson"]} пара*'
                    for lir in i["title"]:
                        if count == 0:
                            text += '\n'
                        try:
                            a = int(lir)
                            if count != 0:
                                text += '\n'
                            text += str(a)
                        except:

                            text += lir
                        count += 1
                    text += f'\nкаб: {i["cabinet"]}\n'
            else:
                text += '\nпар нет кумарим'
            await message.answer(text, parse_mode="Markdown")
        else:
            await message.answer("Вышло обновление бота. пропишите /start для того чтобы продолжить.")
    else:
        await message.answer("Права дайте боту, а")


@dp.message_handler(text='♿️Расписание на неделю♿')
async def week_lessons(message: types.Message):
    if await check_admin(message):
        response = get_data(message)
        if len(response) != 0:
            group_number = str(response[0]['group_number'])
            await bot.send_photo(chat_id=message.chat.id, photo=open(f'server/bot/data/{group_number}.png', 'rb'))
        else:
            await message.answer("Вышло обновление бота. пропишите /start для того чтобы продолжить.")
    else:
        await message.answer("Права дайте боту, а")


@dp.message_handler(text='🔔 Подписаться на рассылку')
async def is_sender(message: types.Message):
    if await check_admin(message):
        response = get_data(message)
        if len(response) != 0:
            obj_id = response[0]['id']
            data = {'is_sender': True}
            response = db_service.patch_chat(chat_id=obj_id, chat_data=data)
            reply_kb = create_reply_kb([response])
            await message.answer('Тыкай', reply_markup=reply_kb)
        else:
            await message.answer("Вышло обновление бота. пропишите /start для того чтобы продолжить.")


@dp.message_handler(text='🔕 Отписаться от рассылки')
async def is_sender(message: types.Message):
    if await check_admin(message):
        response = get_data(message)
        if len(response) != 0:
            obj_id = response[0]['id']
            data = {'is_sender': False}
            response = db_service.patch_chat(chat_id=obj_id, chat_data=data)
            reply_kb = create_reply_kb([response])
            await message.answer('Тыкай', reply_markup=reply_kb)

        else:
            await message.answer("Вышло обновление бота. пропишите /start для того чтобы продолжить.")
    else:
        await message.answer("Права дайте боту, а")


@dp.message_handler(text='🗿Расписание звонков🗿')
async def install_group(message: types.Message):
    if await check_admin(message):
        response = get_data(message)
        if len(response) != 0:
            await message.answer('🤹 ‍️БУДНИ 🤹️\n1. 09:00 - 09:45 | 09:55 - 10:40\n2. 10:50 - 11:35 | 11:55 - 12:40\n3. 13:00 - 13:45 | 13:55 - 14:40\n4. 14:50 - 15:35 | 15:45 - 16:30\n'
                                '\n🏳️‍🌈 СУББОТА 🏳️‍🌈\n1. 09:00 - 09:45 | 09:55 - 10:40\n2. 10:50 - 11:35 | 11:50 - 12:35\n3. 12:50 - 13:35 | 13:45 - 14:30\n4. 14:40 - 15:25 | 15:35 - 16:20\n')
        else:
            await message.answer("Вышло обновление бота. пропишите /start для того чтобы продолжить.")
    else:
        await message.answer("Права дайте боту, а")


@dp.message_handler(text='обновить расписание на день')
async def update_day_lessons(message: types.Message):
    if str(message.chat.id) == '1044392516':
        await message.answer('start')
        groups = []
        data = []
        with open('server/bot/data/lessons.json') as file:
            test = json.load(file)
        try:
            driver = webdriver.Remote('http://selenium:4444', desired_capabilities=DesiredCapabilities.CHROME)
            driver.get(url='https://mgkct.minskedu.gov.by/персоналии/учащимся/расписание-занятий-на-день')
            time.sleep(3)
            with open('server/bot/data/day.html', 'w') as file:
                file.write(driver.page_source)
        except:
            pass
        driver.close()
        driver.quit()
        with open('server/bot/data/day.html') as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        group_lxml = soup.find('div', id="wrapperTables").find_all('div')
        week_day_today = group_lxml[0].text.strip().split(' ')[-1]
        for item in group_lxml[::2]:
            groups.append(item.text.strip().split(' ')[0])
        if datetime.date.weekday(datetime.date.today()) == 5:
            datetime_now = (datetime.date.today() + datetime.timedelta(days=2)).strftime('%d.%m.%y')
        else:
            datetime_now = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m.%y')
        data.append({
            'day': datetime_now,
            'week_day': week_day_today
        })
        for group_number in groups:
            await message.answer(group_number)
            lessons = []
            group_obj = soup.find('div', string=f'{group_number} - {week_day_today}').find_next().find_all('tr')
            if len(group_obj) != 0:
                for i in range(0, len(group_obj[0].find_all('th'))):
                    lesson = {}
                    lesson['number_lesson'] = group_obj[0].find_all('th')[i].text.split('№')[-1]
                    lesson['title'] = group_obj[1].find_all('td')[i].text.strip()
                    try:
                        test_cab = []
                        test_cab_str = ''
                        for i in group_obj[2].find_all('td')[i]:
                            test_cab.append(i.text)
                        for i in test_cab:
                            if i == '':
                                test_cab_str += " "
                            test_cab_str += i
                        lesson['cabinet'] = test_cab_str
                    except:
                        lesson['cabinet'] = "-"
                    lessons.append(lesson)
                data.append({group_number: lessons})
            else:
                data.append({f'{group_number}': [{
                    'number_lesson': None,
                    'title': None,
                    'cabinet': None,
                    }]
                })
        with open('server/bot/data/lessons.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        await message.answer('ready')
    else:
        await message.answer('Access is denied')


@dp.message_handler(text='обновить расписание на неделю')
async def update_week_lessons(message: types.Message):
    if str(message.chat.id) == '1044392516':
        await message.answer('start')
        groups = []
        with open('server/bot/data/day.html') as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        group_lxml = soup.find('div', id="wrapperTables").find_all('div')
        for item in group_lxml[::2]:
            groups.append(item.text.strip().split(' ')[0])
        driver = webdriver.Remote('http://selenium:4444', desired_capabilities=DesiredCapabilities.CHROME)
        for i in groups:
            try:
                driver.get(
                    url=f'https://mgkct.minskedu.gov.by/персоналии/учащимся/расписание-занятий-на-неделю?group={i}')
                with open('server/service/templates/week.html', 'w') as file:
                    file.write(driver.page_source)
                driver.get(url=f'http://web-app:8000/api/week/')
                driver.set_window_size(1870, 920)
                elements = driver.find_elements(By.CLASS_NAME, 'content')
                elements[-1].screenshot(f'server/bot/data/{i}.png')
                await message.answer(i)
            except:
                pass
        driver.quit()
    else:
        await message.answer('Access is denied')


@dp.message_handler(text='разослать сообщение')
async def send_all(message: types.Message, state: FSMContext):
    if str(message.chat.id) == '1044392516':
        await message.answer("Введи сообщение: ")
        await state.set_state(SendMessage.get_message.state)
    else:
        await message.answer('Access is denied')


@dp.message_handler(state=SendMessage)
async def send_message(message: types.Message, state: FSMContext):
    await message.answer('start')
    users = db_service.get_all_users()
    for i in users:
        try:
            await bot.send_message(chat_id=str(i['telegram_id']), text=message.text)
        except:
            pass
    await state.finish()
    await message.answer('end')


executor.start_polling(dp, skip_updates=True, on_startup=startup)
