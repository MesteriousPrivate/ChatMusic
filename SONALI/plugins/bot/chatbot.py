from pyrogram import Client, filters, enums
from SONALI import app
import shutil
from typing import List
import asyncio
import re
import config
import random
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction, ChatMemberStatus as CMS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, VideoChatScheduled
from pyrogram.errors import ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, FloodWait, RPCError
from pyrogram.types import ChatMemberUpdated

mongodb = MongoCli(config.MONGO_DB_URI)
db = mongodb.Anonymous

CHAT_STORAGE = [
    "mongodb+srv://chatbot1:a@cluster0.pxbu0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot2:b@cluster0.9i8as.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot3:c@cluster0.0ak9k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot4:d@cluster0.4i428.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot5:e@cluster0.pmaap.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot6:f@cluster0.u63li.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot7:g@cluster0.mhzef.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot8:h@cluster0.okxao.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot9:i@cluster0.yausb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot10:j@cluster0.9esnn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
]

VIPBOY = MongoCli(random.choice(CHAT_STORAGE))
chatdb = VIPBOY.Anonymous
chatai = chatdb.Word.WordDb
storeai = VIPBOY.Anonymous.Word.NewWordDb  

sticker_db = db.stickers.sticker

chatbot_settings = db.chatbot_settings  # ✅ ON/OFF System ke liye database

reply = []
sticker = []
LOAD = "FALSE"

async def load_caches():
    global reply, sticker, LOAD
    if LOAD == "TRUE":
        return
    LOAD = "TRUE"
    reply.clear()
    sticker.clear()
    
    print("All cache cleaned ✅")
    await asyncio.sleep(1)
    try:
        print("Loading All Caches...")
        
        reply = await chatai.find().to_list(length=10000)
        print("Replies Loaded ✅")
        await asyncio.sleep(1)
        sticker = await sticker_db.find().to_list(length=None)
        if not sticker:
            sticker_id = "CAACAgUAAxkBAAENzH5nsI3qB-eJNDAUZQL9v3SQl_m-DAACigYAAuT1GFUScU-uCJCWAjYE"
            await sticker_db.insert_one({"sticker_id": sticker_id})
        print("Sticker Loaded ✅")
        print("All caches loaded 👍 ✅")
        LOAD = "FALSE"
    except Exception as e:
        print(f"Error loading caches: {e}")
        LOAD = "FALSE"
    return

# ✅ Chatbot ON/OFF Status Check Function
async def is_chat_enabled(chat_id: int) -> bool:
    chat = await chatbot_settings.find_one({"chat_id": chat_id})
    return chat and chat.get("enabled", False)  # ✅ Default: OFF

# ✅ Chatbot ON/OFF Set Karne Ka Function
async def set_chat_status(chat_id: int, status: bool):
    await chatbot_settings.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

@app.on_message(filters.command("chat") & filters.group)
async def toggle_chat(client: Client, message: Message):
    user = message.from_user
    chat_id = message.chat.id

    # ✅ Sirf Admins/Owner Allowed
    chat_member = await client.get_chat_member(chat_id, user.id)
    if chat_member.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
        return await message.reply_text("❌ **Sirf Admin/Owner is command ka use kar sakte hain!**")

    # ✅ Agar koi sirf `/chat` likhe to status dikhaye
    if len(message.command) == 1:
        enabled = await is_chat_enabled(chat_id)
        return await message.reply_text(f"🤖 **Chatbot Status:** {'🟢 ON' if enabled else '🔴 OFF'}")

    # ✅ ON/OFF System
    action = message.command[1].lower()
    if action == "on":
        await set_chat_status(chat_id, True)
        return await message.reply_text("✅ **Chatbot Enabled!** Ab ye group me messages ka reply karega.")

    elif action == "off":
        await set_chat_status(chat_id, False)
        return await message.reply_text("🚫 **Chatbot Disabled!** Ab ye group me reply nahi karega.")

    else:
        return await message.reply_text("❌ **Galat command! Use:**\n`/chat on` - Enable chatbot\n`/chat off` - Disable chatbot")
        
async def get_reply(message_text: str):
    global reply
    matched_replies = [reply_data for reply_data in reply if reply_data["word"] == message_text]

    if matched_replies:
         return random.choice(matched_replies)
        
    return random.choice(reply) if reply else None

async def save_reply(original_message: Message, reply_message: Message):
    global reply
    try:
        reply_data = {
            "word": original_message.text,
            "text": None,
            "check": "none",
        }

        if reply_message.sticker:
            reply_data["text"] = reply_message.sticker.file_id
            reply_data["check"] = "sticker"
        elif reply_message.photo:
            reply_data["text"] = reply_message.photo.file_id
            reply_data["check"] = "photo"
        elif reply_message.video:
            reply_data["text"] = reply_message.video.file_id
            reply_data["check"] = "video"
        elif reply_message.audio:
            reply_data["text"] = reply_message.audio.file_id
            reply_data["check"] = "audio"
        elif reply_message.animation:
            reply_data["text"] = reply_message.animation.file_id
            reply_data["check"] = "gif"
        elif reply_message.voice:
            reply_data["text"] = reply_message.voice.file_id
            reply_data["check"] = "voice"
        elif reply_message.text:
            reply_text = reply_message.text
            reply_data["text"] = reply_text
            reply_data["check"] = "none"
            

        is_chat = await chatai.find_one(reply_data)
        if not is_chat:
            await chatai.insert_one(reply_data)
            reply.append(reply_data)

    except Exception as e:
        print(f"Error in save_reply: {e}")
          

async def reply_message(client, chat_id, bot_id, message_text, message):
    try:
        reply_data = await get_reply(message_text)
        if reply_data:
            response_text = reply_data["text"]
            translated_text = response_text
            
            if reply_data["check"] == "sticker":
                await message.reply_sticker(reply_data["text"])
            elif reply_data["check"] == "photo":
                await message.reply_photo(reply_data["text"])
            elif reply_data["check"] == "video":
                await message.reply_video(reply_data["text"])
            elif reply_data["check"] == "audio":
                await message.reply_audio(reply_data["text"])
            elif reply_data["check"] == "gif":
                await message.reply_animation(reply_data["text"])
            elif reply_data["check"] == "voice":
                await message.reply_voice(reply_data["text"])
            else:
                results = f"**[{translated_text}](https://t.me/Lucyxbot?start=start)**"
                await message.reply_text(translated_text, disable_web_page_preview=True)

    except (ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError) as e:
        return
    except Exception as e:
        print(f"Error in reply_message:- {e}")
        return
#  OWNER CAN ENABLE DISABLE COMMAND NEW 
@app.on_message(filters.command("chatbot") & filters.user(1786683163))
async def chatbot_toggle(client: Client, message: Message):
    if len(message.command) == 1:
        return await message.reply_text("❌ **Use:**\n`/chatbot enable` - Sab group me chatbot ON\n`/chatbot disable` - Sab group me chatbot OFF\n`/chatbot reset` - Sab group me chatbot OFF kar ke reset karega")

    action = message.command[1].lower()
    
    if action == "enable":
        await chatbot_settings.update_many({}, {"$set": {"enabled": True}})
        return await message.reply_text("✅ **Chatbot Enabled!** Ab sabhi groups me chatbot kaam karega.")

    elif action == "disable":
        await chatbot_settings.update_many({}, {"$set": {"enabled": False}})
        return await message.reply_text("🚫 **Chatbot Disabled!** Ab kisi bhi group me chatbot reply nahi karega, lekin DM me ON rahega.")

    elif action == "reset":
        await chatbot_settings.delete_many({})  # ✅ Sabhi settings hata do (reset)
        return await message.reply_text("🔄 **Chatbot Reset!** Ab sabhi groups me default OFF ho gaya. Jise chalu karna ho, wo `/chat on` kare.")

    else:
        return await message.reply_text("❌ **Galat command! Use:**\n`/chatbot enable` - Sab group me chatbot ON\n`/chatbot disable` - Sab group me chatbot OFF\n`/chatbot reset` - Sab group me chatbot OFF kar ke reset karega")

#old with upgrade
@app.on_message(filters.incoming, group=1)
async def chatbot(client: Client, message: Message):
    global sticker
    bot_id = client.me.id
    
    if not sticker:
        await load_caches()
        return
    
    # ✅ Agar chatbot globally OFF hai to return kar do (lekin DM me hamesha ON rahega)
    if message.chat.type != enums.ChatType.PRIVATE and not await is_chat_enabled(message.chat.id):
        return

    if not message.from_user or message.from_user.is_bot:
        return
        
    user_id = message.from_user.id if message.from_user else message.chat.id
    chat_id = message.chat.id
    bot_id = client.me.id
    
    try:
        if message.text and any(message.text.startswith(prefix) for prefix in ["!", "/", "@", ".", "?", "#"]):
            return
          
        if (message.reply_to_message and message.reply_to_message.from_user.id == client.me.id) or (not message.reply_to_message):
            
            if message.text and message.from_user:
                message_text = message.text.lower()
                
                if "gn" in message_text or "good night" in message_text:
                    return await message.reply_text(f"Good Night! Sweet dreams {message.from_user.mention} 🌙✨")
    
                elif "gm" in message_text or "good morning" in message_text:
                    return await message.reply_text(f"Good Morning ji! {message.from_user.mention} 🙈")
    
                elif "hello" in message_text or "hii" in message_text or "hey" in message_text:
                    return await message.reply_text(f"Hi {message.from_user.mention} 😁 kaise ho??")
    
                elif "bye" in message_text or "goodbye" in message_text:
                    return await message.reply_text(f"Goodbye! Take care! {message.from_user.mention} 👋😏")
    
                elif "thanks" in message_text or "thank you" in message_text:
                    return await message.reply_text("hehe welcome! 😜")

                else:
                    try:
                        await client.read_chat_history(message.chat.id)
                    except Exception:
                        pass
                    await reply_message(client, chat_id, bot_id, message_text, message)
                    return
        if message.reply_to_message:
            await save_reply(message.reply_to_message, message)
            
    except (ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError) as e:
        return
    except (Exception, asyncio.TimeoutError) as e:
    #    print(f"Error in send reply:- {e}")
        return

