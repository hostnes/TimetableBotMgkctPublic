import logging

from aiogram import Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By

from tier_state import InstallGroupState, SendMessage
from connect_server import users_service
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

async def startup(_):
    time.sleep(5)
    users_service.check_connect()


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    query_params = {'telegram_id': message.from_user.id}
    user_response = users_service.get_users(query_params)
    reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    if len(user_response) == 0:
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
        if user_response[0]['is_sender'] == True:
            reply_kb.add(KeyboardButton("🔕 Отписаться от рассылки"))
        else:
            reply_kb.add(KeyboardButton("🔔 Подписаться на расслыку"))
    if len(user_response) != 1:
        user_data = {'first_name': message.from_user.first_name,
                     'telegram_id': message.from_user.id}
        response = users_service.post_user(user_data)
    await message.answer('Тыкай', reply_markup=reply_kb)


@dp.message_handler(text='🪦Расписание на день🪦')
async def day_lessons(message: types.Message):
    query_params = {'telegram_id': message.from_user.id}
    response = users_service.get_users(query_params)
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


@dp.message_handler(text='♿️Расписание на неделю♿')
async def week_lessons(message: types.Message):
    query_params = {'telegram_id': message.from_user.id}
    response = users_service.get_users(query_params)
    group_number = str(response[0]['group_number'])
    await bot.send_photo(chat_id=message.chat.id, photo=open(f'server/bot/data/{group_number}.png', 'rb'))
    # await bot.send_photo(chat_id=message.chat.id, photo=open(f'data/{group_number}.png', 'rb'))


@dp.message_handler(text='👞🔄👟 Изменить группу')
async def change_group(message: types.Message, state: FSMContext):
    query_params = {'telegram_id': message.from_user.id}
    response = users_service.get_users(query_params)
    await state.update_data(user_id=response[0]['id'])
    await state.update_data(is_sender=response[0]['is_sender'])

    await message.answer('введите номер группы: ', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(InstallGroupState.get_group.state)


@dp.message_handler(text='🍻 Установить группу 🍻')
async def install_group(message: types.Message, state: FSMContext):
    query_params = {'telegram_id': message.from_user.id}
    response = users_service.get_users(query_params)
    await state.update_data(user_id=response[0]['id'])
    await message.answer('введите номер группы: ', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(InstallGroupState.get_group.state)


@dp.message_handler(state=InstallGroupState.get_group.state)
async def get_group_for_install(message: types.Message, state: FSMContext):
    query_params = {'telegram_id': message.from_user.id}
    user_response = users_service.get_users(query_params)
    data = await state.get_data()
    reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    pagination_buttons = []
    pagination_buttons_2 = []
    pagination_buttons.append(KeyboardButton("🪦Расписание на день🪦"))
    pagination_buttons.append(KeyboardButton("♿️Расписание на неделю♿"))
    reply_kb.row(*pagination_buttons)
    pagination_buttons_2.append(KeyboardButton("👞🔄👟 Изменить группу"))
    pagination_buttons_2.append(KeyboardButton("🗿Расписание звонков🗿"))
    reply_kb.row(*pagination_buttons_2)
    if user_response[0]['is_sender'] == True:
        reply_kb.add(KeyboardButton("🔕 Отписаться от рассылки"))
    else:
        reply_kb.add(KeyboardButton("🔔 Подписаться на расслыку"))
    if message.text in groups:
        user_data = {'group_number': message.text}
        response = users_service.patch_user(user_id=data['user_id'], user_data=user_data)
        await message.answer('окэ', reply_markup=reply_kb)
        await state.finish()
    else:
        await message.answer('введи норм группу э:')


@dp.message_handler(text='🔔 Подписаться на расслыку')
async def is_sender(message: types.Message):
    pagination_buttons = []
    pagination_buttons_2 = []
    query_params = {'telegram_id': message.from_user.id}
    response = users_service.get_users(query_params)
    user_id = response[0]['id']
    reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    pagination_buttons.append(KeyboardButton("🪦Расписание на день🪦"))
    pagination_buttons.append(KeyboardButton("♿️Расписание на неделю♿"))
    reply_kb.row(*pagination_buttons)
    pagination_buttons_2.append(KeyboardButton("👞🔄👟 Изменить группу"))
    pagination_buttons_2.append(KeyboardButton("🗿Расписание звонков🗿"))
    reply_kb.row(*pagination_buttons_2)
    user_data = {'is_sender': True}
    response = users_service.patch_user(user_id=user_id, user_data=user_data)
    reply_kb.add(KeyboardButton("🔕 Отписаться от рассылки"))
    await message.answer('Тыкай', reply_markup=reply_kb)


@dp.message_handler(text='🔕 Отписаться от рассылки')
async def is_sender(message: types.Message):
    pagination_buttons = []
    pagination_buttons_2 = []
    query_params = {'telegram_id': message.from_user.id}
    response = users_service.get_users(query_params)
    user_id = response[0]['id']
    reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    pagination_buttons.append(KeyboardButton("🪦Расписание на день🪦"))
    pagination_buttons.append(KeyboardButton("♿️Расписание на неделю♿"))
    reply_kb.row(*pagination_buttons)
    pagination_buttons_2.append(KeyboardButton("👞🔄👟 Изменить группу"))
    pagination_buttons_2.append(KeyboardButton("🗿Расписание звонков🗿"))
    reply_kb.row(*pagination_buttons_2)
    user_data = {'is_sender': False}
    reply_kb.add(KeyboardButton("🔔 Подписаться на расслыку"))
    response = users_service.patch_user(user_data, user_id)
    await message.answer('Тыкай', reply_markup=reply_kb)


@dp.message_handler(text='🗿Расписание звонков🗿')
async def install_group(message: types.Message, state: FSMContext):
    await message.answer('🤹 ‍️БУДНИ 🤹️\n1. 09:00 - 09:45 | 09:55 - 10:40\n2. 10:50 - 11:35 | 11:55 - 12:40\n3. 13:00 - 13:45 | 13:55 - 14:40\n4. 14:50 - 15:35 | 15:45 - 16:30\n'
                         '\n🏳️‍🌈 СУББОТА 🏳️‍🌈\n1. 09:00 - 09:45 | 09:55 - 10:40\n2. 10:50 - 11:35 | 11:50 - 12:35\n3. 12:50 - 13:35 | 13:45 - 14:30\n4. 14:40 - 15:25 | 15:35 - 16:20\n')


@dp.message_handler(commands=["info"])
async def info(msg: types.Message):
    users = users_service.get_all_users()
    await msg.answer(f"Самый лучший бот, для самого лучшего коллджа МИРА 😈😈😈\n"
                     "Создатель: @hostnes\n"
                     f"Количесто пользователей использующий бота: {int(len(users)) + 340}\n"
                     "Проект на GitHub: https://github.com/hostnes/TimetableBotMgkctPublic\n"
                     "Конфигурация сервера: 3 ядра CPU, 3 гб памяти, 15 гб NVMe")


@dp.message_handler(commands=["admin"])
async def info(msg: types.Message):
    if str(msg.from_user.id) == '1044392516':
        reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        reply_kb.add(KeyboardButton("разослать сообщение"))
        reply_kb.add(KeyboardButton("обновить расписание на день"))
        reply_kb.add(KeyboardButton("обновить расписание на неделю"))
        await msg.answer("админка: ", reply_markup=reply_kb)
    else:
        await msg.answer("Права к админке надо заслужить. хе")


@dp.message_handler(text='обновить расписание на день')
async def update_day_lessons(message: types.Message):
    if str(message.from_user.id) == '1044392516':
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
    if str(message.from_user.id) == '1044392516':
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
    if str(message.from_user.id) == '1044392516':
        await message.answer("Введи сообщение: ")
        await state.set_state(SendMessage.get_message.state)
    else:
        await message.answer('Access is denied')


@dp.message_handler(state=SendMessage)
async def get_group_for_install(message: types.Message, state: FSMContext):
    await message.answer('start')
    users = users_service.get_all_users()
    for i in users:
        try:
            await bot.send_message(chat_id=str(i['telegram_id']), text=message.text)
        except:
            pass
    await state.finish()
    await message.answer('end')


executor.start_polling(dp, skip_updates=True, on_startup=startup)
