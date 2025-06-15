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
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import LOG, LOG_GROUP_ID
from YukkiMusic import app

from YukkiMusic.utils.database import delete_served_chat, get_assistant, is_on_off


@Client.on_message(filters.new_chat_members)
async def on_bot_added(client, message):
    try:
        userbot = await get_assistant(message.chat.id)
        chat = message.chat
        for members in message.new_chat_members:
            if members.id == client.id:
                count = await client.get_chat_members_count(chat.id)
                username = (
                    message.chat.username if message.chat.username else "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
                )
                bot = await client.get_me()
                msg = (
                    f"**Music bot added in new Group #New_Group**\n\n"
                    f"**Chat Name:** {message.chat.title}\n"
                    f"**Chat Id:** {message.chat.id}\n"
                    f"**Chat Username:** @{username}\n"
                    f"**Chat Member Count:** {count}\n"
                    f"**Added By:** {message.from_user.mention}"
                    f"**Bot:** {bot.mention}"
                )
                await app.send_message(
                    LOG_GROUP_ID,
                    text=msg,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text=f"Added by: {message.from_user.first_name}",
                                    user_id=message.from_user.id,
                                )
                            ]
                        ]
                    ),
                )
                if message.chat.username:
                    await userbot.join_chat(message.chat.username)
    except Exception:
        pass


@Client.on_message(filters.left_chat_member)
async def on_bot_kicked(client, message: Message):
    try:
        userbot = await get_assistant(message.chat.id)

        left_chat_member = message.left_chat_member
        if left_chat_member and left_chat_member.id == client.id:
            remove_by = (
                message.from_user.mention if message.from_user else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
            )
            title = message.chat.title
            username = (
                f"@{message.chat.username}" if message.chat.username else "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
            )
            chat_id = message.chat.id
            bot = await client.get_me()
            left = (
                f"Bot was Removed in {title} #Left_group\n"
                f"**Chat Name**: {title}\n"
                f"**Chat Id**: {chat_id}\n"
                f"**Chat Username**: {username}\n"
                f"**Removed By**: {remove_by}"
                f"**Bot:** {bot.mention}"
            )

            await app.send_message(
                LOG_GROUP_ID,
                text=left,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"Removed By: {message.from_user.first_name}",
                                user_id=message.from_user.id,
                            )
                        ]
                    ]
                ),
            )
            await delete_served_chat(chat_id)
            await userbot.leave_chat(chat_id)
    except Exception as e:
        pass
