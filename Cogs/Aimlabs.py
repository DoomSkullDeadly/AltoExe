import discord
from discord.ext import commands
from discord import app_commands
import logging


class AimLabs(commands.Cog, name="submit"):
    def __init__(self, client: discord.Client):
        self.client = client
        self.pagination = self.client.get_cog("EmbedPaginator")
        self.logger = logging.getLogger('lavalink')
        self.submission_channel = None
        self.verification_channel = None

    @app_commands.guild_only()
    @app_commands.command(description="pls work")
    async def channels(self, interaction: discord.Interaction, input: str):
        self.submission_channel = self.client.get_channel(1153051949588041870)
        if self.submission_channel is None:
            print("fuck pt.1")
        self.verification_channel = self.client.get_channel(1153055395259101194)
        if self.verification_channel is None:
            print("fuck pt.2")
        await interaction.response.send_message(f"did it work? {input}")

    @app_commands.guild_only()
    @app_commands.command(description="Submit your score!")
    async def submit(self, interaction: discord.Interaction, score: str, image: discord.Attachment):
        attachment = image
        await attachment.save(f"Aimlabs/{interaction.user.id}-{attachment.id}-{attachment.filename}")
        await interaction.response.send_message(f"Successfully submitted score!")
        await self.send_to_verify(interaction.user, score, attachment)

    async def send_to_verify(self, user: discord.User, score: str, attachment: discord.Attachment):
        content = f"@{user.id} submitted a score of {score}"
        file = await attachment.to_file()
        message = await self.verification_channel.send(content=content, file=file)
        await message.add_reaction("✅")
        await message.add_reaction("❌")


async def setup(client: discord.Client):
    await client.add_cog(AimLabs(client))
