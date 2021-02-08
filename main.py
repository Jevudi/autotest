from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
#Удаление ударения
def stress_del(word):
    if word.count('а́') > 0:
        word = word.replace('а́','а')
    if word.count('е́́') > 0:
        word = word.replace('е́́','е')
    if word.count('и́') > 0:
        word = word.replace('и́́','и')
    if word.count('о́') > 0:
        word = word.replace('о́́','о')
    if word.count('у́') > 0:
        word = word.replace('у́́','у')
    if word.count('ы́́') > 0:
        word = word.replace('ы́́','ы')
    if word.count('э́́') > 0:
        word = word.replace('э́́','э')
    if word.count('ю́́') > 0:
        word = word.replace('ю́́','ю')
    if word.count('я́') > 0:
        word = word.replace('я́','я')
    return word

#ожидание появления элемента на странице
def waiting(seconds, element_id):
    driver.implicitly_wait(seconds)  # seconds
    myDynamicElement = driver.find_elements_by_id(element_id)

#Печатает тест из оуна три раза
def printing_x_3():
    elem = driver.find_element_by_id('prno')
    right_version = driver.find_element_by_id('trainer_rno_right').text
    right_version = stress_del(right_version)
    elem.send_keys(right_version)
    time.sleep(3)
    elem = driver.find_element_by_id('prno')
    elem.send_keys(right_version)
    time.sleep(3)
    elem = driver.find_element_by_id('prno')
    elem.send_keys(right_version)

#Открываем файл с конфигом
config = open('config.txt', 'r')
#Тут будет пароль
passandlogin = []
#Отделяет логин от пароля
for line in config:
    passandlogin.append(line)
    print(line)
login = passandlogin[0]
password = passandlogin[1]
print('login: ' + login)

df = pd.read_csv('russian_language_base.csv')

question1 = ''
truevariant1 = ''
variant2 = ''
answer_from_base_counter = 0
cycle_counter = 0
mistake_counter = 0

driver = webdriver.Firefox("C:/Users/Jevud/PycharmProjects/")

#авторизация на сайте веб грамотей и заход в тест, на вход логин и пароль
driver.get('https://gramotei.cerm.ru/')
elem = driver.find_element_by_name('simora_login')
elem.send_keys(login)
elem = driver.find_element_by_name('simora_pass')
elem.send_keys(password)
elem.send_keys(Keys.ENTER)
time.sleep(20)
elem = driver.find_elements_by_class_name('exercise__playBtn')
elem[-1].click()
time.sleep(5)
while True:
    answer_from_base = False
    variant3 = ' '
    variant2 = ' '
    variant1 = ' '
    trueletter = None
    index_word_in_base = None
    # если есть кнопка продолжения то кликает на неё
    waiting(5, 'trainer_question')
    if len(driver.find_elements_by_class_name('button btn_yellow')) > 0:
        print('Кнопка продолжения задекчена')
        elem = driver.find_element_by_class_name('button btn_yellow')
        elem.click()
    # выполняется в случае если нет ошибки на данный момент (если не надо писать текст)
    if len(driver.find_elements_by_id('trainer_rno_note')) == 0:
        #Берём вопрос
        elem = driver.find_element_by_id('trainer_question')
        question1 = stress_del(elem.text)
        # Cмотрит варианты ответа
        elem = driver.find_elements_by_class_name('trainer_variant')
        variant1 = elem[0].text
        variant2 = elem[1].text
        #если вариантов больше 3 то берёт во внимание третий
        if len(driver.find_elements_by_class_name('trainer_variant')) == 3:
            variant3 = elem[2].text
        #ищет индекс вопроса в базе
        index_word_in_base = (df.index[df.question == question1])
        #и если находит, то присваивает trueletter ответ
        if index_word_in_base.size > 0:
            trueletter = (df['answer'].loc[index_word_in_base]).values[-1]
            #Срвнивает с ответом
            if trueletter == variant3:
                elem = driver.find_elements_by_class_name('trainer_variant')
                elem[2].click()
                answer_from_base_counter += 1
                answer_from_base = True
            if trueletter == variant2:
                elem = driver.find_elements_by_class_name('trainer_variant')
                elem[1].click()
                answer_from_base_counter += 1
                answer_from_base = True
            elif trueletter == variant1:
                elem = driver.find_element_by_class_name('trainer_variant')
                elem.click()
                answer_from_base_counter += 1
                answer_from_base = True
        #Кликает на случайный если не находит ответа в базе
        else:
            elem = driver.find_element_by_class_name('trainer_variant')
            elem.click()

    # Ждёт ошибки 10 секунд, если не появляется идёт дальше
    waiting(5, 'trainer_rno_note')

    # если есть ошибка и надо вводить текст
    if len(driver.find_elements_by_id('trainer_rno_note')) > 0:
        #пишет текст 3 раза
        printing_x_3()
        #Передаёт другую переменную как правильный вариант
        truevariant1 = variant2
        mistake_counter += 1
        #Удаляет строку из базы если ответ был не правильный
        if answer_from_base == True:
            df = df.drop(df[df.question == question1].index)
    else:
        truevariant1 = variant1


    #Обновление таблицы (только если ответ не был взят из базы)
    cycle_counter += 1
    if answer_from_base == False:
        df1 = pd.DataFrame({
            'question': [str(question1)],
            'answer': [str(truevariant1)],
        })
        df = df.append(df1)
        df.to_csv('russian_language_base.csv')
    # Печать логов
    print(' ')
    print(' ')
    print('Слово: ' + question1)
    print('Первый вариант: ' + variant1)
    print('Второй вариант: ' + variant2)
    print('Правильный ответ: ' + truevariant1)
    print('----------------------------------')
    print('Из базы было взято ' + str(answer_from_base_counter) + ' Ответов')
    print('Пройдено вопросов: ' + str(cycle_counter))
    print('Сделано ошибок:' + str(mistake_counter))
    print('Процент ошибок:' + str(mistake_counter / cycle_counter * 100))
