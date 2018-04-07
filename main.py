from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
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
    update.message.reply_text('Здесь будет более красивый текст....')
    print(user_data)
    if 'status' not in user_data.keys():
        user_data['status'] = USER_INACTIVE
        msg_handle(bot, update, user_data)


@run_async
def msg_handle(bot, update, user_data):
    text, params, cid = demojize(update.message.text), {}, update.message.chat.id

    res = apiai.run(update.message.text, update.message.chat.id)
    fulfillment = dialogflow.get_fulfillment(res)
    if fulfillment.count(';-)') > 0:
        fulfillment, params = fulfillment.split(';-)')
        _params = list(map(lambda x: x.split('='), params.split(';')))[:-1]
        params = {}
        for n, v in _params:
            params[n] = v

    if not dialogflow.is_incomplete(res):  # and user_data != {} and user_data['status'] == USER_ACTIVE:
        action = dialogflow.get_action(res)
        params = dialogflow.get_params(res)
        if action == ACT_GETDATA:
            user_data['status'] = USER_ACTIVE
            user_data['phone'] = params['phone']
            user_data['email'] = params['email']
            user_data['city'] = params['city']
        elif action == ACT_S_ALL:
            update.message.reply_text(fulfillment)
            src = airports.get_iata(params['from-city'])[0]
            dst = airports.get_iata(params['geo-city'])[0]
            start_date = tools.tools.parse_time(params['from'])
            end_date = tools.tools.parse_time(params['to'])
            hotel_type = int(params['hotel-type'])
            num_persons = params['numpersons']
            near_to = params['nearto']

            ticket = avia.get_ticket(src, dst, start_date, end_date, num_persons, 0)
            if ticket:
                update.message.reply_text("Итак, вот рейс, который вам подойдет")
                bot.send_photo(cid, photo=ticket['img'],
                               caption="Итого: %dРУБ" % ticket['price'])
                update.message.reply_text("Чтобы забронировать, перейдите по ссылке: {}".format(ticket['link']))
                return

    if 'k' in params.keys():
        update.message.reply_text(fulfillment, reply_markup=kbs[int(params['k'])])
    else:
        update.message.reply_text(fulfillment)


def main():
    updater = Updater(settings.get_tg_token())
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, msg_handle, pass_user_data=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
