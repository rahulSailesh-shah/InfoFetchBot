from bot.discordBot import DiscordBot
from dotenv import load_dotenv
from agents.webInfo import WebInfoAgent


load_dotenv()

def main():
    bot = DiscordBot()
    bot.run()

if __name__ == '__main__':
    main()
