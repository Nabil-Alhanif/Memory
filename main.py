import discord
import os
from bot import CustomBot

from cogs.greetings import Greetings
from cogs.scraper import Scraper
from cogs.wikipedia import Wikipedia
from cogs.words import Words
from cogs.commandErrHandler import CommandErrHandler

from module.activate import keep_alive

def main():
    keep_alive()

    TOKEN = os.environ['TOKEN']

    intents = discord.Intents.default()
    intents.members = True

    bot = CustomBot(
        command_prefix='$',
        intents=intents,
        case_insensitive=True
    )

    bot.add_cog(Greetings(bot))
    bot.add_cog(Scraper(bot))
    bot.add_cog(Wikipedia(bot))
    bot.add_cog(Words(bot))
    bot.add_cog(CommandErrHandler(bot))

    bot.run(TOKEN)

if __name__ == "__main__":
    main()
