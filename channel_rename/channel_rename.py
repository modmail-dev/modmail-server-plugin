from __future__ import annotations

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel, getLogger

logger = getLogger(__name__)


class ChannelRename(commands.Cog):
    """Plugin to rename a thread channel."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    @checks.thread_only()
    async def rename(self, ctx, *, name: str):
        """
        Rename the thread channel.
        """
        try:
            await ctx.channel.edit(name=name)
        except discord.Forbidden:
            await ctx.reply("I do not have permission to edit channels.")
        except discord.HTTPException:
            await ctx.reply("Failed to rename the channel, perhaps the name is invalid?")
        else:
            await ctx.reply(f"Channel renamed to `{name}`")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    @checks.thread_only()
    async def resetname(self, ctx):
        """
        Reset the channel name back to the user's username.
        """
        name = self.bot.format_channel_name(ctx.thread.recipient)
        try:
            await ctx.channel.edit(name=name)
        except discord.Forbidden:
            await ctx.reply("I do not have permission to edit channels.")
        except discord.HTTPException as e:
            if "Contains words not allowed" in e.text:
                name = self.bot.format_channel_name(ctx.recipient, force_null=True)
                await ctx.channel.edit(name=name)
            else:
                await ctx.reply("Failed to reset the channel name. Try the rename command instead.")
        else:
            await ctx.reply(f"Channel renamed to `{name}`")


async def setup(bot):
    await bot.add_cog(ChannelRename(bot))
