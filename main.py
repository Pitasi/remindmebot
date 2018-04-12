#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import environ
from telegram.ext import Updater, CommandHandler
import logging
import pickle
from threading import Event
from time import time
from datetime import timedelta
from src.remind_command import remind
from fixtures.replies import HELP_TEXT


# Get config from env. variables
TOKEN = environ.get('TOKEN')
WEBHOOK_URL = environ.get('WEBHOOK_URL')
JOBS_PICKLE = environ.get('STORAGE_PATH', 'storage/jobs.pickle')


def load_jobs(jq):
    now = time()

    count = 0
    with open(JOBS_PICKLE, 'rb') as fp:
        while True:
            try:
                next_t, job = pickle.load(fp)
            except EOFError:
                break  # Loaded all job tuples

            # Create threading primitives
            enabled = job._enabled
            removed = job._remove

            job._enabled = Event()
            job._remove = Event()

            if enabled:
                job._enabled.set()

            if removed:
                job._remove.set()

            next_t -= now  # Convert from absolute to relative time

            job._queue = jq
            jq._put(job, next_t)
            count += 1
    logger.info("[pickle] Loaded {} jobs".format(count))


def save_jobs(jq):
    if jq is None:
        return

    logger.info("[pickle] Saving jobs to file...")
    job_tuples = jq._queue.queue

    count = 0
    with open(JOBS_PICKLE, 'wb') as fp:
        for next_t, job in job_tuples:
            # Back up objects
            _job_queue = job._job_queue
            _remove = job._remove
            _enabled = job._enabled

            # Replace un-pickleable threading primitives
            job._job_queue = None  # Will be reset in jq.put
            job._remove = job.removed  # Convert to boolean
            job._enabled = job.enabled  # Convert to boolean

            # Pickle the job
            pickle.dump((next_t, job), fp)
            count += 1

            # Restore objects
            job._job_queue = _job_queue
            job._remove = _remove
            job._enabled = _enabled
    logger.info("[pickle] Saved {} jobs".format(count))


def save_jobs_job(bot, job):
    save_jobs(job.job_queue)


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

    job_queue = updater.job_queue

    try:
        load_jobs(job_queue)
    except FileNotFoundError:
        # First run
        # Periodically save jobs
        job_queue.run_repeating(save_jobs_job, timedelta(minutes=1))
        pass

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

    # After shutting down
    save_jobs(job_queue)


if __name__ == '__main__':
    main()
