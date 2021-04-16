import discord
from discord.ext import commands
import io
import matplotlib
import numpy as np

matplotlib.use('Agg')
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

    @commands.command()
    async def bar(self, ctx, numbers: commands.Greedy[int]):
        fig = plt.figure()
        plt.bar(numbers, numbers)
        plt.grid(True)
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, 'thing.png'))

    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.command()
    async def line(self, ctx, numbers: commands.Greedy[float]):
        fig = plt.figure()
        plt.plot(numbers, marker='o')
        buf = io.BytesIO()
        plt.grid(True)
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, 'thing.png'))

    @commands.command()
    async def linear(self, ctx, m: float, b: float):
        fig = plt.figure()
        x = np.linspace(-100, 100, 50000)
        plt.ylim([-50, 50])
        y = m * x + b
        plt.plot(x, y)
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, 'thing.png'))

    @commands.command()
    async def quadratic(self, ctx, a: float=1.0, b: float=1.0, c: float=1.0):
        fig = plt.figure()
        x = np.linspace(-100, 100, 50000)
        plt.ylim([-50, 50])
        y = (x**2)*a+(b*x)+c
        plt.plot(x, y)
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, 'thing.png'))
        plt.clf()

    @commands.command()
    async def quadratic(self, ctx, a: float = 1.0, b: float = 1.0, c: float = 1.0):
        fig = plt.figure()
        x = np.linspace(-100, 100, 50000)
        plt.ylim([-50, 50])
        y = (x**2)*a+(b*x)+c
        plt.plot(x, y)
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, 'thing.png'))
        plt.clf()

    @commands.command()
    async def exponential(self, ctx, a: float = 1.0, b: float = 1.0, c: float = 1.0):
        fig = plt.figure()
        x = np.linspace(-100, 100, 50000)
        y = (a*b)**x + c
        plt.plot(x, y)
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, 'thing.png'))
        plt.clf()


def setup(bot):
    bot.add_cog(Graphs(bot))
