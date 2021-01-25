from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

df = pd.read_csv('russian_language_base.csv')

question1 = ''
truevariant1 = ''
variant2 = ''

driver = webdriver.Firefox()

#авторизация на сайте веб грамотей и заход в тест, на вход логин и пароль
driver.get('https://gramotei.cerm.ru/')
elem = driver.find_element_by_name('simora_login')
elem.send_keys('y3172942')
elem = driver.find_element_by_name('simora_pass')
elem.send_keys('569362')
elem.send_keys(Keys.ENTER)
time.sleep(10)
elm = driver.find_element_by_class_name('exercise__playBtn')
elm.click()
time.sleep(5)
while True:
    trueletter = None
    a = None
    time.sleep(5)
    # выполняется в случае если нет ошибки на данный момент (не надо писать текст)
    if len(driver.find_elements_by_id('trainer_rno_note')) == 0:
        #Берём вопрос
        elem = driver.find_element_by_id('trainer_question')
        question1 = elem.text
        #ищет индекс слова в базе
        a = (str(df.index[df.question == question1]))[12:13]
        if a != ']':
            a = int(a)
            #= нужная буква
            trueletter = (df['answer'].loc[a])
        #Берём варианты
        elem = driver.find_elements_by_class_name('trainer_variant')
        variant1 = elem[0].text
        variant2 = elem[1].text
        #сравниваем с тем что есть
        if type(trueletter) != str:
            trueletter = None
            print('авиву')
        print(question1)
        print('trueletter = ' + str(trueletter))
        print('variant2 = ' + str(variant2))
        if trueletter == variant2:
            elem = driver.find_elements_by_class_name('trainer_variant')
            elem[1].click()
            print('Вариант был взят из базы')
        else:
            elem = driver.find_element_by_class_name('trainer_variant')
            elem.click()
    time.sleep(15)
    if len(driver.find_elements_by_id('trainer_rno_note')) > 0:
        #пишет текст 3 раза
        elem = driver.find_element_by_id('prno')
        right_version = driver.find_element_by_id('trainer_rno_right').text
        elem.send_keys(right_version)
        time.sleep(5)
        elem = driver.find_element_by_id('prno')
        elem.send_keys(right_version)
        time.sleep(5)
        elem = driver.find_element_by_id('prno')
        elem.send_keys(right_version)
        #Передаёт другую переменную как правильный вариант
        truevariant1 = variant2
    else:
        truevariant1 = variant1

    #Обновление таблицы
    df1 = pd.DataFrame({
        'question': [str(question1)],
        'answer': [str(truevariant1)],
    })
    df = df.append(df1)
    df.to_csv('russian_language_base.csv')
