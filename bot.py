import os
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters
from boto3 import session as ses
from botocore.client import Config

DOCUMENT, MIDDLE, FINAL = range(3)


def start(bot, updater):
    updater.message.reply_text('Hello, send me file to upload (document only)')
    return DOCUMENT


def upload_document(bot, updater):
    session = ses.Session()
    client = session.client('s3',
                            region_name='fra1',
                            endpoint_url='https://summerbot.fra1.digitaloceanspaces.com',
                            aws_access_key_id=os.environ['DO_PUBLIC'],
                            aws_session_token=os.environ['DO_SECRET'])
    updater.message.reply_text(
        f'your link for download:\n it might be working \n {updater.message.document.get_file().file_path}')
    client.upload_file(updater.message.document.get_file().file_path, "summerbot", updater.message.document.file_name)
    updater.message.reply_text(
        f'your link for download:\n it might be working \n {updater.message.document.get_file().file_path}')
    return MIDDLE


def say_howdy(bot, updater):
    updater.message.reply_text('I am in MIDDLE state')
    return FINAL


def say_good_bye(bot, updater):
    updater.message.reply_text('I am in FINAL state, goodbye')


def cancel(bot, updater):
    updater.message.reply_text('Good bye')
    return ConversationHandler.END


def help(bot, updater):
    updater.message.reply_text('Bot started')


def main():
    TOKEN = os.environ['TELEGRAM_TOKEN']
    PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher
    command = CommandHandler('help', help)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states= {DOCUMENT: [MessageHandler(Filters.document, upload_document), CommandHandler('init', start)],
                 MIDDLE: [MessageHandler(Filters.text, say_howdy)],
                 FINAL: [MessageHandler(Filters.text, say_good_bye)]},
        fallbacks= [CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(command)

    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook("https://summerpractise.herokuapp.com/" + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()