# -*- coding: utf-8 -*-
import asyncio
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import C2CMessage, GroupMessage, Message
from openai import OpenAI

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()


class MyClient(botpy.Client):
    client = OpenAI(api_key=test_config["outer_ai"]["token"], base_url=test_config["outer_ai"]["url"])

    class send_message:
        def __init__(self, message):
            self.message = message

        async def send_c2c(self, content):
            await self.message._api.post_c2c_message(
                openid=self.message.author.user_openid, msg_type=0, msg_id=self.message.id,
                content=f"{content}",
                # markdown={"content": f"{self.ai_chat(message.content)}"}
            )

        async def send_group(self, content):
            await self.message._api.post_group_message(
                group_openid=self.message.group_openid, msg_type=0, msg_id=self.message.id,
                content=f"{content}",
                # markdown={"content": f"{self.ai_chat(message.content)}"}
            )

    def ai_chat(self, text):
        print('发送Ai请求', text)
        response = self.client.chat.completions.create(
            model=test_config["outer_ai"]["model"],
            messages=[
                {"role": "user",
                 "content": text}
            ],
            temperature=0.6,
            max_tokens=1024,
            stream=False,

        )
        content = response.choices[0].message.content
        content = content.split('</think>')[-1]
        content = content.strip()
        print('AI 回应:', content)
        return content

    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_c2c_message_create(self, message: C2CMessage):
        sd = self.send_message(message)
        await sd.send_c2c('AI思考中...')
        try:
            await sd.send_c2c(self.ai_chat(message.content))
        except Exception as e:
            await sd.send_c2c(f"哎呀，思考出错了")

    async def on_group_at_message_create(self, message: GroupMessage):
        sd = self.send_message(message)
        # await sd.send_group('AI思考中...')
        try:
            await sd.send_group(self.ai_chat(message.content))
        except Exception as e:
            await sd.send_group(f"哎呀，思考出错了")


if __name__ == "__main__":
    intents = botpy.Intents(public_messages=True)
    # intents.all()
    client = MyClient(intents=intents, is_sandbox=True)
    client.run(appid=test_config["qqbot"]["appid"], secret=test_config["qqbot"]["secret"])
