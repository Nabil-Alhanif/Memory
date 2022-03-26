import discord
from discord.ext import commands
from module.activate import keep_alive

class CustomBot(commands.Bot):
    async def on_ready(self):
        keep_alive()
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        reactivate = (message.content == '$reactivate')
        if reactivate:
            await message.channel.send('Reactivating...')
            keep_alive()
            await message.channel.send('Activated!')

            await message.channel.send('t+start 150000')
            return

        await self.process_commands(message)
