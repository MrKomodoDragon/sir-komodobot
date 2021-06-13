import io

import discord
import matplotlib
import numpy as np
from discord.ext import commands
from Equation import Expression

# Yes i know this is blocking, i'll do it later, but for nwo this isn't loaded so it shouldn't be a problem
matplotlib.use("Agg")
import re

import matplotlib.pyplot as plt


class Graphs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check(self, v):
        v = list(v.group())
        v.insert(-1, "*")
        return "".join(v)

    async def pie_func(self, ctx, numbers):
        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("equal")
        ax.pie(numbers, autopct="%1.2f%%")
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, "thing.png"))

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
        await ctx.send(file=discord.File(buf, "thing.png"))

    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.command()
    async def line(self, ctx, numbers: commands.Greedy[float]):
        fig = plt.figure()
        plt.plot(numbers, marker="o")
        buf = io.BytesIO()
        plt.grid(True)
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, "thing.png"))

    @commands.command()
    async def linear(self, ctx, m: float, b: float):
        fig = plt.figure()
        x = np.linspace(-100, 100, 50000)
        plt.ylim([-50, 50])
        y = m * x + b
        plt.plot(x, y)
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, "thing.png"))

    @commands.command()
    async def quadratic(self, ctx, a: float = 1.0, b: float = 1.0, c: float = 1.0):
        fig = plt.figure()
        x = np.linspace(-100, 100, 50000)
        plt.ylim([-50, 50])
        y = (x ** 2) * a + (b * x) + c
        plt.plot(x, y)
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, "thing.png"))
        plt.clf()

    @commands.command()
    async def exponential(self, ctx, a: float = 1.0, b: float = 1.0, c: float = 1.0):
        fig = plt.figure()
        x = np.linspace(-100, 100, 50000)
        y = (a * b) ** x + c
        plt.plot(x, y)
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, "thing.png"))
        plt.clf()

    @commands.command()
    async def graph(self, ctx, *, equation: str):
        fig = plt.figure()
        equation = equation.replace("y=", "")
        equation = equation.replace("y= ", "")
        equation = equation.replace("y =", "")
        equation = equation.replace("y = ", "")
        equation = str(re.sub(r"([0-9\.] ?x)", self.check, equation))
        equation = str(re.sub(r"([0-9\.] ?\()", self.check, equation))
        equation = equation.replace(")(", ")*(")
        expr = Expression(equation, ["x"])
        x = np.linspace(-100, 100, 50000)
        plt.ylim([-50, 50])
        y = []
        for i in x:
            y.append(expr(i))
        plt.plot(x, y)
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        await ctx.send(file=discord.File(buf, "thing.png"))
        plt.clf()


def setup(bot):
    bot.add_cog(Graphs(bot))
