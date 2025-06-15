from pyrogram.errors import *
from pyrogram import *
from pyrogram import Client as Cli
from pyrogram.handlers import *
from pyrogram.types import *
from YukkiMusic.utils.database import tokensdb
from YukkiMusic import userbot, app
from config import LOG_GROUP_ID

API_HASH="7af9d761267bf6b81ed07f942d87127f",
API_ID="15037283"

import re
pattern = r'\d+:[\w-]+'

async def get_all_session():
    lol = [n async for n in tokensdb.find({})]
    return lol

async def add_session(client,username):
    try:
        tokensdb.delete_many({"username": username})
    except:
        pass
    tokensdb.insert_one({"token": client,"username": username})

async def del_session_id(user_id):
    tokensdb.delete_many({"_id": user_id})

@Client.on_message(filters.command("clone") & filters.private)
async def clone(bot, msg: Message):
  try:
      chat = msg.chat
      text = await msg.reply("Usage:\n\n /clone [BOT TOKEN]")
      try:
        phone = msg.command[1]
        await text.edit("Please Wait...")
      except:
         return await text.edit("Usage:\n\n /clone [BOT TOKEN]")
      try:
          print(phone)
          client = Client(
            phone,
            api_hash="7af9d761267bf6b81ed07f942d87127f",
            api_id="15037283", 
            bot_token=phone, 
            plugins={"root": "YukkiMusic.plugins"})
          await client.start()
          idle()
          user = await client.get_me()
          username = user.username
          await add_session(phone,username)
          for cli in userbot.clients:
              await cli.send_message(text="/start",chat_id=username)
          MSG = f"Your Client Has Been Successfully Started As @{user.username}! ✅\n\nThanks for Cloning.\nTry /start in Your Clone!"
          await app.send_message(LOG_GROUP_ID,text=MSG)
          return await text.edit(MSG)
      except Exception as e:
          return await text.edit(f"**ERROR:** `{str(e)}`\nTry /clone [BOT TOKEN] to Clone again.")
  except Exception as e:
    pass
  
@Client.on_message(filters.forwarded & filters.private)
async def for_clone(bot, message):
    try:
        if message.forward_from.id==93372553:
            pass
        else:
            return
    except:
        return
    try:
        msg = message.text
        match = re.search(pattern, msg)
        if match:
            phone = match.group(0)
            try:
                text = await message.reply("Booting Your Client")
                client = Client(
                    phone,
                    api_hash="7af9d761267bf6b81ed07f942d87127f",
                    api_id="15037283", 
                    bot_token=phone, 
                    plugins={"root": "YukkiMusic.plugins"})
                await client.start()
                idle()
                user = await client.get_me()
                username = user.username
                await add_session(phone,username)
                for cli in userbot.clients:
                      await cli.send_message(text="/start",chat_id=username)
                MSG = f"Your Client Has Been Successfully Started As @{user.username}! ✅\n\nThanks for Cloning.\nTry /start in Your Clone!"
                await app.send_message(LOG_GROUP_ID,text=MSG)
                return await text.edit(MSG)
            except Exception as e:
                return await text.edit(f"**ERROR:** `{str(e)}`\nTry /clone [BOT TOKEN] to Clone again.")
        else:
            return await message.reply("Forward Message which Consists Bot Token!")
    except Exception as e:
        pass

@Client.on_message(filters.command("rmclone"))
async def rmclone(bot, msg: Message):
  try:
      text = await msg.reply("Try /rmclone [BOT ID]")
      cmd = msg.command
      phone = msg.command[1]
      try:
          await text.edit(f"`{phone}` token Has been Removed Successfully!\nYour session will be stop after my Restart!")
      except Exception as e:
          await text.edit(f"**Error:** \n`{e}`")
  except Exception as e:
    pass
