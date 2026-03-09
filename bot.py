import asyncio
import logging
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from config import config
from database import get_credits, deduct_credits, has_enough_credits, get_all_users, add_credits, PLAN_COSTS, get_user_status, increment_book_count, increment_cheatsheet_count
from scraper import scrape_channel
from processor import process_content, generate_with_failover
from generator import save_markdown, generate_pdf

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot and Dispatcher initialization
bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# States
class BotStates(StatesGroup):
    selecting_plan = State()
    selecting_type = State()
    entering_url = State()
    processing = State()
    admin_adding_credits = State()

# Keyboards
def get_plan_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Starter (200 post) - 1 Credit", callback_data="plan_starter")],
        [InlineKeyboardButton(text="Pro (450 post) - 2 Credits", callback_data="plan_pro")],
        [InlineKeyboardButton(text="Max (800 post) - 3.5 Credits", callback_data="plan_max")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_type_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Generate Book 📚", callback_data="type_book")],
        [InlineKeyboardButton(text="Generate Cheatsheet 📝", callback_data="type_cheatsheet")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "-"
    
    credits, is_new = get_user_status(user_id, full_name, username)

    if is_new:
        admin_notification = (
            "🆕 **Yangi foydalanuvchi!**\n\n"
            f"👤 Ism: {full_name}\n"
            f"🆔 ID: `{user_id}`\n"
            f"🔗 Username: {username}"
        )
        try:
            await bot.send_message(config.ADMIN_ID, admin_notification, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to notify admin about new user: {e}")
    
    welcome_text = (
        f"👋 Xush kelibsiz, {full_name}! Men Telegram kanal postlaridan kitob yoki qo'llanma Darslik yozuvchi botman.\n\n"
        f"💰 **Sizning balansingiz:** {credits} credit(lar)\n\n"
        "✨ **Rejalar va Narxlar:**\n"
        "• **Starter**: 200 ta post - 1 credit.\n"
        "• **Pro**: 450 ta post - 2 credit.\n"
        "• **Max**: 800 ta post - 3.5 credit.\n\n"
        "Iltimos, rejangizni tanlang:"
    )
    await message.answer(welcome_text, reply_markup=get_plan_keyboard(), parse_mode="Markdown")
    await state.set_state(BotStates.selecting_plan)

# Admin Panel
@dp.message(Command("monte"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return # Silent fail for non-admins

    users = get_all_users()
    user_rows = []
    for u in users:
        uid, creds, books, cheats, name, uname, date = u
        formatted_date = date.split()[0] if date else "-"
        status = "🌟 ADMIN" if uid == config.ADMIN_ID else "👤 User"
        user_rows.append(
            f"{status} | `{uid}` | {creds}cr\n"
            f"└ {name} ({uname}) | 📅 {formatted_date}\n"
            f"└ 📚: {books} | 📝: {cheats}"
        )
    
    user_list = "\n\n".join(user_rows)
    
    admin_text = (
        "🏗 **Admin Panel**\n\n"
        "Foydalanuvchilar Ro'yxati:\n\n"
        f"{user_list}\n\n"
        "Kredit qo'shish uchun `ID Amount` ko'rinishida yozing (masalan: `1234567 10`):"
    )
    await message.answer(admin_text, parse_mode="Markdown")
    await state.set_state(BotStates.admin_adding_credits)

@dp.message(BotStates.admin_adding_credits)
async def process_admin_add(message: types.Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        await state.clear()
        return

    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError
        
        target_id = int(parts[0])
        amount = float(parts[1])
        
        add_credits(target_id, amount)
        await message.answer(f"✅ User `{target_id}` ga {amount} credit qo'shildi.", parse_mode="Markdown")
        
        # Notify the user
        try:
            notification_text = f"🎁 Admin @ataxanov7z has increased your limit to {amount} credits!"
            await bot.send_message(target_id, notification_text)
        except Exception as e:
            logger.error(f"Failed to notify user {target_id} about credit increase: {e}")
            
    except ValueError:
        await message.answer("❌ Xato format. Iltimos `ID Amount` ko'rinishida yozing.")
    finally:
        await state.clear()

@dp.callback_query(F.data.startswith("plan_"))
async def process_plan_selection(callback: types.CallbackQuery, state: FSMContext):
    plan_code = callback.data.split("_")[1]
    plan_display = plan_code.capitalize()
    
    cost = PLAN_COSTS.get(plan_display, 1.0)
    user_id = callback.from_user.id
    current_credits = get_credits(user_id)

    if current_credits < cost:
        await callback.answer(
            f"❌ Balansingizda yetarli mablag' mavjud emas!\n\n"
            f"Sizda: {current_credits} credit\n"
            f"Kerak: {cost} credit\n\n"
            f"Iltimos, @ataxanov7z bilan bog'laning.",
            show_alert=True
        )
        return
    
    await state.update_data(plan=plan_display, cost=cost)
    
    await callback.message.edit_text(
        f"Siz **{plan_display}** rejasini tanladingiz (Narxi: {cost} credit).\n\nEndi xizmat turini tanlang:",
        reply_markup=get_type_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(BotStates.selecting_type)

@dp.callback_query(F.data.startswith("type_"))
async def process_type_selection(callback: types.CallbackQuery, state: FSMContext):
    selected_type = callback.data.split("_")[1]
    await state.update_data(selected_type=selected_type)
    
    type_name = "Kitob" if selected_type == "book" else "Cheatsheet"
    await callback.message.edit_text(
        f"Siz '{type_name}' yaratishni tanladingiz.\n\nIltimos, Telegram kanal linkini yuboring (masalan, https://t.me/startup_blogs):"
    )
    await state.set_state(BotStates.entering_url)

def sanitize_url(url):
    """
    Security: Basic URL sanitization to prevent non-Telegram links or injection.
    """
    url = url.strip()
    pattern = r'^(https?://)?(t\.me|telegram\.me|t\.me/joinchat/)[a-zA-Z0-9_+/-]+$'
    if re.match(pattern, url):
        return url
    return None

@dp.message(BotStates.entering_url)
async def process_url(message: types.Message, state: FSMContext):
    url = sanitize_url(message.text)
    if not url:
        await message.answer("⚠️ Iltimos, faqat to'g'ri Telegram kanal linkini yuboring.")
        return

    data = await state.get_data()
    plan = data.get("plan", "Starter")
    cost = data.get("cost", 1)
    
    user_id = message.from_user.id
    if not has_enough_credits(user_id, plan):
        current_credits = get_credits(user_id)
        await message.answer(
            f"❌ Balansingizda yetarli mablag' mavjud emas.\n"
            f"Sizda: {current_credits} credit bor. Tanlangan reja ({plan}) uchun {PLAN_COSTS.get(plan)} credit kerak.\n\n"
            "Iltimos, [@ataxanov7z](https://t.me/ataxanov7z) bilan bog'laning va credit sotib oling!",
            parse_mode="Markdown"
        )
        await state.clear()
        return

    mode = data.get("selected_type")
    
    # Notify user that processing has started
    status_msg = await message.answer("⏳ Processing... (1/3): Xabarlarni yig'ish boshlandi...")
    await state.set_state(BotStates.processing)
    
    # Run heavy tasks in background
    asyncio.create_task(background_processing(message, status_msg, url, mode, plan, cost, user_id, state))

async def background_processing(message: types.Message, status_msg: types.Message, url, mode, plan, cost, user_id, state: FSMContext):
    try:
        # Determine post limit based on plan
        post_limit = {"Starter": 200, "Pro": 450, "Max": 800}.get(plan, 200)

        # 1. Scrape
        await status_msg.edit_text(f"⏳ Processing... (1/3): {post_limit} ta post olinmoqda...")
        raw_posts = await scrape_channel(url, limit=post_limit)
        
        if not raw_posts:
            await status_msg.edit_text("❌ Hech qanday post topilmadi. Kanal ommaviy ekanligini tekshiring.")
            await state.clear()
            return

        # 2. AI Process
        await status_msg.edit_text("⏳ Processing... (2/3): AI tahlil qilmoqda (Gemini/GPT)...")
        prompt = process_content(raw_posts, mode, plan)
        content_md = await generate_with_failover(prompt)

        # 3. Generate Files
        await status_msg.edit_text("⏳ Processing... (3/3): Fayllar yaratilmoqda...")
        safe_name = "".join([c if c.isalnum() else "_" for c in url.split("/")[-1]])
        md_file = f"output_{safe_name}_{user_id}.md"
        pdf_file = f"output_{safe_name}_{user_id}.pdf"
        
        await asyncio.to_thread(save_markdown, content_md, md_file)
        await asyncio.to_thread(generate_pdf, content_md, pdf_file)

        # 4. Send Results
        await status_msg.edit_text("✅ Tayyor! Fayllar yuborilmoqda...")
        
        type_name = "Kitob" if mode == "book" else "Qo'llanma"
        await message.reply_document(FSInputFile(pdf_file), caption=f"Sizning {type_name} ready! (Plan: {plan})")
        await message.reply_document(FSInputFile(md_file), caption=f"Sizning {type_name} ready! (Markdown)")

        # Deduct credits and increment counter
        deduct_credits(user_id, cost)
        if mode == "book":
            increment_book_count(user_id)
        else:
            increment_cheatsheet_count(user_id)
            
        new_balance = get_credits(user_id)
        await message.answer(f"✅ {cost} credit yechib olindi. Qolgan balans: **{new_balance}**", parse_mode="Markdown")
        
        # Cleanup
        if os.path.exists(md_file): os.remove(md_file)
        if os.path.exists(pdf_file): os.remove(pdf_file)
        
    except Exception as e:
        logger.error(f"Error in background_processing: {e}")
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    finally:
        await state.clear()



async def main():
    # config.validate()  # Already called at import time in config.py now
    print("Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
