#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#


from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from config import BANNED_USERS
from strings import command
from YukkiMusic import Platform, app
from YukkiMusic.core.call import Yukki
from YukkiMusic.misc import db
from YukkiMusic.utils.database import get_loop
from YukkiMusic.utils.decorators import AdminRightsCheck
from YukkiMusic.utils.inline.play import stream_markup, telegram_markup
from YukkiMusic.utils.stream.autoclear import auto_clean
from YukkiMusic.utils.thumbnails import gen_thumb


@Client.on_message(command("SKIP_COMMAND") & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):
    user = await cli.get_me()
    BOT_USERNAME = user.username
    if not len(message.command) < 2:
        loop = await get_loop(chat_id)
        if loop != 0:
            return await message.reply_text(_["admin_12"])
        state = message.text.split(None, 1)[1].strip()
        if state.isnumeric():
            state = int(state)
            check = db.get(chat_id)
            if check:
                count = len(check)
                if count > 2:
                    count = int(count - 1)
                    if 1 <= state <= count:
                        for x in range(state):
                            popped = None
                            try:
                                popped = check.pop(0)
                                if popped.get("mystic"):
                                    try:
                                        await popped.get("mystic").delete()
                                    except Exception:
                                        pass
                            except Exception:
                                return await message.reply_text(_["admin_16"])
                            if popped:
                                await auto_clean(popped)
                            if not check:
                                try:
                                    await message.reply_text(
                                        _["admin_10"].format(
                                            message.from_user.first_name
                                        ),
                                        disable_web_page_preview=True,
                                    )
                                    await Yukki.stop_stream(chat_id)
                                except Exception:
                                    return
                                break
                    else:
                        return await message.reply_text(_["admin_15"].format(count))
                else:
                    return await message.reply_text(_["admin_14"])
            else:
                return await message.reply_text(_["queue_2"])
        else:
            return await message.reply_text(_["admin_13"])
    else:
        check = db.get(chat_id)
        popped = None
        try:
            popped = check.pop(0)
            if popped:
                await auto_clean(popped)
                if popped.get("mystic"):
                    try:
                        await popped.get("mystic").delete()
                    except Exception:
                        pass
            if not check:
                await message.reply_text(
                    _["admin_10"].format(message.from_user.first_name),
                    disable_web_page_preview=True,
                )
                try:
                    return await Yukki.stop_stream(chat_id)
                except Exception:
                    return
        except Exception:
            try:
                await message.reply_text(
                    _["admin_10"].format(message.from_user.first_name),
                    disable_web_page_preview=True,
                )
                return await Yukki.stop_stream(chat_id)
            except Exception:
                return
    queued = check[0]["file"]
    title = (check[0]["title"]).title()
    user = check[0]["by"]
    user_id = message.from_user.id
    streamtype = check[0]["streamtype"]
    videoid = check[0]["vidid"]
    duration_min = check[0]["dur"]
    status = True if str(streamtype) == "video" else None
    if "live_" in queued:
        n, link = await Platform.youtube.video(videoid, True)
        if n == 0:
            return await message.reply_text(_["admin_11"].format(title))
        try:
            await Yukki.skip_stream(chat_id, link, video=status)
        except Exception:
            return await message.reply_text(_["call_7"])
        button = telegram_markup(_, chat_id)
        img = await gen_thumb(videoid)
        run = await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(
                user,
                f"https://t.me/{BOT_USERNAME}?start=info_{videoid}",
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"
    elif "vid_" in queued:
        mystic = await message.reply_text(_["call_8"], disable_web_page_preview=True)
        try:
            file_path, direct = await Platform.youtube.download(
                videoid,
                mystic,
                videoid=True,
                video=status,
            )
        except Exception:
            return await mystic.edit_text(_["call_7"])
        try:
            await Yukki.skip_stream(chat_id, file_path, video=status)
        except Exception:
            return await mystic.edit_text(_["call_7"])
        button = stream_markup(_, videoid, chat_id)
        img = await gen_thumb(videoid)
        run = await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(
                title[:27],
                f"https://t.me/{BOT_USERNAME}?start=info_{videoid}",
                duration_min,
                user,
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "stream"
        await mystic.delete()
    elif "index_" in queued:
        try:
            await Yukki.skip_stream(chat_id, videoid, video=status)
        except Exception:
            return await message.reply_text(_["call_7"])
        button = telegram_markup(_, chat_id)
        run = await message.reply_photo(
            photo=config.STREAM_IMG_URL,
            caption=_["stream_2"].format(user),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"
    else:
        try:
            await Yukki.skip_stream(chat_id, queued, video=status)
        except Exception:
            return await message.reply_text(_["call_7"])
        if videoid == "telegram":
            button = telegram_markup(_, chat_id)
            run = await message.reply_photo(
                photo=(
                    config.TELEGRAM_AUDIO_URL
                    if str(streamtype) == "audio"
                    else config.TELEGRAM_VIDEO_URL
                ),
                caption=_["stream_1"].format(
                    title, config.SUPPORT_GROUP, check[0]["dur"], user
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        elif videoid == "soundcloud":
            button = telegram_markup(_, chat_id)
            run = await message.reply_photo(
                photo=(
                    config.SOUNCLOUD_IMG_URL
                    if str(streamtype) == "audio"
                    else config.TELEGRAM_VIDEO_URL
                ),
                caption=_["stream_1"].format(
                    title, config.SUPPORT_GROUP, check[0]["dur"], user
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        elif "saavn" in videoid:
            button = telegram_markup(_, chat_id)
            url = check[0]["url"]
            details = await Platform.saavn.info(url)
            run = await message.reply_photo(
                photo=details["thumb"] or config.TELEGRAM_AUDIO_URL,
                caption=_["stream_1"].format(title, url, check[0]["dur"], user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        else:
            button = stream_markup(_, videoid, chat_id)
            img = await gen_thumb(videoid)
            run = await message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    title[:27],
                    f"https://t.me/{BOT_USERNAME}?start=info_{videoid}",
                    duration_min,
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
