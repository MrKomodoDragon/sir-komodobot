import datetime
import os
import random

import aiohttp
import asyncpraw
import discord
from asyncdagpi import Client
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from dotenv import load_dotenv
from utils.fuzzy import finder

from jishaku.paginators import PaginatorInterface, WrappedPaginator

load_dotenv()

id = os.getenv('REDDIT_CLIENT_ID')
secret = os.getenv('REDDIT_CLIENT_SECRET')

dagpi = Client(os.getenv('DAGPI_TOKEN'))

reddit = asyncpraw.Reddit(
    client_id=id,
    client_secret=secret,
    user_agent='Sir Komodo the Great Bot',
)


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Posts a random joke', brief='joke')
    async def joke(self, ctx):
        with open('jokes.txt', 'r') as f:
            jokes = list(f)
            await ctx.send(random.choice(jokes))

    @commands.command(
        description='Posts a random Knock-Knock Joke', brief='knockknock'
    )
    async def knockknock(self, ctx):
        with open('knock-knock.txt', 'r') as f:
            jokes = list(f)
            await ctx.send(random.choice(jokes))

    @commands.command(description='Posts a dad-joke', brief='dadjoke')
    async def dadjoke(self, ctx):
        with open('dadjokes.txt', 'r') as f:
            jokes = list(f)
            await ctx.send(random.choice(jokes))

    @commands.command(description='Posts a very *punny* pun', brief='pun')
    async def pun(self, ctx):
        with open('puns.txt', 'r') as f:
            jokes = list(f)
            await ctx.send(random.choice(jokes))

    @commands.command(description='Makes text bold', brief='bold hello')
    async def bold(self, ctx, *, message):
        await ctx.send(f'**{message}**')

    @commands.command(
        description='Turns text in to regional indicators',
        brief='emojify hello',
    )
    async def emojify(self, ctx, *, message):
        emojis = []
        message1 = message.lower()
        letters = list(message1)
        for i in letters:
            if i.isalpha():
                emojis.append(f':regional_indicator_{i}:')
            elif i == ' ':
                emojis.append(' ')
            else:
                emojis.append(i)
        sentence = ' '.join(emojis)
        await ctx.send(sentence)

    @commands.command(
        aliases=['pander', 'pando'],
        description='Look at some pandas',
        brief='panda',
    )
    async def panda(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/panda') as r:
                res = await r.json()
        embed = discord.Embed(title='PANDA!!!', color=0x0000FF)
        embed.set_image(url=res['link'])
        embed.set_footer(text='Powered by https://some-random-api.ml')
        await ctx.send(embed=embed)

    @commands.command(
        aliases=['bird', 'birdo', 'birbo'],
        description='Look at some birbs',
        brief='birb',
    )
    async def birb(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/birb') as r:
                res = await r.json()
        embed = discord.Embed(title='BIRB!!!', color=0x0000FF)
        embed.set_image(url=res['link'])
        embed.set_footer(text='Powered by https://some-random-api.ml')
        await ctx.send(embed=embed)

    @commands.command(
        aliases=['foxo', 'foxxo', 'foxy', 'foxxy'],
        description='Look at some foxed',
        brief='fox',
    )
    async def fox(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/fox') as r:
                res = await r.json()
        embed = discord.Embed(title='FOXXY!!!', color=0x0000FF)
        embed.set_image(url=res['link'])
        embed.set_footer(text='Powered by https://some-random-api.ml')
        await ctx.send(embed=embed)

    @commands.command(
        aliases=['redpando', 'redpander'],
        description='Look at some red pandas',
        brief='birb',
    )
    async def redpanda(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/red_panda') as r:
                res = await r.json()
        embed = discord.Embed(title='RED PANDO!!!', color=0x0000FF)
        embed.set_image(url=res['link'])
        embed.set_footer(text='Powered by https://some-random-api.ml')
        await ctx.send(embed=embed)

    @commands.command(
        aliases=['koaler'], description='Look at some red pandas', brief='birb'
    )
    async def koala(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/koala') as r:
                res = await r.json()
        embed = discord.Embed(title='KOALA!!!', color=0x0000FF)
        embed.set_image(url=res['link'])
        embed.set_footer(text='Powered by https://some-random-api.ml')
        await ctx.send(embed=embed)

    @commands.command(
        aliases=['cato'], description='Look at some red pandas', brief='birb'
    )
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://some-random-api.ml/img/cat') as r:
                res = await r.json()
        embed = discord.Embed(title='CATTO!!!', color=0x0000FF)
        embed.set_image(url=res['link'])
        embed.set_footer(text='Powered by https://some-random-api.ml')
        await ctx.send(embed=embed)

    @commands.command(
        description='gives you some cute animal pics!',
        aliases=['cute', 'awww'],
        brief='aww',
    )
    async def aww(self, ctx):
        subreddit = await reddit.subreddit('aww')
        submission = await subreddit.random()
        if not submission.over_18:
            titled = submission.title
            url = submission.url
            reddited = submission.subreddit_name_prefixed
            reddit_embed = discord.Embed(
                title=f'**{titled}**',
                url=f'https://reddit.com/comments/{submission.id}',
                color=discord.Colour.orange(),
            )
            reddit_embed.set_author(
                name=f'{reddited}',
                url=f'https://www.reddit.com/r/{subreddit}',
                icon_url='https://external-preview.redd.it/'
                'iDdntscPf-nfWKqzHRGFmhVxZm4hZgaKe5oyFws-yzA.png?a'
                'uto=webp&s=38648ef0dc2c3fce76d5e1d8639234d8da0152b2',
            )
            reddit_embed.set_image(url=f'{url}')
            await ctx.send(embed=reddit_embed)

    @commands.command(
        aliases=['dog', 'doggy'],
        description='Look at some red pandas',
        brief='birb',
    )
    async def doggo(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://dog.ceo/api/breeds/image/random') as r:
                res = await r.json()
        embed = discord.Embed(title='DOGGO!!!', color=0xFF0000)
        embed.set_image(url=res['message'])
        embed.set_footer(text='Powered by https://dog.ceo')
        await ctx.send(embed=embed)

    class PaginatorEmbedInterface(PaginatorInterface):
        def __init__(self, *args, **kwargs):
            self._embed = discord.Embed()
            super().__init__(*args, **kwargs)

        @property
        def send_kwargs(self) -> dict:
            display_page = self.display_page
            self._embed.description = (
                f'**:7298_Nitro_Gif: Emoji List**\n{self.pages[display_page]}'
            )
            self._embed.set_footer(
                text=f'Page {display_page + 1}/{self.page_count}'
            )
            return {'embed': self._embed}

        max_page_size = 2048

        @property
        def page_size(self) -> int:
            return self.paginator.max_size

    @commands.command(description='Look at some red pandas', brief='birb')
    @commands.cooldown(1, 3.0, BucketType.member)
    async def meme(self, ctx):
        subreddit = await reddit.subreddit('memes')
        submission = await subreddit.random()
        if not submission.over_18:
            titled = submission.title
            url = submission.url
            reddited = submission.subreddit_name_prefixed
            reddit_embed = discord.Embed(
                title=f'**{titled}**',
                url=f'https://reddit.com/comments/{submission.id}',
                color=discord.Colour.orange(),
            )
            reddit_embed.set_author(
                name=f'{reddited}',
                url=f'https://www.reddit.com/r/{subreddit}',
                icon_url='https://external-preview.redd.it/iDdntscPf-nfWKqzHRG'
                'FmhVxZm4hZgaKe5oyFws-yzA.png?auto=webp&s=38648e'
                'f0dc2c3fce76d5e1d8639234d8da0152b2',
            )
            reddit_embed.set_image(url=f'{url}')
            await ctx.trigger_typing()
            await ctx.send(embed=reddit_embed)

    @commands.command(description='Look at some red pandas', brief='birb')
    async def facepalm(self, ctx):
        subreddit = await reddit.subreddit('facepalm')
        submission = await subreddit.random()
        if not submission.over_18:
            titled = submission.title
            url = submission.url
            reddited = submission.subreddit_name_prefixed
            reddit_embed = discord.Embed(
                title=f'**{titled}**',
                url=f'https://reddit.com/comments/{submission.id}',
                color=discord.Colour.orange(),
            )
            reddit_embed.set_author(
                name=f'{reddited}',
                url=f'https://www.reddit.com/r/{subreddit}',
                icon_url='https://external-preview.redd.it/iDdntscP'
                'f-nfWKqzHRGFmhVxZm4hZgaKe5oyFws-yzA.png?auto=webp'
                '&s=38648ef0dc2c3fce76d5e1d8639234d8da0152b2',
            )
            reddit_embed.set_image(url=f'{url}')
            await ctx.send(embed=reddit_embed)

    @commands.command(
        aliases=['ducc', 'ducco', 'ducko'],
        description='Look at some red pandas',
        brief='birb',
    )
    async def duck(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://random-d.uk/api/random') as r:
                res = await r.json()
        embed = discord.Embed(title='DUCCCY!!!', color=0x0000FF)
        embed.set_image(url=res['url'])
        embed.set_footer(text=res['message'])
        await ctx.send(embed=embed)

    @commands.command(description='Look at some red pandas', brief='birb')
    async def roast(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        roast = await dagpi.roast()
        await ctx.send(f'**{member.name}**, {roast}')

    @commands.command(description='Look at some red pandas', brief='birb')
    async def top(ctx, subreddit):
        subreddit = await reddit.subreddit(subreddit)
        top_posts = subreddit.top('hour')
        await ctx.send(top_posts)

    @commands.command()
    async def emoji(self, ctx, *, search: str = None):
        lists = []
        paginator = WrappedPaginator(max_size=500, prefix='', suffix='')
        if search is not None:
            emojis = finder(
                search, self.bot.emojis, key=lambda i: i.name, lazy=False
            )
            if emojis == []:
                return await ctx.send('no emoji found')
            for i in emojis:
                if i.animated is True:
                    lists.append(f'{str(i)} `<a:{i.name}:{i.id}>`')
                else:
                    lists.append(f'{str(i)} `<:{i.name}:{i.id}>`')
            paginator.add_line('\n'.join(lists))
            interface = self.PaginatorEmbedInterface(
                ctx.bot, paginator, owner=ctx.author
            )
            return await interface.send_to(ctx)
        for i in self.bot.emojis:
            if i.animated is True:
                lists.append(f'{str(i)} `<a:{i.name}:{i.id}>`')
            else:
                lists.append(f'{str(i)} `<:{i.name}:{i.id}>`')
        paginator.add_line('\n'.join(lists))
        interface = self.PaginatorEmbedInterface(
            ctx.bot, paginator, owner=ctx.author
        )
        await interface.send_to(ctx)

    @commands.command()
    async def opt_in(self, ctx):
        opt_in = await self.bot.pg.fetchrow(
            'SELECT opt_in from emotes WHERE member_id = $1', ctx.author.id
        )
        opt_in = opt_in['opt_in']
        if opt_in is True:
            await ctx.send('You Have Already opted-in to emotes')
        else:
            await self.bot.pg.execute(
                'UPDATE emotes set opt_in = TRUE WHERE member_id = $1',
                ctx.author.id,
            )
            await ctx.send('You have opted-in to emoji.')

    @commands.command()
    async def opt_out(self, ctx):
        opt_in = await self.bot.pg.fetchrow(
            'SELECT opt_in from emotes WHERE member_id = $1', ctx.author.id
        )
        opt_in = opt_in['opt_in']
        if opt_in is False:
            await ctx.send('You Have Already opted out of emotes')
        else:
            await self.bot.pg.execute(
                'UPDATE emotes set opt_in = FALSE WHERE member_id = $1',
                ctx.author.id,
            )
            await ctx.send('You have opted out of emoji.')

    @commands.command(description='Fetches a random quote')
    async def quote(self, ctx):
        async with self.bot.session.get(
            'https://api.quotable.io/random'
        ) as random:
            data = await random.json()
        await ctx.send(
            embed=discord.Embed(
                title='Random Quote',
                description=f'**Quote**: '
                f'{data["content"]}\n**Author**: {data["author"]}',
            )
        )

    @commands.command(help='Posts a random bignate comic', brief='bignate')
    async def bignate(self, ctx):
        start_date = datetime.date(1991, 2, 1)
        end_date = datetime.date(2020, 12, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + datetime.timedelta(
            days=random_number_of_days
        )
        date = str(random_date).replace('-', '/')
        async with self.bot.session.get(
            f'http://gocomics.com/bignate/{date}'
        ) as r:
            await ctx.trigger_typing()
            data = await r.text()
            soup = BeautifulSoup(data, 'html.parser')
            comic = soup.find('picture', class_='item-comic-image')
            embed = discord.Embed(
                title=comic.img['alt'],
                color=0x0000FF,
                url=f'http://gocomics.com/bignate/{date}',
            )
            embed.set_image(url=comic.img['src'])
            await ctx.send(embed=embed)

    @commands.command()
    async def xkcdsearch(self, ctx, *, search):
        relevant_xkcd_url = (
            'https://relevantxkcd.appspot.com/process?action=xkcd&query='
        )
        search_url = relevant_xkcd_url + search
        async with self.bot.session.get(search_url) as resp:
            text = await resp.text()
            results = text.split('\n')
            num = results[2].split(' ')[0]
            async with self.bot.session.get(
                f'https://xkcd.com/{num}/info.0.json'
            ) as info:
                comix = await info.json()
            round_relevance = round(float(results[0]) * 1000, 1)
            relevance = f'**Relevance: {round_relevance}%**'
            embed = discord.Embed(
                title=f"**{num}: {comix['title']}**",
                colour=discord.Colour(0xFFFFFF),
                url=f'https://xkcd.com/{num}/',
                description=comix['alt'],
            )
            embed.set_image(url=comix['img'])
            embed.set_author(
                name='XKCD',
                url='https://xkcd.com',
                icon_url='https://cdn.changelog.com/uploads/icons'
                '/news_sources/P2m/icon_small.png?v=63722746912',
            )
            embed.set_footer(
                text=f'Comic Released on:'
                f" {comix['month']}/{comix['day']}/{comix['year']}"
                ' (view more comics at https://xkcd.com)'
            )
            await ctx.send(f'{relevance}', embed=embed)

    @commands.command()
    async def mock(self, ctx, *, text=None):
        text = (
            ctx.message.reference.resolved.content
            if ctx.message.reference
            else text or 'You specified no text'
        )
        output_text = ''
        for char in text:
            if char.isalpha():
                output_text += (
                    char.upper() if random.random() > 0.5 else char.lower()
                )
            else:
                output_text += char
        await ctx.send(output_text)

    @commands.command()
    async def blob(self, ctx):
        emoji = [i for i in self.bot.emojis if i.name.startswith('blob')]
        await ctx.send(str(random.choice(emoji)))

    @commands.command()
    async def roo(self, ctx):
        emoji = [i for i in self.bot.emojis if i.name.startswith('roo')]
        await ctx.send(str(random.choice(emoji)))


def setup(bot):
    bot.add_cog(Fun(bot))
