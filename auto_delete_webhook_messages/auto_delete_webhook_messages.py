"""
Automatically delete the annoying [modmail] None on development, etc. messages in #github.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import discord
    from discord.ext.commands import Bot


CHANNEL_ID = 515072282906066945
WEBHOOK_ID = 515468206224441364


async def on_message(message: discord.Message):
    if message.channel.id != CHANNEL_ID or message.webhook_id != WEBHOOK_ID:
        return
    if message.embeds and message.embeds[0].title:
        title = message.embeds[0].title
        if title.startswith("[modmail] None on") or (('[modmail] Python' in title or
                                                      '[modmail] GitHub Actions checks' in title)
                                                     and 'success on' in title):
            await message.delete()


async def setup(bot: Bot):
    bot.add_listener(on_message)


async def teardown(bot):
    bot.remove_listener(on_message)
