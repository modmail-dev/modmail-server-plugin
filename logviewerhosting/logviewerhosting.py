import os

import discord
from discord.ext import commands
from discord.utils import utcnow, format_dt
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError, InvalidURI

from core.utils import getLogger

LOGGER = getLogger(__name__)


class LogviewerHosting(commands.Cog):
    """
    Utilities regarding Lorenzo´s Logviewerhosting
    Current Feature(s):
    - Send info on thread_creation which logviewers are hosted for the user

    Required .env Variables: `LOGVIEWER_MANAGEMENT_URI` (for thread_creation info)
    Optional .env Variables: `LOGVIEWERHOST_DOMAIN`
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_thread_ready(self, thread, creator, category, initial_message):
        logviewer_management_db_uri = os.getenv("LOGVIEWER_MANAGEMENT_URI", None)
        if logviewer_management_db_uri is None:
            LOGGER.warning(
                "Thread creation logviewer info cannot be sent. "
                "LOGVIEWER_MANAGEMENT_URI .env variable missing."
            )
            return

        try:
            management_db_client: AsyncIOMotorClient = AsyncIOMotorClient(
                logviewer_management_db_uri, serverSelectionTimeoutMS=5000
            )

        except Exception as e:
            LOGGER.warning(f"Failed to connection to logviewer management db.\n{e}", exc_info=True)
            return
        database = management_db_client.get_database("logviewer_management")
        if database is None:
            LOGGER.warning(f"Logviewer management db cannot be found.")
            return
        instances_collection = database.get_collection("instances")
        if instances_collection is None:
            LOGGER.warning(f"No instances collection found.")
            return

        all_users_active_instances = await instances_collection.find(
            {"owner": str(thread.recipient.id), "active": True},
            {"mongo_uri": 0},  # Mongo_uri should not be requested and stored in memory
        ).to_list()
        if all_users_active_instances:
            management_db_client.close()
            log_domain = os.getenv("LOGVIEWERHOST_DOMAIN", "logs.vodka")
            user_subdomains = []
            for instance in all_users_active_instances:
                created_at = format_dt(instance["created_at"], "R")
                user_subdomains.append(f"- https://{instance['name']}.{log_domain}/ (created {created_at})")

            fmt = "\n".join(user_subdomains)

            embed = discord.Embed(
                title="📝 Hosted logviewers by @ Lorenzo",
                description=f"This user has currently hosted the following logviewers ({len(all_users_active_instances)}):\n"
                f"{fmt}",
                color=self.bot.main_color,
            )
            await thread.channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(LogviewerHosting(bot))
