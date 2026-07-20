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