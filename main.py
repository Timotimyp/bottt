import telebot
from telebot import types
import math
import pymorphy2
import wikipedia, re
import requests
import json


morph = pymorphy2.MorphAnalyzer()
wikipedia.set_lang("ru")

bot = telebot.TeleBot('5387429562:AAGQl6ZU5qftDhPPvnaYdx3rpiQvvuxaAc4')


@bot.message_handler(commands=["start"])
def start(message, res=False):
    markup_registration = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_r = types.KeyboardButton("Начать регистрацию")
    markup_registration.add(btn_r)

    print(message.chat.id)
    bot.send_message(message.chat.id, 'Я на связи. Напиши мне что-нибудь )', reply_markup=markup_registration)


markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_1 = types.KeyboardButton("Цифры")
btn2_1 = types.KeyboardButton("Слова")
btn3_1 = types.KeyboardButton("Фильмы")
btn4_1 = types.KeyboardButton("Добавить в закладки")
markup.add(btn1_1, btn2_1, btn3_1,
           btn4_1)

markup_first_step = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_2 = types.KeyboardButton("Поиск")
btn2_2 = types.KeyboardButton("Последние")
btn3_2 = types.KeyboardButton("Помощь")
markup_first_step.add(btn1_2, btn2_2, btn3_2)

markup_second_step = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_3 = types.KeyboardButton("Оу, я это уже видел")
btn2_3 = types.KeyboardButton("Это что-то новинькое")
markup_second_step.add(btn1_3, btn2_3)


@bot.message_handler(content_types=["text"])
def func(message):
    print(1)
    re = requests.get('https://botesite.herokuapp.com/api/chat_id_for_registration').json()
    print(re)
    chat_id = re['chat_id']

    if message.text == "Начать регистрацию":
        if message.chat.id in chat_id:
            bot.send_message(message.chat.id, 'Вы уже зарегистрированны', reply_markup=markup)
        else:
            r = bot.send_message(message.chat.id, text="Придумайте логин", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(r, login_check)

    elif message.chat.id in chat_id:

        if message.text == "Цифры":
            r = bot.send_message(message.chat.id, text="Напиши цифру", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(r, answer_number)

        if message.text == "Слова":
            r = bot.send_message(message.chat.id, text="Напиши слово", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(r, string_answer)

        if message.text == "Фильмы":
            bot.send_message(message.chat.id, text="Выберите опцию", reply_markup=markup_first_step)

        if message.text == "Помощь":
            helper(message)

        if message.text == "Поиск":
            r = bot.send_message(message.chat.id, text="Напиши фильм", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(r, film_answer)

        if message.text == "Последние":
            re = requests.get(f'https://botesite.herokuapp.com/api/get_last_film/{message.chat.id}').json()
            if re['film']:
                bot.send_message(message.chat.id, text=re['film'], reply_markup=markup)
            else:
                bot.send_message(message.chat.id, text='Ваши запросы не найдены', reply_markup=markup)

    else:
        bot.send_message(message.chat.id, 'Пожалуйста, пройдите регистрацию')


def login_check(message):

    re = requests.get('https://botesite.herokuapp.com/api/logins_for_registration').json()
    logins = re['logins']

    if message.text in logins:
        bot.send_message(message.chat.id, 'Такой логин уже существует')
        r = bot.send_message(message.chat.id, text="Попоробуйте другой")
        bot.register_next_step_handler(r, login_check)
    else:
        login = message.text
        r = bot.send_message(message.chat.id, 'Придумайте пароль')
        bot.register_next_step_handler(r, end_authorization, login)


def end_authorization(message, login):
    print(requests.post('https://botesite.herokuapp.com/api/create_new_profile',
               json={'chat_id': message.chat.id,
                     'login': login,
                     'password': message.text}).json())
    bot.send_message(message.chat.id, 'Спасибо за регестрацию! тепер в можете пользоваться нашим сайтом и ботом!\n'
                                      'https://botesite.herokuapp.com/', reply_markup=markup)

def answer_number(message):
    q = message.text

    requests.post('https://botesite.herokuapp.com/api/create_history_post',
                        json={'chat_id': message.chat.id,
                              'request': q,
                              'subject': 'number'}).json()

    if q.isdigit():
        if int(q) < 1000:
            r = bot.send_message(message.chat.id, text=f"Квадрат числа: {int(q) ** 2}\n"
                                                   f"Сумма чисел: {sum([int(i) for i in q])}\n"
                                                   f"Корень числа: {math.sqrt(int(q))}\n"
                                                   f"Факториал числа: {math.factorial(int(q))}\n"
                                                   f"произведение чисел: {eval(' * '.join([i for i in q]))}\n"
                                                   f"Простое или составное: {is_prime(int(q))}\n"
                                                   f"Чётное или не особо: {'Чётное' if int(q) % 2 == 0 else 'Не чётное'}\n"
                                                   f""
                                                   f""
                                                   f""
                                                   f"", reply_markup=markup)
            bot.register_next_step_handler(r, is_bookmark, message.text)
        else:
            r = bot.send_message(message.chat.id, text='Слишком большое число. Мы такое считать не можем :(', reply_markup=markup)
            bot.register_next_step_handler(r, is_bookmark, message.text)
    else:
        r = bot.send_message(message.chat.id, text='Неправильный формат ввода', reply_markup=markup)
        bot.register_next_step_handler(r, is_bookmark, message.text)


def string_answer(message):

    requests.post('https://botesite.herokuapp.com/api/create_history_post',
                        json={'chat_id': message.chat.id,
                              'request': message.text,
                              'subject': 'word'}).json()

    p = morph.parse(message.text)[0]
    r = bot.send_message(message.chat.id, text=f"Часть речи:{p.tag.POS}\n"
                                           f"Одушевленность:{p.tag.animacy}\n"
                                           f"Вид:{p.tag.aspect}\n"
                                           f"Падеж:{p.tag.case}\n"
                                           f"Род:{p.tag.gender}\n"
                                           f"Включенность:{p.tag.involvement}\n"
                                           f"Наклонение:{p.tag.mood}\n"
                                           f"Число:{p.tag.number}\n"
                                           f"Лицо:{p.tag.person}\n"
                                           f"Время:{p.tag.tense}\n"
                                           f"Переходность:{p.tag.transitivity}\n"
                                           f"Залог:{p.tag.voice}\n"
                                           f"\n"
                                           f"\n"
                                           f"{rr(message)}", reply_markup=markup)

    bot.register_next_step_handler(r, is_bookmark, message.text)


def rating(message, film_name):
    if message.text == "Оу, я это уже видел":
        r = bot.send_message(message.chat.id, text="Это прекрасно, Оцените фильм от 1 до 10", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(r, save_rating, film_name)

    if message.text == "Это что-то новинькое":
        bot.send_message(message.chat.id, text="Очень хороший фильм, советую посмотреть)", reply_markup=markup)


def save_rating(message, film_name):
    response = requests.get(
        f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={film_name}&page=1',
        headers={'X-API-KEY': "7f118a01-f5a2-4b10-b7ea-85463dff50e2"
                 })

    re = response.json()

    gg = [i['genre'].capitalize() for i in re['films'][0]['genres']]
    try:
        if 0 < int(message.text) <= 10:
            if int(message.text) >= 5:
                re = requests.get(f'https://botesite.herokuapp.com/api/get_genres/{message.chat.id}').json()
                print(re['error'])
                if re['error'] == 'No error':
                    gen = re['genres']

                    if gen:
                        gen = json.loads(gen.replace("'", '"'))
                        for i in gg:
                            if i in gen:
                                gen[i] += 1
                            else:
                                gen[i] = 1
                    else:
                        gen = dict()
                        for i in gg:
                            gen[i] = 1
                    js_dik = json.dumps(gen, ensure_ascii=False)
                    print(js_dik)
                    requests.post(f'https://botesite.herokuapp.com/api/new_genres/{message.chat.id}',
                          json={'gen': js_dik}).json()


            r = bot.send_message(message.chat.id, "Спасибо за оценку)", reply_markup=markup)
            bot.register_next_step_handler(r, is_bookmark, film_name)
        else:
            r = bot.send_message(message.chat.id, text="Оцените фильм от 1 до 10!!!", reply_markup=None)
            bot.register_next_step_handler(r, save_rating, film_name)
    except ValueError:
        r = bot.send_message(message.chat.id, text="Оцените фильм от 1 до 10!!!", reply_markup=None)
        bot.register_next_step_handler(r, save_rating, film_name)



def rr(message):
    try:
        ny = wikipedia.page(message.text)
        wikitext = ny.content[:1000]
        wikimas = wikitext.split('.')
        wikimas = wikimas[:-1]
        wikitext2 = ''
        for x in wikimas:
            if not ('==' in x):
                if (len((x.strip())) > 3):
                    wikitext2 = wikitext2 + x + '.'
            else:
                break
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)
        return wikitext2
    except Exception as e:
        return 'В энциклопедии нет информации об этом'


def is_bookmark(message, content):
    if message.text == "Добавить в закладки":
        print(requests.post(f'https://botesite.herokuapp.com/api/add_bookmark/{message.chat.id}',
                      json={
                            'request': content}).json())
        bot.send_message(message.chat.id, 'Успешно добавленно в закладки')
    else:
        func(message)


def film_answer(message):

    requests.post('https://botesite.herokuapp.com/api/create_history_post',
                        json={'chat_id': message.chat.id,
                              'request': message.text,
                              'subject': 'film'}).json()
    try:

        response = requests.get(
            f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={message.text.capitalize()}&page=1',
            headers={'X-API-KEY': "7f118a01-f5a2-4b10-b7ea-85463dff50e2"
                     })

        re = response.json()

        poster = requests.get(re['films'][0]['posterUrl'])
        out = open("img.jpg", "wb")
        out.write(poster.content)
        out.close()
        q = open("img.jpg", "rb")
        f = ", ".join(i['genre'].capitalize() for i in re['films'][0]['genres'])
        ff = ", ".join(i['country'] for i in re['films'][0]['countries'])
        r = bot.send_photo(message.chat.id, q, caption=f"Название: {re['films'][0]['nameRu']}\n"
                                                       f"Название в оригинале: {re['films'][0]['nameEn']}\n"
                                                       f"Описание: {re['films'][0]['description']}\n"
                                                       f"Длина фильма: {re['films'][0]['filmLength']}\n"
                                                       f"Страна Производства: {ff}\n"
                                                       f"Жанр: {f}\n"
                                                       f"Рэйтинг: {re['films'][0]['rating']}\n", reply_markup=markup_second_step)
        bot.register_next_step_handler(r, rating, message.text)

    except:
        bot.send_message(message.chat.id, text='Такой фильм не найден', reply_markup=markup)


def is_prime(n):
    if n < 2:
        return 'Составное'
    if n == 2:
        return 'Простое'
    limit = math.sqrt(n)
    i = 2
    while i <= limit:
        if n % i == 0:
            return 'Составное'
        i += 1
    return 'Простое'


def helper(message):

    re = requests.get(f'https://botesite.herokuapp.com/api/get_genres/{message.chat.id}').json()
    if re['genres']:
        gen = re['genres']
        w = json.loads(gen.replace("'", '"'))

        e = []

        for i in w.keys():
            e.append(i)

        e = e[:3]
        q = {}
        list_second_step = []
        q1 = {}

        response = requests.get(
            'https://kinopoiskapiunofficial.tech/api/v2.2/films/top?type=TOP_100_POPULAR_FILMS&page=1',
            headers={'X-API-KEY': "7f118a01-f5a2-4b10-b7ea-85463dff50e2"
                     })

        re = response.json()


        for i in range(int(re['pagesCount'])):
            f = ", ".join(i['genre'].capitalize() for i in re['films'][i]['genres'])
            q[re['films'][i]['nameRu']] = f, re['films'][i]['rating']

        for i in q.keys():
            for j in e:
                if j in q[i][0].split(", "):
                    list_second_step.append(i)

        for i in list_second_step:
            if i not in q1:
                q1[i] = 1
            else:
                q1[i] += 1
        f = dict(sorted(q1.items(), key=lambda x: x[-1]))
        list_last_step = [i for i in f.keys()]
        list_last_step = list_last_step[len(list_last_step) - 3:len(list_last_step)]
        last = {}

        for i in list_last_step:
            last[i] = q[i][-1]
        ff = dict(sorted(last.items(), key=lambda x: x[-1]))
        name = [i for i in ff.keys()][-1]

        response = requests.get(
            f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={name}&page=1',
            headers={'X-API-KEY': "7f118a01-f5a2-4b10-b7ea-85463dff50e2"
                     })
        re = response.json()

        p = requests.get(re['films'][0]['posterUrl'])
        out = open("img.jpg", "wb")
        out.write(p.content)
        out.close()
        q = open("img.jpg", "rb")
        f = ", ".join(i['genre'].capitalize() for i in re['films'][0]['genres'])
        ff = ", ".join(i['country'] for i in re['films'][0]['countries'])
        if 'nameEn' in re['films'][0]:
            na = re['films'][0]['nameEn']
        else:
            na = re['films'][0]['nameRu']
        r = bot.send_photo(message.chat.id, q, caption=f"Советую посмотреть:\nНазвание: {re['films'][0]['nameRu']}\n"
                                                       f"Название в оригинале: {na}\n"
                                                       f"Описание: {re['films'][0]['description']}\n"
                                                       f"Длина фильма: {re['films'][0]['filmLength']}\n"
                                                       f"Страна Производства: {ff}\nЖанр: {f}\n"
                                                       f"Рэйтинг: {re['films'][0]['rating']}", reply_markup=markup)

        print(requests.post('https://botesite.herokuapp.com/api/create_history_post',
                            json={'chat_id': message.chat.id,
                                  'request': re['films'][0]['nameRu'],
                                  'subject': 'film'}).json())

        bot.register_next_step_handler(r, is_bookmark, re['films'][0]['nameRu'])
    else:
        bot.send_message(message.chat.id, 'Мы не можем помочь с выбором фильма, так как вы ещё не оценили ни одного(')


bot.infinity_polling()

