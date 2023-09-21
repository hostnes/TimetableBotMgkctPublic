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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bot.bot_creation import bot
week_days = {
    0: 'понедельник',
    1: 'вторник',
    2: 'среда',
    3: 'четверг',
    4: 'пятница',
    5: 'суббота',
    6: 'воскресенье',
}


def pars_html():
    # driver = webdriver.Remote('http://selenium:4444', desired_capabilities=DesiredCapabilities.CHROME)
    driver = webdriver.Safari()
    try:
        driver.get(url='https://mgkct.minskedu.gov.by/персоналии/учащимся/расписание-занятий-на-день')
        time.sleep(3)
        with open('data/day.html', 'w') as file:
            file.write(driver.page_source)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
    week_day_today = week_days[1 + datetime.datetime.weekday(datetime.datetime.today())]
    # with open('bot/data/day.html') as file:
    with open('data/day.html') as file:
        src = file.read()
    data = []
    soup = BeautifulSoup(src, 'lxml')
    group_lxml = soup.find('div', id="wrapperTables").find_all('div')
    group = []
    for key, day in week_days.items():
        try:
            driver = soup.find('div', string=f'65 - {day}').find_next().find_all('tr')
            week_day_today = day
        except:
            pass
    data.append(
        {'day': (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m.%y'), 'week_day': week_day_today})
    for item in group_lxml[::2]:
        group.append(item.text.strip().split(' ')[0])
    for group_number in group:
        print(group_number)
        if group_number == 'Лицей':
            break
        number_lessons = []
        lessons = []
        cabinets = []
        bad_group = ['160*', '161*', '162*', '163*', '164*']
        driver = soup.find('div', string=f'{group_number} - {week_day_today}').find_next().find_all('tr')

        if len(driver) != 0:
            for i in driver[0].find_all('th'):
                number_lessons.append(i.text.strip().split('№')[-1])

            for i in driver[1].find_all('td'):
                lessons.append(i.text.strip())

            for i in driver[2].find_all('td'):
                test = []
                for item in i:
                    if str(item) == '<br/>':
                        pass
                    else:
                        test.append(item)
                cabinets.append(test)
            correctness_data = len(lessons) - len(cabinets)
            for i in range(0, correctness_data):
                cabinets.append(['-'])
            for key1, value1 in bad_group_numbers.items():
                if group_number == key1:
                    group_number = value1
            data.append({f'{group_number}': {
                'number_lessons': number_lessons,
                'lessons': lessons,
                'cabinets': cabinets,
            }
            })
        else:
            for key1, value1 in bad_group_numbers.items():
                if group_number == key1:
                    group_number = value1
            data.append({f'{group_number}': {
                'number_lessons': None,
                'lessons': None,
                'cabinets': None,
            }
            })

        with open('data/lessons.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

pars_html()
