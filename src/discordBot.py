from typing import Final
import os
from discord import Intents, Client, Message
from random import choice, randint


class DiscordBot:
    def __init__(self):
        self.TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
        intents: Intents = Intents.default()
        intents.message_content = True
        self.client: Client = Client(intents=intents)

        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    async def send_message(self, message: Message, user_message: str) -> None:
        if not user_message:
            print('(Message was empty because intents were not enabled probably)')
            return

        is_private = user_message[0] == '?'
        user_message = user_message[1:] if is_private else user_message

        try:
            answer = "Hello, I'm a bot!"
            print("Answer:", answer)
            await message.channel.send(answer)
        except Exception as e:
            print(e)

    async def on_ready(self):
        print(f'{self.client.user} is now running!')

    async def on_message(self, message: Message):
        if message.author == self.client.user:
            return

        username: str = str(message.author)
        user_message: str = message.content
        channel: str = str(message.channel)

        print(f'[{channel}] {username}: "{user_message}"')
        await self.send_message(message, user_message)

    def run(self):
        self.client.run(self.TOKEN)
