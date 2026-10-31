import telebot
import random
import string
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

BOT_TOKEN = "8997990355:AAGucc-wUiESOd09_gWK4Jr44vx12Ig1UQg"
bot = telebot.TeleBot(BOT_TOKEN)
CREATOR = "@vczra"

user_counts = {}


# ================= تولید آیدی (همه دقیقاً ۵ کاراکتر) =================

def gen_english():
    """۵ کاراکتر، فقط حروف انگلیسی"""
    return random.choice(string.ascii_lowercase) + \
           "".join(random.choices(string.ascii_lowercase, k=4))


def gen_english_dash():
    """۵ کاراکتر، حروف + حتماً یک _ (بدون عدد)"""
    while True:
        first = random.choice(string.ascii_lowercase)
        rest = "".join(random.choices(
            string.ascii_lowercase + "_", k=4))
        uid = first + rest
        if "_" in uid and len(uid) == 5:
            return uid


def gen_mix():
    """۵ کاراکتر، حروف + عدد + حتماً یک _"""
    while True:
        first = random.choice(string.ascii_lowercase)
        rest = "".join(random.choices(
            string.ascii_lowercase + string.digits + "_", k=4))
        uid = first + rest
        if "_" in uid and any(c.isdigit() for c in uid) and len(uid) == 5:
            return uid


def gen_english_number():
    """۵ کاراکتر، حروف + حتماً عدد (بدون _)"""
    while True:
        first = random.choice(string.ascii_lowercase)
        rest = "".join(random.choices(
            string.ascii_lowercase + string.digits, k=4))
        uid = first + rest
        if any(c.isdigit() for c in uid) and "_" not in uid and len(uid) == 5:
            return uid


def generate_ids(func, count):
    """تولید count آیدی یکتا"""
    s = set()
    tries = 0
    limit = max(count * 100, 1000)
    while len(s) < count and tries < limit:
        s.add(func())
        tries += 1
    return list(s)


# ================= کیبوردها =================

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🍃 کرک"))
    return kb


def type_menu():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("1️⃣ ۵ رقمی انگلیسی", callback_data="t1"))
    kb.row(InlineKeyboardButton("2️⃣ انگلیسی + خط تیره", callback_data="t2"))
    kb.row(InlineKeyboardButton("3️⃣ مخلوط (حرف+عدد+خط تیره)", callback_data="t3"))
    kb.row(InlineKeyboardButton("4️⃣ انگلیسی + عدد", callback_data="t4"))
    return kb


# ================= /start =================

@bot.message_handler(commands=['start'])
def cmd_start(m):
    bot.send_message(
        m.chat.id,
        "سلام 👋\n\n"
        "به ربات کرک آیدی تلگرامی خوش اومدی 🍃\n\n"
        "روی دکمه زیر بزن تا شروع کنیم 👇",
        reply_markup=main_menu()
    )


# ================= دکمه کرک =================

@bot.message_handler(func=lambda m: m.text == "🍃 کرک")
def ask_count(m):
    msg = bot.send_message(
        m.chat.id,
        "🔢 مقدار آیدی تولید شده دلخواه وارد کنید:\n"
        "(مثلاً 50 یا 100 — حداکثر 200)"
    )
    bot.register_next_step_handler(msg, receive_count)


# ================= دریافت تعداد =================

def receive_count(m):
    if not m.text or not m.text.strip().isdigit():
        bot.send_message(
            m.chat.id,
            "❌ لطفاً فقط عدد وارد کن.\nدوباره /start بزن.",
            reply_markup=main_menu()
        )
        return

    n = int(m.text.strip())
    if n < 1:
        n = 1
    if n > 200:
        n = 200
        bot.send_message(m.chat.id, "⚠ حداکثر ۲۰۰ آیدی مجازه.")

    user_counts[m.chat.id] = n

    bot.send_message(
        m.chat.id,
        f"✅ تعداد ثبت شد: {n}\n\n"
        f"حالا نوع آیدی رو انتخاب کن:",
        reply_markup=type_menu()
    )


# ================= انتخاب نوع و تولید =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("t"))
def handle_type(c):
    chat_id = c.from_user.id
    n = user_counts.get(chat_id, 0)

    if n == 0:
        bot.answer_callback_query(c.id, "اول تعداد رو وارد کن ❌")
        return

    type_map = {
        "t1": ("۵ رقمی انگلیسی", gen_english),
        "t2": ("انگلیسی + خط تیره", gen_english_dash),
        "t3": ("مخلوط (حرف+عدد+خط تیره)", gen_mix),
        "t4": ("انگلیسی + عدد", gen_english_number),
    }

    title, func = type_map[c.data]
    bot.answer_callback_query(c.id, f"در حال تولید {n} آیدی... 🍃")

    ids = generate_ids(func, n)

    # مرتب‌سازی حروف‌به‌حروف → ظاهر متقارن‌تر
    ids.sort()

    # هر آیدی داخل <code> → فونت ثابت + هم‌عرض + تراز عالی
    body = "\n".join(f"<code>@{i}</code>" for i in ids)

    header = (
        "🍃 <b>آیدی‌های پیدا شده مناسب برای شما</b>\n"
        f"نوع: {title}\n"
        f"تعداد: {n}\n"
        "─────────────────\n"
    )
    footer = f"\n─────────────────\n✨ ساخته شده توسط\n{CREATOR}"

    full = header + body + footer

    try:
        if len(full) <= 4000:
            bot.send_message(chat_id, full, parse_mode="HTML")
        else:
            lines = [f"<code>@{i}</code>" for i in ids]
            part = header
            for line in lines:
                if len(part) + len(line) + 1 > 3800:
                    bot.send_message(chat_id, part, parse_mode="HTML")
                    part = ""
                part += line + "\n"
            part += footer
            bot.send_message(chat_id, part, parse_mode="HTML")

        bot.send_message(
            chat_id,
            "می‌خوای دوباره کرک کنی؟ 👇",
            reply_markup=main_menu()
        )
        print(f">>> SENT {len(ids)} ids ✅")
    except Exception as e:
        print("SEND ERROR:", e)
        bot.send_message(chat_id, f"خطا: {e}")


print("🍃 ربات روشن شد...")
bot.infinity_polling()