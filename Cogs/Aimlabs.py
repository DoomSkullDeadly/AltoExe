import discord
from discord.ext import commands
from discord import app_commands
import logging
import json


class AimLabs(commands.Cog, name="submit"):
    def __init__(self, client: discord.Client):
        self.client = client
        self.pagination = self.client.get_cog("EmbedPaginator")
        self.logger = logging.getLogger('lavalink')
        self.submission_channel = None
        self.verification_channel = None
        self.leaderboard_message = None
        self.data = json.load(open("Aimlabs/data.json"))
        self.temp_data = {}

    @app_commands.guild_only()
    @app_commands.command(description="pls work")
    async def channels(self, interaction: discord.Interaction):
        self.submission_channel = self.client.get_channel(1153051949588041870)
        if self.submission_channel is None:
            print("fuck pt.1")
        self.verification_channel = self.client.get_channel(1153055395259101194)
        if self.verification_channel is None:
            print("fuck pt.2")
        await interaction.response.send_message("did it work?", ephemeral=True)

    @app_commands.guild_only()
    @app_commands.command(description="Create leaderboard")
    async def create_leaderboard(self, interaction: discord.Interaction, message_id: str = None):
        if message_id is not None:
            message_id = int(message_id)
            self.leaderboard_message = await self.submission_channel.fetch_message(message_id)
            await interaction.response.send_message("Set to leaderboard", ephemeral=True)
        else:
            self.leaderboard_message = await self.submission_channel.send("#__**Leaderboard**__#")
            await interaction.response.send_message("Created leaderboard", ephemeral=True)

    async def update_leaderboard(self):
        self.data = {k: v for k, v in sorted(self.data.items(), key=lambda item: item[1]["score"], reverse=True)}
        users = [self.client.get_user(int(user)).mention for user in self.data]
        scores = [self.data[user]["score"] for user in self.data]
        content = "#__**Leaderboard**__#\n{}".format('\n'.join('{} - {}'.format(*t) for t in zip(users, scores)))
        print(content)
        await self.leaderboard_message.edit(content=content)

    @app_commands.guild_only()
    @app_commands.command(description="Finds your place on the leaderboard!")
    async def find_me(self, interaction: discord.Interaction):
        if str(interaction.user.id) in self.data:
            self.data = {k: v for k, v in sorted(self.data.items(), key=lambda item: item[1]["score"], reverse=True)}
            counter = 0
            for i in self.data:
                counter += 1
                if str(interaction.user.id) == i:
                    await interaction.response.send_message(f"You are currently ***#{counter}*** on the leaderboard!", ephemeral=True)
                    break
        else:
            await interaction.response.send_message("You do not have a valid score submitted!", ephemeral=True)

    @app_commands.guild_only()
    @app_commands.command(description="Submit your score!")
    async def submit(self, interaction: discord.Interaction, score: int, image: discord.Attachment):
        if str(interaction.user.id) in self.data:
            if self.data[str(interaction.user.id)]["score"] > score:
                await interaction.response.send_message(f"Your already have a higher score!", ephemeral=True)
                return
        attachment = image
        filename = f"{interaction.user.id}-{attachment.id}-{attachment.filename}"
        await attachment.save(f"Aimlabs/{filename}")
        self.temp_data[str(interaction.user.id)] = {"score": score, "proof": filename, "verifier": None, "status": "pending"}
        await interaction.response.send_message(f"Successfully submitted score!", ephemeral=True)
        await self.send_to_verify(interaction, score, attachment)

    async def send_to_verify(self, interaction: discord.Interaction, score: str, attachment: discord.Attachment):
        user = interaction.user
        uuid = str(user.id)
        content = f"{user.mention} submitted a score of {score}"
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
                self.temp_data[uuid]["status"] = "rejected"
                self.temp_data[uuid]["verifier"] = Reaction.user_id
                await message.delete()
                await interaction.edit_original_response(content=f"Your score of {score} has been rejected!")
                return
            elif str(Reaction.emoji) == "✅":
                self.temp_data[uuid]["status"] = "accepted"
                self.temp_data[uuid]["verifier"] = Reaction.user_id
                if uuid in self.data:
                    if self.data[uuid]["score"] < self.temp_data[uuid]["score"]:
                        self.data[uuid] = self.temp_data[uuid]
                else:
                    self.data[uuid] = self.temp_data[uuid]
                with open("Aimlabs/data.json", "w") as f:
                    f.write(json.dumps(self.data, indent=4))
                await message.delete()
                await interaction.edit_original_response(content=f"Your score of {score} has been accepted!")
                break

        await self.update_leaderboard()


async def setup(client: discord.Client):
    await client.add_cog(AimLabs(client))
