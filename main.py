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

bot.run(discord_token)
