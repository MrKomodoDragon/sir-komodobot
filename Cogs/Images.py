import inspect
import similar
import unicodedata
import time
import humanize
import typing
import aiozaneapi
from asyncdagpi import ImageFeatures, Client
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from asyncpraw.reddit import Reddit
import os
import io
from twemoji_parser import emoji_to_url
import json
from PIL import Image

load_dotenv()

dagpi = Client(os.getenv('DAGPI_TOKEN'))
client = aiozaneapi.Client(os.getenv('ZANE_TOKEN'))


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Credit to cryptex for the get_url command, pretty cool
    async def get_url(self, ctx, thing):  # sourcery no-metrics
        if ctx.message.reference:
            if ctx.message.reference.cached_message:
                if (
                    ctx.message.reference.cached_message.embeds
                    and ctx.message.reference.cached_message.embeds[0].type
                    == 'image'
                ):
                    url = ctx.message.reference.cached_message.embeds[
                        0
                    ].thumbnail.proxy_url
                    url = url.replace(
                        'cdn.discordapp.com', 'media.discordapp.net'
                    )
                    return url
                elif (
                    ctx.message.reference.cached_message.embeds
                    and ctx.message.reference.cached_message.embeds[0].type
                    == 'rich'
                ):
                    url = ctx.message.reference.cached_message.embeds[
                        0
                    ].image.proxy_url
                    url = url.replace(
                        'cdn.discordapp.com', 'media.discordapp.net'
                    )
                    return url
                elif (
                    ctx.message.reference.cached_message.attachments
                    and ctx.message.reference.cached_message.attachments[
                        0
                    ].width
                    and ctx.message.reference.cached_message.attachments[
                        0
                    ].height
                ):
                    url = ctx.message.reference.cached_message.attachments[
                        0
                    ].proxy_url
                    url = url.replace(
                        'cdn.discordapp.com', 'media.discordapp.net'
                    )
                    return url
            else:
                message = await self.bot.get_channel(
                    ctx.message.reference.channel_id
                ).fetch_message(ctx.message.reference.message_id)
                if message.embeds and message.embeds[0].type == 'image':
                    url = message.embeds[0].thumbnail.proxy_url
                    url = url.replace(
                        'cdn.discordapp.com', 'media.discordapp.net'
                    )
                    return url
                elif (
                    message.attachments
                    and message.attachments[0].width
                    and message.attachments[0].height
                ):
                    url = message.attachments[0].proxy_url
                    url = url.replace(
                        'cdn.discordapp.com', 'media.discordapp.net'
                    )
                    return url

        if (
            ctx.message.attachments
            and ctx.message.attachments[0].width
            and ctx.message.attachments[0].height
        ):
            return ctx.message.attachments[0].proxy_url.replace(
                'cdn.discordapp.com', 'media.discordapp.net'
            )

        if thing is None:
            url = str(ctx.author.avatar_url_as(format='png'))
        elif isinstance(thing, (discord.PartialEmoji, discord.Emoji)):
            url = str(thing.url)
        elif isinstance(thing, (discord.Member, discord.User)):
            url = str(thing.avatar_url_as(format='png'))
        else:
            thing = str(thing).strip('<>')
            if (
                thing.startswith('http')
                or thing.startswith('https')
                or thing.startswith('www')
            ):
                url = thing
            else:
                url = await emoji_to_url(thing)
        async with self.bot.session.get(url) as resp:
            if resp.status != 200:
                raise commands.CommandError('Invalid Picture')
        url = url.replace('cdn.discordapp.com', 'media.discordapp.net')
        return url

    @commands.command()
    async def pixel(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
            img = await dagpi.image_process(ImageFeatures.pixel(), url)
            file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
            await ctx.send(file=file)

    @commands.command()
    async def deepfry(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.deepfry(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def ascii(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.ascii(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def colors(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.colors(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def america(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.america(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def communism(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.communism(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def triggered(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.triggered(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def wasted(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.wasted(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def invert(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.invert(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def blur(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.blur(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def sobel(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.sobel(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def rgb(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.rgb(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def hog(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.hog(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def triangle(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
            url = url.replace('cdn.discordapp.com', 'media.discordapp.net')
        img = await dagpi.image_process(ImageFeatures.triangle(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command(aliases=['5g1g'])
    async def _5g1g(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ],
        thing2: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
            url2 = await self.get_url(ctx, thing2)
        img = await dagpi.image_process(
            ImageFeatures.five_guys_one_girl(), url=url, url2=url2
        )
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command(aliases=['gay'])
    async def why_are_u_gay(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ],
        thing2: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
            url2 = await self.get_url(ctx, thing2)
        img = await dagpi.image_process(
            ImageFeatures.why_are_you_gay(), url=url, url2=url2
        )
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def angel(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.angel(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def satan(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.satan(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def hitler(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.hitler(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def obama(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.obama(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def bad(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.bad(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def sith(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.sith(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def jail(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        img = await dagpi.image_process(ImageFeatures.jail(), url)
        file = discord.File(fp=img.image, filename=f'pixel.{img.format}')
        await ctx.send(file=file)

    @commands.command()
    async def magic(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.channel.typing():
            url = await self.get_url(ctx, thing)
        image = await client.magic(url)
        file = discord.File(image, 'magic.gif')
        await ctx.send(file=file)

    @commands.command()
    async def caption(
        self,
        ctx,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        async with ctx.typing():
            ur = await self.get_url(ctx, thing)
        data = {
            'Content': ur,
            'Type': 'CaptionRequest',
        }
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        url = 'https://captionbot.azurewebsites.net/api/messages'
        r = await self.bot.session.post(
            url, data=json.dumps(data), headers=headers
        )
        t = await r.text()
        embed = discord.Embed(title=t)
        embed.set_image(url=ur)
        await ctx.send(embed=embed)

    @commands.command()
    async def funispin(
        self,
        ctx,
        *,
        thing: typing.Union[
            discord.Member, discord.PartialEmoji, discord.Emoji, str
        ] = None,
    ):
        url = await self.get_url(ctx, thing)
        byte = await self.bot.session.get(url)
        byte = await byte.read()
        im = Image.open(io.BytesIO(byte))
        im.convert('RGBA')
        frames = []
        im.resize((256, 256))
        for i in range(0, 2073600, 6):
            im = im.rotate(i)
            frames.append(im.convert('RGBA'))
        frames += reversed(frames)
        thingy = io.BytesIO()
        frames[0].save(
            thingy,
            format='gif',
            save_all=True,
            append_images=frames[1:],
            duration=1,
            loop=0,
        )
        thingy.seek(0)
        await ctx.send(file=discord.File(thingy, 'thing.gif'))


def setup(bot):
    bot.add_cog(Images(bot))
