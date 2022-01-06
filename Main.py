
#!--------------------------------IMPORT MODULES-----------------------------------# 


import os
import json
import asyncio
import discord
from datetime import datetime
from discord.utils import get
from discord.ext import commands


#!--------------------------------STARTUP-----------------------------------# 


#** Startup Sequence **
print("--------------------------STARTING UP-------------------------")
print("Startup Time: "+datetime.now().strftime("%H:%M - %d/%m/%Y")+"\n")


#!--------------------------------DISCORD BOT-----------------------------------# 


#** Load Config File **
with open('Config.json') as ConfigFile:
    Config = json.load(ConfigFile)
    ConfigFile.close()

#** Creating Bot Client **
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = Config['Prefix'], 
                      case_insensitive=True, 
                      intents=intents,
                      help_command=None)

#** Setup Emojis **
Emojis = Config['Variables']['Emojis']
Emojis["True"] = "✅"
Emojis["False"] = "❌"


#!--------------------------------COMMAND CHECKS-----------------------------------#


def is_admin():
    async def predicate(ctx):
        if ctx.author.id in ["315237737538125836"]:
            return True
        return False
    return commands.check(predicate)


#!--------------------------------DISCORD EVENTS-----------------------------------# 


@client.event
async def on_ready():
    print("Connection Established!")
    print("Preparing Internal Cache...")
    await client.wait_until_ready()
    client.startup = datetime.now()
    print("Bot Is Now Online & Ready!\n")


@client.event
async def on_guild_join(Guild):
    for Channel in Guild.channels:
        if isinstance(Channel, discord.channel.TextChannel):
            await Channel.send(Config['Welcome_Message'])
            break


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        Temp = await ctx.message.channel.send("**Command Not Found!**\nFor a full list of commands, run `!help`")
        await asyncio.sleep(5)
        await ctx.message.delete()
        await Temp.delete()
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        Temp = await ctx.message.channel.send("**Missing Paramater `"+str(error.param)+"`!**\nFor a full list of commands & their parameters, run `!help`")
        await asyncio.sleep(5)
        await ctx.message.delete()
        await Temp.delete()
        return
    elif isinstance(error, commands.CheckFailure):
        print(error)
        if str(error) == "UserVoice":
            Temp = await ctx.message.channel.send("To use this command, please join a Voice Channel!")
        elif str(error) == "BotVoice":
            Temp = await ctx.message.channel.send("I'm Not Currently Connected!")
        elif str(error) == "SameVoice":
            Temp = await ctx.message.channel.send("You must be in my Voice Channel to use this!")
        elif str(error) == "NotPlaying":
            Temp = await ctx.message.channel.send("I'm Not Currently Playing Anything!")
        else:
            raise error
        await asyncio.sleep(5)
        await ctx.message.delete()
        await Temp.delete()
        return
    else:
        raise error


#!--------------------------------DISCORD COMMANDS-----------------------------------# 


@client.command()
@is_admin()
async def reload(ctx, CogName):
    try:
        client.reload_extension("Cogs."+CogName.title())
    except:
        print(CogName+" Not Found!")
    await ctx.message.delete()


#!-------------------------------LOAD COGS-------------------------------#


for Cog in Config['Active_Extensions']:
    client.load_extension(Cog)


#!--------------------------------DISCORD LOOP-----------------------------------# 

#** Connecting To Discord **    
print("---------------------CONNECTING TO DISCORD--------------------")
client.run(os.environ["MUSICA_TOKEN"])