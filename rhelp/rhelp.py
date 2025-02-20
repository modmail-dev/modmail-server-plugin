from typing import Union, Optional, Any

import discord
from discord.ext import commands

from core import checks
from cogs.utility import PermissionLevel, UnseenFormatter

from bot import ModmailBot


class Rhelp(commands.Cog):

    """Plugin to send command or config help dialogs to a thread recipient.
    
    Created by Martin B <@618805150756110336>"""

    def __init__(self, bot: ModmailBot):
        self.bot = bot

    async def get_help_embed(
        self, command: Union[commands.Command, commands.Group], ctx
    ) -> Optional[discord.Embed]:
        """
        Gets the help embed from the Modmail Help Command.

        """
        help_command = self.bot.help_command

        help_command.context = ctx
        help_command.context.bot = self.bot
        verified_checks_previous = help_command.verify_checks
        help_command.verify_checks = False

        result = await help_command._get_help_embed(command)

        if not result:
            return None

        embed, perm_level = result

        if isinstance(command, commands.Group):
            embed.add_field(name="Permission Level", value=perm_level, inline=False)
            format_ = ""
            length = len(command.commands)

            for i, command in enumerate(
                await help_command.filter_commands(command.commands, sort=True, key=lambda c: c.name)
            ):
                if length == i + 1:  # last
                    branch = "└─"
                else:
                    branch = "├─"
                format_ += f"`{branch} {command.name}` - {command.short_doc}\n"

            embed.add_field(name="Sub Command(s)", value=format_[:1024], inline=False)
            embed.set_footer(
                text=f'Type "{ctx.clean_prefix}{help_command.command_attrs["name"]} command" '
                "for more info on a command."
            )
        elif isinstance(command, commands.Command):
            embed.set_footer(text=f"Permission level: {perm_level}")

        help_command.verify_checks = verified_checks_previous
        return embed

    async def get_config_embed(self, command) -> Optional[discord.Embed]:
        splitted_cmd = command.split("config_")[1]
        config_help = self.bot.config.config_help
        embed = None

        def fmt(val):
            return UnseenFormatter().format(val, prefix=self.bot.prefix, bot=self.bot)

        if (
            not (
                splitted_cmd in self.bot.config.public_keys or splitted_cmd in self.bot.config.protected_keys
            )
            or splitted_cmd not in config_help
        ):
            return None

        for i, (current_key, info) in enumerate(config_help.items()):
            if current_key == splitted_cmd:
                config_embed = discord.Embed(title=f"{current_key}", color=self.bot.main_color)
                config_embed.add_field(name="Default:", value=fmt(info["default"]), inline=False)
                config_embed.add_field(name="Information:", value=fmt(info["description"]), inline=False)
                if info["examples"]:
                    example_text = ""
                    for example in info["examples"]:
                        example_text += f"- {fmt(example)}\n"
                    config_embed.add_field(name="Example(s):", value=example_text, inline=False)

                note_text = ""
                for note in info.get("notes", []):
                    note_text += f"- {fmt(note)}\n"
                if note_text:
                    config_embed.add_field(name="Note(s):", value=note_text, inline=False)

                if info.get("image") is not None:
                    config_embed.set_image(url=fmt(info["image"]))

                if info.get("thumbnail") is not None:
                    config_embed.set_thumbnail(url=fmt(info["thumbnail"]))

                embed = config_embed
                break
        return embed

    @commands.command(name="rhelp")
    @checks.thread_only()
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def rhelp(self, ctx: commands.Context, *, command: str):
        """
        ``DE:`` Sendet die Hilfe für einen bestimmten Befehl an den Nutzer im aktuellen Thread.
        ``EN:`` Sends help for a specific command to the user in the current thread.
        """
        command = command.lower()
        embed = None
        is_configuration = False

        if not command.startswith("config_"):
            bot_command = self.bot.get_command(command)
            if not bot_command or (bot_command and isinstance(bot_command, commands.Cog)):
                return await ctx.send(f"Bot Command `{command}` not found.")

            help_embed = await self.get_help_embed(bot_command, ctx)
            if help_embed is None:
                return await ctx.send(
                    f"Something went wrong while generating the help embed for the command `{command}`."
                )
            help_embed.set_author(name="Command Help")
            embed = help_embed
        else:
            is_configuration = True
            config_embed = await self.get_config_embed(command)
            if not config_embed:
                return await ctx.send(
                    f"Configuration key `{command.split('config_')[1]}` not found or failed to create the embed."
                )
            config_embed.set_author(name="Configuration Option Help")
            embed = config_embed

        if embed:
            help_type = "configuration option help" if is_configuration else "command help"
            target_command = command.split("config_")[1] if is_configuration else command

            try:
                ctx.message.content = (
                    f"Please read below, there you will find the {help_type} for `{target_command}`:"
                )
                await ctx.thread.reply(ctx.message)
                await ctx.thread.recipient.send(embed=embed)
                await ctx.send(
                    f"{help_type.capitalize()} for `{target_command}` sent to the user.",
                    delete_after=10,
                )
                if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                    await ctx.message.delete(delay=15)
            except Exception:
                await ctx.send(f"Something failed during sending the {help_type} anonymously to the user.")

    @commands.command(name="arhelp")
    @checks.thread_only()
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def arhelp(self, ctx: commands.Context, *, command: str):
        """
        ``DE:`` Sendet die Hilfe für einen bestimmten Befehl an den Nutzer im aktuellen Thread.
        ``EN:`` Sends help for a specific command to the user in the current thread.
        """
        command = command.lower()
        embed = None
        is_configuration = False

        if not command.startswith("config_"):
            bot_command = self.bot.get_command(command)
            if not bot_command or (bot_command and isinstance(bot_command, commands.Cog)):
                return await ctx.send(f"Bot Command `{command}` not found.")
            help_embed = await self.get_help_embed(bot_command, ctx)
            if help_embed is None:
                return await ctx.send(
                    f"Something went wrong while generating the help embed for the command `{command}`."
                )
            help_embed.set_author(name="Command Help")
            embed = help_embed
        else:
            is_configuration = True
            config_embed = await self.get_config_embed(command)
            if not config_embed:
                return await ctx.send(f"Configuration key `{command.split('config_')[1]}` not found.")
            config_embed.set_author(name="Configuration Option Help")
            embed = config_embed

        if embed:
            help_type = "configuration option help" if is_configuration else "command help"
            target_command = command.split("config_")[1] if is_configuration else command

            try:
                ctx.message.content = (
                    f"Please read below, there you will find the {help_type} for `{target_command}`:"
                )
                await ctx.thread.reply(ctx.message, anonymous=True)
                await ctx.thread.recipient.send(embed=embed)
                await ctx.send(
                    f"{help_type.capitalize()} for `{target_command}` sent anonymously to the user.",
                    delete_after=10,
                )
                if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                    await ctx.message.delete(delay=15)
            except Exception:
                await ctx.send(f"Something failed during sending the {help_type} anonymously to the user.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Rhelp(bot))
