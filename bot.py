# bot.py
import asyncio
import logging
import os
import random
import re
import sys

import aiohttp
import aiosqlite
import aiozaneapi
import async_cleverbot as ac
import asyncpg
import discord
from asyncdagpi import Client
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext.commands.errors import CheckFailure
from discord.ext.commands.help import MinimalHelpCommand
from dotenv import load_dotenv
from fuzzywuzzy import process

from jishaku.paginators import PaginatorInterface, WrappedPaginator

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

dagpi = Client(os.getenv("DAGPI_TOKEN"))
cleverbot = ac.Cleverbot(os.getenv("CHATBOT_TOKEN"))


client = aiozaneapi.Client(os.getenv("ZANE_TOKEN"))


async def get_prefix(bot, message):
    if message.guild is None:
        return "kb+"
    if message.guild.id in bot.prefixes.keys():
        return commands.when_mentioned_or(*bot.prefixes[message.guild.id])(bot, message)
    prefixes = await bot.pg.fetchval(
        "select prefixes from prefixes where guild_id = $1", message.guild.id
    )
    bot.prefixes[message.guild.id] = prefixes
    return commands.when_mentioned_or(*prefixes)(bot, message)


class Context(commands.Context):
    def embed(self, **kwargs):
        color = kwargs.pop("color", self.bot.embed_color)
        embed = discord.Embed(**kwargs, color=color)
        embed.timestamp = self.message.created_at
        embed.set_footer(
            text=f"Requested by {self.author}", icon_url=self.author.avatar_url
        )
        return embed

    async def remove(self, *args, **kwargs):
        m = await self.send(*args, **kwargs)
        await m.add_reaction("❌")
        try:
            await self.bot.wait_for(
                "reaction_add",
                timeout=120,
                check=lambda r, u: u.id == self.author.id
                and r.message.id == m.id
                and str(r.emoji) == str("❌"),
            )
            await m.delete()
        except asyncio.TimeoutError:
            pass

    @property
    def clean_prefix(self):
        """:class:`str`: The cleaned up invoke prefix. i.e. mentions are ``@name`` instead of ``<@id>``."""
        user = self.guild.me if self.guild else self.bot.user
        # this breaks if the prefix mention is not the bot itself but I
        # consider this to be an *incredibly* strange use case. I'd rather go
        # for this common use case rather than waste performance for the
        # odd one.
        pattern = re.compile(r"<@!?%s>" % user.id)
        return pattern.sub("@%s" % user.display_name.replace("\\", r"\\"), self.prefix)


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or Context)


intents = discord.Intents.all()
bot = Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    intents=intents,
    owner_ids={835302686983192586, 693987130036453398},
    help_command=commands.MinimalHelpCommand(),
    activity=discord.Game(name="Listening for kb+help"),
)
password = os.getenv("POSTGRES_PASS")
pg = bot.loop.run_until_complete(
    asyncpg.create_pool(f"postgresql://postgres:{password}@localhost:5432/komodobot")
)
bot.pg = pg
bot.session = aiohttp.ClientSession(
    headers={
        "User-Agent": f"python-requests/2.25.1 Sir KomodoBot/1.1.0 Python/"
        f"{sys.version_info[0]}."
        f"{sys.version_info[1]}."
        f"{sys.version_info[2]} aiohttp/{aiohttp.__version__}"
    }
)
bot.embed_color = 0x36393E
bot.afk = {}
bot.prefixes = {}
bot.blacklists = {}


message_cooldown = commands.CooldownMapping.from_cooldown(
    1.0, 3.0, commands.BucketType.user
)


async def create_cache():
    await bot.wait_until_ready()
    prefixes = await bot.pg.fetch("SELECT * FROM PREFIXES")
    for prefix in prefixes:
        bot.prefixes[prefix["guild_id"]] = prefix["prefixes"]
    blacklists = await bot.pg.fetch("SELECT * FROM blacklist")
    bot.blacklists = dict(blacklists)
    return


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


os.environ["JISHAKU_NO_UNDERSCORE"] = True.__str__()

os.environ["JISHAKU_NO_DM_TRACEBACK"] = True.__str__()
os.environ["JISHAKU_HIDE"] = True.__str__()

"""
@bot.command()
@commands.is_owner()
async def servers(ctx):
    activeservers = bot.guilds
    for guild in activeservers:
        await ctx.send(f'{guild.name}: {guild.id}')
"""


@bot.event
async def on_guild_join(guild):
    await bot.pg.execute("INSERT INTO prefixes VALUES($1, $2)", guild.id, ["kb+"])


@bot.event
async def on_guild_remove(guild):
    await bot.pg.execute("DELETE FROM prefixes where guild_id = $1", guild.id)


"""
@bot.command(description='Kicks a member, Admin Only')
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has kicked.')




@bot.command()
async def purge(ctx, number, member: discord.Member = None):
    def mycheck(message):
        return message.author.id == member.id

    if member is None:
        await ctx.channel.purge(limit=int(number))
    else:
        await ctx.channel.purge(limit=int(number), check=mycheck)


@bot.check
async def blacklist(ctx):
    if ctx.author.id in bot.blacklists.keys():
        raise commands.CheckFailure()
    return True
"""


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(
            f"{error.param.name} is a required argument that is missing!"
        )
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(
            f"{ctx.author.mention},"
            f" try running the command again after"
            f" {round(error.retry_after)} seconds"
        )
    if isinstance(error, commands.CommandNotFound):
        return

    raise error


@bot.listen("on_message_edit")
async def on_message_edit(old, new):
    if old.embeds != []:
        return
    if new.embeds != []:
        return
    await bot.process_commands(new)


"""
@bot.command()
async def xkcd(ctx):
    comic_num = random.randint(1, 2415)
    async with aiohttp.ClientSession() as cs:
        async with cs.get(f'https://xkcd.com/{comic_num}/info.0.json') as r:
            res = await r.json()
    embed = discord.Embed(
        title=f"**{comic_num}: {res['title']}**",
        colour=discord.Colour(0xFFFFFF),
        url=f'https://xkcd.com/{comic_num}/',
        description=res['alt'],
    )
    embed.set_image(url=res['img'])
    embed.set_author(
        name='XKCD',
        url='https://xkcd.com',
        icon_url='https://cdn.changelog.com/uploads/'
        'icons/news_sources/P2m/icon_small.png?v=63722746912',
    )
    embed.set_footer(
        text=f'Comic Released on:'
        f" {res['month']}/{res['day']}/{res['year']}"
        ' (view more comics at https://xkcd.com)'
    )
    await ctx.send(embed=embed)


@bot.command()
async def gif(ctx, *, img, num=1):
    img = img.replace(' ', '+')
    async with aiohttp.ClientSession() as cs:
        link = 'http://api.giphy.com/v1/gifs/search?q='
        f'{img}&api_key=0wltGsImBHY0GZGudUZG8aa6xybPJDit&limit={img}'
        async with cs.get(link) as r:
            res = await r.json()
            img = res['data'][num - 1]['url']
            await ctx.send(
                f'{img}\n'
                'https://user-images.githubusercontent.com/74436682/108'
                '932641-8e088c80-75fe-11eb-9d69-da16519a41a8.png'
            )


@bot.command()
@commands.is_owner()
async def leave(ctx):
    await ctx.guild.leave()


@bot.command()
async def cb(ctx, emotion='neutral'):
    emotions = {'neutral': ac.Emotion.neutral}
    await ctx.reply('Your chatbot session has started. Type `stop` to end it.')
    while True:

        def check(message):
            return (
                message.author == ctx.author and message.channel == ctx.channel
            )

        text = await bot.wait_for('message', check=check)
        if not (3 <= len(text.content) <= 60):
            await ctx.send(
                'Text must be longer than 3 chars and shorter than 60.'
            )
        else:
            async with ctx.channel.typing():
                response = await cleverbot.ask(
                    text.content, emotion=emotions[f'{emotion}']
                )
                await text.reply(response)
                if text.content == 'stop':
                    await text.reply('Your chatbot session has ended')
                    break


@bot.command()
async def snipe(ctx):
    await ctx.send(
        'Snipe Bad, I wont do it. People delet messages for reson,'
        ' why u tryna peek at them? <:angery:747680299311300639>'
    )


@bot.command()
async def getpic(ctx, url: str):
    try:
        link = url.strip('<>')
        await ctx.send(f'https://image.thum.io/get/{link}')
    except Exception:
        await ctx.send("Couldn't screenshot due to error")


@bot.command()
async def redirectcheck(ctx, website):
    website = website.strip('<>')
    async with aiohttp.ClientSession(
        headers={'User-Agent': 'python-requests/2.20.0'}
    ).get(website) as resp:
        soup = BeautifulSoup(await resp.text(), features='lxml')
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical is None:
            return await ctx.send(f'`{resp.real_url}`')
        await ctx.send(f"`{canonical['href']}`")


@bot.command(aliases=['src'])
async def source(ctx):
    embed = discord.Embed(title="Sir KomodoBot's Source")
    embed.description = 'Here is my repo link:'
    ' https://github.com/MrKomodoDragon/sir-komodobot\n'
    "\nDon't forget to leave a star!"
    '\n(Also, '
    '[please respect the license!]'
    '(https://github.com/MrKomodoDragon/sir-komodobot/blob/main/LICENSE))'
    await ctx.send(embed=embed)
"""


extensions = [
    #'Fun',
    #'Utility',
    #'Images',
    "jishaku",
    #'Music',
    #'Economy',
    #'Owner',
    #'Prefix',
    #'blocktest'
]

bot.loop.create_task(create_cache())
for extension in extensions:
    bot.load_extension(f"Cogs.{extension}")


bot.run(TOKEN)
