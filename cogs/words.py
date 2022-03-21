import random

import discord
from discord.ext import commands

class Words(commands.Cog, name='Words'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sortWord", help="Sort each of the given word alphabetically")
    async def sortWord(self, ctx, *args):
        ret = ''
        for arg in args:
            arg = ''.join(sorted(str(arg)))
            ret = ret + arg + '\n'
            
        await ctx.send(ret)

    @commands.command(name="anagram", help="Produce an anagram of the given word(s)")
    async def anagram(self, ctx, *args):
        if (len(args) == 0):
            await ctx.send(f'Hey {ctx.author.mention}, please give an input first!')
            
        ret = ''
        for arg in args:
            res = []
            arg = str(arg)
            
            for i in range(len(arg)):
                res.insert(random.randint(0, i), arg[i])
                
            arg = ''
            for i in res:
                arg += i
                
            ret = ret + arg + '\n'

        await ctx.send(ret)
