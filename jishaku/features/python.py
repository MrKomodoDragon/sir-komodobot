# -*- coding: utf-8 -*-

"""
jishaku.features.python
~~~~~~~~~~~~~~~~~~~~~~~~

The jishaku Python evaluation/execution commands.

:copyright: (c) 2021 Devon (Gorialis) R
:license: MIT, see LICENSE for more details.

"""

import discord
from discord.ext import commands

from jishaku.codeblocks import codeblock_converter
from jishaku.exception_handling import ReplResponseReactor
from jishaku.features.baseclass import Feature
from jishaku.flags import JISHAKU_RETAIN, SCOPE_PREFIX
from jishaku.functools import AsyncSender
from jishaku.paginators import PaginatorInterface, WrappedPaginator
from jishaku.repl import (
    AsyncCodeExecutor,
    Scope,
    all_inspections,
    disassemble,
    get_var_dict_from_ctx,
)


class PythonFeature(Feature):
    """
    Feature containing the Python-related commands
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scope = Scope()
        self.retain = JISHAKU_RETAIN
        self.last_result = None

    @property
    def scope(self):
        """
        Gets a scope for use in REPL.

        If retention is on, this is the internal stored scope,
        otherwise it is always a new Scope.
        """

        if self.retain:
            return self._scope
        return Scope()

    @Feature.Command(parent='jsk', name='retain')
    async def jsk_retain(self, ctx: commands.Context, *, toggle: bool = None):
        """
        Turn variable retention for REPL on or off.

        Provide no argument for current status.
        """

        if toggle is None:
            if self.retain:
                return await ctx.send('Variable retention is set to ON.')

            return await ctx.send('Variable retention is set to OFF.')

        if toggle:
            if self.retain:
                return await ctx.send(
                    'Variable retention is already set to ON.'
                )

            self.retain = True
            self._scope = Scope()
            return await ctx.send(
                'Variable retention is ON. Future REPL sessions will retain their scope.'
            )

        if not self.retain:
            return await ctx.send('Variable retention is already set to OFF.')

        self.retain = False
        return await ctx.send(
            'Variable retention is OFF. Future REPL sessions will dispose their scope when done.'
        )

    @Feature.Command(parent='jsk', name='py', aliases=['python'])
    async def jsk_python(
        self, ctx: commands.Context, *, argument: codeblock_converter
    ):
        """
        Direct evaluation of Python code.
        """

        arg_dict = get_var_dict_from_ctx(ctx, SCOPE_PREFIX)
        arg_dict['_'] = self.last_result

        scope = self.scope

        try:
            async with ReplResponseReactor(ctx.message):
                with self.submit(ctx):
                    executor = AsyncCodeExecutor(
                        argument.content, scope, arg_dict=arg_dict
                    )
                    async for send, result in AsyncSender(executor):
                        if result is None:
                            continue

                        self.last_result = result

                        if isinstance(result, discord.File):
                            send(await ctx.send(file=result))
                        elif isinstance(result, discord.Embed):
                            send(await ctx.send(embed=result))
                        elif isinstance(result, PaginatorInterface):
                            send(await result.send_to(ctx))
                        else:
                            if not isinstance(result, str):
                                # repr all non-strings
                                result = repr(result)

                            if len(result) > 2000:
                                # inconsistency here, results get wrapped in codeblocks when they are too large
                                #  but don't if they're not. probably not that bad, but noting for later review
                                paginator = WrappedPaginator(
                                    prefix='```py', suffix='```', max_size=1985
                                )

                                paginator.add_line(result)

                                interface = PaginatorInterface(
                                    ctx.bot, paginator, owner=ctx.author
                                )
                                send(await interface.send_to(ctx))
                            else:
                                if result.strip() == '':
                                    result = '\u200b'

                                send(
                                    await ctx.send(
                                        result.replace(
                                            self.bot.http.token,
                                            '[token omitted]',
                                        )
                                    )
                                )
        finally:
            scope.clear_intersection(arg_dict)

    @Feature.Command(
        parent='jsk',
        name='py_inspect',
        aliases=['pyi', 'python_inspect', 'pythoninspect'],
    )
    async def jsk_python_inspect(
        self, ctx: commands.Context, *, argument: codeblock_converter
    ):
        """
        Evaluation of Python code with inspect information.
        """

        arg_dict = get_var_dict_from_ctx(ctx, SCOPE_PREFIX)
        arg_dict['_'] = self.last_result

        scope = self.scope

        try:
            async with ReplResponseReactor(ctx.message):
                with self.submit(ctx):
                    executor = AsyncCodeExecutor(
                        argument.content, scope, arg_dict=arg_dict
                    )
                    async for send, result in AsyncSender(executor):
                        self.last_result = result

                        header = (
                            repr(result)
                            .replace('``', '`\u200b`')
                            .replace(self.bot.http.token, '[token omitted]')
                        )

                        if len(header) > 485:
                            header = header[0:482] + '...'

                        paginator = WrappedPaginator(
                            prefix=f'```prolog\n=== {header} ===\n',
                            max_size=1985,
                        )

                        for name, res in all_inspections(result):
                            paginator.add_line(f'{name:16.16} :: {res}')

                        interface = PaginatorInterface(
                            ctx.bot, paginator, owner=ctx.author
                        )
                        send(await interface.send_to(ctx))
        finally:
            scope.clear_intersection(arg_dict)

    @Feature.Command(parent='jsk', name='dis', aliases=['disassemble'])
    async def jsk_disassemble(
        self, ctx: commands.Context, *, argument: codeblock_converter
    ):
        """
        Disassemble Python code into bytecode.
        """

        arg_dict = get_var_dict_from_ctx(ctx, SCOPE_PREFIX)

        async with ReplResponseReactor(ctx.message):
            paginator = WrappedPaginator(
                prefix='```py', suffix='```', max_size=1985
            )

            for line in disassemble(argument.content, arg_dict=arg_dict):
                paginator.add_line(line)

            interface = PaginatorInterface(
                ctx.bot, paginator, owner=ctx.author
            )
            await interface.send_to(ctx)
