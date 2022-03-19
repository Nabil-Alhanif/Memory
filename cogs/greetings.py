import discord
from discord.ext import commands

class Greetings(commands.Cog, name='Greetings'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hey")
    async def greet(self, ctx):
        await ctx.send(f'Hey {ctx.author.mention}')
