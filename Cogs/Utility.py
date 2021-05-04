from PIL import Image
import asyncio
import datetime
import pathlib
import time
import unicodedata
from collections import Counter

import dateparser.search
import discord
import googletrans
import humanize
import mystbin
import psutil
from discord.ext import commands, menus
import io
import bs4
import string
from jishaku.functools import executor_function
import random

'''
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
'''


class TodoSource(menus.ListPageSource):
    async def format_page(self, menu, todos):
        # sourcery skip: comprehension-to-generator
        ctx = menu.ctx
        count = await ctx.bot.pg.fetchval(
            'SELECT COUNT(*) FROM TODOS WHERE user_id = $1', ctx.author.id
        )
        cur_page = f'Page {menu.current_page + 1}/{self.get_max_pages()}'
        return ctx.embed(
            title=f"{menu.ctx.author.name}'s todo list | {count} total entries | {cur_page}",
            description='\n'.join(
                [
                    f"[{todo['jump_url']}]({todo['row_number']} {todo['task']}"
                    for todo in todos
                ]
            ),
        )


class TodoPages(menus.MenuPages):
    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f', position=menus.Last(2))
    async def end_menu(self, _):
        self.message.delete()
        self.stop()


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        _page_types = {
            'latest': 'https://discordpy.readthedocs.io/en/latest',
            'python': 'https://docs.python.org/3',
            'asyncpg': 'https://magicstack.github.io/asyncpg/current/',
            'zaneapi': 'https://docs.zaneapi.com/en/latest/',
            'aiohttp': 'https://docs.aiohttp.org/en/stable/',
        }
        self.rtfm_lock = asyncio.Lock
        self.afk = {}
        self.bot.codes = {
            1: 'HEARTBEAT',
            2: 'IDENTIFY',
            3: 'PRESENCE',
            4: 'VOICE_STATE',
            5: 'VOICE_PING',
            6: 'RESUME',
            7: 'RECONNECT',
            8: 'REQUEST_MEMBERS',
            9: 'INVALIDATE_SESSION',
            10: 'HELLO',
            11: 'HEARTBEAT_ACK',
            12: 'GUILD_SYNC',
        }

        self.bot.socket_stats = Counter()
        self.bot.socket_receive = 0
        self.bot.start_time = time.time()

    async def uhh_rtfm_pls(self, ctx, key, obj):
        page_types = {
            'latest': 'https://discordpy.readthedocs.io/en/master',
            'python': 'https://docs.python.org/3',
            'asyncpg': 'https://magicstack.github.io/asyncpg/current/',
            'zaneapi': 'https://docs.zaneapi.com/en/latest/',
            'aiohttp': 'https://docs.aiohttp.org/en/stable/',
        }
        if obj is None:
            await ctx.send(page_types[key])
            return

        async with self.bot.session.get(
            f'https://idevision.net/api/public/rtfm?query={obj}&location={page_types.get(key)}&show-labels=false&label-labels=false'
        ) as resp:
            if resp.status == 429:
                time = resp.headers.get('ratelimit-retry-after')
                await asyncio.sleep(time)
                return await self.uhh_rtfm_pls(ctx, key, obj)
            matches = await resp.json()
            matches = matches['nodes']
            embed = discord.Embed(color=0x525A32)
            listy = []
            for k, v in matches.items():
                listy.append(f'[`{k}`]({v})')
            embed.description = '\n'.join(listy)
            return await ctx.send(embed=embed)

    @commands.command(description='Checks Latency of Bot')
    async def ping(self, ctx):
        x = await ctx.send('Pong!')
        ping = round(self.bot.latency * 1000)
        content1 = f'Pong! `{ping}ms`'
        await x.edit(content=str(content1))

    @commands.group(
        invoke_without_command=True,
        aliases=[
            'read_the_friendly_manual',
            'rtfd',
            'read_the_friendly_doc',
            'read_tfm',
            'read_tfd',
        ],
    )
    async def rtfm(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, 'latest', thing)

    @rtfm.command(name='py', aliases=['python'])
    async def rtfm_py(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, 'python', thing)

    @rtfm.command(name='asyncpg', aliases=['apg'])
    async def rtfm_asyncpg(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, 'asyncpg', thing)

    @rtfm.command(name='zaneapi')
    async def rtfm_zaneapi(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, 'zaneapi', thing)

    @rtfm.command(name='aiohttp')
    async def rtfm_aiohttp(self, ctx, *, thing: str = None):
        await self.uhh_rtfm_pls(ctx, 'aiohttp', thing)


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
            'https://api.github.com/repos/MrKomodoDragon/sir-komodobot/commits'
        ) as f:
            resp = await f.json()
        embed = discord.Embed(
            description='\n'.join(
                f"[`{commit['sha'][:6]}`]({commit['html_url']}) {commit['commit']['message']}"
                for commit in resp[:5]
            ),
            color=0x525A32,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx):  # sourcery no-metrics
        p = pathlib.Path('./')
        process = psutil.Process()
        start = time.perf_counter()
        await ctx.trigger_typing()
        end = time.perf_counter()
        final = end - start
        api_latency = round(final * 1000, 3)
        cm = cr = fn = cl = ls = fc = 0
        for f in p.rglob('*.py'):
            if str(f).startswith('venv'):
                continue
            fc += 1
            with f.open() as of:
                for line in of.readlines():
                    line = line.strip()
                    if line.startswith('class'):
                        cl += 1
                    if line.startswith('def'):
                        fn += 1
                    if line.startswith('async def'):
                        cr += 1
                    if '#' in line:
                        cm += 1
                    ls += 1
        async with self.bot.session.get(
            'https://api.github.com/repos/MrKomodoDragon/sir-komodobot/commits'
        ) as f:
            resp = await f.json()
        embed = discord.Embed(
            title='Information about Sir KomodoBot',
            description=f'My owner is **,,MrKomodoDragon#7975**\n**Amount of Guilds:** {len(self.bot.guilds)}\n**Amount of members watched:** {len(self.bot.users)}\n**Amount of cogs loaded:** {len(self.bot.cogs)}\n**Amount of commands:** {len(self.bot.commands)}',
        )
        embed.add_field(
            name='Recent Commits',
            value='\n'.join(
                f"[`{commit['sha'][:6]}`]({commit['html_url']}) {commit['commit']['message']}"
                for commit in resp[:5]
            ),
        )
        embed.add_field(
            name='System Info',
            value=f'```py\nCPU Usage: {process.cpu_percent()}%\nMemory Usage: {humanize.naturalsize(process.memory_full_info().rss)}\nPID: {process.pid}\nThread(s): {process.num_threads()}```',
            inline=False,
        )
        embed.add_field(
            name='Websocket Latency:',
            value=f'```py\n{round(self.bot.latency*1000)} ms```',
        )
        embed.add_field(
            name='API Latency', value=f'```py\n{round(api_latency)} ms```'
        )
        embed.add_field(
            name='File Stats:',
            value=f'```py\nFiles: {fc}\nLines: {ls:,}\nClasses: {cl}\nFunctions: {fn}\nCoroutines: {cr}\nComments: {cm:,}```',
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command(
        help='Covid stats. Use world as country to view total stats',
        aliases=['cv'],
    )
    async def covid(self, ctx, *, countryName=None):
        try:
            if countryName is None:
                embed = discord.Embed(
                    title=f'This command is used like this: ```{ctx.prefix}covid [country]```',
                    colour=discord.Colour.blurple(),
                    timestamp=ctx.message.created_at,
                )
                await ctx.send(embed=embed)
            else:
                await ctx.trigger_typing()
                url = f'https://coronavirus-19-api.herokuapp.com/countries/{countryName}'
                async with self.bot.session.get(url) as r:
                    json_stats = await r.json()
                    country = json_stats['country']
                    totalCases = f'{json_stats["cases"]:,}'
                    todayCases = f'{json_stats["todayCases"]:,}'
                    totalDeaths = f'{json_stats["deaths"]:,}'
                    todayDeaths = f'{json_stats["todayDeaths"]:,}'
                    recovered = f'{json_stats["recovered"]:,}'
                    active = f'{json_stats["active"]:,}'
                    critical = f'{json_stats["critical"]:,}'
                    casesPerOneMillion = (
                        f'{json_stats["casesPerOneMillion"]:,}'
                    )
                    deathsPerOneMillion = (
                        f'{json_stats["deathsPerOneMillion"]:,}'
                    )
                    totalTests = f'{json_stats["totalTests"]:,}'
                    testsPerOneMillion = (
                        f'{json_stats["testsPerOneMillion"]:,}'
                    )

                    embed2 = discord.Embed(
                        title=f'**COVID-19 Status Of {country}**!',
                        description="This Information Isn't Live Always, Hence It May Not Be Accurate!",
                        colour=discord.Colour.blurple(),
                        timestamp=ctx.message.created_at,
                    )
                    embed2.add_field(
                        name='**Total Cases**', value=totalCases, inline=True
                    )
                    embed2.add_field(
                        name='**Today Cases**', value=todayCases, inline=True
                    )
                    embed2.add_field(
                        name='**Total Deaths**', value=totalDeaths, inline=True
                    )
                    embed2.add_field(
                        name='**Today Deaths**', value=todayDeaths, inline=True
                    )
                    embed2.add_field(
                        name='**Recovered**', value=recovered, inline=True
                    )
                    embed2.add_field(
                        name='**Active**', value=active, inline=True
                    )
                    embed2.add_field(
                        name='**Critical**', value=critical, inline=True
                    )
                    embed2.add_field(
                        name='**Cases Per One Million**',
                        value=casesPerOneMillion,
                        inline=True,
                    )
                    embed2.add_field(
                        name='**Deaths Per One Million**',
                        value=deathsPerOneMillion,
                        inline=True,
                    )
                    embed2.add_field(
                        name='**Total Tests**', value=totalTests, inline=True
                    )
                    embed2.add_field(
                        name='**Tests Per One Million**',
                        value=testsPerOneMillion,
                        inline=True,
                    )
                    embed2.set_footer(
                        text=f'Requested by {ctx.author.name}',
                        icon_url=ctx.author.avatar_url,
                    )

                    await ctx.send(embed=embed2)

        except:
            embed3 = discord.Embed(
                title='Invalid Country Name Or API Error! Try Again..!',
                colour=discord.Colour.blurple(),
                timestamp=ctx.message.created_at,
            )
            embed3.set_author(name='Error!')
            await ctx.send(embed=embed3)

    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters.
        Only up to 25 characters at a time.
        """

        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'

        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send('Output too long to display.')
        await ctx.send(msg)

    @commands.command()
    async def afk(self, ctx, *, reason='Away from computer'):
        self.bot.afk[ctx.author.id] = reason
        await ctx.send(f'I have set your afk to {reason}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        for id in self.bot.afk.keys():
            if message.author.id == id:
                del self.bot.afk[id]
                return await message.channel.send(
                    f'{message.author.mention}, Welcome back! I have removed your afk status'
                )
            member = message.guild.get_member(id)
            if member.mentioned_in(message):
                await message.channel.send(
                    f'{str(member)} is afk for: {self.bot.afk[id]}'
                )

    @commands.group()
    async def todo(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send_help(str(ctx.command))

    # thanks ppotatoo for this code
    @todo.command()
    async def add(self, ctx, *, thing):
        await self.bot.pg.execute(
            'INSERT INTO todos VALUES($1, $2, $3)',
            ctx.author.id,
            thing,
            datetime.datetime.utcnow(),
        )
        await ctx.send(
            embed=ctx.embed(
                title='I added one task to your list: ', description=thing
            )
        )

    @todo.command()
    async def list(self, ctx):
        """View all your todos."""
        sql = (
            'SELECT DISTINCT todo, sort_date, '
            'ROW_NUMBER () OVER (ORDER BY sort_date) FROM todos '
            'WHERE user_id = $1 ORDER BY sort_date'
        )
        todos = await self.bot.pg.fetch(sql, ctx.author.id)

        pages = TodoPages(source=TodoSource(todos))

        await pages.start(ctx)

    @todo.command()
    async def remove(self, ctx, id: int):
        sql = (
            'SELECT DISTINCT todo, sort_date, '
            'ROW_NUMBER () OVER (ORDER BY sort_date) FROM todos '
            'WHERE user_id = $1 ORDER BY sort_date'
        )
        todos = await self.bot.pg.fetch(sql, ctx.author.id)
        text = todos[id - 1]['todo']
        await self.bot.pg.execute(
            'DELETE FROM todos WHERE user_id = $1 AND todo = $2',
            ctx.author.id,
            text,
        )
        await ctx.send(
            embed=ctx.embed(
                title=f'Removed one task:', description=f'`{id}` => {text}'
            )
        )

    @todo.command(name='info')
    async def todo_info(self, ctx, id: int):
        """
        View info about a certain task.
        You can see the exact time the task was created.
        """
        sql = (
            'SELECT DISTINCT todo, sort_date, time, '
            'ROW_NUMBER () OVER (ORDER BY sort_date) FROM todos '
            'WHERE user_id = $1 ORDER BY sort_date'
        )
        todos = await self.bot.pg.fetch(sql, ctx.author.id)
        todo = todos[id - 1]['todo']
        pro = humanize.naturaltime(
            datetime.datetime.utcnow() - todos[id - 1]['time']
        )
        embed = ctx.embed(title=f'Task `{id}`', description=todo)
        embed.add_field(name='Info', value=f'This todo was created **{pro}**.')
        await ctx.send(embed=embed)

    @todo.command(usage='<task ID 1> <task ID 2>')
    async def swap(self, ctx, t1: int, t2: int):
        """Swap the places of two tasks."""
        sql = (
            'SELECT DISTINCT sort_date, todo '
            'FROM todos '
            'WHERE user_id = $1 ORDER BY sort_date'
        )
        todos = await self.bot.db.fetch(sql, ctx.author.id)
        task1 = todos[t1 - 1]
        task2 = todos[t2 - 1]
        await self.bot.pg.execute(
            'UPDATE todos SET sort_date = $1 WHERE user_id = $2 AND todo = $3',
            task2['sort_date'],
            ctx.author.id,
            task1['todo'],
        )
        await self.bot.pg.execute(
            'UPDATE todos SET sort_date = $1 WHERE user_id = $2 AND todo = $3',
            task1['sort_date'],
            ctx.author.id,
            task2['todo'],
        )
        await ctx.send(
            embed=ctx.embed(
                description=f'Succesfully swapped places of todo `{t1}` and `{t2}`'
            )
        )

    @todo.command()
    async def raw(self, ctx, id: int):
        """View the raw todo for a task."""
        sql = (
            'SELECT DISTINCT todo, sort_date, '
            'ROW_NUMBER () OVER (ORDER BY sort_date) FROM todos '
            'WHERE user_id = $1 ORDER BY sort_date'
        )

        todos = await self.bot.db.fetch(sql, ctx.author.id)
        if id > len(todos):
            return await ctx.send(
                f"You only have {len(todos)} {ctx.plural('task(s)', len(todos))}"
            )
        await ctx.send(
            todos[id - 1]['todo'],
            allowed_mentions=discord.AllowedMentions().none(),
        )

    @commands.command(help='Searches PyPI for a Python Package')
    async def pypi(self, ctx, package: str):
        async with self.bot.session.get(
            f'https://pypi.org/pypi/{package}/json'
        ) as f:
            if not f or f.status != 200:
                return await ctx.send(
                    embed=ctx.embed(description='Package not found.')
                )
            package = await f.json()
        data = package.get('info')
        embed = ctx.embed(
            title=f"{data.get('name')} {data['version'] or ''}",
            url=data.get('project_url', 'None provided'),
            description=data['summary'] or 'None provided',
        )
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/381963689470984203/814267252437942272/pypi.png'
        )
        embed.add_field(
            name='Author Info:',
            value=f'**Author Name**: `{data["author"] or "None provided"}`\n'
            f'**Author Email**: `{data["author_email"] or "None provided"}`',
        )
        urls = data.get('project_urls', 'None provided')
        embed.add_field(
            name='Package Info:',
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
        code = code.lstrip('```').rstrip('```')
        code = code.splitlines()
        lang = code.pop(0)
        code = '\n'.join(code)
        json = {'language': lang, 'source': code}
        async with self.bot.session.post(
            'https://emkc.org/api/v1/piston/execute', json=json
        ) as resp:
            data = await resp.json()
        if data.get('message'):
            return await ctx.send(
                embed=ctx.embed(
                    title='Something went wrong...',
                    description=data.get('message'),
                )
            )
        if len(data.get('output')) > 2000:
            thing = await client.post(content=data.get('output'), syntax=lang)
            return await ctx.send(
                embed=ctx.embed(
                    title='Your output was too long so I uploaded it here:',
                    description=thing,
                )
            )
        await ctx.send(
            embed=ctx.embed(
                title=f'Ran your code in `{lang}`',
                description=f'```{lang}\n{data.get("output")}\n```',
            )
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        self.bot.socket_stats['COMMAND_ERROR'] += 1

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        self.bot.socket_receive += 1
        if msg.get('op') != 0:
            self.bot.socket_stats[self.bot.codes[msg.get('op')]] += 1
        else:
            self.bot.socket_stats[msg.get('t')] += 1

    @commands.command()
    async def remind(self, ctx, *, task: str):
        settings = {
            'TIMEZONE': 'UTC',
            'TO_TIMEZONE': 'UTC',
            'PREFER_DATES_FROM': 'future',
            'PREFER_DAY_OF_MONTH': 'first',
        }
        time_to_remind = dateparser.search.search_dates(
            task, settings=settings
        )
        if time_to_remind is None:
            return await ctx.send("I couldn't find a valid time to remind you")
        thing = time_to_remind[0][1] - datetime.datetime.utcnow()
        reason = task.replace(time_to_remind[0][0], '').replace(' ', '', 1)
        await ctx.send(thing)
        await ctx.send(
            f"Alright {ctx.author.mention}, I'll remind you to {reason} after {humanize.naturaldelta(thing)}"
        )
        await asyncio.sleep(
            (time_to_remind[0][1] - datetime.datetime.utcnow()).total_seconds()
        )
        return await ctx.send(
            f'{ctx.author.mention}, here is you reminder to do {reason}: {ctx.message.jump_url}'
        )

    @commands.command()
    @commands.is_owner()
    async def code(self, ctx, *, code):
        json = {'code': code}
        async with self.bot.session.post(
            'https://carbonara.vercel.app/api/cook', json=json
        ) as resp:
            img = await resp.read()
        await ctx.send(file=discord.File(io.BytesIO(img), 'thing.png'))

    @commands.command()
    async def pep(self, ctx, pep: int):
        async with self.bot.session.get(
            f'https://www.python.org/dev/peps/pep-{pep:0>4}/'
        ) as resp:
            data = await resp.text(encoding='utf-8')
        soup = bs4.BeautifulSoup(data, 'html.parser')
        tr = soup.find_all('tr', class_='field')
        title = soup.find('title')
        th = [thing.th.contents[0] for thing in tr if thing.th.contents]

        td = [thing.td.contents[0] for thing in tr if thing.td.contents]
        thing = [i for i in zip(th, td)]
        embed = ctx.embed(
            title=title.contents[0],
            url=f'https://www.python.org/dev/peps/pep-{pep:0>4}/',
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

def setup(bot):
    bot.add_cog(Utility(bot))
