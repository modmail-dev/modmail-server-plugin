from typing import Union, Optional, Any

import discord
from discord.ext import commands

from core import checks
from cogs.utility import PermissionLevel, UnseenFormatter

from bot import ModmailBot


class Rhelp(commands.Cog):
    def __init__(self, bot: ModmailBot):
        self.bot = bot

    async def get_help_embed(
        self, command: Union[commands.Command, commands.Group], ctx
    ) -> Optional[discord.Embed]:
        """
        Gets the help embed from the ModMailHelp Command.

        """
        help_command = self.bot.help_command

        help_command.context = ctx
        help_command.context.bot = self.bot

        result = await help_command._get_help_embed(command)

        if not result:
            return None

        embed, perm_level = result

        if isinstance(command, commands.Group):
            embed.add_field(name="Permission Level", value=perm_level, inline=False)
        elif isinstance(command, commands.Command):
            embed.set_footer(text=f"Permission level: {perm_level}")

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
        Sendet die Hilfe für einen bestimmten Befehl an den Nutzer im aktuellen Thread.
        """
        command = command.lower()
        embed = None
        if not command.startswith("config_"):
            bot_command = self.bot.get_command(command)
            if not bot_command:
                return await ctx.send(f"Bot Command `{command}` not found.")
            help_embed = await self.get_help_embed(bot_command, ctx)
            if help_embed is None:
                return await ctx.send(
                    f"Something went wrong while generating the help embed for the command `{command}`."
                )
            help_embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
            embed = help_embed
        else:

            config_embed = await self.get_config_embed(command)
            if not config_embed:
                return await ctx.send(f"Configuration key `{command.split('_config')[1]}` not found.")
            config_embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
            embed = config_embed

        if embed:
            try:
                await ctx.thread.recipient.send(embed=embed)
                await ctx.send(f"Command help for `{command}` sent to the user.")
            except Exception:
                await ctx.send(f"The command help could not get sent to the user.")

    @commands.command(name="arhelp")
    @checks.thread_only()
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def arhelp(self, ctx: commands.Context, *, command: str):
        """
        Sendet die Hilfe für einen bestimmten Befehl an den Nutzer im aktuellen Thread.
        """
        command = command.lower()
        embed = None
        if not command.startswith("config_"):
            bot_command = self.bot.get_command(command)
            if not bot_command:
                return await ctx.send(f"Bot Command `{command}` not found.")
            help_embed = await self.get_help_embed(bot_command, ctx)
            if help_embed is None:
                return await ctx.send(
                    f"Something went wrong while generating the help embed for the command `{command}`."
                )
            help_embed.set_author(
                name="Modmail Support Agent",
                icon_url="https://discordapp.com/assets/f78426a064bc9dd24847519259bc42af.png",
            )
            embed = help_embed
        else:

            config_embed = await self.get_config_embed(command)
            if not config_embed:
                return await ctx.send(f"Configuration key `{command.split('_config')[1]}` not found.")
            config_embed.set_author(
                name="Modmail Support Agent",
                icon_url="https://discordapp.com/assets/f78426a064bc9dd24847519259bc42af.png",
            )
            embed = config_embed

        if embed:
            try:
                await ctx.thread.recipient.send(embed=embed)
                await ctx.send(f"Command help for `{command}` sent to the user.")
            except Exception:
                await ctx.send(f"The command help could not get sent to the user.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Rhelp(bot))
