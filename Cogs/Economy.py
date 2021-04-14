import discord
from discord.ext import commands
import asyncpg
import random

from discord.ext.commands.cooldowns import BucketType


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def register(self, ctx):
        """Register with the database"""
        try:
            value = await self.bot.pg.fetchrow(
                'SELECT * from economy where member_id = $1', ctx.author.id
            )
            if value is None:
                await self.bot.pg.execute(
                    'INSERT INTO economy VALUES($1, 500, 0)', ctx.author.id
                )
                await ctx.send(
                    embed=discord.Embed(
                        title='Success!',
                        description=f'You have successfully registered. You currently have $500 in your wallet. Try running some commands in `{ctx.prefix}help economy to get some more money!',
                    )
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        description='You have already registered!'
                    )
                )
        except:
            await ctx.send(embed=discord.Embed(description='An error occured'))

    @commands.command()
    @commands.cooldown(2, 7200, BucketType.user)
    async def work(self, ctx):
        """Work to get some money"""
        salary = random.randint(100, 500)
        await self.bot.pg.execute(
            'UPDATE economy set wallet = wallet+$1 where member_id = $2',
            salary,
            ctx.author.id,
        )
        await ctx.send(
            embed=discord.Embed(
                description=f'You work and get paid ${salary}.'
            )
        )


def setup(bot):
    bot.add_cog(Economy(bot))
