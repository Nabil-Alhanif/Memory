from discord.ext import commands
import wikipedia

class Wikipedia(commands.Cog, name='Wikipedia'):
    def __init__(self, bot):
        self.bot = bot

    def processQuery(self, *args):
        query = ""
        for arg in args:
            query += (" " + str(arg).strip())

        return query.strip()

    @commands.command(name="search", help="Search a query on wikipedia")
    async def search(self, ctx, *args):
        query = self.processQuery(args)

        await ctx.send(f"Hey {ctx.author.mention}, you're requesting a wikipedia search for {query}!")
        res = wikipedia.search(query)

        if (len(res) == 0):
            await ctx.send(f"Hey {ctx.author.mention}, It seems that I couldn't find anything related to {query} in wikipedia. Please try again with another keyword!")
        else:
            await ctx.send(res)

    @commands.command(name="summary", help="Get a wikipedia page summary")
    async def summary(self, ctx, *args):
        query = self.processQuery(args)

        await ctx.send(f"Hey {ctx.author.mention}, you're requesting a summary of a wikipedia article identified by {query}!")
        res = wikipedia.search(query)
        if (len(res) == 0):
            await ctx.send(f"Hey {ctx.author.mention}, It seems that I couldn't find anything related to {query} in wikipedia. Please try again with another keyword!")
        else:
            await ctx.send(res[0])
            page = wikipedia.page(title=res[0])
            await ctx.send(page.summary)
