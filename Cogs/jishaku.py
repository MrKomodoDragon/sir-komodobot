from discord.ext import commands

from jishaku.cog import OPTIONAL_FEATURES, STANDARD_FEATURES


class jishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
    pass


def setup(bot: commands.Bot):
    bot.add_cog(jishaku(bot=bot))
