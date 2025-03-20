from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SONALI import app
from config import BOT_USERNAME
from SONALI.utils.errors import capture_err
import httpx 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_txt = """
✰ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ɴᴏxx ɴᴇᴛᴡᴏʀᴋ ✰
 
✰ ʀᴇᴘᴏ ɴᴀᴀ ᴍɪʟᴇɢᴀ ʏᴀʜᴀ ʙʀᴜʜ
 
✰ ʙᴀᴋɪɪ ᴛᴜᴍ ᴏᴡɴᴇʀ sᴇ ᴘᴜᴄʜʜ sᴀᴋᴛᴇ ʜᴏ

✰ || @TMZEROO ||
 
✰ 𝗥ᴜɴ 24x7 𝗟ᴀɢ 𝗙ʀᴇᴇ 𝗪ɪᴛʜᴏᴜᴛ 𝗦ᴛᴏᴘ
 
"""




@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
        [ 
          InlineKeyboardButton("ᴀᴅᴅ ᴍᴇᴇʜ ʙᴀʙʏ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
          InlineKeyboardButton("ʜᴇʟᴘ", url="https://t.me/Nycreation_chatzone"),
          InlineKeyboardButton("ɴᴏxx", url="https://t.me/NoxxNetwork"),
          ],
               [
                InlineKeyboardButton("ᴏᴜʀ ᴀʟʟ ʙᴏᴛs", url=f"https://t.me/NoxxNetwork/15"),
],
[
InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ ʙᴏᴛ", url=f"https://t.me/NyCreation_bot"),

        ]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo="https://files.catbox.moe/2oj1vp.webp",
        caption=start_txt,
        reply_markup=reply_markup
    )
