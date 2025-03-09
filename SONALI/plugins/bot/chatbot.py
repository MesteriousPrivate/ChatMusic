from pyrogram import Client, filters, enums
from SONALI import app
import random
import asyncio
import config
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.errors import ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError

# Database Connection
mongodb = MongoCli(config.MONGO_DB_URI)
db = mongodb.Anonymous
chatbot_settings = db.chatbot_settings  # Chatbot enable/disable ka database

# Chat Storage (Randomly select one)
CHAT_STORAGE = [
    "mongodb+srv://chatbot1:a@cluster0.pxbu0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://chatbot2:b@cluster0.9i8as.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
]
VIPBOY = MongoCli(random.choice(CHAT_STORAGE))
chatdb = VIPBOY.Anonymous
chatai = chatdb.Word.WordDb

# Cache
reply = []
LOAD = "FALSE"

# ✅ Function to check chatbot status in a group
async def is_chatbot_enabled(chat_id: int) -> bool:
    """Check karega ki chatbot uss group me enabled hai ya nahi."""
    chat = await chatbot_settings.find_one({"chat_id": chat_id})
    return bool(chat and chat.get("enabled", True))  # Default enabled

# ✅ Admins Only: Enable/Disable chatbot
@app.on_message(filters.command("chat") & filters.group)
async def toggle_chatbot(client: Client, message: Message):
    user = message.from_user
    chat_id = message.chat.id

    # Check if user is admin/owner
    chat_member = await client.get_chat_member(chat_id, user.id)
    if chat_member.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
        return await message.reply_text("❌ **Sirf Admin/Owner is command ka use kar sakte hain!**")

    # Agar sirf `/chat` likha hai to status dikhaye
    if len(message.command) == 1:
        status = await is_chatbot_enabled(chat_id)
        return await message.reply_text(f"🤖 **Chatbot Status:** {'✅ Enabled' if status else '🚫 Disabled'}")

    # Enable or Disable chatbot
    action = message.command[1].lower()
    if action == "on":
        await chatbot_settings.update_one({"chat_id": chat_id}, {"$set": {"enabled": True}}, upsert=True)
        return await message.reply_text("✅ **Chatbot Enabled!** Ab ye group me messages ka reply karega.")

    elif action == "off":
        await chatbot_settings.update_one({"chat_id": chat_id}, {"$set": {"enabled": False}}, upsert=True)
        return await message.reply_text("🚫 **Chatbot Disabled!** Ab ye group me reply nahi karega.")

    else:
        return await message.reply_text("❌ **Galat command!** Use: `/chat on` ya `/chat off`")

# ✅ Function to get reply from database
async def get_reply(message_text: str):
    global reply
    matched_replies = [reply_data for reply_data in reply if reply_data["word"] == message_text]
    return random.choice(matched_replies) if matched_replies else (random.choice(reply) if reply else None)

# ✅ Function to send chatbot reply
async def reply_message(client, chat_id, bot_id, message_text, message):
    try:
        reply_data = await get_reply(message_text)
        if reply_data:
            if reply_data["check"] == "sticker":
                return await message.reply_sticker(reply_data["text"])
            elif reply_data["check"] == "photo":
                return await message.reply_photo(reply_data["text"])
            elif reply_data["check"] == "video":
                return await message.reply_video(reply_data["text"])
            elif reply_data["check"] == "audio":
                return await message.reply_audio(reply_data["text"])
            elif reply_data["check"] == "gif":
                return await message.reply_animation(reply_data["text"])
            elif reply_data["check"] == "voice":
                return await message.reply_voice(reply_data["text"])
            else:
                return await message.reply_text(reply_data["text"], disable_web_page_preview=True)
    except (ChatAdminRequired, UserIsBlocked, ChatWriteForbidden, RPCError):
        return
    except Exception as e:
        print(f"Error in reply_message: {e}")
        return

# ✅ Chatbot Function (Only Works if Enabled)
@app.on_message(filters.incoming, group=1)
async def chatbot(client: Client, message: Message):
    if not message.from_user or message.from_user.is_bot:
        return

    chat_id = message.chat.id
    message_text = message.text.lower() if message.text else None

    # Personal chat me chatbot hamesha active rahega
    if message.chat.type == enums.ChatType.PRIVATE:
        chatbot_enabled = True
    else:
        chatbot_enabled = await is_chatbot_enabled(chat_id)  # Group me enabled/disabled check karo

    # Agar chatbot disabled hai, to ignore kar do
    if not chatbot_enabled:
        return

    # Simple Replies
    if message_text:
        if "gn" in message_text or "good night" in message_text:
            return await message.reply_text(f"🌙 **Good Night!** Sweet dreams {message.from_user.mention} ✨")
        elif "gm" in message_text or "good morning" in message_text:
            return await message.reply_text(f"🌞 **Good Morning!** {message.from_user.mention} 😃")
        elif "hello" in message_text or "hii" in message_text or "hey" in message_text:
            return await message.reply_text(f"👋 **Hi {message.from_user.mention}!** Kaise ho?")
        elif "bye" in message_text or "goodbye" in message_text:
            return await message.reply_text(f"👋 **Goodbye!** Take care {message.from_user.mention}!")
        elif "thanks" in message_text or "thank you" in message_text:
            return await message.reply_text("😜 **Hehe welcome!**")

    # Agar koi command ya bot mention hai to ignore kar do
    if message_text and any(message_text.startswith(prefix) for prefix in ["!", "/", "@", ".", "?", "#"]):
        return

    # Fetch Reply from Database
    await reply_message(client, chat_id, client.me.id, message_text, message)
