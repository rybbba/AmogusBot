import logging
from uuid import uuid4
import re

from telegram import (
    InlineQueryResultArticle,
    InlineQueryResultCachedAudio,
    InputTextMessageContent,
    Update,
)
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, CallbackContext
from telegram.error import Unauthorized

from google.oauth2 import service_account
from google.cloud import texttospeech

from audio_amogus import gen_amogus
from conf_reader import read_conf


def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""Для дальнейшего использования бота, в данной беседе стоит отключить уведомления и заархивировать её. """
        """Бот будет присылать сюда каждое сгенерированное для вас аудиосообщение. """,
    )


def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    if not re.match(r"^[\s\w]{,20}ус$", query):
        return

    query = query.lower()
    audio_title = query.replace("+", "")

    gen_amogus(
        query,
        context.bot_data["amogus_file"],
        context.bot_data["voice_file"],
        context.bot_data["output_file"],
        context.bot_data["google_client"],
    )
    with open(context.bot_data["output_file"], "rb") as audio_file:
        try:
            mess = context.bot.send_audio(
                update.effective_user.id, audio_file, title=audio_title
            )
        except Unauthorized:
            results = [
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Ошибка доступа",
                    input_message_content=InputTextMessageContent(
                        "http://t.me/amoguser_bot"
                    ),
                    description="Для работы с ботом, нужно написать /start ему в личные сообщения",
                )
            ]
            update.inline_query.answer(results, cache_time=0)
            return

    audio_id = mess["audio"]["file_id"]
    logging.info(
        f"Query {query} from {update.effective_user.username} was accepted and created audio with ID {audio_id}"
    )

    results = [InlineQueryResultCachedAudio(id=str(uuid4()), audio_file_id=audio_id)]

    update.inline_query.answer(results)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    parser = read_conf("settings.conf")

    telegram_token = parser["keys"]["telegram_token"]
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher

    
    google_client = texttospeech.TextToSpeechClient(
        credentials=service_account.Credentials.from_service_account_file(parser["keys"]["google_credientals"])
    )

    dispatcher.bot_data["google_client"] = google_client
    dispatcher.bot_data["amogus_file"] = parser["paths"]["amogus_file"]
    dispatcher.bot_data["voice_file"] = parser["paths"]["voice_file"]
    dispatcher.bot_data["output_file"] = parser["paths"]["output_file"]

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(InlineQueryHandler(inline_handler))

    updater.start_polling()
    updater.idle()
