#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import environ
from telegram.ext import Updater, CommandHandler
import logging
from src.remind_command import remind
from fixtures.replies import HELP_TEXT

# Get config from env. variables
TOKEN = environ.get('TOKEN')
WEBHOOK_URL = environ.get('WEBHOOK_URL')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Basic handlers
def start(bot, update):
    update.message.reply_text(HELP_TEXT, parse_mode='HTML', reply_to_message_id=update.message.message_id)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


# Wrapping all up
def main():
    # Set up
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("r", remind, pass_job_queue=True))
    dp.add_handler(CommandHandler("remind", remind, pass_job_queue=True))

    dp.add_error_handler(error)

    # Start
    if WEBHOOK_URL is not None:
        logger.info("Running in webhook mode")
        updater.start_webhook(listen="0.0.0.0", port=443, url_path=TOKEN)
        updater.bot.set_webhook(WEBHOOK_URL + '/' + TOKEN)
    else:
        logger.info("Running in long-polling mode")
        updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
