import asyncio
import datetime
import io
import pathlib
import random
import string
import time
import unicodedata
from collections import Counter

import bs4
import dateparser.search
import discord
import googletrans
import humanize
import mystbin
import psutil
from bs4 import BeautifulSoup
from discord.ext import commands, menus
from PIL import Image

from jishaku.functools import executor_function

"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        _page_types = {
            "latest": "https://discordpy.readthedocs.io/en/latest",
            "python": "https://docs.python.org/3",
            "asyncpg": "https://magicstack.github.io/asyncpg/current/",
            "zaneapi": "https://docs.zaneapi.com/en/latest/",
            "aiohttp": "https://daggy1234.github.io/polaroid/api/image.html",
        }
        self.rtfm_lock = asyncio.Lock
        self.afk = {}
        self.bot.codes = {
            1: "HEARTBEAT",
            2: "IDENTIFY",
            3: "PRESENCE",
            4: "VOICE_STATE",
            5: "VOICE_PING",
            6: "RESUME",
            7: "RECONNECT",
            8: "REQUEST_MEMBERS",
            9: "INVALIDATE_SESSION",
            10: "HELLO",
            11: "HEARTBEAT_ACK",
            12: "GUILD_SYNC",
        }

        self.bot.socket_stats = Counter()
        self.bot.socket_receive = 0
        self.bot.start_time = time.time()

    async def uhh_rtfm_pls(self, ctx, key, obj):
        page_types = {
            "latest": "https://discordpy.readthedocs.io/en/latest",
            "python": "https://docs.python.org/3",
            "asyncpg": "https://magicstack.github.io/asyncpg/current/",
            "zaneapi": "https://docs.zaneapi.com/en/latest/",
            "aiohttp": "https://docs.aiohttp.org/en/stable/",
            "polaroid": "https://daggy1234.github.io/polaroid/",
        }
        if obj is None:
            await ctx.send(page_types[key])
            return

        async with self.bot.session.get(
            f"https://idevision.net/api/public/rtfm?query={obj}&location={page_types.get(key)}&show-labels=false&label-labels=false"
        ) as resp:
            if resp.status == 429:
                time = resp.headers.get("ratelimit-retry-after")
                await asyncio.sleep(time)
                return await self.uhh_rtfm_pls(ctx, key, obj)
            matches = await resp.json()
            matches = matches["nodes"]
            embed = discord.Embed(color=0x525A32)
            listy = []
            for k, v in matches.items():
                listy.append(f"[`{k}`]({v})")
            embed.description = "\n".join(listy)
            return await ctx.send(embed=embed)

    @commands.command(description="Checks Latency of Bot")
    async def ping(self, ctx):
        x = await ctx.send("Pong!")
        ping = round(self.bot.latency * 1000)
        content1 = f"Pong! `{ping}ms`"
        await x.edit(content=str(content1))

    @commands.group(
        invoke_without_command=True,
        aliases=[
            "read_the_friendly_manual",
            "rtfd",
            "read_the_friendly_doc",
            "read_tfm",
            "read_tfd",
        ],
    )
    async def rtfm(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, "latest", thing)

    @rtfm.command(name="py", aliases=["python"])
    async def rtfm_py(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, "python", thing)

    @rtfm.command(name="asyncpg", aliases=["apg"])
    async def rtfm_asyncpg(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, "asyncpg", thing)

    @rtfm.command(name="zaneapi")
    async def rtfm_zaneapi(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, "zaneapi", thing)

    @rtfm.command(name="aiohttp")
    async def rtfm_aiohttp(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, "aiohttp", thing)

    @rtfm.command(name="polaroid")
    async def rtfm_polaroid(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, "polaroid", thing)

    @rtfm.command(name="rust")
    async def rust(self, ctx, *, text: str):
        def soup_match(tag):
            return (
                all(string in tag.text for string in text.strip().split())
                and tag.name == "li"
            )

        async with self.bot.session.get(
            "https://doc.rust-lang.org/std/all.html"
        ) as resp:
            soup = BeautifulSoup(str(await resp.text()), "lxml")
        e = [x.select_one("li > a") for x in soup.find_all(soup_match, limit=8)]
        lines = [
            f"[`{a.string}`](https://doc.rust-lang.org/std/{a.get('href')})" for a in e
        ]
        await ctx.send(embed=discord.Embed(description="\n".join(lines)))

    @executor_function
    @staticmethod
    def translate_text(destination, args: str):
        translator = googletrans.Translator()
        return translator.translate(args, dest=destination)

    @commands.command()
    async def translate(self, ctx, destination, text_to_translate):
        result = await self.translate_text(destination, text_to_translate)
        return await ctx.send(embed=ctx.embed(description=result.text))

    @commands.command()
    async def commits(self, ctx):
        async with self.bot.session.get(
            "https://api.github.com/repos/MrKomodoDragon/sir-komodobot/commits"
        ) as f:
            resp = await f.json()
        embed = discord.Embed(
            description="\n".join(
                f"[`{commit['sha'][:6]}`]({commit['html_url']}) {commit['commit']['message']}"
                for commit in resp[:5]
            ),
            color=0x525A32,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx):  # sourcery no-metrics
        p = pathlib.Path("./")
        process = psutil.Process()
        start = time.perf_counter()
        await ctx.trigger_typing()
        end = time.perf_counter()
        final = end - start
        api_latency = round(final * 1000, 3)
        async with self.bot.session.get(
            "https://api.github.com/repos/MrKomodoDragon/sir-komodobot/commits"
        ) as f:
            resp = await f.json()
        embed = discord.Embed(
            title="Information about Sir KomodoBot",
            description=f"My owner is **,,MrKomodoDragon#7975**\n**Amount of Guilds:** {len(self.bot.guilds)}\n**Amount of members watched:** {len(self.bot.users)}\n**Amount of cogs loaded:** {len(self.bot.cogs)}\n**Amount of commands:** {len(self.bot.commands)}",
        )
        embed.add_field(
            name="Recent Commits",
            value="\n".join(
                f"[`{commit['sha'][:6]}`]({commit['html_url']}) {commit['commit']['message']}"
                for commit in resp[:5]
            ),
        )
        embed.add_field(
            name="System Info",
            value=f"```py\nCPU Usage: {process.cpu_percent()}%\nMemory Usage: {humanize.naturalsize(process.memory_full_info().rss)}\nPID: {process.pid}\nThread(s): {process.num_threads()}```",
            inline=False,
        )
        embed.add_field(
            name="Websocket Latency:",
            value=f"```py\n{round(self.bot.latency*1000)} ms```",
        )
        embed.add_field(name="API Latency", value=f"```py\n{round(api_latency)} ms```")
        await ctx.send(embed=embed)

    @commands.command()
    async def afk(self, ctx, *, reason="Away from computer"):
        self.bot.afk[ctx.author.id] = reason
        await ctx.send(f"I have set your afk to {reason}")

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if ctx.invoked_with == "afk":
            return
        if message.author.bot:
            return
        for id in self.bot.afk.keys():
            if message.author.id == id:
                del self.bot.afk[id]
                return await message.channel.send(
                    f"{message.author.mention}, Welcome back! I have removed your afk status"
                )
            member = message.guild.get_member(id)
            if member.mentioned_in(message):
                await message.channel.send(
                    f"{str(member)} is afk for: {self.bot.afk[id]}"
                )

    @commands.command(help="Searches PyPI for a Python Package")
    async def pypi(self, ctx, package: str):
        async with self.bot.session.get(f"https://pypi.org/pypi/{package}/json") as f:
            if not f or f.status != 200:
                return await ctx.send(embed=ctx.embed(description="Package not found."))
            package = await f.json()
        data = package.get("info")
        embed = ctx.embed(
            title=f"{data.get('name')} {data['version'] or ''}",
            url=data.get("project_url", "None provided"),
            description=data["summary"] or "None provided",
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/381963689470984203/814267252437942272/pypi.png"
        )
        embed.add_field(
            name="Author Info:",
            value=f'**Author Name**: `{data["author"] or "None provided"}`\n'
            f'**Author Email**: `{data["author_email"] or "None provided"}`',
        )
        urls = data.get("project_urls", "None provided")
        embed.add_field(
            name="Package Info:",
            value=f'**Documentation**: `{urls.get("Documentation", "None provided")}`\n'
            f'**Homepage**: `{urls.get("Homepage", "None provided")}`\n'
            f'**Keywords**: `{data["keywords"] or "None provided"}`\n'
            f'**License**: `{data["license"] or "None provided"}`',
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def eval(self, ctx, *, code):
        client = mystbin.Client()
        code = code.lstrip("```").rstrip("```")
        code = code.splitlines()
        lang = code.pop(0)
        code = "\n".join(code)
        json = {"language": lang, "source": code}
        async with self.bot.session.post(
            "https://emkc.org/api/v1/piston/execute", json=json
        ) as resp:
            data = await resp.json()
        if data.get("message"):
            return await ctx.send(
                embed=ctx.embed(
                    title="Something went wrong...",
                    description=data.get("message"),
                )
            )
        if len(data.get("output")) > 2000:
            thing = await client.post(content=data.get("output"), syntax=lang)
            return await ctx.send(
                embed=ctx.embed(
                    title="Your output was too long so I uploaded it here:",
                    description=thing,
                )
            )
        await ctx.send(
            embed=ctx.embed(
                title=f"Ran your code in `{lang}`",
                description=f'```{lang}\n{data.get("output")}\n```',
            )
        )

    @commands.command()
    async def remind(self, ctx, *, task: str):
        utcnow = datetime.datetime.utcnow()
        settings = {
            "TIMEZONE": "UTC",
            "TO_TIMEZONE": "UTC",
            "PREFER_DATES_FROM": "future",
            "PREFER_DAY_OF_MONTH": "first",
        }
        time_to_remind = dateparser.search.search_dates(task, settings=settings)
        if time_to_remind is None:
            return await ctx.send("I couldn't find a valid time to remind you")
        thing = time_to_remind[0][1] - utcnow
        reason = task.replace(time_to_remind[0][0], "")
        reason = reason.replace(" ", "", 1)
        await ctx.send(thing)
        await ctx.send(
            f"Alright {ctx.author.mention}, I'll remind you to {reason} after {humanize.naturaldelta(thing)}"
        )
        await asyncio.sleep(
            (time_to_remind[0][1] - datetime.datetime.utcnow()).total_seconds()
        )
        return await ctx.send(
            f"{ctx.author.mention}, here is your reminder to do {reason}: {ctx.message.jump_url}"
        )

    @commands.command()
    @commands.is_owner()
    async def code(self, ctx, *, code):
        json = {"code": code}
        async with self.bot.session.post(
            "https://carbonara.vercel.app/api/cook", json=json
        ) as resp:
            img = await resp.read()
        await ctx.send(file=discord.File(io.BytesIO(img), "thing.png"))

    @commands.command()
    async def pep(self, ctx, pep: int):
        async with self.bot.session.get(
            f"https://www.python.org/dev/peps/pep-{pep:0>4}/"
        ) as resp:
            data = await resp.text(encoding="utf-8")
        soup = bs4.BeautifulSoup(data, "html.parser")
        tr = soup.find_all("tr", class_="field")
        title = soup.find("title")
        th = [thing.th.contents[0] for thing in tr if thing.th.contents]

        td = [thing.td.contents[0] for thing in tr if thing.td.contents]
        thing = [i for i in zip(th, td)]
        embed = ctx.embed(
            title=title.contents[0],
            url=f"https://www.python.org/dev/peps/pep-{pep:0>4}/",
        )
        for i in thing:
            embed.add_field(name=i[0], value=i[1], inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def hoisters(self, ctx):
        await ctx.send(
            [
                i
                for i in ctx.guild.members
                if any(i.startswith(s) for s in string.punctuation)
            ]
        )

    @commands.command()
    async def choose(self, ctx, *args: str):
        await ctx.send(random.choice(args))

    @commands.command()
    async def buttons(self, ctx):
        thing = discord.http.Route("POST", f"/channels/{ctx.channel.id}/messages")
        json = {
            "content": "a",
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 3,
                            "custom_id": "dkfsdfjlskfj",
                            "placeholder": "ksdfjlsfjl",
                            "min_values": 10,
                            "max_values": 20,
                            "options": [
                                {"label": "a", "value": "a"},
                                {"label": "b", "value": "b"},
                                {"label": "c", "value": "c"},
                                {"label": "d", "value": "d"},
                                {"label": "e", "value": "e"},
                                {"label": "f", "value": "f"},
                                {"label": "g", "value": "g"},
                                {"label": "h", "value": "h"},
                                {"label": "i", "value": "i"},
                                {"label": "j", "value": "j"},
                                {"label": "k", "value": "fgdfgdg"},
                                {"label": "l", "value": "erteter"},
                                {"label": "m", "value": "rtertert"},
                                {
                                    "label": "n",
                                    "value": "rteteggk;dlgk;lgkd;gkd;fgkfd;tet",
                                },
                                {"label": "o", "value": "rterterte"},
                                {"label": "p", "value": "retetet"},
                                {
                                    "label": "q",
                                    "value": "eteaaaaaaaaaaaaaaaaaaaaaaaatert",
                                },
                                {"label": "r", "value": "fgdgfgdddddddddddddddddd"},
                                {"label": "s", "value": "fgdgdgfjlkkkkkkkkkdg"},
                                {
                                    "label": "t",
                                    "value": "fgdhggdjflkkkkkkkkkkkkkkkkhhggdg",
                                },
                                {"label": "u", "value": "fgdlfdgkjjjjjjjjjjgdg"},
                                {"label": "v", "value": "dgdgdffdglk;;;;;g"},
                                {"label": "w", "value": "dfgddfgkldgkdlkg;fdgg"},
                            ],
                        }
                    ],
                }
            ],
        }

        await self.bot.http.request(thing, json=json)


def setup(bot):
    bot.add_cog(Utility(bot))
