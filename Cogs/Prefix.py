import discord
from discord.ext import commands


class Prefixes(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        await ctx.send(', '.join(await self.bot.get_prefix(ctx.message)))

    @prefix.command(name='add')
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix_add(self, ctx, prefix: str):
        if prefix in self.bot.prefixes[ctx.guild.id]:
            ("<:bonk:759934836193361991> That's already a prefix")
        cache_prefix = self.bot.prefixes[ctx.guild.id]
        cache_prefix.append(prefix)
        prefixes = await self.bot.pg.fetchval(
            'select prefixes from prefixes where guild_id = $1', ctx.guild.id
        )
        prefixes.append(prefix)
        await self.bot.pg.execute(
            'UPDATE prefixes SET prefixes = prefixes || $1 where guild_id = $2',
            prefixes,
            ctx.guild.id,
        )
        await ctx.send('Updated the prefixes for this server')


def setup(bot):
    bot.add_cog(Prefixes(bot))
