from telegram import TelegramError, error
from src.dates import parse_date, now
import fixtures.replies as replies


def callback_timer(bot, job):
    user_name = job.context["user_name"]
    user_id = job.context["user_id"]
    chat_id = job.context["chat_id"]
    success_msg_id = job.context["success_msg_id"]
    reply_to_message_id = job.context["reply_to_message_id"]

    try:
        bot.delete_message(chat_id=chat_id, message_id=success_msg_id)
    except TelegramError:
        pass

    user_tag = replies.TAG_URL.format(id=user_id, name=user_name)
    try:
        bot.send_message(
            chat_id=chat_id,
            text=replies.ALERT_TEXT.format(user_tag),
            reply_to_message_id=reply_to_message_id,
            parse_mode="HTML"
        )
    except error.BadRequest:
        bot.send_message(
            chat_id=chat_id,
            text=replies.ALERT_TEXT.format(user_tag),
            parse_mode="HTML"
        )


def remind(bot, update, job_queue):
    try:
        cmd, raw_date = update.message.text.split(maxsplit=1)
    except ValueError:
        update.message.reply_text(replies.USAGE_TEXT, parse_mode="HTML")
        return

    date = parse_date(raw_date)
    if date is None or date < now():
        update.message.reply_text(replies.USAGE_TEXT, parse_mode="HTML")
        return

    # Send a success message
    success_msg = update.message.reply_text(
        replies.SUCCESS_TEXT.format(year=date.year, month=date.month, day=date.day, hour=date.hour, minute=date.minute),
        reply_to_message_id=update.message.message_id,
        disable_web_page_preview=True,
        parse_mode="HTML"
    )

    # Schedule alert
    delta_seconds = (date - now()).total_seconds()
    context = dict(
        user_name=update.message.from_user.first_name,
        user_id=update.message.from_user.id,
        chat_id=update.message.chat_id,
        success_msg_id=success_msg.message_id,
        reply_to_message_id=update.message.reply_to_message.message_id if update.message.reply_to_message is not None else update.message.message_id
    )
    job_queue.run_once(callback_timer, delta_seconds, context=context)

