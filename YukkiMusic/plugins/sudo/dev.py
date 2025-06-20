#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#

# This aeval and sh module is taken from < https://github.com/TheHamkerCat/WilliamButcherBot >
# Credit goes to TheHamkerCat.
#

import os
import re
import sys
import asyncio
import traceback
from inspect import getfullargspec
from io import StringIO
from time import time

from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from YukkiMusic import app
from YukkiMusic.misc import SUDOERS

## -------- end of required imports to run this script

## ------ Below are some optional Imports you can remove it if is imported  you don't need to import it when using eval command

from pyrogram.raw.functions import *
from pyrogram.raw.types import *

from YukkiMusic import userbot
from YukkiMusic.core.call import Yukki

## end


async def aexec(code, client, message):
    local_vars = {}
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n")),
        globals(),
        local_vars,
    )
    __aexec_func = local_vars["__aexec"]
    return await __aexec_func(client, message)


async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})


@Client.on_edited_message(
    filters.command(["ev", "eval"]) & SUDOERS & ~filters.forwarded & ~filters.via_bot
)
@Client.on_message(
    filters.command(["ev", "eval"]) & SUDOERS & ~filters.forwarded & ~filters.via_bot
)
async def executor(client: app, message: Message):
    if len(message.command) < 2:
        return await edit_or_reply(message, text="<b>Give me something to exceute</b>")
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await message.delete()
    t1 = time()
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = "\n"
    if exc:
        evaluation += exc
    elif stderr:
        evaluation += stderr
    elif stdout:
        evaluation += stdout
    else:
        evaluation += "Success"
    final_output = f"<b>RESULTS:</b>\n<pre language='python'>{evaluation}</pre>"
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation))
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏳",
                        callback_data=f"runtime {t2-t1} Seconds",
                    )
                ]
            ]
        )
        await message.reply_document(
            document=filename,
            caption=f"<b>EVAL :</b>\n<code>{cmd[0:980]}</code>\n\n<b>Results:</b>\nAttached Document",
            quote=False,
            reply_markup=keyboard,
        )
        await message.delete()
        os.remove(filename)
    else:
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏳",
                        callback_data=f"runtime {round(t2-t1, 3)} Seconds",
                    ),
                    InlineKeyboardButton(
                        text="🗑",
                        callback_data=f"forceclose abc|{message.from_user.id}",
                    ),
                ]
            ]
        )
        await edit_or_reply(message, text=final_output, reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"runtime"))
async def runtime_func_cq(_, cq):
    runtime = cq.data.split(None, 1)[1]
    await cq.answer(runtime, show_alert=True)


@Client.on_callback_query(filters.regex("forceclose"))
async def forceclose_command(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(
                "This is not for you stay away from here", show_alert=True
            )
        except Exception:
            return
    await CallbackQuery.message.delete()
    try:
        await CallbackQuery.answer()
    except Exception:
        return


@Client.on_edited_message(
    filters.command("sh") & SUDOERS & ~filters.forwarded & ~filters.via_bot
)
@Client.on_message(filters.command("sh") & SUDOERS & ~filters.forwarded & ~filters.via_bot)
async def shellrunner(client, message: Message):
    if len(message.command) < 2:
        return await edit_or_reply(
            message, text="<b>Give some commands like:</b>\n/sh git pull"
        )

    text = message.text.split(None, 1)[1]
    output = ""

    async def run_command(command):
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            return stdout.decode().strip(), stderr.decode().strip()
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                etype=exc_type,
                value=exc_obj,
                tb=exc_tb,
            )
            return None, ''.join(errors)

    if "\n" in text:
        commands = text.split("\n")
        for cmd in commands:
            stdout, stderr = await run_command(cmd)
            output += f"<b>Command:</b> {cmd}\n"
            if stdout:
                output += f"<b>Output:</b>\n<pre>{stdout}</pre>\n"
            if stderr:
                output += f"<b>Error:</b>\n<pre>{stderr}</pre>\n"
    else:
        stdout, stderr = await run_command(text)
        if stdout:
            output += f"<b>Output:</b>\n<pre>{stdout}</pre>\n"
        if stderr:
            output += f"<b>Error:</b>\n<pre>{stderr}</pre>\n"

    if not output.strip():
        output = "<b>OUTPUT :</b>\n<code>None</code>"

    if len(output) > 4096:
        with open("output.txt", "w+") as file:
            file.write(output)
        await client.send_document(
            message.chat.id,
            "output.txt",
            reply_to_message_id=message.id,
            caption="<code>Output</code>",
        )
        os.remove("output.txt")
    else:
        await edit_or_reply(message, text=output)

    await message.stop_propagation()
