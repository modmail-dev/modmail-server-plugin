from __future__ import annotations

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel, getLogger

logger = getLogger(__name__)


class LeaveServer(commands.Cog):
    """A plugin that makes the bot leave a server."""


    @commands.command()
    @checks.has_permissions(PermissionLevel.OWNER)
    async def findallservers(self, ctx):
        """
        This command shows you all the servers and their IDs that your bot is in.
        """
        await ctx.reply(discord.utils.escape_markdown(discord.utils.escape_mentions(
            "\n".join([f"{i}. {s} ({s.id})" for i, s in enumerate(ctx.bot.guilds, start=1)])
        )))

    @commands.command()
    @checks.has_permissions(PermissionLevel.OWNER)
    async def leaveserver(self, ctx, *, guild: discord.Guild):
        """
        Leaves the specified server. Use `{prefix}findallservers` to find all the servers your bot is in.
        """
        name = discord.utils.escape_markdown(discord.utils.escape_mentions(str(guild)))
        try:
            await guild.leave()
        except Exception:
            await ctx.reply(f"Failed to leave {name}.")
        else:
            await ctx.reply(f"Successfully left {name}.")


async def setup(bot):
    await bot.add_cog(LeaveServer())
