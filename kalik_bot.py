from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, CallbackQueryHandler, PicklePersistence
from telegram.ext.dispatcher import run_async
import pickle
import settings
import os.path


@run_async
def help(update, context):
    chat_id = update.message.chat.id
    context.bot.send_message(chat_id, text="""
        <b>Kalik Bot Commands:</b>

        /help - show this help
        /kalik - send Kalik-based message
        """, parse_mode='HTML')


def make_sentence():
    sentence = None
    while sentence is None:
        sentence = text_model.make_sentence()

    return sentence


@run_async
def sendKalik(update, context):
    keyboard = [[InlineKeyboardButton("I like it!😊", callback_data='like'),
                 InlineKeyboardButton("It's crap😒", callback_data='dislike')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        chat_id = update.message.chat.id
        kalik_message = make_sentence()
        print(kalik_message)
        msg = context.bot.send_message(chat_id,
                                       kalik_message,
                                       reply_markup=reply_markup,
                                       parse_mode='HTML'
                                       )
    except Exception as e:
        print(e)


def vote(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    msg_id = query.message.message_id
    user_id = query.from_user.id

    messages = feedback.get(chat_id, {})
    values = messages.get(msg_id, {})
    if query.data == 'like':
        values[user_id] = 1
    else:
        values[user_id] = -1
    messages[msg_id] = values
    values['text'] = query.message.text
    feedback[chat_id] = messages
    query.answer()
    print(feedback)


def stop(signum, frame):
    with open('feedback', 'wb') as f:
        pickle.dump(feedback, f)


def read_feedback():
    global feedback
    if os.path.exists('feedback'):
        with open('feedback', 'rb') as f:
            feedback = pickle.load(f)
    else:
        feedback = {}


def read_model():
    global text_model
    with open('model.data', 'rb') as f:
        text_model = pickle.load(f)


def main():
    read_feedback()
    read_model()

    updater = Updater(settings.AUTH_TOKEN, user_sig_handler=stop, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('start', help))
    updater.dispatcher.add_handler(CommandHandler('kalik', sendKalik))
    updater.dispatcher.add_handler(CallbackQueryHandler(vote))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
