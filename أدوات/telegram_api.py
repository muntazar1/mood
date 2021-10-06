import os
import sys
import json

from telegram import Bot
from telegram import ParseMode


class TelegramApi:
    channel_id: str = "@psh_team_decode_python_files"
    # channel_id: str = "@test_psh_bots"

    def __init__(self, hash_type):
        self.hash_type = hash_type
        try:
            message = input("Enter infos about the tool..\n: ")
        except UnicodeDecodeError:
            print("encode error... try in English...")
            try:
                message = input("Enter infos about the tool..\n: ")
            except UnicodeDecodeError:
                message = ""

        if not message.strip():
            message = "لم يتم فحصها!"
        self.send(message)

    def send(self, text: str):
        bot = Bot(os.environ.get("BOT_TOKEN"))
        bot.send_document(
            self.channel_id,
            open(sys.argv[2], "r"),
            caption=self.message_body.format(hash_type=json.dumps(self.hash_type, indent=2), text=f"{text}"),
            parse_mode=ParseMode.HTML

        )

    @property
    def message_body(self) -> str:
        docs_path = os.environ["VIRTUAL_ENV"] + "/share/decode-bot-messages/"
        with open(docs_path + "message-body.txt", "r") as file:
            data = file.read()
        return data