from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from api import dialogflow, airports, avia, hotels
from telegram.ext.dispatcher import run_async
from emoji import emojize, demojize
from tools.enums import *
from tools import settings
from json import loads
import tools.tools
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

apiai = dialogflow.ApiAI(settings.get_apiai_token())

kbs = []
kbs += [[['Отель', 'Хостел', 'Апарт-отель'],
         ['не важно']]]
kbs = list(map(lambda x: ReplyKeyboardMarkup(x, one_time_keyboard=True), kbs))


def start(bot, update, user_data):
    user_data['status'] = USER_INACTIVE
    user_data['recent_src'] = set()
    user_data['recent_dst'] = set()
    msg_handle(bot, update, user_data)


@run_async
def msg_handle(bot, update, user_data, _d=None, _c=None):
    if _d and _c:
        text, params, cid = _d, {}, _c
    else:
        text, params, cid = demojize(update.message.text), {}, update.message.chat.id
    res = apiai.run(text, cid)
    fulfillment = dialogflow.get_fulfillment(res)
    if fulfillment.count(';-)') > 0:
        fulfillment, params = fulfillment.split(';-)')
        _params = list(map(lambda x: x.split('='), params.split(';')))[:-1]
        params = {}
        for n, v in _params:
            params[n] = v

    if not dialogflow.is_incomplete(res) and user_data != {}:
        action = dialogflow.get_action(res)
        params = dialogflow.get_params(res)
        if action == ACT_GETDATA:
            user_data['status'] = USER_ACTIVE
            try:
                user_data['phone'] = params['phone']
                user_data['email'] = params['email']
                user_data['city'] = params['city']
            except KeyError:
                pass
        if user_data['status'] == USER_ACTIVE:
            if action == ACT_S_ALL or (action == ACT_RETRY and 'recent_req' in user_data.keys()):
                if action == ACT_RETRY:
                    params = user_data['recent_req']
                    bot.send_message(cid, "Хорошо, попробуем еще раз")
                else:
                    bot.send_message(cid, fulfillment)
                src = airports.get_iata(params['from-city'])[0]
                dst = airports.get_iata(params['geo-city'])[0]
                start_date = tools.tools.parse_time(params['from'])
                end_date = tools.tools.parse_time(params['to'])
                hotel_type = int(params['hotel-type'])
                num_persons = int(params['numpersons'])
                near_to = params['nearto']

                user_data['recent_src'].add(params['from-city'])
                user_data['recent_dst'].add(params['geo-city'])
                user_data['recent_req'] = params

                ticket = avia.get_ticket(src, dst, start_date, end_date, num_persons, 0)
                if ticket:
                    bot.send_message(cid, "Итак, вот рейс, который вам подойдет")
                    bot.send_photo(cid, photo=ticket['img'],
                                   caption="Итого: %dРУБ" % ticket['price'])
                    bot.send_message(cid,
                                     "Чтобы забронировать, нажмите кнопку\nА пока мы подготовим отели.",
                                     reply_markup=tools.tools.gen_goto_booking_site(ticket['link']))

                    htls = hotels.get_hotel(near_to, start_date, end_date, num_persons, hotel_type)
                    if htls:
                        if len(htls) > 4:
                            bot.send_message(cid, "А вот и идеи для вашего проживания:")
                            fallbackurl = htls[-1]
                            htls = htls[:-1]
                            names = ['Первый', 'Второй', 'Третий']
                            i = 0
                            for htl in htls[:3]:
                                bot.send_photo(cid, photo=htl['img'], caption="{} вариант:\n".format(names[i]))
                                bot.send_message(cid, "{} {}\nСтоимость: {}РУБ/сут\nРейтинг: {} {}".format(
                                    tools.tools.decode_hotel_type(hotel_type),
                                    htl['name'],
                                    htl['cost'],
                                    htl['rank'],
                                    emojize('🌟' * htl['stars'])))
                                i += 1
                            bot.send_message(cid,
                                             "Какой отель наравится больше?\n"
                                             "Нажми на кнопку, чтобы забронировать!\n\n"
                                             "Удачного путешествия!",
                                             reply_markup=tools.tools.gen_hotels_selector(htls, fallbackurl))
                        else:
                            bot.send_message(cid, "Прости, но не удалось найти подходящих отелей\n"
                                                  "Я могу попытаться снова, просто скажи")
                    else:
                        bot.send_message(cid, "Прости, но у нас неполадки на сервере, найти отель не удалось\n"
                                              "Я могу попытаться снова, просто скажи")
                else:
                    bot.send_message(cid, "Прости, но у нас неполадки на сервере, найти билеты не удалось\n"
                                          "Я могу попытаться снова, просто скажи")
                return

    if 'k' in params.keys():
        bot.send_message(cid, fulfillment, reply_markup=kbs[int(params['k'])])
    elif 'b' in params.keys():
        bot.send_message(cid, fulfillment, reply_markup=tools.tools.gen_btns(int(params['b']), user_data))
    else:
        bot.send_message(cid, fulfillment)


@run_async
def cb_handle(bot, update, user_data):
    msg_handle(bot, update, user_data,
               update['callback_query']['data'],
               update['callback_query']['message']['chat']['id'])


def main():
    updater = Updater(settings.get_tg_token())
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, msg_handle, pass_user_data=True))
    dp.add_handler(CallbackQueryHandler(cb_handle, pass_user_data=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
