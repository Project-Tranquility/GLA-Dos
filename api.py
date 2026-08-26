import fastapi
from pydantic import BaseModel
from bot_instance import bot
import aiosqlite 

app = fastapi.FastAPI()

DATABASE = "db/data.db"

class Request(BaseModel):
    id: int
    indentification: str
    text: str

async def check_user(user_json):
    try:
        async with aiosqlite.connect("db/data.db") as db:
            cursor = await db.execute(
                "SELECT id, name, account, devid FROM users WHERE account = ?",
                (user_json,),
            )
            row = await cursor.fetchone()
    except Exception as e:
        return None
    if not row:
        return None
    if row[2] == user_json:
        return row[3]

@app.post("/dm")
async def serveur(req: Request):
    if not req:
        return {"status": "refused", "error": ""}
    user_json = req.indentification
    user_id = await check_user(user_json)
    if user_id is None:
        return {"status": "refused", "reason": "register not found"}
    user = bot.get_user(user_id)
    if user is None:
        try:
            user = await bot.fetch_user(user_id)
        except Exception:
            return {"status": "refused", "reason": "discord user not found"}
    print(user)
    await user.send(req.text)
    return {"status": "accepted"}

async def verify_glados_api(x_glados_key: str = fastapi.Header(...)):
    api_key = x_glados_key
    try:
        async with aiosqlite.connect("db/data.db") as db:
            cursor = await db.execute(
                "SELECT id, name, account, devid, key FROM users WHERE key = ?",
                (api_key,),
            )
        row = await cursor.fetchone()
    except Exception as e:
        raise fastapi.HTTPException(404, "Not Found")
    if not row:
        raise fastapi.HTTPException(403, "Forbiden")

async def take_devid(x_glados_key: str = fastapi.Header(...)):
    api_key = x_glados_key
    try:
        async with aiosqlite.connect("db/data.db") as db:
            cursor = await db.execute(
                "SELECT id, name, account, devid, key FROM users WHERE key = ?",
                (api_key,),
            )
            row = await cursor.fetchone()
    except Exception as e:
        raise fastapi.HTTPException(404, "Not Found")
    if not row:
        raise fastapi.HTTPException(403, "Forbiden")
    return row[3]
class MessagePayload(BaseModel):
    text: str

@app.post("/discord/say")
async def say_in_channel(payload: MessagePayload, devid: int = fastapi.Depends(take_devid)):
    channel = bot.get_user(devid) or await bot.fetch_user(devid)
    if channel is None:
        raise fastapi.HTTPException(404, "Channel not found")
    await channel.send(payload.text)
    return {"ok": True}