from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from emoji import emojize, demojize
from api.airports import get_iata
from tools.enums import *
from tools import settings
from api import dialogflow
from json import loads
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

apiai = dialogflow.ApiAI(settings.get_apiai_token())

kbs = []
kbs += [[['5', '4-5', '3-5'],
         ['2-4', '2-3'],
         ['не важно']]]
kbs = list(map(lambda x: ReplyKeyboardMarkup(x, one_time_keyboard=True), kbs))


def start(bot, update, user_data):
    update.message.reply_text("Здесь будет более красивый текст....")
    print(user_data)
    if 'status' not in user_data.keys():
        user_data['status'] = USER_INACTIVE
        msg_handle(bot, update, user_data)


def msg_handle(bot, update, user_data):
    text, params = demojize(update.message.text), {}
    res = apiai.run(update.message.text, update.message.chat.id)
    if user_data != {} and not dialogflow.is_incomplete(res) and user_data['status'] == USER_ACTIVE:
        action = dialogflow.get_action(res)
        params = dialogflow.get_params(res)
        if action == ACT_GETDATA:
            user_data['status'] = USER_ACTIVE
            user_data['phone'] = params['phone']
            user_data['email'] = params['email']
            user_data['city'] = params['city']
        elif action == ACT_S_ALL:
            pass

    fulfillment = dialogflow.get_fulfillment(res)
    if fulfillment.count(';-)') > 0:
        fulfillment, params = fulfillment.split(";-)")
        _params = list(map(lambda x: x.split('='), params.split(';')))[:-1]
        params = {}
        for n, v in _params:
            params[n] = v

    if 'k' in params.keys():
        update.message.reply_text(fulfillment, reply_markup=kbs[int(params['k'])])
    else:
        update.message.reply_text(fulfillment)


def main():
    updater = Updater(settings.get_tg_token())
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, msg_handle, pass_user_data=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
