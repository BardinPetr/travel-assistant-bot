from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from tools.enums import *
from tools import settings
from api import dialogflow
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

apiai = dialogflow.ApiAI(settings.get_apiai_token())


def start(bot, update, user_data):
    update.message.reply_text("Здесь будет более красивый текст....")
    user_data['status'] = USER_INACTIVE
    msg_handle(bot, update, user_data)


def msg_handle(bot, update, user_data):
    res = apiai.run(update.message.text, update.message.chat.id)
    if not dialogflow.is_incomplete(res) and user_data['status'] == USER_ACTIVE:
        action = dialogflow.get_action(res)
        params = dialogflow.get_params(res)
        if action == ACT_GETDATA:
            user_data['status'] = USER_ACTIVE
            user_data['phone'] = params['phone']
            user_data['email'] = params['email']
            user_data['city'] = params['city']

    update.message.reply_text(dialogflow.get_fulfillment(res))


def main():
    updater = Updater(settings.get_tg_token())
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, msg_handle, pass_user_data=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
