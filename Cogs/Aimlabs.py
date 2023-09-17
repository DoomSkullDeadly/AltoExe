import discord
from discord.ext import commands


class AimLabs(commands.Cog, name="submit"):
    def __init__(self, client: discord.Client):
        pass


async def setup(client: discord.Client):
    await client.add_cog(AimLabs(client))
