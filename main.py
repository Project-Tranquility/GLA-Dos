import discord
from dotenv import load_dotenv
from os import getenv
import aiosqlite
import asyncio
import uvicorn
from bot_instance import bot
from api import app

load_dotenv()

discord_token = getenv("TOKEN")

@bot.event
async def on_ready():
    await init_db()
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Just a hello word command")
async def hello(ctx):
    await ctx.respond("Hello too")

@bot.slash_command(name="whoami", description="juste un qui je suis")
async def whoami(ctx):
    await ctx.respond(f"Ton id {ctx.author.id} Ton nom de compte {ctx.author.name} ton nom affiché {ctx.author.global_name} {ctx.author.display_name}")

@bot.slash_command(name="add", description="add a user")
async def add(ctx):
    async with aiosqlite.connect("db/data.db") as db:
        await db.execute(
            "INSERT INTO users (name, account, devid) VALUES (?, ?, ?)",
            (ctx.author.global_name, ctx.author.name, ctx.author.id),
        )
        await db.commit()
    await ctx.respond("Tu es désormais enregistré")

@bot.slash_command(name="delete", description="se désinscrire du bot")
async def delete(ctx):
    async with aiosqlite.connect("db/data.db") as db:
        id = ctx.author.id
        result = await db.execute(
            "DELETE FROM users WHERE devid = ?",
            (id,),
        )
        await db.commit()
    if result.rowcount == 0:
        await ctx.respond("Tu n'est pas enregister")
        return
    await ctx.respond("Tu es desinscrit de la liste")

@bot.slash_command(name="status", description="status of your account", )
async def status(ctx):
    id = ctx.author.id
    try:
        async with aiosqlite.connect("db/data.db") as db:
            cursor = await db.execute(
                "SELECT id, name, account, devid FROM users WHERE devid = ?",
                (id,),
            )
            row = await cursor.fetchone()
    except Exception as e:
        return
    if not row:
        await ctx.respond("Tu n'es pas enregistré", ephemeral=True)
        return

    message = f"ID: {row[0]}, Nom: {row[1]}, Compte: {row[2]}, DevID: {row[3]}"
    await ctx.respond(message, ephemeral=True)

@bot.slash_command(name="list", description="list all user")
async def select(ctx):
    if ctx.author.name != "tadomika_ari":
        await ctx.respond("Pas les perms")
        return
    async with aiosqlite.connect("db/data.db") as db:
        result = await db.execute("SELECT id, name, account, devid FROM users")
        rows = await result.fetchall()
    if not rows:
        await ctx.respond("Aucun utilisateur enregistré")
        return
    message = "\n".join(f"{row[1]} {row[2]} {row[3]}" for row in rows)
    await ctx.respond(message)

async def init_db():
    print("Création de la base de donnée")
    async with aiosqlite.connect("db/data.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, account TEXT NOT NULL, devid INTEGER NOT NULL)")
        await db.commit()
    print("Base de donnée créer")

async def main():
    port = int(getenv("PORT"))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, loop="asyncio")
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        bot.start(discord_token)
    )
asyncio.run(main())