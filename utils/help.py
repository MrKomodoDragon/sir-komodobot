import discord
from discord.ext import commands
import itertools
from discord.ext import menus

# Copyright © 2021 MrKomodoDragon
#
# this help command is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# this file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this help command. If not, see <https://www.gnu.org/licenses/>.


class MyNewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command))
        can_run = await command.can_run(self.context)
        if can_run is True:
            embed.add_field(
                name='Can Run?', value='<:greenTick:596576670815879169>'
            )
        elif can_run is False:
            embed.add_field(
                name='Can Run?', value='<:redTick:596576672149667840>'
            )
        embed.add_field(
            name='Help',
            value=command.help or command.description or 'No help found',
        )
        alias = command.aliases
        if alias:
            embed.add_field(
                name='Aliases', value=', '.join(alias), inline=False
            )

        channel = self.get_destination()
        await channel.send(embed=embed)

    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            joined = '`,\u2002`'.join(c.name for c in commands)
            emoji_dict = {
                'economy': '💵',
                'fun': '<:rooDuck:739614767941156874>',
                'images': '📸',
                'utility': '⚙️',
                'music': '🎵',
                'jishaku': '<:verycool:739613733474795520>',
                'socket': '🔌',
                '\u200bNo Category': '<:rooSob:744345453923139714>',
                '\u200bno category': '<:rooSob:744345453923139714>',
            }
            emoji = emoji_dict[heading.lower()]
            self.paginator.add_line(f'{emoji if emoji else ""}  **{heading}**')

            self.paginator.add_line(f'> `{joined}`')

    def get_ending_note(self):
        command_name = self.invoked_with
        return (
            'Type `{0}{1}` `[command]` for more info on a command.\n'
            'You can also type `{0}{1}` `[category]` for more info on a category.'.format(
                self.clean_prefix, command_name
            )
        )

    def get_opening_note(self):
        return '`<arg>` means the argument is required\n`[arg]` means it is optional'

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        self.paginator.add_line(
            'Useful Links: [Invite Link](https://mrkomododragon.github.io/sir-komodobot/invite) | [Support Server](https://mrkomododragon.github.io/sir-komodobot/support)| [Source](https://github.com/MrKomodoDragon/sir-komodobot) | [Website](https://mrkomododragon.github.io/sir-komodobot)'
        )

        def get_category(command, *, no_category='\u200bNo Category'):
            cog = command.cog
            return cog.qualified_name if cog is not None else no_category

        filtered = await self.filter_commands(
            bot.commands, sort=True, key=get_category
        )
        to_iterate = itertools.groupby(filtered, key=get_category)

        for category, actual_commands in to_iterate:
            self.add_bot_commands_formatting(list(actual_commands), category)

        self.paginator.add_line(self.get_ending_note())

        await self.send_pages()

    def add_subcommand_formatting(self, command):
        fmt = (
            '`{0}` \N{EN DASH} {1}'
            if command.description or command.help
            else '`{0}` \N{EN DASH} {1} This command is not documented'
        )
        self.paginator.add_line(
            fmt.format(
                self.get_command_signature(command),
                command.description or command.help,
            )
        )

    async def send_cog_help(self, cog):
        bot = self.context.bot
        if bot.description:
            self.paginator.add_line(bot.description)

        note = self.get_opening_note()
        if note:
            self.paginator.add_line(note, empty=True)

        filtered = await self.filter_commands(cog.get_commands(), sort=False)
        if filtered:
            self.paginator.add_line(
                '**%s %s**' % (cog.qualified_name, self.commands_heading)
            )
            if cog.description:
                self.paginator.add_line(cog.description, empty=True)
            for command in filtered:
                self.add_subcommand_formatting(command)

        await self.send_pages()
