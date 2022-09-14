
#!-------------------------IMPORT MODULES--------------------#


import json
import discord
import logging
import importlib
import asyncio
from datetime import datetime
from discord.ext import commands


#!-------------------------------IMPORT CLASSES--------------------------------#


import Classes.Users
import Classes.Utils
import Classes.Database
import Classes.MusicUtils


#!------------------------ADMIN COG-----------------------#


class AdminCog(commands.Cog, name="Admin"):

    def __init__(self, client: discord.Client):

        #** Assign Discord Bot Client As Class Object **
        self.client = client
        self.logger = logging.getLogger()
        
        #** Instanciate Classes If One Or More Attributes Missing **
        if not hasattr(client, 'database') or not hasattr(client, 'music') or not hasattr(client, 'utils') or not hasattr(client, 'userClass'):
            try:
                client.database = Classes.Database.UserData()
            except:
                self.logger.warning("Database Functionality Unavailable!")
            client.music = Classes.MusicUtils.SongData()
            client.utils = Classes.Utils.Utility(client)
            client.userClass = Classes.Users

    
    #{ Check Function To See If User ID Is Bot Admin }
    def is_admin():
    
        #** When Called, Check If User Id In List & If So Return True **
        async def predicate(ctx):
            if ctx.author.id in [315237737538125836, 233641884801695744]:
                return True
            return False
        return commands.check(predicate)
    
    
    @commands.command(hidden=True)
    @is_admin()
    async def reload(self, ctx, input):
        
        #** If Passed Name Is A Class, Use Importlib To Reload File **
        if input.lower() in ['musicutils', 'database', 'users', 'utils']:      
            try:   
                #** Re-add Attribute To Client Class **
                if input.lower() == "database":
                    importlib.reload(Classes.Database)
                    self.client.database = Classes.Database.UserData()
                elif input.lower() == "music":
                    importlib.reload(Classes.MusicUtils)
                    self.client.music = Classes.MusicUtils.SongData()
                elif input.lower() == "utils":
                    importlib.reload(Classes.Utils)
                    self.client.utils = Classes.Utils.Utility(self.client)
                else:
                    importlib.reload(Classes.Users)
                    self.client.userClass = Classes.Users

            except Exception as e:
                #** Return Error To User **
                await ctx.send(f"**An Error Occured Whilst Trying To Reload The {input.title()} Class!**\n```{e}```")
                return
        
        #** If Input Is 'Config', reload Config File **
        elif input.lower() == "config":  
            try:
                #** ReLoad Config File **
                with open('Config.json') as ConfigFile:
                    self.client.config = json.load(ConfigFile)
                    self.logger.info("Loaded Config File")
                    ConfigFile.close()

            except Exception as e:
                #** Return Error To User **
                await ctx.send(f"**An Error Occured Whilst Trying To Reload The Config File!**\n```{e}```")
                return
            
        #** If Input Not Config Or Class, Try To Reload Cog Under Name **
        else:
            
            try:
                #** ReLoad Specified Cog **
                await self.client.reload_extension("Cogs."+input.title())
                self.client.logger.info(f"Extension Loaded: Cogs.{input.title()}")

            except Exception as e:
                #** Return Error To User **
                await ctx.send(f"**An Error Occured Whilst Trying To Reload {input.title()} Cog!**\n```{e}```")
                return
            
        #** Send Confirmation Message **
        await ctx.send(f"**Sucessfully Reloaded:** `{input.title()}`!")
    

    @commands.command(hidden=True)
    @is_admin()
    async def sync(self, ctx, *args):
        
        #** If Input is Blank, Sync Application Commands To Current Guild **
        if not(args):
            args = ["Current Server"]
            self.client.tree.copy_global_to(guild=ctx.guild)
        
        #** If Input = Global, Send Warning Message **
        elif args[0].lower() == "global":
            warning = await ctx.send("**Warning! Syncing Globally Will Make The Changes Available To __All Servers__!**\n*Are You Sure You Want To Continue?*")
            
            #** Add Reactions **
            await warning.add_reaction("✅")
            await warning.add_reaction("❌")
            
            def ReactionAdd(Reaction):
                return (Reaction.message_id == warning.id) and (Reaction.user_id != self.client.user.id)

            #** Wait For User To React To Tick & Stop Function Execution When Reacting With No **
            while True:
                Reaction = await self.client.wait_for("raw_reaction_add", check=ReactionAdd)
                if Reaction.event_type == 'REACTION_ADD':
                    if str(Reaction.emoji) == "❌":
                        await warning.delete()
                        temp = await ctx.send("Cancelled Command Sync Operation!")
                        await asyncio.sleep(10)
                        await ctx.message.delete()
                        await temp.delete()
                        return
                    elif str(Reaction.emoji) == "✅":
                        await warning.delete()
                        break
        
        #** If Input is Integer, Check If Guild ID, & Sync To That Guild
        elif args[0].isdecimal():
            guild = self.client.get_guild(int(args[0]))
            if guild is None:
                raise commands.BadArgument()
            self.client.tree.copy_global_to(guild=guild)
        
        #** If Invalid Argument Supplied, Raise Error
        else:
            raise commands.BadArgument()
        
        #** Carry Out Sync **
        await self.client.tree.sync()
            
        #** Send Confirmation Message If Sucessfull **
        self.client.logger.info(f'Synced Application Commands. Scope: "{args[0]}"')
        temp = await ctx.send(f"Sucessfully Synced Application Commands!\nScope: `{args[0]}`")
        
        
    @commands.command(hidden=True)
    @is_admin()
    async def debug(self, ctx, option):
        
        #** Format Original Embed **
        embed = discord.Embed(
            title=f"Debug Information For `{option.title()}`",
            colour=discord.Colour.blue()
        )
        
        #** If Option Is 'Server', Format Embed Description With Server Info **
        if option.lower() == "server":
            
            print("Server")
        
        #** If Option Is 'Lavalink', Format Embed Description With Current Lavalink Node Info **
        elif option.lower() == "lavalink":
            
            #** Check If Client Has 
            if hasattr(self.client, 'lavalink'):
                
                #** Start Description Embed & Locate Default Node From Lavalink Node Manager **
                description = f"Available Nodes: `{len(self.client.lavalink.node_manager.available_nodes)}`\n\n**Stats For Default-Node:**\n"
                for node in self.client.lavalink.node_manager.nodes:
                    if node.name == "default-node":
                        
                        #** Check If Node Is Available Or Not & Add Stats To Description Before Breaking For Loop **
                        print(node.stats.is_fake)
                        if node.available and not(node.stats.is_fake):
                            description += f"```Total Players: {node.stats.players}\nActive Players: {node.stats.playing_players}```"
                            embed.add_field(name="CPU Usage:", value=f"{round(node.stats.lavalink_load * 100, 2)}%")
                            embed.add_field(name="Memory Usage:", value=f"{round(node.stats.memory_used / 1000000000, 2)}GB")
                            embed.add_field(name="Allocated Memory:", value=f"{round(node.stats.memory_allocated / 1000000000, 2)}GB")
                            embed.add_field(name="Uptime:", value=self.client.utils.format_time(node.stats.uptime))
                            embed.add_field(name="Missing Frames:", value=f"{node.stats.frames_deficit * -1}")
                            embed.add_field(name="Lavalink Penalty:", value=f"{round(node.stats.penalty.total, 2)}")
                            break
                        
                        #** Format Description With Node Offline & Break For Loop
                        else:
                            description += "*Node Unavailable!*"
                            break
                
                #** Set Embed Description To Formatted Embed **
                embed.description = description
                            
            #** Let User Know Lavalink Isn't Connected If Attribute Not Found **
            else:
                embed.description = "Lavalink Not Connected!"
            
        #** If Option Is 'Database', Format Embed Description With Database Connection Info **
        elif option.lower() == "database":
            
            print("database")
            
        #** Send Embed To Discord **
        await ctx.send(embed=embed)
        
    
#!-------------------SETUP FUNCTION-------------------#


async def setup(client: discord.Client):
    await client.add_cog(AdminCog(client))