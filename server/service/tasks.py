import asyncio
import datetime
import os

import requests
from celery.task import periodic_task
from celery.schedules import crontab

import time
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bot.bot_creation import bot


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


@periodic_task(run_every=(crontab(hour='*/6')), name='week_task')
def week_task():
    print('start')
    groups = []
    with open('bot/data/day.html') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    group_lxml = soup.find('div', id="wrapperTables").find_all('div')
    for item in group_lxml[::2]:
        groups.append(item.text.strip().split(' ')[0])
    driver = webdriver.Remote('http://selenium:4444', desired_capabilities=DesiredCapabilities.CHROME)
    for i in groups:
        print(i)
        try:
            driver.get(url=f'https://mgkct.minskedu.gov.by/персоналии/учащимся/расписание-занятий-на-неделю?group={i}')
            with open('service/templates/week.html', 'w') as file:
                file.write(driver.page_source)
            driver.get(url=f'http://web-app:8000/api/week/')
            driver.set_window_size(1900, 920)
            elements = driver.find_elements(By.CLASS_NAME, 'content')
            elements[-1].screenshot(f'bot/data/{i}.png')
        except:
            pass
             # await bot.send_message(chat_id='1044392516', text='ошибка в недельном расссписании')
    driver.close()
    driver.quit()
    # await bot.send_message(chat_id='1044392516', text='произошло изменение расписания на неделю')


@periodic_task(run_every=(crontab(minute='*/10')), name='pars_html')
def pars_html():
    groups = []
    data = []
    with open('bot/data/lessons.json') as file:
        test = json.load(file)
    try:
        driver = webdriver.Remote('http://selenium:4444', desired_capabilities=DesiredCapabilities.CHROME)
        driver.get(url='https://mgkct.minskedu.gov.by/персоналии/учащимся/расписание-занятий-на-день')
        time.sleep(3)
        with open('bot/data/day.html', 'w') as file:
            file.write(driver.page_source)
    except:
        pass
    driver.close()
    driver.quit()
    with open('bot/data/day.html') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    group_lxml = soup.find('div', id="wrapperTables").find_all('div')
    week_day_today = group_lxml[0].text.strip().split(' ')[-1]
    if week_day_today != test[0]['week_day']:
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
        with open('bot/data/lessons.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        asyncio.run(class_schedule_task())


async def class_schedule_task():
    users = requests.get(f"http://{os.environ['WEB_APP_HOST']}:8000/api/users/")
    for user in users.json():
        try:
            if user['is_sender'] == True:
                group_number = str(user['group_number'])
                with open('bot/data/lessons.json') as file:
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
                    text += '\nпар нет, иди расчилься'
        except:
            pass
