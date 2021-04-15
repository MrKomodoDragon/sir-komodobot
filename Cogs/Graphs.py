import discord
from discord.ext import commands
import io
import matplotlib.pyplot as plt


class Graphs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def pie_func(self, ctx, numbers):
        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('equal')
        ax.pie(numbers, autopct='%1.2f%%')
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, 'thing.png'))

    @commands.command()
    async def pie(self, ctx, numbers: commands.Greedy[int]):
        await self.pie_func(ctx, numbers)


def setup(bot):
    bot.add_cog(Graphs(bot))
