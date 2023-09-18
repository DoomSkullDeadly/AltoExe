import discord
from discord.ext import commands
from discord import app_commands
import logging
import json


class Verification(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pagination = self.client.get_cog("EmbedPaginator")
        self.logger = logging.getLogger('lavalink')
        self.verification_channel = None
        self.data = json.load(open("verification/data.json"))
        self.member_role = None
        self.guild = None

    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(description="pls work")
    async def channels_ver(self, interaction: discord.Interaction):
        self.verification_channel = self.client.get_channel(1153136423369703484)
        self.guild = self.client.get_guild(159358268693676033)
        self.member_role = self.guild.get_role(579689728023199756)
        if self.verification_channel is None:
            print("fuck")
        await interaction.response.send_message("did it work?", ephemeral=True)

    @app_commands.guild_only()
    @app_commands.command(description="Verify your membership and get the member role!")
    async def verify(self, interaction: discord.Interaction, screenshot: discord.Attachment):
        attachment = screenshot
        filename = f"{interaction.user.id}-{attachment.id}-{attachment.filename}"
        await attachment.save(f"verification/{filename}")
        self.data[str(interaction.user.id)] = {"proof": filename, "verifier": None, "status": "pending"}
        await interaction.response.send_message(f"Successfully submitted for verification!", ephemeral=True)
        await self.send_to_verify_ver(interaction, attachment)

    async def send_to_verify_ver(self, interaction: discord.Interaction, attachment: discord.Attachment):
        user = interaction.user
        uuid = str(user.id)
        content = f"{user.mention} wants to be a member!"
        file = await attachment.to_file()
        message = await self.verification_channel.send(content=content, file=file)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def ReactionAdd(Reaction):
            return (Reaction.message_id == message.id) and (Reaction.user_id != self.client.user.id)

        # ** Wait For User To React To Tick & Stop Function Execution When Reacting With No **
        while True:
            Reaction = await self.client.wait_for("raw_reaction_add", check=ReactionAdd)
            if str(Reaction.emoji) == "❌":
                self.data[uuid]["status"] = "rejected"
                self.data[uuid]["verifier"] = Reaction.user_id
                await message.delete()
                await interaction.edit_original_response(content="Your membership proof has been rejected! Please try again with another screenshot or DM a committee member!")
                return
            elif str(Reaction.emoji) == "✅":
                self.data[uuid]["status"] = "accepted"
                self.data[uuid]["verifier"] = Reaction.user_id
                await self.guild.get_member(int(uuid)).add_roles(self.member_role)
                with open("verification/data.json", "w") as f:
                    f.write(json.dumps(self.data, indent=4))
                await message.delete()
                await interaction.edit_original_response(content=f"Congratulations! You're now a member!")
                break


async def setup(client: discord.Client):
    await client.add_cog(Verification(client))
