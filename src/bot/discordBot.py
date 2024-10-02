from typing import Final
import asyncio
import os, sys
from discord import Intents, Client, Message
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from agents.webInfo import WebInfoAgent
from agents.scraper import WebScraperAgent
from notion.api import create_notion_page
from datetime import datetime
from typing import Tuple

web_info_agent = WebInfoAgent.get_instance()
web_scraper_agent = WebScraperAgent.get_instance()

class CommandType:
    JOB = '/job'
    RESOURCE = '/resource'
    PROJECT = '/project'
    OTHER = '/other'

class Tag:
    JOB = "red"
    RESOURCE = "blue"
    PROJECT = "green"
    OTHER = "yellow"

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
            print('Message was empty because intents were not enabled probably')
            return

        is_private = user_message[0] == '?'
        user_message = user_message[1:] if is_private else user_message

        try:
            await message.channel.send("Processed")
        except Exception as e:
            print(e)

    async def on_ready(self):
        print(f'{self.client.user} is now running!')

    def get_command_type_and_tag(self, message: str) -> Tuple[str, str]:
      command_types = {
          CommandType.JOB: Tag.JOB,
          CommandType.RESOURCE: Tag.RESOURCE,
          CommandType.PROJECT: Tag.PROJECT,
          CommandType.OTHER: Tag.OTHER
      }
      for command, tag in command_types.items():
          if message.startswith(command):
              return command, tag
      return None, None

    def parse_message(self, message: str, command_type: str) -> Tuple[str, str]:
      content = message.replace(command_type, '').strip()
      parts = content.split(' - ', 1)
      if not parts:
          return None, None
      title = parts[0]
      url = parts[1] if len(parts) > 1 else None
      return title, url

    async def process_request(self, title: str, url: str) -> str:
      if url:
          result = web_scraper_agent.initiate_chat(url)
      else:
          result = web_info_agent.initiate_chat(title)
      return result.summary

    async def on_message(self, message: Message):
      if message.author == self.client.user:
          return

      user_message: str = message.content

      command_type, tag = self.get_command_type_and_tag(user_message)
      if not command_type:
          return

      title, url = self.parse_message(user_message, command_type)
      if not title:
          return

      summary = await self.process_request(title, url)
      # summary = "This is a summary"
      print(f"Summary: {summary}")
      if summary:
          create_notion_page(tag, title, datetime.now().strftime('%Y-%m-%d'), summary)

    def run(self):
        self.client.run(self.TOKEN)
