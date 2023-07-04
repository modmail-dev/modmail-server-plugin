from __future__ import annotations

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel, getLogger

logger = getLogger(__name__)


class ChannelRename(commands.Cog):
    """Simple Plugin with one command—rename a thread channel."""

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


async def setup(bot):
    await bot.add_cog(ChannelRename())
