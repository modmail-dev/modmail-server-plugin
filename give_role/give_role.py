from __future__ import annotations

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel, getLogger
from core.utils import human_join

logger = getLogger(__name__)


class GiveRole(commands.Cog):
    """A plugin that gives the thread recipient a role."""

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @checks.thread_only()
    async def giverole(self, ctx, *, role: discord.Role):
        """
        Gives the thread recipient a role. DANGEROUS COMMAND: see description.

        This command is dangerous because it does not check for permissions.
        Anyone who can use this command can give themselves, or anyone else, any role.
        """
        recipients = ctx.thread.recipients
        try:
            for recipient in recipients:
                await ctx.guild.get_member(recipient.id).\
                    add_roles(role, reason=f"Role given by {ctx.author} in Modmail thread.")
        except Exception as e:
            await ctx.send(f"Error giving role: {e}")
            return
        await ctx.send(f"{role.mention} given to {human_join([r.mention for r in recipients])}.",
                       allowed_mentions=discord.AllowedMentions(roles=False, users=False))


async def setup(bot):
    await bot.add_cog(GiveRole())
