import discord
from discord import bot
from dotenv import load_dotenv
from os import getenv

load_dotenv()

discord_token = getenv("TOKEN")

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Just a hello word command")
async def hello(ctx):
    await ctx.respond("Hello too")

bot.run(discord_token)
