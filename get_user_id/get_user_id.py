from __future__ import annotations

from discord.ext import commands

from core import checks
from core.models import PermissionLevel, getLogger

logger = getLogger(__name__)


class GetUserID(commands.Cog):
    """Simple Plugin with one command—get the user ID of the thread."""

    @commands.command()
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    @checks.thread_only()
    async def userid(self, ctx):
        """
        Get the user ID of the thread's recipient.
        """
        recipients = ctx.thread.recipients
        text = ""
        for recipient in recipients:
            text += f"{recipient.id} ({recipient.mention})\n"
        await ctx.send(text.strip())


async def setup(bot):
    await bot.add_cog(GetUserID())
