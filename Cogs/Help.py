
#!-------------------------IMPORT MODULES--------------------#


import math
import json
import copy
import discord
from datetime import datetime
from discord.ext import commands


#!--------------------------------STARTUP-----------------------------------# 


#** Startup Sequence **
print("-----------------------LOADING EXTENTION----------------------")
print("Name: Cogs.Help")
print("Modules Imported: ✓\n")


#!-------------------------HELP COG-----------------------------#


class HelpCog(commands.Cog):

    def __init__(self, client):
        
        #** Assign Class Objects **
        self.client = client
        self.Pagination = self.client.get_cog("EmbedPaginator")
        self.activeCogs = {'Music': 'All music-related commands, including playing music.', 'Account': '', 'Utility': ''}
        
        #** Load Config File **
        with open('Config.json') as ConfigFile:
            Config = json.load(ConfigFile)
            ConfigFile.close()
            
        #** Setup Emojis **
        self.Emojis = Config['Variables']['Emojis']
        
        #** Get List Of Active Commands **
        self.activeCommands = []
        for Command in self.client.walk_commands():
            if not(Command.hidden):
                self.activeCommands.append(Command.name)

    
    @commands.command()
    async def help(self, ctx, *args):
        
        input = " ".join(args)
        
        if input == "":
            
            #** Create Help Embed Showing Command Categories & Basic Info **
            MainMenu = discord.Embed(title = "Alto: Using The Discord Bot",
                              description = "**- !help <catergory>:** *Specifying a catergory shown on this embed will show all "+
                                            "commands within that catergory with a brief description of each.*\n**- !help <command>:"+
                                            "** *For a more detailed description of a command, specify the exact command.*",
                              colour=discord.Colour.blue())
            MainMenu.set_thumbnail(url="https://i.imgur.com/mUNosuh.png")
            
            await ctx.send(embed=MainMenu)
            
        #**--------------COMMAND CATERGORY---------------**#
        
        elif input.title() in list(self.activeCogs.keys()):
            
            #** Get Cog Object **
            Cog = self.client.get_cog(input.title())
            
            #** Create Basic Embed **
            CategoryEmbed = discord.Embed(title = "Catergory: "+input.title(),
                                colour=discord.Colour.blue())
            CategoryEmbed.set_thumbnail(url="https://i.imgur.com/mUNosuh.png")
            
            #** Iterate Through Commands In Cog **
            PageData = []
            for CommandNo, command in enumerate(Cog.walk_commands()):
                
                #** If 10 Commands Reached, Add To Embed Page Number & Create Pagination Object. **
                if (CommandNo % 6) == 0 and CommandNo != 0:
                    CategoryEmbed.set_footer(text="Page "+str(CommandNo // 6))
                    PageDict = copy.deepcopy(CategoryEmbed.to_dict())
                    PageData.append(PageDict)
                    print("[PAGE]\n")
                    print(PageData)
                    print()
                    
                    #** If First Page, Send Embed & Add Reactions **#
                    if (CommandNo / 6) == 1:
                        Page = await ctx.send(embed=CategoryEmbed)
                        await Page.add_reaction(self.Emojis['Back'])
                        await Page.add_reaction(self.Emojis['Next'])
                    
                    #** Clear Embed Fields **
                    CategoryEmbed.clear_fields()
                    print(PageDict)
                
                #** Create Field Description With Command Aliases And Command Description **
                Value = "*"+command.description+"*\n ---------------------------"
                if command.aliases != []:
                    Value = "`Aliases: !"+(", !".join(command.aliases))+"`\n"+Value
                else:
                    Value = "`Aliases: None`"+Value
                    
                #** Add Field About Command To Embed **
                CategoryEmbed.add_field(name="**__"+command.name.title()+"__**", value=Value, inline=False)
            
            if len(list(Cog.walk_commands())) > 6 and (CommandNo % 6) != 0:
                CategoryEmbed.set_footer(text="Page "+str(int(math.ceil(CommandNo / 6))))
                PageData.append(CategoryEmbed.to_dict())
                print("[PAGE]\n")
                print(PageData)
                print()
                
            #** Send Embed if less than 6 commands otherwise Create Pagination For Embed **
            if PageData == []:
                await ctx.send(embed=CategoryEmbed)
            else:
                await self.Pagination.add_pages(Page.id, PageData)
                print("Pagination Sent!")
                
        #**------------------SINGLE COMMAND------------------**#
                
        elif input.lower() in self.activeCommands:
            
            #** Get Command Object **
            Command = self.client.get_command(input.lower())
            
            #** Create Embed Description
            Description = "\n*"+Command.description+"*"
            if Command.aliases != []:
                Description = "`Aliases: !"+(", !".join(Command.aliases))+"`"+Description
            else:
                Description = "`Aliases: None`"+Description
                
            #** Create Embed About Command **
            CommandEmbed = discord.Embed(title = "Command: "+input.title(),
                                description = Description,
                                colour = discord.Colour.blue())
            CommandEmbed.set_thumbnail(url="https://i.imgur.com/mUNosuh.png")
            
            #** Add Usage Field **
            if Command.usage != None:
                Usage = "`"+Command.usage+"`"
            else:
                Usage = "`!"+input.lower()+"`"
            if Command.brief != None:
                Usage += "\n*"+Command.brief+"*"
            CommandEmbed.add_field(name="Usage:", value=Usage, inline=False)

            #** Add Paramaters Field **
            if Command.help != None:
                CommandEmbed.add_field(name="Paramters:", value=Command.help, inline=False)
            
            #** Send Embed To Discord **
            await ctx.send(embed=CommandEmbed)
        

#!-------------------SETUP FUNCTION-------------------#


def setup(client):
    client.add_cog(HelpCog(client))