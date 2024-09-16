from bot.discordBot import DiscordBot
from agents.webInfo import WebInfoAgent
from agents.scraper import WebScraperAgent
from dotenv import load_dotenv

load_dotenv()

def main():
    bot = DiscordBot()
    bot.run()

if __name__ == '__main__':
    main()
