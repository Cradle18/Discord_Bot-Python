import os
import discord
import json
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def test(ctx, a):
    if a == "Hello there":
        a = "General Kenobi"  
    await ctx.send(a)

voice_channel_members = {}

#saves the subscriptions to a json file, so we keep a database of the subscribed
def save_subscriptions():
    with open("subscriptions.json", 'w') as f:
        json.dump({k: list(v) for k, v in voice_channel_members.items()}, f, indent=4)

#loads the json file of subscribers so that the bot knows who already has subscribed.
def load_subscriptions():
    try:
        with open("subscriptions.json", "r") as f:
            return json.load(f, object_hook=lambda d: {int(k): set(v) for k, v in d.items()})
    except FileNotFoundError:
        return {}

@bot.event
async def on_ready():
    global voice_channel_members
    voice_channel_members = load_subscriptions()
    print(f"Loaded {len(voice_channel_members)} guilds with subscriptions")
    print(voice_channel_members)
    


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        guild_id = member.guild.id
        channel_name = after.channel.name

        #check if the guild has subscribed to voice channel notifications
        if guild_id in voice_channel_members:
            print(f"2nd check {voice_channel_members}")
            for user_id in voice_channel_members[guild_id]:
                user = await bot.fetch_user(user_id)
                message = f"{member.display_name} has joined the voice channel"
                await user.send(message)

@bot.command()
async def subscribe(ctx):
    #add the user to the list of subscibed users for the guild
    user_id = ctx.author.id
    guild_id = ctx.guild.id
    

    if guild_id not in voice_channel_members:
        voice_channel_members[guild_id] = set()

    if user_id not in voice_channel_members[guild_id]:
        voice_channel_members[guild_id].add(user_id)
        print(f"Guild {guild_id} has {len(voice_channel_members[guild_id])} subscribers")
        await ctx.send(f"{ctx.author.mention}, you have been subscribed")
    
    save_subscriptions()

@bot.command()
async def unsubscribe(ctx):
    #remove the user from the list of subscribed user for the guild
    user_id = ctx.author.id
    guild_id = ctx.guild.id

    if guild_id in voice_channel_members and user_id in voice_channel_members[guild_id]:
        voice_channel_members[guild_id].remove(user_id)
        save_subscriptions()
        await ctx.send(f"{ctx.author.mention}, you have been unsubscribed from voice channel notifications")
    else:
        await ctx.send(f"{ctx.author.mention}, you are not currently subscribed to voice channel notifications")



bot.run(TOKEN)